# controller/controller_registro.py

from PySide6.QtWidgets import QPushButton, QTabWidget

class ControllerPatientRegistry:
    def __init__(self, ui, model_registry, controller):
        """
        :param ui: QWidget corresponding to the page in the QStackedWidget.
        :param model: Instance of the business logic model.
        :param app_controller: Main application controller that handles navigation and coordination.
        """
        self.ui = ui
        self.model_registry = model_registry
        self.controller = controller

        self.tab = 1 # Initial tab. Default: Dataset

        self.tabWidget_registry = self.ui.findChild(QTabWidget, "tabWidget_registry")
        self.tabWidget_registry.setCurrentIndex(self.tab)

        self.pushButton_registry_start = self.ui.findChild(QPushButton, "pushButton_registry_start")
        self.pushButton_registry_dataset_ok = self.ui.findChild(QPushButton, "pushButton_registry_dataset_ok")
        self.pushButton_registry_criteria_add = self.ui.findChild(QPushButton, "pushButton_registry_criteria_add")
        self.pushButton_registry_variable_add = self.ui.findChild(QPushButton, "pushButton_registry_variable_add")
        self.pushButton_registry_process = self.ui.findChild(QPushButton, "pushButton_registry_process")

        self._setup_signals()
        self._set_tabs_disabled()

    def _setup_signals(self):
        """
        Connect UI elements (buttons, etc.) to their respective slots.
        """
        self.pushButton_registry_start.clicked.connect(self._back_to_start)
        self.pushButton_registry_dataset_ok.clicked.connect(self._ok)
        self.pushButton_registry_criteria_add.clicked.connect(self._ok)
        self.pushButton_registry_variable_add.clicked.connect(self._ok)
        self.pushButton_registry_process.clicked.connect(self._ok)

    def _set_tabs_disabled(self):
        """
        Disables all tabs except the first two.
        """
        tabs = self.tabWidget_registry.count()

        for i in range(2, tabs):
            self.tabWidget_registry.setTabEnabled(i, False)

    def _back_to_start(self):
        self.controller.change_page(0)

    def _next_tab(self):
        """
        Increments the tab index and enables the next tab.
        """
        self.tab = self.tabWidget_registry.currentIndex() + 1
        self.tabWidget_registry.setTabEnabled(self.tab, True)
        self.tabWidget_registry.setCurrentIndex(self.tab)

    def _ok(self):
        self.tab = self.tabWidget_registry.currentIndex()

        # Tab 0: Start
        if self.tab == 0:
            self._next_tab() # Switches to the next tab
            return

        # Tab 1: Dataset
        if self.tab == 1:
            self._next_tab() # Switches to the next tab
            return

        # Tab 2: Inclusion/Exclusion criteria
        if self.tab == 2:
            self._next_tab() # Switches to the next tab
            return

        # Tab 3: Primary variable
        if self.tab == 3:
            self._next_tab() # Switches to the next tab
            return
        
        # Tab 4: Process
        if self.tab == 4:
            self._next_tab() # Switches to the next tab
            return