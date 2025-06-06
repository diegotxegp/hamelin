# model/model_start.py

import os, shutil
import pandas as pd
from PySide6.QtWidgets import QFileDialog

class ModelStart:
    def __init__(self, model):
        self.model = model
        
    def project_list(self):
        """
        Returns a list of projects if the directory exists.
        """
        if self.model.base_projects_dir is not None or os.path.isdir(self.model.base_projects_dir):
            return os.listdir(self.model.base_projects_dir)

    def new_project(self, project_name):
        """
        Creates a new project with the given name.
        """
        # Create Projects folder if it doesn't exist
        if not os.path.exists(self.model.base_projects_dir):
            os.makedirs(self.model.base_projects_dir)
    
        # Create the new project folder inside Projects
        project_dir = os.path.join(self.model.base_projects_dir, project_name)
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
            self.model.project_dir = project_dir

    def select_project(self, project_name):
        """
        Sets the project directory to the given project name.
        """
        project_dir = os.path.join(self.model.base_projects_dir, project_name)
        self.model.project_dir = project_dir
    
    def new_dataset(self, origin_path):
        pass

    def dataset_list(self):
        """
        Returns a list of datasets if the directory exists.
        """
        if self.model.project_dir == None or not os.path.isdir(self.model.project_dir):
            return None
        return os.listdir(self.model.project_dir)