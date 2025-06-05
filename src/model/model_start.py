# model/model_start.py

import os, shutil
import pandas as pd
from PySide6.QtWidgets import QFileDialog

class ModelStart:
    def __init__(self, base_projects_dir):
        self.base_projects_dir = base_projects_dir
        self.project_dir = None

    def project_list(self):
        """
        Returns a list of projects if the directory exists.
        """
        if not os.path.isdir(self.base_projects_dir):
            return None
        return os.listdir(self.base_projects_dir)

    def new_project(self, project_name):
        """
        Creates a new project with the given name.
        """
        # Create Projects folder if it doesn't exist
        if not os.path.exists(self.base_projects_dir):
            os.makedirs(self.base_projects_dir)
    
        # Create the new project folder inside Projects
        self.project_dir = os.path.join(self.base_projects_dir, project_name)
        if not os.path.exists(self.project_dir):
            os.makedirs(self.project_dir)

    def set_project(self, project_name):
        """
        Sets the project directory to the given project name.
        """
        self.project_dir = os.path.join(self.base_projects_dir, project_name)

    def dataset_list(self):
        """
        Returns a list of datasets if the directory exists.
        """
        if self.project_dir == None or not os.path.isdir(self.project_dir):
            return None
        return os.listdir(self.project_dir)

    def attach_csv(self):
        # Open file dialog to select the CSV file
        path, _ = QFileDialog.getOpenFileName(None, "Open CSV File", "", "CSV Files (*.csv)")
        if path:
            # Define the target directory (e.g., 'data' folder inside your project)
            target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..", "data")
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)  # Create the 'data' folder if it doesn't exist

            # Define the target file path where the CSV will be saved
            target_file = os.path.join(target_dir, os.path.basename(path))

            # Copy the CSV file to the target folder
            shutil.copy(path, target_file)

            # Update the model (if necessary)
            message = self.model.load_csv(target_file)

            # Update UI with a success message
            self.ui.textEdit_2.setPlainText(message)
            self.ui.textEdit_3.setPlainText(f"📊 CSV loaded and saved to {target_file}. You may proceed with the analysis.")


    def load_csv(self, file_path):
        try:
            self.df = pd.read_csv(file_path)
            return f"✅ Successfully loaded {len(self.df)} rows."
        except Exception as e:
            return f"❌ Failed to load the file: {str(e)}"