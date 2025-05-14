from PySide6.QtWidgets import QFileDialog, QMainWindow
from view.interface_ui import Ui_MainWindow

class InicioController(QMainWindow):
    def __init__(self, controller, model):
        super().__init__()
        self.controller = controller
        self.model = model

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.tabWidget.setCurrentIndex(0)

        self.setup_signals()

    def setup_signals(self):
        # Connect signals to slots
        self.ui.pushButton_adjuntar.clicked.connect(self.model.attach_csv)
        self.ui.pushButton_opciones.clicked.connect(self.select_option)

    def select_option(self):
        option = self.ui.comboBox_opciones.currentText()
        self.ui.textEdit_4.setPlainText(f"🔎 Selected option: {option}")
        self.ui.textEdit_3.append("⚙️ Configuration set.")
        
        # Now, based on the selected option, show the corresponding page
        if option == "Registro de pacientes":
            self.controller.change_page(1)
        elif option == "Estudio observacional":
            self.controller.change_page(2)
        elif option == "Estudio clínico":
            self.controller.change_page(3)
