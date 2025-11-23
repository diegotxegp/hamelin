"""
Criteria Manager for handling inclusion/exclusion criteria in clinical datasets.
Implements [IS2] Select subpopulations and [IS3] Remove specific instances.
"""

import pandas as pd
from typing import List, Dict, Any, Tuple


class CriteriaRule:
    """Represents a single inclusion or exclusion rule."""
    
    OPERATORS = {
        'equals': '==',
        'not equals': '!=',
        'greater than': '>',
        'less than': '<',
        'greater or equal': '>=',
        'less or equal': '<=',
        'between': 'between',
        'contains': 'in',
        'not contains': 'not in'
    }
    
    def __init__(self, variable: str, operator: str, value: Any, rule_type: str = 'inclusion'):
        """
        Args:
            variable: Column name in the dataset
            operator: Comparison operator (equals, greater than, etc.)
            value: Value to compare against
            rule_type: 'inclusion' or 'exclusion'
        """
        self.variable = variable
        self.operator = operator
        self.value = value
        self.rule_type = rule_type
    
    def apply(self, df: pd.DataFrame) -> pd.Series:
        """
        Apply the rule to a dataframe and return a boolean mask.
        
        Args:
            df: DataFrame to apply rule to
            
        Returns:
            Boolean Series indicating which rows satisfy the rule
        """
        if self.variable not in df.columns:
            raise ValueError(f"Variable '{self.variable}' not found in dataset")
        
        column = df[self.variable]
        
        # Handle different operators
        if self.operator == 'equals':
            mask = column == self.value
        elif self.operator == 'not equals':
            mask = column != self.value
        elif self.operator == 'greater than':
            mask = column > float(self.value)
        elif self.operator == 'less than':
            mask = column < float(self.value)
        elif self.operator == 'greater or equal':
            mask = column >= float(self.value)
        elif self.operator == 'less or equal':
            mask = column <= float(self.value)
        elif self.operator == 'between':
            # Value should be a tuple (min, max)
            if isinstance(self.value, (tuple, list)) and len(self.value) == 2:
                min_val, max_val = float(self.value[0]), float(self.value[1])
                mask = (column >= min_val) & (column <= max_val)
            else:
                raise ValueError(f"'between' operator requires a tuple/list of two values, got: {self.value}")
        elif self.operator == 'contains':
            mask = column.astype(str).str.contains(str(self.value), case=False, na=False)
        elif self.operator == 'not contains':
            mask = ~column.astype(str).str.contains(str(self.value), case=False, na=False)
        else:
            raise ValueError(f"Unknown operator: {self.operator}")
        
        return mask
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary for serialization."""
        return {
            'variable': self.variable,
            'operator': self.operator,
            'value': self.value,
            'rule_type': self.rule_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CriteriaRule':
        """Create rule from dictionary."""
        return cls(
            variable=data['variable'],
            operator=data['operator'],
            value=data['value'],
            rule_type=data.get('rule_type', 'inclusion')
        )
    
    def __str__(self) -> str:
        """Human-readable representation."""
        rule_symbol = "✓" if self.rule_type == 'inclusion' else "✗"
        return f"{rule_symbol} {self.variable} {self.operator} {self.value}"


class CriteriaManager:
    """Manages all inclusion and exclusion criteria for a dataset."""
    
    def __init__(self):
        self.rules: List[CriteriaRule] = []
        self.original_size = 0
        self.filtered_size = 0
    
    def add_rule(self, variable: str, operator: str, value: Any, rule_type: str = 'inclusion'):
        """Add a new criteria rule."""
        rule = CriteriaRule(variable, operator, value, rule_type)
        self.rules.append(rule)
    
    def remove_rule(self, index: int):
        """Remove a rule by index."""
        if 0 <= index < len(self.rules):
            del self.rules[index]
    
    def clear_rules(self):
        """Remove all rules."""
        self.rules.clear()
    
    def apply_criteria(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Apply all criteria rules to a dataframe.
        
        Inclusion rules are combined with OR logic (any inclusion rule passes)
        Exclusion rules are combined with AND logic (all exclusion rules must pass)
        
        Args:
            df: Original dataframe
            
        Returns:
            Tuple of (filtered_df, statistics_dict)
        """
        self.original_size = len(df)
        
        if not self.rules:
            self.filtered_size = self.original_size
            return df.copy(), {
                'original_size': self.original_size,
                'filtered_size': self.filtered_size,
                'removed_count': 0,
                'removal_percentage': 0.0,
                'rules_applied': 0
            }
        
        # Separate inclusion and exclusion rules
        inclusion_rules = [r for r in self.rules if r.rule_type == 'inclusion']
        exclusion_rules = [r for r in self.rules if r.rule_type == 'exclusion']
        
        # Start with all rows
        final_mask = pd.Series([True] * len(df), index=df.index)
        
        # Apply inclusion rules (OR logic)
        if inclusion_rules:
            inclusion_mask = pd.Series([False] * len(df), index=df.index)
            for rule in inclusion_rules:
                try:
                    inclusion_mask |= rule.apply(df)
                except Exception as e:
                    print(f"Warning: Could not apply inclusion rule {rule}: {e}")
            final_mask &= inclusion_mask
        
        # Apply exclusion rules (AND logic - must pass all exclusions)
        for rule in exclusion_rules:
            try:
                # For exclusion, we keep rows that DON'T match the rule
                final_mask &= ~rule.apply(df)
            except Exception as e:
                print(f"Warning: Could not apply exclusion rule {rule}: {e}")
        
        filtered_df = df[final_mask].copy()
        self.filtered_size = len(filtered_df)
        
        removed_count = self.original_size - self.filtered_size
        removal_percentage = (removed_count / self.original_size * 100) if self.original_size > 0 else 0
        
        statistics = {
            'original_size': self.original_size,
            'filtered_size': self.filtered_size,
            'removed_count': removed_count,
            'removal_percentage': removal_percentage,
            'rules_applied': len(self.rules),
            'inclusion_rules': len(inclusion_rules),
            'exclusion_rules': len(exclusion_rules)
        }
        
        return filtered_df, statistics
    
    def get_summary(self) -> str:
        """Get a human-readable summary of criteria."""
        if not self.rules:
            return "No criteria defined"
        
        lines = [f"Total rules: {len(self.rules)}"]
        
        inclusion_rules = [r for r in self.rules if r.rule_type == 'inclusion']
        if inclusion_rules:
            lines.append(f"\nInclusion criteria ({len(inclusion_rules)}):")
            for rule in inclusion_rules:
                lines.append(f"  • {rule}")
        
        exclusion_rules = [r for r in self.rules if r.rule_type == 'exclusion']
        if exclusion_rules:
            lines.append(f"\nExclusion criteria ({len(exclusion_rules)}):")
            for rule in exclusion_rules:
                lines.append(f"  • {rule}")
        
        if self.original_size > 0:
            lines.append(f"\nDataset: {self.filtered_size:,} / {self.original_size:,} rows ({self.filtered_size/self.original_size*100:.1f}%)")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'rules': [rule.to_dict() for rule in self.rules]
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Deserialize from dictionary."""
        self.rules.clear()
        for rule_data in data.get('rules', []):
            self.rules.append(CriteriaRule.from_dict(rule_data))
