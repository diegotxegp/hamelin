import os
from PySide6.QtWidgets import QFileDialog, QMainWindow
from view.inicio_ui import Ui_ventana_inicio
from view.registro_pacientes_ui import Ui_ventana_registro_pacientes

class InicioController(QMainWindow):
    def __init__(self, controller, model):
        super().__init__()
        self.controller = controller
        self.model = model

        self.ui = Ui_ventana_inicio()
        self.ui.setupUi(self)
        self.ui.tabWidget.setCurrentIndex(0)

        self.setup_signals()

    def setup_signals(self):
        # Connect signals to slots
        self.ui.pushButton_adjuntar.clicked.connect(self.model.attach_csv)
        self.ui.pushButton_opciones.clicked.connect(self.select_option)

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
