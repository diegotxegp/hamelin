# controller/controller_observational_study.py

from PySide6.QtWidgets import QPushButton, QTabWidget

class ControllerObservationalStudy:
    def __init__(self, ui, model, controller):
        """
        :param ui: QWidget corresponding to the page in the QStackedWidget.
        :param model: Instance of the business logic model.
        :param app_controller: Main application controller that handles navigation and coordination.
        """
        self.ui = ui
        self.model = model
        self.controller = controller

        self.tabWidget_observacional = self.ui.findChild(QTabWidget, "tabWidget_observacional")
        self.pushButton_observacional_inicio = self.ui.findChild(QPushButton, "pushButton_observacional_inicio")

        self._setup_signals()

        self.tabWidget_observacional.setCurrentIndex(1)

    def _setup_signals(self):
        """
        Connect UI elements (buttons, etc.) to their respective slots.
        """
        self.pushButton_observacional_inicio.clicked.connect(self._back_to_init)

    def _back_to_init(self):
        self.controller.change_page(0)
