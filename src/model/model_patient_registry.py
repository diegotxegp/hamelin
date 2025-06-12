# model/model_patient_registry.py

class ModelPatientRegistry:
    def __init__(self, model):
        self.model = model
        self.primary_variable = None
        self.criteria = None

    def all_variables(self):
        """
        Returns a list of all variables in the dataset.
        """
        return self.model.df.columns.tolist()