# controller/controller_start.py

from PySide6.QtWidgets import QPushButton, QComboBox, QTabWidget, QInputDialog, QListWidget

class ControllerStart:
    def __init__(self, ui, controller):
        """
        Controller for the 'Start' page.

        :param ui: QWidget corresponding to the 'page_start' in the QStackedWidget.
        :param controller: Main application controller that handles navigation and coordination.
        """
        self.ui = ui
        self.controller = controller

        self.tab = 0 # Initial tab. Default: Welcome

        self.tabWidget_start = self.ui.findChild(QTabWidget, "tabWidget_start")
        self.tabWidget_start.setCurrentIndex(self.tab)

        # Tab: Welcome
        self.pushButton_start_welcome_accept = self.ui.findChild(QPushButton, "pushButton_start_welcome_accept")

        # Tab: Project
        self.listWidget_start_project = self.ui.findChild(QListWidget, "listWidget_start_project")
        self.pushButton_start_project_select = self.ui.findChild(QPushButton, "pushButton_start_project_select")

        # Tab: Data
        self.listWidget_start_data = self.ui.findChild(QListWidget, "listWidget_start_data")
        self.pushButton_start_data_select = self.ui.findChild(QPushButton, "pushButton_start_data_select")

        # Tab: Options
        self.comboBox_start_options = self.ui.findChild(QComboBox, "comboBox_start_options")
        self.pushButton_start_options_select = self.ui.findChild(QPushButton, "pushButton_start_options_select")
        
        self._setup_signals()
        self._set_tabs_disabled()

    def _setup_signals(self):
        """
        Connect UI elements (buttons, etc.) to their respective slots.
        """
        # Tab: Welcome
        self.pushButton_start_welcome_accept.clicked.connect(self._ok)

        # Tab: Project
        self.pushButton_start_project_select.clicked.connect(self._ok)

        # Tab: Datos
        self.pushButton_start_data_select.clicked.connect(self._ok)

        # Tab: Opciones
        self.pushButton_start_options_select.clicked.connect(self._ok)

    def _set_tabs_disabled(self):
        self.tabs = self.tabWidget_start.count()

        for i in range(1, self.tabs):
            self.tabWidget_start.setTabEnabled(i, False)

    def _ok(self):
        # Tab 0: Welcome
        if self.tab == 0:
            self._initialize_tab_project()
            self._next_tab()
            return

        # Tab 1: Project
        if self.tab == 1:
            if self.listWidget_start_project.currentItem().text() == "[New project]":
                self._new_project()
            else:
                self._select_project()
                self._initialize_tab_data()
                self._next_tab()
                return

        # Tab 2: Data
        if self.tab == 2:
            dataset_list = self.controller.dataset_list()
            if dataset_list is not None:
                for dataset in dataset_list:
                    self.listWidget_start_data.addItem(dataset)

    def _next_tab(self):
        """
        Increments the tab index and enables the next tab.
        """
        self.tab = self.tabWidget_start.currentIndex() + 1
        self.tabWidget_start.setCurrentIndex(self.tab)
        self.tabWidget_start.setTabEnabled(self.tab, True)

    # Tab: Project
    def _initialize_tab_project(self):
        self.listWidget_start_project.addItem("[New project]")

        project_list = self.controller.project_list()
        if project_list is not None:
            for project in project_list:
                self.listWidget_start_project.addItem(project)

    def _new_project(self):
        """
        Creates a new project.
        """
        name, ok = QInputDialog.getText(self.ui, "New project", "Enter the project name:")
        if ok and name:
            self.controller.new_project(name)
            self._initialize_tab_project()

    def _select_project(self):
        """
        Reads the selected project from the list widget.
        """
        selected_project = self.listWidget_start_project.currentItem().text()
        self.controller.set_project(selected_project)

    def _initialize_tab_data(self):
        self.listWidget_start_data.addItem("[New dataset]")

        dataset_list = self.controller.dataset_list()
        if dataset_list is not None:
            for dataset in dataset_list:
                self.listWidget_start_data.addItem(dataset)

    def _select_option(self):
        """
        Reads the selected option from the combo box and tells the main controller to switch pages.
        """
        pages = {
            "Start": 0,
            "Patient registry": 1,
            "Observational study": 2,
            "Clinical trial": 3,
        }
        option = self.comboBox_start_options.currentText()
        index = pages.get(option, 0)
        self.controller.change_page(index)
