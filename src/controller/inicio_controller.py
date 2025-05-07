import os
import shutil
from PySide6.QtWidgets import QFileDialog, QMainWindow
from view.inicio_ui import Ui_ventana_inicio
from model.model import Model
from view.registro_pacientes_ui import Ui_ventana_registro_pacientes

class InicioController(QMainWindow):
    def __init__(self, controller, model):
        super().__init__()
        self.controller = controller
        self.model = model

        self.ui = Ui_ventana_inicio()
        self.ui.setupUi(self)

        # Instantiate the model
        self.model = Model()

        self.setup_signals()    

    def setup_signals(self):
        # Connect signals to slots
        self.ui.pushButton.clicked.connect(self.attach_csv)
        self.ui.pushButton_2.clicked.connect(self.select_option)

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

    def select_option(self):
        option = self.ui.comboBox.currentText()
        self.ui.textEdit_4.setPlainText(f"🔎 Selected option: {option}")
        self.ui.textEdit_3.append("⚙️ Configuration set.")
        
        # Now, based on the selected option, show the corresponding window
        if option == "Registro de pacientes":
            self.open_patient_registration_window()
        elif option == "Estudio observacional":
            self.open_observational_study_window()
        elif option == "Estudio clínico":
            self.open_clinical_study_window()

    def open_patient_registration_window(self):
        # Create and show the window registro_pacientes
        self.patient_window = Ui_ventana_registro_pacientes
        self.patient_window.show()
        self.close()  # Close the current window
