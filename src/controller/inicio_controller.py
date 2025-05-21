# controller/inicio_controller.py

from PySide6.QtWidgets import QPushButton, QComboBox

class InicioController:
    def __init__(self, ui, model, app_controller):
        """
        Controller for the 'Inicio' (Start) page.

        :param ui: QWidget corresponding to the 'page_inicio' in the QStackedWidget.
        :param model: Instance of the business logic model.
        :param app_controller: Main application controller that handles navigation and coordination.
        """
        self.ui = ui
        self.model = model
        self.controller = app_controller

        self.pushButton_adjuntar = self.ui.findChild(QPushButton, "pushButton_adjuntar")
        self.pushButton_opciones = self.ui.findChild(QPushButton, "pushButton_opciones")
        self.comboBox_opciones = self.ui.findChild(QComboBox, "comboBox_opciones")

        self._setup_signals()

    def _setup_signals(self):
        """
        Connect UI elements (buttons, etc.) to their respective slots.
        """
        self.pushButton_adjuntar.clicked.connect(self.model.attach_csv)
        self.pushButton_opciones.clicked.connect(self._select_option)

    def _select_option(self):
        """
        Reads the selected option from the combo box and tells the main controller to switch pages.
        """
        option = self.comboBox_opciones.currentText()
        self.controller.change_page(option)
