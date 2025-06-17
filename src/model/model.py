# model/model.py

import os

from model.model_start import ModelStart
from model.model_patient_registry import ModelPatientRegistry
from model.model_observational_study import ModelObservationalStudy
from model.model_clinical_trial import ModelClinicalTrial

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

        self.model_start = ModelStart(self)
        self.model_registry = ModelPatientRegistry(self)
        self.model_observational = ModelObservationalStudy(self)
        self.model_clinical = ModelClinicalTrial(self)

    def get_model_start(self):
        return self.model_start
    
    def get_model_registry(self):
        return self.model_registry
    
    def get_model_observational(self):
        return self.model_observational
    
    def get_model_clinical(self):
        return self.model_clinical