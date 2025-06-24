# controller/controller_registro.py

from PySide6.QtWidgets import QPushButton, QTabWidget, QListWidget, QLabel, QComboBox, QWidget, QHBoxLayout, QScrollArea, QTextEdit

from my_ludwig.ludwig_data import input_feature_types, output_feature_types

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
        self.pushButton_registry_variable = self.ui.findChild(QPushButton, "pushButton_registry_variable")
        self.pushButton_registry_criteria = self.ui.findChild(QPushButton, "pushButton_registry_criteria")
        self.pushButton_registry_details = self.ui.findChild(QPushButton, "pushButton_registry_details")
        self.textEdit_registry_process_config = self.ui.findChild(QTextEdit, "textEdit_registry_process_config")
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
        self.pushButton_registry_variable.clicked.connect(self._ok)
        self.pushButton_registry_criteria.clicked.connect(self._ok)
        self.pushButton_registry_details.clicked.connect(self._ok)
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
            self._set_primary_variable()
            self.model_registry.model.autoconfig()
            self._update_tab_criteria()
            self._next_tab() # Switches to the next tab
            return

        # Tab 2: Inclusion/Exclusion criteria
        if self.tab == 2:
            self._read_updated_criteria()
            self._next_tab() # Switches to the next tab
            return
        
        # Tab 3: Details
        if self.tab == 3:
            self._update_tab_process()
            self._next_tab() # Switches to the next tab
            return
        
        # Tab 4: Process
        if self.tab == 4:
            self.model_registry.model.auto_train() # Train the model
            self._update_tab_outcome() # Update the outcome tab
            self._next_tab() # Switches to the next tab
            return
        
    def update_page(self):
        """ Initializes the variable tab. """
        self._update_tab_variable()
        
    def _update_tab_variable(self):
        """ Shows the variables in the dataset."""
        variables = self.model_registry.acceptable_stratify_variables()
        self.listWidget_registry_variable.clear()
        for variable in variables:
            self.listWidget_registry_variable.addItem(variable)

    def _set_primary_variable(self):
        """ Reads the selected project from the list widget. """
        selected_primary_variable = self.listWidget_registry_variable.currentItem().text()
        self.model_registry.model.primary_variable = selected_primary_variable

    def _update_tab_criteria(self):
        """ Updates the criteria tab."""
        criteria = self.model_registry.model.ludwig.input_features | self.model_registry.model.ludwig.target
        io = ["", "input", "output"]

        # Clear the layout
        while self.layout_registry_criteria.count():
            item = self.layout_registry_criteria.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add rows to the layout
        for name, type in criteria.items():
            row = QWidget()
            row_layout = QHBoxLayout(row)

            label_criterium = QLabel(name)
            combo_io = QComboBox()
            combo_type = QComboBox()
            ift = [""] + input_feature_types # Empty string for the first item
            if name != self.model_registry.model.primary_variable:
                combo_io.addItems(io)
                combo_io.setCurrentText("input")
                combo_type.addItems(ift)
            else:
                combo_io.addItems(io)
                combo_io.setCurrentText("output")
                combo_type.addItems(output_feature_types)
                
            combo_type.setCurrentText(type)

            row_layout.addWidget(label_criterium)
            row_layout.addWidget(combo_io)
            row_layout.addWidget(combo_type)
            self.layout_registry_criteria.addWidget(row)

    def _read_updated_criteria(self):
        """Reads the user-modified criteria from the layout."""

        for i in range(self.layout_registry_criteria.count()):
            row_widget = self.layout_registry_criteria.itemAt(i).widget()
            if not row_widget:
                continue
            row_layout = row_widget.layout()
            if not row_layout or row_layout.count() < 3:
                continue

            label = row_layout.itemAt(0).widget()
            combo_io = row_layout.itemAt(1).widget()
            combo_type = row_layout.itemAt(2).widget()

            name = label.text()
            io_value = combo_io.currentText()
            type_value = combo_type.currentText()

            if io_value == "input":
                self.model_registry.model.ludwig.input_features[name] = type_value
            else:
                self.model_registry.model.ludwig.target[name] = type_value

    def _update_tab_process(self):
        """ Updates the process tab. """
        summary_text = (f"Project: {self.model_registry.model.project_dir}\n"
                f"Dataset: {self.model_registry.model.dataset_dir}\n"
                f"Samples: {self.model_registry.model.ludwig.samples}\n"
                f"Input features: {self.model_registry.model.ludwig.input_features}\n"
                f"Target: {self.model_registry.model.ludwig.target}\n"
                f"Separator: {self.model_registry.model.ludwig.separator}\n"
                f"Missing data: {self.model_registry.model.ludwig.missing_data}\n"
                f"Runtime: {self.model_registry.model.ludwig.runtime}\n"
                f"Metric: {self.model_registry.model.ludwig.metric}\n"
                f"Time dependable: {self.model_registry.model.ludwig.timedependable}\n"
                )
        
        self.textEdit_registry_process_config.setText(summary_text)

    def _update_tab_outcome(self):
        """ Updates the outcome tab. """
        outcome_text = (f"Project: {self.model_registry.model.project_dir}\n"
                f"Dataset: {self.model_registry.model.dataset_dir}\n"
                f"Samples: {self.model_registry.model.ludwig.samples}\n"
                f"Input features: {self.model_registry.model.ludwig.input_features}\n"
                f"Target: {self.model_registry.model.ludwig.target}\n"
                f"Separator: {self.model_registry.model.ludwig.separator}\n"
                f"Missing data: {self.model_registry.model.ludwig.missing_data}\n"
                f"Runtime: {self.model_registry.model.ludwig.runtime}\n"
                f"Metric: {self.model_registry.model.ludwig.metric}\n"
                f"Time dependable: {self.model_registry.model.ludwig.timedependable}\n"
                )
        
        self.textEdit_registry_outcome_config.setText(outcome_text)