"""
Statistical Calculator for Table 1 Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides statistical calculations needed for clinical Table 1 generation.

Features:
- Descriptive statistics for continuous variables
- Frequency distributions for categorical variables
- Statistical tests (t-test, Mann-Whitney, chi-square, Fisher's)
- Confidence intervals
- Missing data handling

This module is specifically designed for clinical research Table 1 generation,
following standard medical publication guidelines.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from scipy import stats
import warnings

from hamelin.utils.logger import log


class StatisticalCalculator:
    """
    Statistical calculator for Table 1 generation.
    
    Provides methods for calculating descriptive statistics and
    performing statistical tests commonly used in clinical research.
    """
    
    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize statistical calculator.
        
        Args:
            confidence_level: Confidence level for intervals (default 0.95 for 95% CI)
        """
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level
    
    # =========================================================================
    # CONTINUOUS VARIABLES - Descriptive Statistics
    # =========================================================================
    
    def describe_continuous(
        self,
        data: pd.Series,
        include_ci: bool = True,
        decimal_places: int = 2
    ) -> Dict[str, Any]:
        """
        Calculate descriptive statistics for continuous variable.
        
        Args:
            data: Pandas Series with numeric data
            include_ci: Include confidence intervals
            decimal_places: Number of decimal places
            
        Returns:
            Dictionary with statistics:
            - n: Count of non-missing values
            - mean: Mean value
            - std: Standard deviation
            - median: Median value
            - q1: First quartile
            - q3: Third quartile
            - iqr: Interquartile range
            - min: Minimum value
            - max: Maximum value
            - ci_low: Lower confidence interval (if include_ci=True)
            - ci_high: Upper confidence interval (if include_ci=True)
            - missing: Count of missing values
        """
        # Remove missing values
        clean_data = data.dropna()
        n = len(clean_data)
        missing = len(data) - n
        
        if n == 0:
            log.warning(f"No valid data points for continuous variable")
            return {
                'n': 0,
                'missing': missing,
                'mean': None,
                'std': None,
                'median': None,
                'q1': None,
                'q3': None,
                'iqr': None,
                'min': None,
                'max': None
            }
        
        # Basic statistics
        result = {
            'n': n,
            'missing': missing,
            'mean': round(clean_data.mean(), decimal_places),
            'std': round(clean_data.std(ddof=1), decimal_places),  # Sample std
            'median': round(clean_data.median(), decimal_places),
            'q1': round(clean_data.quantile(0.25), decimal_places),
            'q3': round(clean_data.quantile(0.75), decimal_places),
            'min': round(clean_data.min(), decimal_places),
            'max': round(clean_data.max(), decimal_places)
        }
        
        # IQR
        result['iqr'] = round(result['q3'] - result['q1'], decimal_places)
        
        # Confidence interval for mean (uses t-distribution)
        if include_ci and n > 1:
            se = result['std'] / np.sqrt(n)  # Standard error
            t_crit = stats.t.ppf(1 - self.alpha/2, n - 1)  # t critical value
            margin = t_crit * se
            
            result['ci_low'] = round(result['mean'] - margin, decimal_places)
            result['ci_high'] = round(result['mean'] + margin, decimal_places)
        
        return result
    
    def check_normality(self, data: pd.Series, alpha: float = 0.05) -> Dict[str, Any]:
        """
        Test for normality using Shapiro-Wilk test.
        
        Args:
            data: Pandas Series with numeric data
            alpha: Significance level
            
        Returns:
            Dictionary with:
            - is_normal: Boolean indicating if data is normally distributed
            - statistic: Test statistic
            - p_value: P-value
        """
        clean_data = data.dropna()
        n = len(clean_data)
        
        if n < 3:
            log.warning("Insufficient data for normality test (n < 3)")
            return {'is_normal': None, 'statistic': None, 'p_value': None}
        
        if n > 5000:
            # Shapiro-Wilk can be unreliable for very large samples
            log.info("Large sample size (n > 5000), using alternative normality assessment")
            # For large samples, can use skewness and kurtosis
            skew = stats.skew(clean_data)
            kurt = stats.kurtosis(clean_data)
            is_normal = abs(skew) < 2 and abs(kurt) < 7  # Rule of thumb
            return {
                'is_normal': is_normal,
                'method': 'skewness_kurtosis',
                'skewness': round(skew, 3),
                'kurtosis': round(kurt, 3)
            }
        
        # Shapiro-Wilk test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            statistic, p_value = stats.shapiro(clean_data)
        
        is_normal = p_value > alpha
        
        return {
            'is_normal': is_normal,
            'method': 'shapiro_wilk',
            'statistic': round(statistic, 4),
            'p_value': round(p_value, 4)
        }
    
    # =========================================================================
    # CATEGORICAL VARIABLES - Frequency Distributions
    # =========================================================================
    
    def describe_categorical(
        self,
        data: pd.Series,
        decimal_places: int = 1
    ) -> Dict[str, Any]:
        """
        Calculate frequency distribution for categorical variable.
        
        Args:
            data: Pandas Series with categorical data
            decimal_places: Decimal places for percentages
            
        Returns:
            Dictionary with:
            - categories: Dict mapping category -> {count, percent}
            - n_total: Total observations
            - n_missing: Missing values count
            - n_categories: Number of unique categories
        """
        n_total = len(data)
        clean_data = data.dropna()
        n_valid = len(clean_data)
        n_missing = n_total - n_valid
        
        if n_valid == 0:
            log.warning("No valid data for categorical variable")
            return {
                'categories': {},
                'n_total': n_total,
                'n_missing': n_missing,
                'n_categories': 0
            }
        
        # Calculate frequencies
        value_counts = clean_data.value_counts()
        percentages = (value_counts / n_valid * 100).round(decimal_places)
        
        categories = {}
        for category in value_counts.index:
            categories[str(category)] = {
                'count': int(value_counts[category]),
                'percent': float(percentages[category])
            }
        
        return {
            'categories': categories,
            'n_total': n_total,
            'n_missing': n_missing,
            'n_categories': len(categories)
        }
    
    # =========================================================================
    # STATISTICAL TESTS - Group Comparisons
    # =========================================================================
    
    def compare_continuous(
        self,
        group1: pd.Series,
        group2: pd.Series,
        test: str = 'auto',
        decimal_places: int = 4
    ) -> Dict[str, Any]:
        """
        Compare continuous variable between two groups.
        
        Args:
            group1: First group data
            group2: Second group data
            test: Statistical test to use ('auto', 't-test', 'mann-whitney')
            decimal_places: Decimal places for p-value
            
        Returns:
            Dictionary with:
            - test_name: Name of test performed
            - statistic: Test statistic
            - p_value: P-value
            - significant: Boolean (p < 0.05)
        """
        # Clean data
        g1 = group1.dropna()
        g2 = group2.dropna()
        
        if len(g1) < 2 or len(g2) < 2:
            log.warning("Insufficient data for statistical test")
            return {
                'test_name': 'insufficient_data',
                'statistic': None,
                'p_value': None,
                'significant': None
            }
        
        # Auto-select test based on normality
        if test == 'auto':
            norm1 = self.check_normality(g1)
            norm2 = self.check_normality(g2)
            
            if norm1['is_normal'] and norm2['is_normal']:
                test = 't-test'
            else:
                test = 'mann-whitney'
            
            log.debug(f"Auto-selected {test} based on normality tests")
        
        # Perform test
        if test == 't-test':
            # Independent samples t-test
            statistic, p_value = stats.ttest_ind(g1, g2, equal_var=False)  # Welch's t-test
            test_name = "Welch's t-test"
        
        elif test == 'mann-whitney':
            # Mann-Whitney U test (non-parametric)
            statistic, p_value = stats.mannwhitneyu(g1, g2, alternative='two-sided')
            test_name = "Mann-Whitney U test"
        
        else:
            raise ValueError(f"Unknown test: {test}")
        
        return {
            'test_name': test_name,
            'statistic': round(float(statistic), decimal_places),
            'p_value': round(float(p_value), decimal_places),
            'significant': p_value < 0.05
        }
    
    def compare_categorical(
        self,
        group1: pd.Series,
        group2: pd.Series,
        test: str = 'auto',
        decimal_places: int = 4
    ) -> Dict[str, Any]:
        """
        Compare categorical variable between two groups.
        
        Args:
            group1: First group data
            group2: Second group data
            test: Statistical test ('auto', 'chi-square', 'fisher')
            decimal_places: Decimal places for p-value
            
        Returns:
            Dictionary with test results
        """
        # Create contingency table
        # Combine groups and create indicator
        combined = pd.concat([
            pd.DataFrame({'value': group1.dropna(), 'group': 'group1'}),
            pd.DataFrame({'value': group2.dropna(), 'group': 'group2'})
        ])
        
        contingency = pd.crosstab(combined['value'], combined['group'])
        
        if contingency.size == 0:
            log.warning("Empty contingency table")
            return {
                'test_name': 'insufficient_data',
                'statistic': None,
                'p_value': None,
                'significant': None
            }
        
        # Auto-select test
        if test == 'auto':
            # Use Fisher's exact for small samples or expected frequencies < 5
            expected = stats.contingency.expected_freq(contingency)
            if (expected < 5).any() or contingency.sum().sum() < 20:
                test = 'fisher'
            else:
                test = 'chi-square'
            
            log.debug(f"Auto-selected {test} for categorical comparison")
        
        # Perform test
        if test == 'chi-square':
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
            return {
                'test_name': 'Chi-square test',
                'statistic': round(float(chi2), decimal_places),
                'p_value': round(float(p_value), decimal_places),
                'dof': dof,
                'significant': p_value < 0.05
            }
        
        elif test == 'fisher':
            # Fisher's exact test (only for 2x2 tables)
            if contingency.shape == (2, 2):
                oddsratio, p_value = stats.fisher_exact(contingency)
                return {
                    'test_name': "Fisher's exact test",
                    'odds_ratio': round(float(oddsratio), decimal_places),
                    'p_value': round(float(p_value), decimal_places),
                    'significant': p_value < 0.05
                }
            else:
                log.warning("Fisher's exact test only for 2x2 tables, using chi-square")
                chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
                return {
                    'test_name': 'Chi-square test (fallback)',
                    'statistic': round(float(chi2), decimal_places),
                    'p_value': round(float(p_value), decimal_places),
                    'dof': dof,
                    'significant': p_value < 0.05
                }
        
        else:
            raise ValueError(f"Unknown test: {test}")


if __name__ == "__main__":
    # Test the statistical calculator
    print("Testing Statistical Calculator...\n")
    
    # Create test data
    np.random.seed(42)
    
    # Continuous data
    age_group1 = pd.Series(np.random.normal(45, 10, 50))  # Mean 45, SD 10
    age_group2 = pd.Series(np.random.normal(50, 12, 60))  # Mean 50, SD 12
    
    # Categorical data
    sex_group1 = pd.Series(['M', 'F'] * 25)
    sex_group2 = pd.Series(['M'] * 20 + ['F'] * 40)
    
    # Initialize calculator
    calc = StatisticalCalculator()
    
    # Test 1: Describe continuous variable
    print("=" * 60)
    print("Test 1: Continuous variable description")
    print("=" * 60)
    stats_continuous = calc.describe_continuous(age_group1)
    for key, value in stats_continuous.items():
        print(f"  {key}: {value}")
    
    # Test 2: Normality check
    print("\n" + "=" * 60)
    print("Test 2: Normality test")
    print("=" * 60)
    normality = calc.check_normality(age_group1)
    for key, value in normality.items():
        print(f"  {key}: {value}")
    
    # Test 3: Describe categorical variable
    print("\n" + "=" * 60)
    print("Test 3: Categorical variable description")
    print("=" * 60)
    stats_categorical = calc.describe_categorical(sex_group1)
    print(f"  Total: {stats_categorical['n_total']}")
    print(f"  Missing: {stats_categorical['n_missing']}")
    print(f"  Categories: {stats_categorical['n_categories']}")
    for cat, data in stats_categorical['categories'].items():
        print(f"    {cat}: {data['count']} ({data['percent']}%)")
    
    # Test 4: Compare continuous variables
    print("\n" + "=" * 60)
    print("Test 4: Compare continuous variables between groups")
    print("=" * 60)
    comparison_cont = calc.compare_continuous(age_group1, age_group2)
    for key, value in comparison_cont.items():
        print(f"  {key}: {value}")
    
    # Test 5: Compare categorical variables
    print("\n" + "=" * 60)
    print("Test 5: Compare categorical variables between groups")
    print("=" * 60)
    comparison_cat = calc.compare_categorical(sex_group1, sex_group2)
    for key, value in comparison_cat.items():
        print(f"  {key}: {value}")
    
    print("\n✓ Statistical Calculator test complete")
