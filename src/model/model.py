# model/model.py

import os
import pandas as pd

from model.model_start import ModelStart
from model.model_patient_registry import ModelPatientRegistry
from model.model_observational_study import ModelObservationalStudy
from model.model_clinical_trial import ModelClinicalTrial

from my_ludwig.ludwig import Ludwig
from utils.criteria_manager import CriteriaManager

class Model:
    def __init__(self):
        self.base_projects_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..", "Projects")
        self.project_dir = None
        self.project_name = None
        self.dataset_dir = None
        self.dataset_name = None
        self.df = None
        self.status = None
        self.option = None

        self.primary_variable = None
        self.criteria = None
        self.criteria_manager = CriteriaManager()
        self.filtered_df = None  # Store filtered dataset after applying criteria

        self.model_start = ModelStart(self)
        self.model_registry = ModelPatientRegistry(self)
        self.model_observational = ModelObservationalStudy(self)
        self.model_clinical = ModelClinicalTrial(self)

        self.ludwig = Ludwig()
    
    def update(self):
        self.df = self.ludwig.read_file(self.dataset_dir)

    def autoconfig(self):
        """
        Automatically generates a configuration file using the filtered dataset.
        Implements [IS2] Select subpopulations and [IS3] Remove specific instances.
        """
        # Use filtered dataset if criteria were applied, otherwise use original
        working_dataset = self.get_working_dataset()
        
        # Temporarily update Ludwig's dataframe to the working dataset
        original_df = self.ludwig.df
        self.ludwig.df = working_dataset
        
        try:
            self.ludwig.autoconfig(self.primary_variable)
        finally:
            # Restore original dataframe
            self.ludwig.df = original_df
    
    def train_config(self):
        """ Train the model. """
        self.ludwig.configuration_to_config()
        return self.ludwig.train()
    
    def auto_train(self):
        """
        Train the model using the filtered dataset (if criteria applied).
        Implements [IS2] Select subpopulations and [IS3] Remove specific instances.
        """
        # Use filtered dataset if criteria were applied, otherwise use original
        working_dataset = self.get_working_dataset()
        
        # Temporarily update Ludwig's dataframe to the working dataset
        original_df = self.ludwig.df
        self.ludwig.df = working_dataset
        
        try:
            result = self.ludwig.auto_train(self.primary_variable)
            return result
        finally:
            # Restore original dataframe
            self.ludwig.df = original_df
    
    def train(self):
        """ Train the model. """
        self.ludwig.train()

    def acceptable_stratify_variables(self, min_samples=5, max_categories=10):
        """ Returns a list of variables that are categorical or numeric (suitable for classification or regression). 
        Ensures all variables meet Ludwig's requirements for cross-validation (min 2 samples per class/value).
        """
        acceptable_variables = []
        total_rows = len(self.df)
        
        for col in self.df.columns:
            # Include categorical variables (for classification)
            if pd.api.types.is_categorical_dtype(self.df[col]) or self.df[col].dtype == object:
                counts = self.df[col].value_counts(dropna=True)
                if len(counts) <= max_categories and (counts >= min_samples).all():
                    acceptable_variables.append(col)
            # Include numeric variables (for regression or discrete classification)
            elif self.df[col].dtype in ['int64', 'float64']:
                unique_count = self.df[col].nunique(dropna=True)
                
                # Check if variable has real decimal values (not just .0)
                has_decimals = False
                if self.df[col].dtype == 'float64':
                    # Check if any value has non-zero decimal part
                    has_decimals = (self.df[col].dropna() % 1 != 0).any()
                
                # Treat as continuous if: has real decimals OR >50% values are unique
                if has_decimals or unique_count > total_rows * 0.5:
                    acceptable_variables.append(col)
                # Otherwise, it's discrete/categorical - check for min 2 samples per value
                else:
                    counts = self.df[col].value_counts(dropna=True)
                    min_count = counts.min()
                    if min_count >= 2:
                        acceptable_variables.append(col)
            # Include boolean variables (for binary classification)
            elif self.df[col].dtype == 'bool':
                counts = self.df[col].value_counts(dropna=True)
                if (counts >= 2).all():  # Both True and False must have at least 2 samples
                    acceptable_variables.append(col)
        return acceptable_variables
    
    def apply_criteria(self):
        """
        Apply inclusion/exclusion criteria to the dataset.
        Implements [IS2] Select subpopulations and [IS3] Remove specific instances.
        
        Returns:
            dict: Statistics about the filtering operation
        """
        if self.df is None:
            raise ValueError("No dataset loaded. Cannot apply criteria.")
        
        # Apply criteria and get filtered dataset
        self.filtered_df, statistics = self.criteria_manager.apply_criteria(self.df)
        
        return statistics
    
    def get_working_dataset(self):
        """
        Get the dataset to use for training (filtered if criteria applied, original otherwise).
        
        Returns:
            pd.DataFrame: The dataset to use
        """
        if self.filtered_df is not None and len(self.filtered_df) > 0:
            return self.filtered_df
        return self.df
    