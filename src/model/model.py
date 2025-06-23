# model/model.py

import os

from model.model_start import ModelStart
from model.model_patient_registry import ModelPatientRegistry
from model.model_observational_study import ModelObservationalStudy
from model.model_clinical_trial import ModelClinicalTrial

from my_ludwig.ludwig import Ludwig

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

        self.ludwig = Ludwig()
    
    def update(self):
        self.df = self.ludwig.read_file(self.dataset_dir)

    def autoconfig(self):
        """ Automatically generates a configuration file. """
        return self.ludwig.autoconfig(self.primary_variable)
    
    def train_config(self):
        """ Train the model. """
        self.ludwig.configuration_to_config()
        return self.ludwig.train()
    
    def auto_train(self):
        """ Train the model. """
        return self.ludwig.auto_train(self.primary_variable)
    
    def train(self):
        """ Train the model. """
        self.ludwig.train()
    