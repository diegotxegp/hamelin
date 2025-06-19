# model/model_patient_registry.py

import pandas as pd

class ModelPatientRegistry:
    def __init__(self, model):
        self.model = model
    
    def acceptable_stratify_variables(self, min_samples=5, max_categories=10):
        """ Returns a list of variables that are categorical and have at least min_samples and at most max_categories. """
        acceptable_variables = []
        for col in self.model.df.columns:
            if pd.api.types.is_categorical_dtype(self.model.df[col]) or self.model.df[col].dtype == object:
                counts = self.model.df[col].value_counts(dropna=True)
                if len(counts) <= max_categories and (counts >= min_samples).all():
                    acceptable_variables.append(col)
        return acceptable_variables