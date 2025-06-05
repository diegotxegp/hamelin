# model/model.py

import os

from model.model_start import ModelStart

class Model:
    def __init__(self):
        self.base_projects_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..", "Projects")
        self.project_dir = None
        self.dataset_dir = None
        self.df = None

        self.model_start = ModelStart(self.base_projects_dir)

    def project_list(self):
        return self.model_start.project_list()

    def new_project(self, project_name):
        return self.model_start.new_project(project_name)

    def set_project(self, project_name):
        return self.model_start.set_project(project_name)

    def dataset_list(self):
        return self.model_start.dataset_list()

    def attach_csv(self):
        return self.model_start.attach_csv()

    def load_csv(self, file_path):
        return self.model_start.load_csv(file_path)
