# model/model_start.py

import os, shutil
import pandas as pd

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
            print(f"✅ Project '{project_name}' created.")
            return self.model.project_dir
        else:
            print(f"❌ Project '{project_name}' already exists.")
            return None

    def set_project(self, project_name):
        """
        Sets the project directory to the given project name.
        """
        self.model.project_dir = os.path.join(self.model.base_projects_dir, project_name)
        self.model.project_name = project_name

    def dataset_list(self):
        """
        Returns a list of datasets if the directory exists.
        """
        if self.model.project_dir == None or not os.path.isdir(self.model.project_dir):
            return None
        return os.listdir(self.model.project_dir)
    
    def load_dataset(self, origin_path):
        # Copy the CSV file to the target folder
        self.model.dataset_dir = os.path.join(self.model.project_dir, os.path.basename(origin_path))

        if not self.model.dataset_dir in os.listdir(self.model.project_dir):
            shutil.copy(origin_path, self.model.dataset_dir)
            self._load_csv(self.model.dataset_dir)

    def _load_csv(self, file_path):
        try:
            self.model.df = pd.read_csv(file_path)
            return f"✅ Successfully loaded {len(self.model.df)} rows."
        except Exception as e:
            return f"❌ Failed to load the file: {str(e)}"
        
    def set_dataset(self, dataset_name):
        """
        Sets the dataset directory to the given dataset name.
        """
        self.model.dataset_dir = os.path.join(self.model.project_dir, dataset_name)
        self.model.dataset_name = dataset_name
        self._load_csv(self.model.dataset_dir)