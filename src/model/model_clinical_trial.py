# model/model_clinical_trial.py
class ModelClinicalTrial:
    def __init__(self, model):
        self.model = model
        self.inclusion_criteria = None
        self.investigational_drug = None
        self.control_drug = None
        self.primary_variable = None