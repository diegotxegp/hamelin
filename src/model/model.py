# model/model.py

import os

from model.model_start import ModelStart
from model.model_patient_registry import ModelPatientRegistry
from model.model_observational_study import ModelObservationalStudy

class Model:
    def __init__(self):
        self.base_projects_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..", "Projects")
        self.project_dir = None
        self.dataset_dir = None
        self.df = None
        self.status = None
        self.option = None

        self.model_start = ModelStart(self)
        self.model_registry = ModelPatientRegistry
        self.model_observational = ModelObservationalStudy

    def get_model_start(self):
        return self.model_start
    
    def get_model_registry(self):
        return self.model_registry
    
    def get_model_observational(self):
        return self.model_observational