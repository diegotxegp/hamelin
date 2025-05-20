from PySide6.QtWidgets import QFileDialog, QMainWindow
from view.interface_ui import Ui_MainWindow

class InicioController(QMainWindow):
    def __init__(self, controller, model):
        super().__init__()
        self.controller = controller
        self.model = model

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._setup_signals()

    def _setup_signals(self):
        # Connect signals to slots
        self.ui.pushButton_adjuntar.clicked.connect(self.model.attach_csv)
        self.ui.pushButton_opciones.clicked.connect(self.select_option)

    def select_option(self):
        option = self.ui.comboBox_opciones.currentText()
        self.controller.change_page(option)
