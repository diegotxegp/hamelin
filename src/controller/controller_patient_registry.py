# controller/controller_registro.py

from PySide6.QtWidgets import QPushButton, QTabWidget, QListWidget, QLabel, QComboBox, QWidget, QHBoxLayout, QScrollArea

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

        self.tab = 1 # Initial tab. Default: Variable

        self.tabWidget_registry = self.ui.findChild(QTabWidget, "tabWidget_registry")
        self.tabWidget_registry.setCurrentIndex(self.tab)

        self.pushButton_registry_start = self.ui.findChild(QPushButton, "pushButton_registry_start")
        self.listWidget_registry_variable = self.ui.findChild(QListWidget, "listWidget_registry_variable")
        self.pushButton_registry_variable_ok = self.ui.findChild(QPushButton, "pushButton_registry_variable_ok")
        self.pushButton_registry_criteria_add = self.ui.findChild(QPushButton, "pushButton_registry_criteria_add")
        self.pushButton_registry_details_ok = self.ui.findChild(QPushButton, "pushButton_registry_details_ok")
        self.pushButton_registry_process = self.ui.findChild(QPushButton, "pushButton_registry_process")

        scroll_area = self.ui.findChild(QScrollArea, "scrollArea_registry_criteria")
        contenedor = scroll_area.widget()
        self.layout_registry_criteria = contenedor.layout()

        self._setup_signals()
        self._set_tabs_disabled()

    def _setup_signals(self):
        """
        Connect UI elements (buttons, etc.) to their respective slots.
        """
        self.pushButton_registry_start.clicked.connect(self._back_to_start)
        self.pushButton_registry_variable_ok.clicked.connect(self._ok)
        self.pushButton_registry_criteria_add.clicked.connect(self._ok)
        self.pushButton_registry_details_ok.clicked.connect(self._ok)
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
        
        # Tab 1: Primary variable
        if self.tab == 1:
            self._select_primary_variable()
            self._update_tab_criteria()
            self._next_tab() # Switches to the next tab
            return

        # Tab 2: Inclusion/Exclusion criteria
        if self.tab == 2:
            self._next_tab() # Switches to the next tab
            return
        
        # Tab 3: Details
        if self.tab == 3:
            self._next_tab() # Switches to the next tab
            return
        
        # Tab 4: Process
        if self.tab == 4:
            self._next_tab() # Switches to the next tab
            return
        
    def update_page(self):
        """
        Initializes the variable tab.
        """
        self._update_tab_variable()
        
    def _update_tab_variable(self):
        """
        Shows the variables in the dataset.
        """
        variables = self.model_registry.all_variables()
        self.listWidget_registry_variable.clear()
        for variable in variables:
            self.listWidget_registry_variable.addItem(variable)

    def _select_primary_variable(self):
        """
        Reads the selected project from the list widget.
        """
        selected_primary_variable = self.listWidget_registry_variable.currentItem().text()
        self.model_registry.select_primary_variable(selected_primary_variable)

    def _update_tab_criteria(self):
        """
        Updates the criteria tab.
        """        
        criterios = {
            "Edad": "Numérico",
            "Sexo": "Categórico",
            "Diagnóstico": "Texto libre"
        }

        tipos = ["Numérico", "Categórico", "Texto libre"]

        # Clear the layout
        while self.layout_registry_criteria.count():
            item = self.layout_registry_criteria.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add rows to the layout
        for name, type in criterios.items():
            row = QWidget()
            row_layout = QHBoxLayout(row)

            label = QLabel(name)
            combo = QComboBox()
            combo.addItems(tipos)
            combo.setCurrentText(type)

            row_layout.addWidget(label)
            row_layout.addWidget(combo)
            self.layout_registry_criteria.addWidget(row)