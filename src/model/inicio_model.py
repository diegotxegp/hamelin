# models/inicio_model.py
import pandas as pd

class InicioModel:
    def __init__(self):
        self.df = None

    def load_csv(self, file_path):
        try:
            self.dataframe = pd.read_csv(file_path)
            return f"✅ Successfully loaded {len(self.dataframe)} rows."
        except Exception as e:
            return f"❌ Failed to load the file: {str(e)}"
