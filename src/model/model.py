# model/model.py

import os

from model.model_start import ModelStart

class Model:
    def __init__(self):
        self.base_projects_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..", "Projects")
        self.project_dir = None
        self.dataset_dir = None
        self.df = None
        self.status = None
        self.option = None

        self.model_start = ModelStart(self)

    def get_model_start(self):
        return self.model_start