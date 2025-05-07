# model/model.py
import os
import shutil
from PySide6.QtWidgets import QFileDialog
import pandas as pd

class Model:
    def __init__(self):
        self.df = None

    def attach_csv(self):
        # Open file dialog to select the CSV file
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
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
            self.dataframe = pd.read_csv(file_path)
            return f"✅ Successfully loaded {len(self.dataframe)} rows."
        except Exception as e:
            return f"❌ Failed to load the file: {str(e)}"
