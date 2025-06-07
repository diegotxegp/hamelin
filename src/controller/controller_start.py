# controller/controller_start.py

from PySide6.QtWidgets import QPushButton, QComboBox, QTabWidget, QInputDialog, QListWidget, QTextEdit, QFileDialog

class ControllerStart:
    def __init__(self, ui, model_start, controller):
        """
        Controller for the 'Start' page.

        :param ui: QWidget corresponding to the 'page_start' in the QStackedWidget.
        :param controller: Main application controller that handles navigation and coordination.
        """
        self.ui = ui
        self.model_start = model_start
        self.controller = controller

        self.tab = 0 # Initial tab. Default: Welcome

        self.tabWidget_start = self.ui.findChild(QTabWidget, "tabWidget_start")
        self.tabWidget_start.setCurrentIndex(self.tab)

        # Tab: Welcome
        self.pushButton_start_welcome_ok = self.ui.findChild(QPushButton, "pushButton_start_welcome_ok")

        # Tab: Project
        self.listWidget_start_project = self.ui.findChild(QListWidget, "listWidget_start_project")
        self.pushButton_start_project_ok = self.ui.findChild(QPushButton, "pushButton_start_project_ok")

        # Tab: Data
        self.listWidget_start_data = self.ui.findChild(QListWidget, "listWidget_start_data")
        self.pushButton_start_data_ok = self.ui.findChild(QPushButton, "pushButton_start_data_ok")

        # Tab: Status
        self.textEdit_start_status = self.ui.findChild(QTextEdit, "textEdit_start_status")
        self.pushButton_start_status_ok = self.ui.findChild(QPushButton, "pushButton_start_status_ok")

        # Tab: Options
        self.comboBox_start_options = self.ui.findChild(QComboBox, "comboBox_start_options")
        self.pushButton_start_options_ok = self.ui.findChild(QPushButton, "pushButton_start_options_ok")
        
        self._setup_signals()
        self._set_tabs_disabled()

    def _setup_signals(self):
        """
        Connect UI elements (buttons, etc.) to their respective slots.
        """
        # Tab: Welcome
        self.pushButton_start_welcome_ok.clicked.connect(self._ok)

        # Tab: Project
        self.pushButton_start_project_ok.clicked.connect(self._ok)

        # Tab: Datos
        self.pushButton_start_data_ok.clicked.connect(self._ok)

        # Tab: Status
        self.pushButton_start_status_ok.clicked.connect(self._ok)

        # Tab: Opciones
        self.pushButton_start_options_ok.clicked.connect(self._ok)

    def _set_tabs_disabled(self):
        """
        Disables all tabs except the first one.
        """
        tabs = self.tabWidget_start.count()

        for i in range(1, tabs):
            self.tabWidget_start.setTabEnabled(i, False)

    def _ok(self):
        self.tab = self.tabWidget_start.currentIndex()

        # Tab 0: Welcome
        if self.tab == 0:
            self._initialize_tab_project() # Initializes the project tab
            self._next_tab() # Switches to the next tab
            return

        # Tab 1: Project
        if self.tab == 1:
            if self.listWidget_start_project.currentItem().text() == "[New project]":
                self._new_project()
            else:
                self._select_project() # Selects the project
                self._initialize_tab_data() # Initializes the data tab
                self._next_tab() # Switches to the next tab
                return

        # Tab 2: Data
        if self.tab == 2:
            if self.listWidget_start_data.currentItem().text() == "[New dataset]":
                self._new_dataset()
            else:
                self._select_dataset() # Selects the dataset
                self._initialize_tab_status() # Initializes the status tab
                self._next_tab() # Switches to the next tab
                return

        # Tab 3: Status
        # Tab 4: Options


    def _next_tab(self):
        """
        Increments the tab index and enables the next tab.
        """
        self.tab = self.tabWidget_start.currentIndex() + 1
        self.tabWidget_start.setTabEnabled(self.tab, True)
        self.tabWidget_start.setCurrentIndex(self.tab)

    def _initialize_tab_project(self):
        """
        Initializes the project tab.
        """
        self.listWidget_start_project.clear()

        self.listWidget_start_project.addItem("[New project]") # Writes "[New project]" in the list widget

        project_list = self.model_start.project_list() # Gets the list of projects
        # If the list is not empty, add each project to the list widget
        if project_list is not None:
            for project in project_list:
                self.listWidget_start_project.addItem(project)

    def _new_project(self):
        """
        Creates a new project.
        """
        name, ok = QInputDialog.getText(self.ui, "New project", "Enter the project name:")
        if ok and name:
            np = self.model_start.new_project(name)
            if np == None:
                self.controller.emerging_message(self.ui, "Project name exists", "This project name already exists. Please choose a different name.")
            else:
                self._initialize_tab_project()

    def _select_project(self):
        """
        Reads the selected project from the list widget.
        """
        selected_project = self.listWidget_start_project.currentItem().text()
        self.model_start.select_project(selected_project)

    def _initialize_tab_data(self):
        self.listWidget_start_data.clear()
        
        self.listWidget_start_data.addItem("[New dataset]")

        dataset_list = self.model_start.dataset_list()
        if dataset_list is not None:
            for dataset in dataset_list:
                self.listWidget_start_data.addItem(dataset)

    def _new_dataset(self):
        # Open file dialog to select the CSV file
        origin_path, _ = QFileDialog.getOpenFileName(None, "Open CSV File", "", "CSV Files (*.csv)")
        if origin_path:
            self.model_start.new_dataset(origin_path)

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
