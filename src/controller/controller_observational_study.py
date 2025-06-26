# controller/controller_observational_study.py

from PySide6.QtWidgets import QPushButton, QTabWidget, QListWidget, QLabel, QComboBox, QWidget, QHBoxLayout, QScrollArea, QTextEdit, QLineEdit, QSizePolicy

from my_ludwig.ludwig_data import input_feature_types, output_feature_types, separators, missing_data_options, metrics, goals

class ControllerObservationalStudy:
    def __init__(self, ui, model_observational, controller):
        """
        :param ui: QWidget corresponding to the page in the QStackedWidget.
        :param model: Instance of the business logic model.
        :param app_controller: Main application controller that handles navigation and coordination.
        """
        self.ui = ui
        self.model_observational = model_observational
        self.controller = controller

        self.tab = 1 # Initial tab. Default: Inclusion/Exclusion criteria

        self.tabWidget_observational = self.ui.findChild(QTabWidget, "tabWidget_observational")
        self.tabWidget_observational.setCurrentIndex(self.tab)

        self.pushButton_observational_start = self.ui.findChild(QPushButton, "pushButton_observational_start")
        self.listWidget_observational_variable = self.ui.findChild(QListWidget, "listWidget_observational_variable")
        self.pushButton_observational_variable = self.ui.findChild(QPushButton, "pushButton_observational_variable")
        self.pushButton_observational_criteria = self.ui.findChild(QPushButton, "pushButton_observational_criteria")
        self.pushButton_observational_settings = self.ui.findChild(QPushButton, "pushButton_observational_settings")
        self.textEdit_observational_process_summary = self.ui.findChild(QTextEdit, "textEdit_observational_process_summary")
        self.pushButton_observational_process = self.ui.findChild(QPushButton, "pushButton_observational_process")

        scroll_area = self.ui.findChild(QScrollArea, "scrollArea_observational_criteria")
        container = scroll_area.widget()
        self.layout_observational_criteria = container.layout()
        
        scroll_area = self.ui.findChild(QScrollArea, "scrollArea_observational_settings")
        container = scroll_area.widget()
        self.layout_observational_settings = container.layout()

        self._setup_signals()
        self._set_tabs_disabled()

        self.tabWidget_observational.setCurrentIndex(1)

    def _setup_signals(self):
        """ Connect UI elements (buttons, etc.) to their respective slots. """
        self.pushButton_observational_start.clicked.connect(self._back_to_start)
        self.pushButton_observational_variable.clicked.connect(self._ok)
        self.pushButton_observational_criteria.clicked.connect(self._ok)
        self.pushButton_observational_settings.clicked.connect(self._ok)
        self.pushButton_observational_process.clicked.connect(self._ok)

    def _set_tabs_disabled(self):
        """ Disables all tabs except the first two. """
        tabs = self.tabWidget_observational.count()

        for i in range(2, tabs):
            self.tabWidget_observational.setTabEnabled(i, False)

    def _back_to_start(self):
        self.controller.change_page(0)

    def _next_tab(self):
        """ Increments the tab index and enables the next tab. """
        self.tab = self.tabWidget_observational.currentIndex() + 1
        self.tabWidget_observational.setTabEnabled(self.tab, True)
        self.tabWidget_observational.setCurrentIndex(self.tab)

    def _ok(self):
        self.tab = self.tabWidget_observational.currentIndex()
        
        # Tab 1: Primary variable
        if self.tab == 1:
            self._set_primary_variable()
            self.model_observational.model.autoconfig()
            self._update_tab_criteria()
            self._next_tab() # Switches to the next tab
            return

        # Tab 2: Inclusion/Exclusion criteria
        if self.tab == 2:
            self._read_updated_criteria()
            self._update_tab_settings()
            self._next_tab() # Switches to the next tab
            return
        
        # Tab 3: Settings
        if self.tab == 3:
            self._read_updated_settings()
            self._update_tab_process()
            self._next_tab() # Switches to the next tab
            return
        
        # Tab 4: Process
        if self.tab == 4:
            self.model_observational.model.auto_train() # Train the model
            self._update_tab_outcome() # Update the outcome tab
            self._next_tab() # Switches to the next tab
            return
        
    def update_page(self):
        """ Initializes the variable tab. """
        self._update_tab_variable()

    def _update_tab_variable(self):
        """ Shows the variables in the dataset."""
        variables = self.model_observational.model.acceptable_stratify_variables()
        self.listWidget_observational_variable.clear()
        for variable in variables:
            self.listWidget_observational_variable.addItem(variable)

    def _set_primary_variable(self):
        """ Reads the selected project from the list widget. """
        selected_primary_variable = self.listWidget_observational_variable.currentItem().text()
        self.model_observational.model.primary_variable = selected_primary_variable

    def _update_tab_criteria(self):
        """ Updates the criteria tab."""
        criteria = self.model_observational.model.ludwig.input_features | self.model_observational.model.ludwig.target
        io = ["", "input", "output"]

        # Clear the layout
        while self.layout_observational_criteria.count():
            item = self.layout_observational_criteria.takeAt(0)
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
            if name != self.model_observational.model.primary_variable:
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
            self.layout_observational_criteria.addWidget(row)

    def _read_updated_criteria(self):
        """Reads the user-modified criteria from the layout."""

        for i in range(self.layout_observational_criteria.count()):
            row_widget = self.layout_observational_criteria.itemAt(i).widget()
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
                self.model_observational.model.ludwig.input_features[name] = type_value
            else:
                self.model_observational.model.ludwig.target[name] = type_value

    def _update_tab_settings(self):
        """Updates the settings tab with predefined configuration options depending on primary variable type."""
        target_type = next(iter(self.model_observational.model.ludwig.target.values()))

        settings = {
            "Separator": [""] + separators,
            "Missing-data": [""] + missing_data_options,
            "Metric": metrics.get(target_type, []),
            "Goal":  goals,
            "Time-dependable": ["False", "True"]
        }

        while self.layout_observational_settings.count():
            item = self.layout_observational_settings.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for label_text, options in settings.items():
            row = QWidget()
            row_layout = QHBoxLayout(row)

            label = QLabel(label_text)
            combo = QComboBox()
            combo.addItems(options)

            row_layout.addWidget(label)
            row_layout.addWidget(combo)
            self.layout_observational_settings.addWidget(row)

        row = QWidget()
        row_layout = QHBoxLayout(row)

        label = QLabel("runtime")
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Enter max runtime in seconds (Default: 7200)")
        line_edit.setMaximumWidth(700)

        row_layout.addWidget(label)
        row_layout.addWidget(line_edit)
        self.layout_observational_settings.addWidget(row)

    def _read_updated_settings(self):
        """Reads the user-modified settings from the layout."""

        for i in range(self.layout_observational_settings.count()):
            row_widget = self.layout_observational_settings.itemAt(i).widget()
            if not row_widget:
                continue
            row_layout = row_widget.layout()
            if not row_layout or row_layout.count() < 2:
                continue

            label = row_layout.itemAt(0).widget()
            input_widget = row_layout.itemAt(1).widget()

            key = label.text()

            if isinstance(input_widget, QComboBox):
                value = input_widget.currentText()
            elif isinstance(input_widget, QLineEdit):
                value = input_widget.text()
            else:
                continue  # Skip unknown widgets

            setattr(self.model_observational.model.ludwig, key, value)

    def _update_tab_process(self):
        """ Updates the process tab. """
        summary_text = (f"Project: {self.model_observational.model.project_dir}\n"
                f"Dataset: {self.model_observational.model.dataset_dir}\n"
                f"Samples: {self.model_observational.model.ludwig.samples}\n"
                f"Input features: {self.model_observational.model.ludwig.input_features}\n"
                f"Target: {self.model_observational.model.ludwig.target}\n"
                f"Separator: {self.model_observational.model.ludwig.separator}\n"
                f"Missing data: {self.model_observational.model.ludwig.missing_data}\n"
                f"Runtime: {self.model_observational.model.ludwig.runtime}\n"
                f"Metric: {self.model_observational.model.ludwig.metric}\n"
                f"Time dependable: {self.model_observational.model.ludwig.timedependable}\n"
                )
        
        self.textEdit_observational_process_summary.setText(summary_text)