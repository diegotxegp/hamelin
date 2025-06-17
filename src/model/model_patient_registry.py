# model/model_patient_registry.py

class ModelPatientRegistry:
    def __init__(self, model):
        self.model = model

    def all_variables(self):
        """
        Returns a list of all variables in the dataset.
        """
        return self.model.df.columns.tolist()
    
    def set_primary_variable(self, primary_variable):
        """
        Sets the primary variable to the given variable name.
        """
        self.model.primary_variable = primary_variable