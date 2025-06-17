# model/model_patient_registry.py

from ludwig.ludwig import LudwigModel

class ModelPatientRegistry:
    def __init__(self, model):
        self.model = model

    def all_variables(self):
        """
        Returns a list of all variables in the dataset.
        """
        self.model.variables = self.model.df.columns.tolist()
        return self.model.variables
    
    def select_primary_variable(self, primary_variable):
        """
        Sets the primary variable to the given variable name.
        """
        self.model.primary_variable = primary_variable