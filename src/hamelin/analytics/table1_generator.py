"""
Table 1 Generator
~~~~~~~~~~~~~~~~~

Automated generation of baseline characteristics tables for medical publications.
Produces publication-ready tables in APA/NEJM style with appropriate statistical tests.

Features:
- Auto-detection of variable types (continuous/categorical)
- Normality testing (Shapiro-Wilk) to choose Mean±SD vs Median[IQR]
- Stratification by outcome variable
- Statistical comparisons (t-test, chi-square, Mann-Whitney)
- Export to CSV, Excel, and styled HTML (for Word)
"""

import pandas as pd
import numpy as np
from typing import Optional, Union, List, Dict
from dataclasses import dataclass
from scipy import stats
from pathlib import Path

from hamelin.utils.logger import log
from hamelin.utils.theme_colors import colors


@dataclass
class VariableConfig:
    """Configuration for a variable in Table 1"""
    name: str
    var_type: str  # 'continuous' or 'categorical'
    label: Optional[str] = None  # Display name
    grouping: Optional[str] = None  # For categorical: how to group
    
    def __post_init__(self):
        if self.var_type not in ['continuous', 'categorical']:
            raise ValueError(f"var_type must be 'continuous' or 'categorical', got '{self.var_type}'")
        
        # Use column name as label if not provided
        if self.label is None:
            self.label = self.name


class Table1Generator:
    """
    Automated baseline characteristics table generator.
    
    Usage:
        >>> df = pd.read_csv('data.csv')
        >>> gen = Table1Generator(df)
        >>> gen.add_variable('Age', 'continuous')
        >>> gen.add_variable('Sex', 'categorical')
        >>> table = gen.generate(stratify_by='Outcome')
        >>> gen.export_to_html('table1.html')
    
    Attributes:
        df (pd.DataFrame): Source dataframe
        variables (List[VariableConfig]): Variables to include in table
        result_table (pd.DataFrame): Generated table (after calling generate())
    """
    
    def __init__(self, dataframe: pd.DataFrame):
        """
        Initialize Table 1 Generator.
        
        Args:
            dataframe: Source data with patients as rows, variables as columns
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("dataframe must be a pandas DataFrame")
        
        if len(dataframe) == 0:
            raise ValueError("dataframe cannot be empty")
        
        self.df = dataframe.copy()
        self.variables: List[VariableConfig] = []
        self.result_table: Optional[pd.DataFrame] = None
        self.stratify_column: Optional[str] = None
        # Optional {label: value} header shown above the table in every
        # export - see set_study_info().
        self.study_info: Dict[str, str] = {}

        log.info(f"Table1Generator initialized with {len(self.df)} rows, {len(self.df.columns)} columns")

    def set_study_info(self, info: Dict[str, Optional[str]]) -> None:
        """Study identity/provenance to show above the table in every
        export (CSV, Excel, HTML) - project name, protocol number, primary
        objective, ethics approval. None of it feeds into the statistics;
        it's what a reviewer or co-author needs to know which study this
        table came from without the file having to travel alongside a
        separate note. Keys with an empty/None value are skipped, so a
        project that hasn't filled in e.g. ethics approval yet just omits
        that line instead of showing it blank."""
        self.study_info = {k: v for k, v in info.items() if v}
    
    def add_variable(
        self, 
        name: str, 
        var_type: str, 
        label: Optional[str] = None,
        grouping: Optional[str] = None
    ) -> None:
        """
        Add a variable to include in Table 1.
        
        Args:
            name: Column name in dataframe
            var_type: 'continuous' or 'categorical'
            label: Display name (default: use column name)
            grouping: For categorical variables, how to group values
        
        Raises:
            KeyError: If column name not found in dataframe
            ValueError: If var_type is invalid
        """
        if name not in self.df.columns:
            raise KeyError(f"Column '{name}' not found in dataframe")
        
        var_config = VariableConfig(
            name=name,
            var_type=var_type,
            label=label,
            grouping=grouping
        )
        
        self.variables.append(var_config)
        log.debug(f"Added variable: {name} ({var_type})")
    
    def auto_detect_variables(self, exclude: Optional[List[str]] = None) -> None:
        """
        Automatically detect and add all variables from dataframe.
        
        Uses heuristics to determine if variable is continuous or categorical:
        - Numeric with >10 unique values → continuous
        - Numeric with ≤10 unique values → categorical
        - Object/string → categorical
        - Boolean → categorical
        
        Args:
            exclude: List of column names to exclude from detection
        """
        if exclude is None:
            exclude = []
        
        for col in self.df.columns:
            if col in exclude:
                continue
            
            var_type = self._detect_variable_type(col)
            self.add_variable(col, var_type)
        
        log.info(f"Auto-detected {len(self.variables)} variables")
    
    def _detect_variable_type(self, column: str) -> str:
        """
        Detect if a variable is continuous or categorical.
        
        Args:
            column: Column name in dataframe
        
        Returns:
            'continuous' or 'categorical'
        """
        series = self.df[column]
        
        # Check data type
        if pd.api.types.is_numeric_dtype(series):
            unique_count = series.nunique()
            
            # Heuristic: >10 unique values → continuous
            if unique_count > 10:
                return 'continuous'
            else:
                return 'categorical'
        else:
            # Non-numeric → categorical
            return 'categorical'
    
    def generate(self, stratify_by: Optional[str] = None) -> pd.DataFrame:
        """
        Generate the baseline characteristics table.
        
        Args:
            stratify_by: Column name to stratify by (e.g., outcome variable)
                        If None, generates overall statistics only
        
        Returns:
            DataFrame with formatted statistics
        
        Raises:
            ValueError: If no variables have been added
        """
        if len(self.variables) == 0:
            raise ValueError("No variables added. Use add_variable() or auto_detect_variables()")
        
        log.info(f"Generating Table 1 with {len(self.variables)} variables")
        
        self.stratify_column = stratify_by
        
        # Build table rows
        rows = []
        
        # Sample size row
        if stratify_by is None:
            n_row = {'Variable': 'N', 'Overall': len(self.df), 'p-value': ''}
        else:
            groups = self.df[stratify_by].unique()
            n_row = {'Variable': 'N'}
            for group in sorted([g for g in groups if pd.notna(g)]):
                group_df = self.df[self.df[stratify_by] == group]
                n_row[str(group)] = len(group_df)
            n_row['p-value'] = ''
        
        rows.append(n_row)
        
        # Process each variable
        for var in self.variables:
            if var.var_type == 'continuous':
                var_rows = self._process_continuous(var, stratify_by)
            else:
                var_rows = self._process_categorical(var, stratify_by)
            
            rows.extend(var_rows)
        
        # Create result dataframe
        self.result_table = pd.DataFrame(rows)
        
        log.info(f"Table 1 generated successfully with {len(self.result_table)} rows")
        return self.result_table
    
    def _process_continuous(
        self, 
        var: VariableConfig, 
        stratify_by: Optional[str]
    ) -> List[Dict]:
        """
        Process a continuous variable for Table 1.
        
        Args:
            var: Variable configuration
            stratify_by: Stratification column (or None)
        
        Returns:
            List of row dictionaries
        """
        rows = []
        series = self.df[var.name].dropna()
        
        # Test for normality
        is_normal = self._test_normality(series)
        
        if stratify_by is None:
            # Overall statistics only
            formatted = self._format_continuous(series, is_normal)
            rows.append({
                'Variable': var.label,
                'Overall': formatted,
                'p-value': ''
            })
        else:
            # Stratified statistics
            groups = sorted([g for g in self.df[stratify_by].unique() if pd.notna(g)])
            row = {'Variable': var.label}
            
            group_data = []
            for group in groups:
                group_series = self.df[self.df[stratify_by] == group][var.name].dropna()
                formatted = self._format_continuous(group_series, is_normal)
                row[str(group)] = formatted
                group_data.append(group_series)
            
            # Statistical test
            if len(groups) == 2:
                p_value = self._compare_continuous(group_data[0], group_data[1], is_normal)
                row['p-value'] = self._format_pvalue(p_value)
            else:
                row['p-value'] = ''
            
            rows.append(row)
        
        return rows
    
    def _process_categorical(
        self, 
        var: VariableConfig, 
        stratify_by: Optional[str]
    ) -> List[Dict]:
        """
        Process a categorical variable for Table 1.
        
        Args:
            var: Variable configuration
            stratify_by: Stratification column (or None)
        
        Returns:
            List of row dictionaries (one per category)
        """
        rows = []
        series = self.df[var.name].dropna()
        categories = sorted([c for c in series.unique() if pd.notna(c)])
        
        if stratify_by is None:
            # Overall statistics
            for i, category in enumerate(categories):
                count = (series == category).sum()
                total = len(series)
                formatted = self._format_categorical(count, total)
                
                # First row shows variable name
                var_name = var.label if i == 0 else ''
                rows.append({
                    'Variable': f"{var_name}",
                    '  Category': f"  {category}",
                    'Overall': formatted,
                    'p-value': ''
                })
        else:
            # Stratified statistics
            groups = sorted([g for g in self.df[stratify_by].unique() if pd.notna(g)])
            
            # Prepare contingency table for chi-square test
            contingency = []
            for category in categories:
                cat_counts = []
                for group in groups:
                    group_df = self.df[self.df[stratify_by] == group]
                    count = (group_df[var.name] == category).sum()
                    cat_counts.append(count)
                contingency.append(cat_counts)
            
            # Chi-square test
            if len(groups) == 2 and len(categories) >= 2:
                p_value = self._compare_categorical(contingency)
            else:
                p_value = None
            
            # Format rows
            for i, category in enumerate(categories):
                row = {'Variable': var.label if i == 0 else '', '  Category': f"  {category}"}
                
                for j, group in enumerate(groups):
                    group_df = self.df[self.df[stratify_by] == group]
                    count = (group_df[var.name] == category).sum()
                    total = len(group_df[var.name].dropna())
                    formatted = self._format_categorical(count, total)
                    row[str(group)] = formatted
                
                # p-value only on first row
                if i == 0 and p_value is not None:
                    row['p-value'] = self._format_pvalue(p_value)
                else:
                    row['p-value'] = ''
                
                rows.append(row)
        
        return rows
    
    def _format_continuous(self, series: pd.Series, is_normal: bool) -> str:
        """
        Format continuous variable statistics.
        
        Args:
            series: Data series
            is_normal: Whether data is normally distributed
        
        Returns:
            Formatted string: "Mean ± SD" or "Median [IQR]"
        """
        if len(series) == 0:
            return "N/A"
        
        if is_normal:
            # Mean ± SD
            mean = series.mean()
            std = series.std()
            return f"{mean:.2f} ± {std:.2f}"
        else:
            # Median [IQR]
            median = series.median()
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            return f"{median:.2f} [{q1:.2f}-{q3:.2f}]"
    
    def _format_categorical(self, count: int, total: int) -> str:
        """
        Format categorical variable statistics.
        
        Args:
            count: Number in category
            total: Total number
        
        Returns:
            Formatted string: "n (%)"
        """
        if total == 0:
            return "0 (0.0%)"
        
        percentage = (count / total) * 100
        return f"{count} ({percentage:.1f}%)"
    
    def _test_normality(self, series: pd.Series, alpha: float = 0.05) -> bool:
        """
        Test if data is normally distributed using Shapiro-Wilk test.
        
        Args:
            series: Data series
            alpha: Significance level (default: 0.05)
        
        Returns:
            True if data appears normally distributed
        """
        if len(series) < 3:
            # Not enough data for test
            return False
        
        if len(series) > 5000:
            # Shapiro-Wilk not reliable for large samples
            # Use skewness and kurtosis instead
            skew = stats.skew(series)
            kurt = stats.kurtosis(series)
            return abs(skew) < 2 and abs(kurt) < 7
        
        try:
            stat, p_value = stats.shapiro(series)
            return p_value >= alpha
        except Exception as e:
            log.warning(f"Normality test failed: {e}")
            return False
    
    def _compare_continuous(
        self, 
        group1: pd.Series, 
        group2: pd.Series, 
        is_normal: bool
    ) -> float:
        """
        Compare two continuous groups statistically.
        
        Args:
            group1: First group data
            group2: Second group data
            is_normal: Whether data is normally distributed
        
        Returns:
            p-value from statistical test
        """
        if len(group1) < 2 or len(group2) < 2:
            return np.nan
        
        try:
            if is_normal:
                # Student's t-test
                stat, p_value = stats.ttest_ind(group1, group2, nan_policy='omit')
            else:
                # Mann-Whitney U test (non-parametric)
                stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
            
            return p_value
        except Exception as e:
            log.warning(f"Statistical comparison failed: {e}")
            return np.nan
    
    def _compare_categorical(self, contingency: List[List[int]]) -> float:
        """
        Compare categorical groups using chi-square test.
        
        Args:
            contingency: Contingency table as list of lists
        
        Returns:
            p-value from chi-square test
        """
        try:
            contingency_array = np.array(contingency)
            
            # Check if valid for chi-square (expected frequency >= 5)
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_array)
            
            if np.any(expected < 5):
                log.warning("Low expected frequencies, consider Fisher's exact test")
            
            return p_value
        except Exception as e:
            log.warning(f"Chi-square test failed: {e}")
            return np.nan
    
    def _format_pvalue(self, p_value: float) -> str:
        """
        Format p-value for display.
        
        Args:
            p_value: Statistical p-value
        
        Returns:
            Formatted string (e.g., "0.001", "<0.001", "0.450")
        """
        if pd.isna(p_value):
            return ''
        
        if p_value < 0.001:
            return '<0.001'
        elif p_value < 0.01:
            return f'{p_value:.3f}'
        else:
            return f'{p_value:.3f}'
    
    def export_to_csv(self, filepath: Union[str, Path]) -> None:
        """
        Export table to CSV file, with the study_info header (if set) as
        plain "label,value" rows above the table.

        Args:
            filepath: Output file path

        Raises:
            ValueError: If table not generated yet
        """
        if self.result_table is None:
            raise ValueError("Table not generated yet. Call generate() first")

        filepath = Path(filepath)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if self.study_info:
                import csv as csv_module
                writer = csv_module.writer(f)
                for label, value in self.study_info.items():
                    writer.writerow([label, value])
                writer.writerow([])
            self.result_table.to_csv(f, index=False)
        log.info(f"Table exported to CSV: {filepath}")

    def export_to_excel(self, filepath: Union[str, Path]) -> None:
        """
        Export table to Excel file with formatting, with the study_info
        header (if set) as rows above the table in the same sheet.

        Args:
            filepath: Output file path

        Raises:
            ValueError: If table not generated yet
        """
        if self.result_table is None:
            raise ValueError("Table not generated yet. Call generate() first")

        filepath = Path(filepath)

        # Export with basic formatting
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            start_row = 0
            if self.study_info:
                info_rows = [[label, value] for label, value in self.study_info.items()]
                pd.DataFrame(info_rows).to_excel(
                    writer, sheet_name='Table 1', index=False, header=False, startrow=0
                )
                start_row = len(info_rows) + 1
            self.result_table.to_excel(writer, sheet_name='Table 1', index=False, startrow=start_row)

        log.info(f"Table exported to Excel: {filepath}")
    
    def export_to_html(self, filepath: Union[str, Path]) -> None:
        """
        Export table to styled HTML file (suitable for copying to Word).
        
        Args:
            filepath: Output file path
        
        Raises:
            ValueError: If table not generated yet
        """
        if self.result_table is None:
            raise ValueError("Table not generated yet. Call generate() first")
        
        filepath = Path(filepath)
        
        # Create styled HTML
        html = self._generate_styled_html()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        log.info(f"Table exported to HTML: {filepath}")
    
    def _generate_styled_html(self) -> str:
        """
        Generate styled HTML for the table.
        
        Returns:
            HTML string with CSS styling
        """
        # CSS styling for professional appearance. Colours are explicit
        # here rather than left to inherit from whatever widget ends up
        # displaying this HTML (a QTextBrowser) - that widget has no
        # styling of its own, so on a system whose native Qt palette
        # defaults to dark, unset colours here rendered as invisible
        # (near-black) text on that widget's own (also unstyled, near-
        # black) background.
        c = colors()
        css = f"""
        <style>
            body {{
                font-family: 'Times New Roman', Times, serif;
                font-size: 12pt;
                margin: 20px;
                color: {c.text_primary};
                background: {c.card_background};
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
                color: {c.text_primary};
            }}
            th {{
                border-top: 2px solid {c.text_primary};
                border-bottom: 1px solid {c.text_primary};
                padding: 8px;
                text-align: left;
                font-weight: bold;
            }}
            td {{
                border: none;
                padding: 6px 8px;
                text-align: left;
            }}
            tr:last-child td {{
                border-bottom: 2px solid {c.text_primary};
            }}
            .category {{
                padding-left: 20px;
            }}
            .study-info {{
                font-size: 10pt;
                margin-bottom: 16px;
            }}
            .study-info div {{
                margin: 2px 0;
            }}
        </style>
        """

        # Convert table to HTML. escape=True (pandas' default) so a value
        # like the formatted p-value "<0.001" renders as literal text
        # instead of being parsed as the start of an HTML tag, which
        # silently swallowed the cell.
        html_table = self.result_table.to_html(index=False, escape=True, border=0)

        # Study identity/provenance block, if set - see set_study_info().
        # html.escape on both label and value: a free-text field like the
        # primary objective can legitimately contain "<" or "&".
        study_info_html = ""
        if self.study_info:
            import html as html_module
            lines = "".join(
                f"<div><b>{html_module.escape(str(label))}:</b> {html_module.escape(str(value))}</div>"
                for label, value in self.study_info.items()
            )
            study_info_html = f'<div class="study-info">{lines}</div>'

        # Full HTML document
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Table 1: Baseline Characteristics</title>
            {css}
        </head>
        <body>
            <h2>Table 1: Baseline Characteristics</h2>
            {study_info_html}
            {html_table}
            <p><small>
            Continuous variables presented as Mean ± SD (normal distribution) or Median [IQR] (non-normal distribution).
            Categorical variables presented as n (%).
            </small></p>
        </body>
        </html>
        """

        return html
    
    def __repr__(self) -> str:
        """String representation"""
        n_vars = len(self.variables)
        n_rows = len(self.df)
        return f"Table1Generator(variables={n_vars}, rows={n_rows})"
