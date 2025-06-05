# controller/controller_start.py

from PySide6.QtWidgets import QPushButton, QComboBox, QTabWidget, QInputDialog, QListWidget

class ControllerStart:
    def __init__(self, ui, model, controller):
        """
        Controller for the 'Start' page.

        :param ui: QWidget corresponding to the 'page_inicio' in the QStackedWidget.
        :param model: Instance of the business logic model.
        :param app_controller: Main application controller that handles navigation and coordination.
        """
        self.ui = ui
        self.model = model
        self.controller = controller

        self.tabWidget_start = self.ui.findChild(QTabWidget, "tabWidget_start")
        self.tabWidget_start.setCurrentIndex(0)

        # Tab: Welcome
        self.pushButton_start_welcome_accept = self.ui.findChild(QPushButton, "pushButton_start_welcome_accept")

        # Tab: Project
        self.listWidget_start_project = self.ui.findChild(QListWidget, "listWidget_start_project")
        self.pushButton_start_project_select = self.ui.findChild(QPushButton, "pushButton_start_project_select")
        self.listWidget_start_project.addItem("[New project]")
        project_list = self.model.project_list()
        for project in project_list:
            self.listWidget_start_project.addItem(project)

        # Tab: Data
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
        self.pushButton_start_welcome_accept.clicked.connect(self._next_tab)

        # Tab: Project
        self.pushButton_start_project_select.clicked.connect(self._new_project)

        # Tab: Datos
        self.pushButton_start_data_select.clicked.connect(self.model.attach_csv)

        # Tab: Opciones
        self.pushButton_start_options_select.clicked.connect(self._select_option)

    def _set_tabs_disabled(self):
        self.tabs = self.tabWidget_start.count()

        for i in range(1, self.tabs):
            self.tabWidget_start.setTabEnabled(i, False)

    def _next_tab(self):
        """
        Increments the tab index and enables the next tab.
        """
        next_tab = self.tabWidget_start.currentIndex() + 1
        self.tabWidget_start.setCurrentIndex(next_tab)
        self.tabWidget_start.setTabEnabled(next_tab, True)

    def _new_project(self):
        """
        Creates a new project.
        """
        if self.listWidget_start_project.currentItem().text() == "[New project]":
            name, ok = QInputDialog.getText(self.ui, "New project", "Enter the project name:")
            if ok and name:
                self.model.new_project(name)
                self.listWidget_start_project.addItem(name)

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
