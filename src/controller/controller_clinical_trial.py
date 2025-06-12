# controller/controller_clinical_trial.py

from PySide6.QtWidgets import QPushButton, QTabWidget

class ControllerClinicalTrial:
    def __init__(self, ui, model_clinical, controller):
        """
        :param ui: QWidget corresponding to the page in the QStackedWidget.
        :param model: Instance of the business logic model.
        :param app_controller: Main application controller that handles navigation and coordination.
        """
        self.ui = ui
        self.model = model_clinical
        self.controller = controller

        self.tab = 1 # Initial tab. Default: Inclusion/Exclusion criteria

        self.tabWidget_clinical = self.ui.findChild(QTabWidget, "tabWidget_clinical")
        self.tabWidget_clinical.setCurrentIndex(self.tab)

        self.pushButton_clinical_start = self.ui.findChild(QPushButton, "pushButton_clinical_start")

        self._setup_signals()
        self._set_tabs_disabled()

    def _setup_signals(self):
        """
        Connect UI elements (buttons, etc.) to their respective slots.
        """
        self.pushButton_clinical_start.clicked.connect(self._back_to_init)

    def _set_tabs_disabled(self):
        """
        Disables all tabs except the first one.
        """
        tabs = self.tabWidget_clinical.count()

        for i in range(2, tabs):
            self.tabWidget_clinical.setTabEnabled(i, False)

    def _back_to_init(self):
        self.controller.change_page(0)
