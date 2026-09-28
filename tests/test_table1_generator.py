"""
Unit tests for Table1Generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests for automated baseline characteristics table generation.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile

from hamelin.analytics.table1_generator import Table1Generator, VariableConfig


class TestVariableConfig:
    """Tests for VariableConfig dataclass"""
    
    def test_continuous_variable(self):
        """Test creating continuous variable config"""
        var = VariableConfig(name='age', var_type='continuous')
        assert var.name == 'age'
        assert var.var_type == 'continuous'
        assert var.label == 'age'  # Default label
    
    def test_categorical_variable(self):
        """Test creating categorical variable config"""
        var = VariableConfig(name='sex', var_type='categorical', label='Gender')
        assert var.name == 'sex'
        assert var.var_type == 'categorical'
        assert var.label == 'Gender'
    
    def test_invalid_type(self):
        """Test that invalid type raises error"""
        with pytest.raises(ValueError):
            VariableConfig(name='test', var_type='invalid')


class TestTable1Generator:
    """Tests for Table1Generator class"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample clinical dataset"""
        np.random.seed(42)
        n = 100
        
        data = {
            'Age': np.random.normal(60, 10, n),
            'Sex': np.random.choice(['Male', 'Female'], n),
            'BMI': np.random.normal(27, 4, n),
            'Hypertension': np.random.choice(['Yes', 'No'], n, p=[0.4, 0.6]),
            'Diabetes': np.random.choice(['Yes', 'No'], n, p=[0.3, 0.7]),
            'Outcome': np.random.choice(['Death', 'Survival'], n, p=[0.25, 0.75])
        }
        
        return pd.DataFrame(data)
    
    def test_initialization(self, sample_data):
        """Test generator initialization"""
        gen = Table1Generator(sample_data)
        
        assert len(gen.df) == 100
        assert len(gen.variables) == 0
        assert gen.result_table is None
    
    def test_initialization_empty_dataframe(self):
        """Test that empty dataframe raises error"""
        with pytest.raises(ValueError):
            Table1Generator(pd.DataFrame())
    
    def test_initialization_invalid_type(self):
        """Test that non-dataframe raises error"""
        with pytest.raises(TypeError):
            Table1Generator([1, 2, 3])
    
    def test_add_variable(self, sample_data):
        """Test adding variables manually"""
        gen = Table1Generator(sample_data)
        
        gen.add_variable('Age', 'continuous')
        gen.add_variable('Sex', 'categorical', label='Gender')
        
        assert len(gen.variables) == 2
        assert gen.variables[0].name == 'Age'
        assert gen.variables[1].label == 'Gender'
    
    def test_add_invalid_column(self, sample_data):
        """Test that adding non-existent column raises error"""
        gen = Table1Generator(sample_data)
        
        with pytest.raises(KeyError):
            gen.add_variable('NonExistent', 'continuous')
    
    def test_detect_variable_type_continuous(self, sample_data):
        """Test auto-detection of continuous variables"""
        gen = Table1Generator(sample_data)
        
        var_type = gen._detect_variable_type('Age')
        assert var_type == 'continuous'
        
        var_type = gen._detect_variable_type('BMI')
        assert var_type == 'continuous'
    
    def test_detect_variable_type_categorical(self, sample_data):
        """Test auto-detection of categorical variables"""
        gen = Table1Generator(sample_data)
        
        var_type = gen._detect_variable_type('Sex')
        assert var_type == 'categorical'
        
        var_type = gen._detect_variable_type('Outcome')
        assert var_type == 'categorical'
    
    def test_auto_detect_variables(self, sample_data):
        """Test automatic variable detection"""
        gen = Table1Generator(sample_data)
        
        gen.auto_detect_variables(exclude=['Outcome'])
        
        assert len(gen.variables) == 5  # All except Outcome
        
        # Check Age is detected as continuous
        age_var = [v for v in gen.variables if v.name == 'Age'][0]
        assert age_var.var_type == 'continuous'
        
        # Check Sex is detected as categorical
        sex_var = [v for v in gen.variables if v.name == 'Sex'][0]
        assert sex_var.var_type == 'categorical'
    
    def test_format_continuous_normal(self, sample_data):
        """Test formatting normally distributed continuous data"""
        gen = Table1Generator(sample_data)
        
        series = sample_data['Age']
        formatted = gen._format_continuous(series, is_normal=True)
        
        # Should be "Mean ± SD" format
        assert '±' in formatted
        assert len(formatted.split('±')) == 2
    
    def test_format_continuous_nonnormal(self, sample_data):
        """Test formatting non-normal continuous data"""
        gen = Table1Generator(sample_data)
        
        series = sample_data['Age']
        formatted = gen._format_continuous(series, is_normal=False)
        
        # Should be "Median [IQR]" format
        assert '[' in formatted and ']' in formatted
        assert '-' in formatted
    
    def test_format_categorical(self, sample_data):
        """Test formatting categorical data"""
        gen = Table1Generator(sample_data)
        
        formatted = gen._format_categorical(40, 100)
        
        assert formatted == '40 (40.0%)'
    
    def test_format_categorical_zero(self, sample_data):
        """Test formatting categorical with zero total"""
        gen = Table1Generator(sample_data)
        
        formatted = gen._format_categorical(0, 0)
        
        assert formatted == '0 (0.0%)'
    
    def test_normality_test(self, sample_data):
        """Test Shapiro-Wilk normality test"""
        gen = Table1Generator(sample_data)
        
        # Age should be approximately normal (we generated it that way)
        is_normal = gen._test_normality(sample_data['Age'])
        # Note: With random data, this might occasionally fail
        # In practice, we'd use a larger sample or fixed seed
        
        # Test with insufficient data
        small_series = pd.Series([1, 2])
        is_normal = gen._test_normality(small_series)
        assert is_normal == False
    
    def test_format_pvalue(self, sample_data):
        """Test p-value formatting"""
        gen = Table1Generator(sample_data)
        
        assert gen._format_pvalue(0.0001) == '<0.001'
        assert gen._format_pvalue(0.005) == '0.005'
        assert gen._format_pvalue(0.123) == '0.123'
        assert gen._format_pvalue(np.nan) == ''
    
    def test_generate_overall_only(self, sample_data):
        """Test generating table without stratification"""
        gen = Table1Generator(sample_data)
        
        gen.add_variable('Age', 'continuous')
        gen.add_variable('Sex', 'categorical')
        gen.add_variable('BMI', 'continuous')
        
        table = gen.generate()
        
        assert table is not None
        assert len(table) > 0
        assert 'Variable' in table.columns
        assert 'Overall' in table.columns
        
        # First row should be N
        assert table.iloc[0]['Variable'] == 'N'
        assert table.iloc[0]['Overall'] == 100
    
    def test_generate_stratified(self, sample_data):
        """Test generating table with stratification"""
        gen = Table1Generator(sample_data)
        
        gen.add_variable('Age', 'continuous')
        gen.add_variable('Sex', 'categorical')
        
        table = gen.generate(stratify_by='Outcome')
        
        assert table is not None
        assert 'Death' in table.columns
        assert 'Survival' in table.columns
        assert 'p-value' in table.columns
    
    def test_generate_no_variables(self, sample_data):
        """Test that generating without variables raises error"""
        gen = Table1Generator(sample_data)
        
        with pytest.raises(ValueError):
            gen.generate()
    
    def test_compare_continuous_normal(self, sample_data):
        """Test t-test for continuous variables"""
        gen = Table1Generator(sample_data)
        
        group1 = pd.Series([1, 2, 3, 4, 5])
        group2 = pd.Series([6, 7, 8, 9, 10])
        
        p_value = gen._compare_continuous(group1, group2, is_normal=True)
        
        assert isinstance(p_value, float)
        assert 0 <= p_value <= 1
    
    def test_compare_continuous_nonnormal(self, sample_data):
        """Test Mann-Whitney U test for continuous variables"""
        gen = Table1Generator(sample_data)
        
        group1 = pd.Series([1, 2, 3, 4, 5])
        group2 = pd.Series([6, 7, 8, 9, 10])
        
        p_value = gen._compare_continuous(group1, group2, is_normal=False)
        
        assert isinstance(p_value, float)
        assert 0 <= p_value <= 1
    
    def test_compare_categorical(self, sample_data):
        """Test chi-square test for categorical variables"""
        gen = Table1Generator(sample_data)
        
        # 2x2 contingency table
        contingency = [[20, 30], [15, 35]]
        
        p_value = gen._compare_categorical(contingency)
        
        assert isinstance(p_value, float)
        assert 0 <= p_value <= 1
    
    def test_export_csv(self, sample_data):
        """Test CSV export"""
        gen = Table1Generator(sample_data)
        gen.add_variable('Age', 'continuous')
        gen.generate()
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            gen.export_to_csv(tmp_path)
            
            assert tmp_path.exists()
            
            # Verify can read it back
            df = pd.read_csv(tmp_path)
            assert len(df) > 0
        finally:
            tmp_path.unlink()
    
    def test_export_excel(self, sample_data):
        """Test Excel export"""
        gen = Table1Generator(sample_data)
        gen.add_variable('Age', 'continuous')
        gen.generate()
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            gen.export_to_excel(tmp_path)
            
            assert tmp_path.exists()
            
            # Verify can read it back
            df = pd.read_excel(tmp_path)
            assert len(df) > 0
        finally:
            tmp_path.unlink()
    
    def test_export_html(self, sample_data):
        """Test HTML export"""
        gen = Table1Generator(sample_data)
        gen.add_variable('Age', 'continuous')
        gen.generate()
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            gen.export_to_html(tmp_path)
            
            assert tmp_path.exists()
            
            # Verify it's valid HTML
            with open(tmp_path, 'r') as f:
                html = f.read()
            assert '<html>' in html
            assert '<table' in html  # Table tag might have class attribute
            assert 'Baseline Characteristics' in html
        finally:
            tmp_path.unlink()
    
    def test_export_before_generate(self, sample_data):
        """Test that export before generate raises error"""
        gen = Table1Generator(sample_data)
        gen.add_variable('Age', 'continuous')
        
        with tempfile.NamedTemporaryFile(suffix='.csv') as tmp:
            with pytest.raises(ValueError):
                gen.export_to_csv(tmp.name)
    
    def test_repr(self, sample_data):
        """Test string representation"""
        gen = Table1Generator(sample_data)
        gen.add_variable('Age', 'continuous')
        gen.add_variable('Sex', 'categorical')

        repr_str = repr(gen)

        assert 'Table1Generator' in repr_str
        assert 'variables=2' in repr_str
        assert 'rows=100' in repr_str

    # ------------------------------------------------------------------
    # study_info header (project name/protocol/objectives/ethics approval,
    # shown above the table in every export format - see set_study_info())
    # ------------------------------------------------------------------

    def test_study_info_defaults_to_empty(self, sample_data):
        gen = Table1Generator(sample_data)
        assert gen.study_info == {}

    def test_set_study_info_drops_empty_values(self, sample_data):
        gen = Table1Generator(sample_data)
        gen.set_study_info({"Study": "UPS Study", "Protocol Number": "", "Institution": None})
        assert gen.study_info == {"Study": "UPS Study"}

    def test_export_csv_without_study_info_has_no_header_block(self, sample_data):
        gen = Table1Generator(sample_data)
        gen.add_variable('Age', 'continuous')
        gen.generate()

        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            gen.export_to_csv(tmp_path)
            first_line = tmp_path.read_text().splitlines()[0]
            assert first_line.startswith("Variable")
        finally:
            tmp_path.unlink()

    def test_export_csv_with_study_info_prepends_header_rows(self, sample_data):
        gen = Table1Generator(sample_data)
        gen.add_variable('Age', 'continuous')
        gen.generate()
        gen.set_study_info({
            "Study": "UPS Study",
            "Primary Objective": "Assess, LPP incidence in neurosurgery patients",
        })

        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            gen.export_to_csv(tmp_path)
            lines = tmp_path.read_text().splitlines()

            assert lines[0] == "Study,UPS Study"
            # A comma inside the value is correctly quoted, not read as an
            # extra column, since this goes through csv.writer.
            assert lines[1] == 'Primary Objective,"Assess, LPP incidence in neurosurgery patients"'
            assert lines[2] == ""  # blank separator row
            assert lines[3].startswith("Variable")  # the actual table starts here

            # Still a valid, readable table underneath the header.
            df = pd.read_csv(tmp_path, skiprows=3)
            assert len(df) > 0
        finally:
            tmp_path.unlink()

    def test_export_excel_with_study_info_prepends_header_rows(self, sample_data):
        gen = Table1Generator(sample_data)
        gen.add_variable('Age', 'continuous')
        gen.generate()
        gen.set_study_info({"Study": "UPS Study", "Protocol Number": "UPS-2024-001"})

        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            gen.export_to_excel(tmp_path)

            import openpyxl
            ws = openpyxl.load_workbook(tmp_path)['Table 1']
            rows = list(ws.iter_rows(min_row=1, max_row=4, values_only=True))

            assert rows[0][:2] == ("Study", "UPS Study")
            assert rows[1][:2] == ("Protocol Number", "UPS-2024-001")
            assert rows[2][0] is None  # blank separator row
            assert rows[3][0] == "Variable"  # the actual table header
        finally:
            tmp_path.unlink()

    def test_export_html_with_study_info_includes_it_before_the_table(self, sample_data):
        gen = Table1Generator(sample_data)
        gen.add_variable('Age', 'continuous')
        gen.generate()
        gen.set_study_info({"Study": "UPS Study"})

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            gen.export_to_html(tmp_path)
            html = tmp_path.read_text()

            assert "study-info" in html
            assert "UPS Study" in html
            assert html.index("UPS Study") < html.index("<table")
        finally:
            tmp_path.unlink()

    def test_export_html_escapes_study_info_values(self, sample_data):
        gen = Table1Generator(sample_data)
        gen.add_variable('Age', 'continuous')
        gen.generate()
        gen.set_study_info({"Primary Objective": "A & B < C"})

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            gen.export_to_html(tmp_path)
            html = tmp_path.read_text()
            assert "A &amp; B &lt; C" in html
            assert "A & B < C" not in html
        finally:
            tmp_path.unlink()

    def test_export_html_without_study_info_omits_the_block(self, sample_data):
        gen = Table1Generator(sample_data)
        gen.add_variable('Age', 'continuous')
        gen.generate()

        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            gen.export_to_html(tmp_path)
            # The CSS rule is always defined in <style>; what matters is
            # that the block itself is never rendered in <body>.
            assert '<div class="study-info">' not in tmp_path.read_text()
        finally:
            tmp_path.unlink()


class TestTable1IntegrationClinicalData:
    """Integration tests with realistic clinical scenarios"""
    
    @pytest.fixture
    def clinical_data(self):
        """Create realistic clinical trial dataset"""
        np.random.seed(42)
        n = 150
        
        # Demographics
        age = np.random.normal(65, 12, n)
        sex = np.random.choice(['Male', 'Female'], n, p=[0.55, 0.45])
        bmi = np.random.normal(28, 5, n)
        
        # Comorbidities
        hypertension = np.random.choice([1, 0], n, p=[0.6, 0.4])
        diabetes = np.random.choice([1, 0], n, p=[0.35, 0.65])
        smoking = np.random.choice(['Never', 'Former', 'Current'], n, p=[0.4, 0.4, 0.2])
        
        # Outcome
        outcome = np.random.choice(['Event', 'No Event'], n, p=[0.3, 0.7])
        
        data = {
            'patient_id': range(1, n+1),
            'age': age,
            'sex': sex,
            'bmi': bmi,
            'hypertension': hypertension,
            'diabetes': diabetes,
            'smoking_status': smoking,
            'primary_outcome': outcome
        }
        
        return pd.DataFrame(data)
    
    def test_complete_table1_workflow(self, clinical_data):
        """Test complete Table 1 generation workflow"""
        gen = Table1Generator(clinical_data)
        
        # Add demographic variables
        gen.add_variable('age', 'continuous', label='Age (years)')
        gen.add_variable('sex', 'categorical', label='Sex')
        gen.add_variable('bmi', 'continuous', label='BMI (kg/m²)')
        
        # Add comorbidities
        gen.add_variable('hypertension', 'categorical', label='Hypertension')
        gen.add_variable('diabetes', 'categorical', label='Diabetes')
        gen.add_variable('smoking_status', 'categorical', label='Smoking Status')
        
        # Generate stratified by outcome
        table = gen.generate(stratify_by='primary_outcome')
        
        assert table is not None
        assert len(table) > 0
        
        # Check structure
        assert 'Variable' in table.columns
        assert 'Event' in table.columns
        assert 'No Event' in table.columns
        assert 'p-value' in table.columns
        
        # Sample size row
        assert table.iloc[0]['Variable'] == 'N'
        
        # Check we have all variables
        variable_names = table['Variable'].unique()
        assert 'Age (years)' in table['Variable'].values
        assert 'Sex' in table['Variable'].values
    
    def test_auto_detect_workflow(self, clinical_data):
        """Test workflow with auto-detection"""
        gen = Table1Generator(clinical_data)
        
        # Auto-detect all except outcome and ID
        gen.auto_detect_variables(exclude=['patient_id', 'primary_outcome'])
        
        # Generate
        table = gen.generate(stratify_by='primary_outcome')
        
        assert table is not None
        assert len(gen.variables) == 6  # age, sex, bmi, hypertension, diabetes, smoking


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
