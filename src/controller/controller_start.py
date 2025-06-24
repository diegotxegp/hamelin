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
        self.pushButton_start_welcome = self.ui.findChild(QPushButton, "pushButton_start_welcome")

        # Tab: Project
        self.listWidget_start_project = self.ui.findChild(QListWidget, "listWidget_start_project")
        self.pushButton_start_project = self.ui.findChild(QPushButton, "pushButton_start_project")

        # Tab: Data
        self.listWidget_start_data = self.ui.findChild(QListWidget, "listWidget_start_data")
        self.pushButton_start_data = self.ui.findChild(QPushButton, "pushButton_start_data")

        # Tab: Status
        self.textEdit_start_status = self.ui.findChild(QTextEdit, "textEdit_start_status")
        self.textEdit_start_status_text = self.ui.findChild(QTextEdit, "textEdit_start_status_text")
        self.pushButton_start_status = self.ui.findChild(QPushButton, "pushButton_start_status")

        # Tab: Options
        self.comboBox_start_options = self.ui.findChild(QComboBox, "comboBox_start_options")
        self.pushButton_start_options = self.ui.findChild(QPushButton, "pushButton_start_options")
        
        self._setup_signals()
        self._set_tabs_disabled()

    def _setup_signals(self):
        """
        Connect UI elements (buttons, etc.) to their respective slots.
        """
        # Tab: Welcome
        self.pushButton_start_welcome.clicked.connect(self._ok)

        # Tab: Project
        self.pushButton_start_project.clicked.connect(self._ok)

        # Tab: Datos
        self.pushButton_start_data.clicked.connect(self._ok)

        # Tab: Status
        self.pushButton_start_status.clicked.connect(self._ok)

        # Tab: Opciones
        self.pushButton_start_options.clicked.connect(self._ok)

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
            self._update_tab_project() # Updates the project tab
            self._next_tab() # Switches to the next tab
            return

        # Tab 1: Project
        if self.tab == 1:
            if self.listWidget_start_project.currentItem().text() == "[New project]":
                self._new_project()
            else:
                self._set_project() # Selects the project
                self._update_tab_data() # Updates the data tab
                self._next_tab() # Switches to the next tab
                return

        # Tab 2: Data
        if self.tab == 2:
            if self.listWidget_start_data.currentItem().text() == "[New dataset]":
                self._load_dataset()
            else:
                self._set_dataset() # Selects the dataset
                self._update_tab_status() # Updates the status tab
                self._next_tab() # Switches to the next tab
                return

        # Tab 3: Status
        if self.tab == 3:
            self._set_status() # Selects the status
            self._next_tab() # Switches to the next tab
            return
        
        # Tab 4: Options
        if self.tab == 4:
            self._select_option() # Selects the option
            return


    def _next_tab(self):
        """
        Increments the tab index and enables the next tab.
        """
        self.tab = self.tabWidget_start.currentIndex() + 1
        self.tabWidget_start.setTabEnabled(self.tab, True)
        self.tabWidget_start.setCurrentIndex(self.tab)

    def _update_tab_project(self):
        """
        Updates the project tab.
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
                self.controller.popup_message(self.ui, "Project name exists", "This project name already exists. Please choose a different name.")
            else:
                self._update_tab_project()

    def _set_project(self):
        """
        Reads the selected project from the list widget.
        """
        selected_project = self.listWidget_start_project.currentItem().text()
        self.model_start.set_project(selected_project)

    def _update_tab_data(self):
        self.listWidget_start_data.clear()
        
        self.listWidget_start_data.addItem("[New dataset]")

        dataset_list = self.model_start.dataset_list()
        if dataset_list is not None:
            for dataset in dataset_list:
                self.listWidget_start_data.addItem(dataset)

    def _load_dataset(self):
        # Open file dialog to select the CSV file
        origin_path, _ = QFileDialog.getOpenFileName(None, "Open CSV File", "", "CSV Files (*.csv)")
        if origin_path:
            self.model_start.load_dataset(origin_path)

        self._update_tab_data()

    def _set_dataset(self):
        """
        Reads the selected dataset from the list widget.
        """
        selected_dataset = self.listWidget_start_data.currentItem().text()
        self.model_start.set_dataset(selected_dataset)

    def _update_tab_status(self):
        self.textEdit_start_status_text.clear()

        self.model_start.read_status_from_file()

        if self.model_start.model.status is not None:
            self.textEdit_start_status_text.setPlainText(self.model_start.model.status)

    def _set_status(self):
        """ Reads the selected status from the list widget. """
        status = self.textEdit_start_status_text.toPlainText()

        if status is not None:
            self.model_start.set_status_in_file(status)

    def _new_status(self):
        """
        Creates a new status.
        """
        name, ok = QInputDialog.getText(self.ui, "New status", "Enter the status name:")
        if ok and name:
            ns = self.model_start.new_status(name)
            if ns == None:
                self.controller.popup_message(self.ui, "Status name exists", "This status name already exists. Please choose a different name.")
            else:
                self._update_tab_status()

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
