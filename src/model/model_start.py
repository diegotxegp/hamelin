# model/model_start.py

import os, shutil

from my_ludwig.ludwig import Ludwig

class ModelStart:
    def __init__(self, model):
        self.model = model
        
    def project_list(self):
        """ Returns a list of projects if the directory exists. """
        base_projects_dir = self.model.base_projects_dir

        if base_projects_dir is not None and os.path.isdir(base_projects_dir):
            return os.listdir(base_projects_dir)

    def new_project(self, project_name):
        """ Creates a new project with the given name. """
        base_projects_dir = self.model.base_projects_dir

        # Create Projects folder if it doesn't exist
        if not os.path.exists(base_projects_dir):
            os.makedirs(base_projects_dir)
    
        # Create the new project folder inside Projects
        project_dir = os.path.join(base_projects_dir, project_name)
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
            print(f"✅ Project '{project_name}' created.")
            return project_dir
        else:
            print(f"❌ Project '{project_name}' already exists.")
            return None

    def set_project(self, project_name):
        """ Sets the project directory to the given project name. """
        self.model.project_dir = os.path.join(self.model.base_projects_dir, project_name)
        self.model.project_name = project_name

    def dataset_list(self):
        """ Returns a list of datasets if the directory exists. """
        project_dir = self.model.project_dir

        if project_dir is not None and os.path.isdir(project_dir):
            return os.listdir(project_dir)
    
    def load_dataset(self, origin_path):
        """ Copy the new dataset to the project directory """
        project_dir = self.model.project_dir
        dataset_dir = os.path.join(project_dir, os.path.basename(origin_path))

        if not dataset_dir in os.listdir(project_dir):
            shutil.copy(origin_path, dataset_dir)
        
    def set_dataset(self, dataset_name):
        """ Sets the dataset directory to the given dataset name. """
        self.model.dataset_dir = os.path.join(self.model.project_dir, dataset_name)
        self.model.dataset_name = dataset_name
        self.model.update()