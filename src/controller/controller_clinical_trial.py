# controller/controller_clinical_trial.py

from PySide6.QtWidgets import QPushButton, QTabWidget, QListWidget, QLabel, QComboBox, QWidget, QHBoxLayout, QScrollArea, QTextEdit, QLineEdit, QSizePolicy

from my_ludwig.ludwig_data import input_feature_types, output_feature_types, separators, missing_data_options, metrics, goals

class ControllerClinicalTrial:
    def __init__(self, ui, model_clinical, controller):
        """
        :param ui: QWidget corresponding to the page in the QStackedWidget.
        :param model: Instance of the business logic model.
        :param app_controller: Main application controller that handles navigation and coordination.
        """
        self.ui = ui
        self.model_clinical = model_clinical
        self.controller = controller

        self.tab = 1 # Initial tab. Default: Primary variable

        self.tabWidget_clinical = self.ui.findChild(QTabWidget, "tabWidget_clinical")
        self.tabWidget_clinical.setCurrentIndex(self.tab)

        # Start tab
        self.pushButton_clinical_start = self.ui.findChild(QPushButton, "pushButton_clinical_start")
        
        # Primary variable tab
        self.listWidget_clinical_variable = self.ui.findChild(QListWidget, "listWidget_clinical_variable")
        self.pushButton_clinical_variable_add = self.ui.findChild(QPushButton, "pushButton_clinical_variable_add")
        
        # Criteria tab
        self.scrollArea_clinical_criteria = self.ui.findChild(QScrollArea, "scrollArea_clinical_criteria")
        container_criteria = self.scrollArea_clinical_criteria.widget()
        self.layout_clinical_criteria = container_criteria.layout()
        self.pushButton_clinical_criteria_add = self.ui.findChild(QPushButton, "pushButton_clinical_criteria_add")
        
        # Investigational drug tab
        self.scrollArea_clinical_investigational = self.ui.findChild(QScrollArea, "scrollArea_clinical_investigational")
        self.pushButton_clinical_investigational_add = self.ui.findChild(QPushButton, "pushButton_clinical_investigational_add")
        
        # Control drug tab
        self.scrollArea_clinical_control = self.ui.findChild(QScrollArea, "scrollArea_clinical_control")
        self.pushButton_clinical_control_add = self.ui.findChild(QPushButton, "pushButton_clinical_control_add")
        
        # Disease tab
        self.scrollArea_clinical_disease = self.ui.findChild(QScrollArea, "scrollArea_clinical_disease")
        self.pushButton_clinical_disease_add = self.ui.findChild(QPushButton, "pushButton_clinical_disease_add")
        
        # Process tab
        self.textEdit_4 = self.ui.findChild(QTextEdit, "textEdit_4")
        self.pushButton_clinical_process = self.ui.findChild(QPushButton, "pushButton_clinical_process")

        self._setup_signals()
        self._set_tabs_disabled()
        self._setup_scroll_areas()

    def _setup_signals(self):
        """
        Connect UI elements (buttons, etc.) to their respective slots.
        """
        self.pushButton_clinical_start.clicked.connect(self._back_to_start)
        self.pushButton_clinical_variable_add.clicked.connect(self._ok)
        self.pushButton_clinical_criteria_add.clicked.connect(self._ok)
        self.pushButton_clinical_investigational_add.clicked.connect(self._ok)
        self.pushButton_clinical_control_add.clicked.connect(self._ok)
        self.pushButton_clinical_disease_add.clicked.connect(self._ok)
        self.pushButton_clinical_process.clicked.connect(self._ok)

    def _set_tabs_disabled(self):
        """
        Disables all tabs except the first two.
        """
        tabs = self.tabWidget_clinical.count()

        for i in range(2, tabs):
            self.tabWidget_clinical.setTabEnabled(i, False)
            
    def _setup_scroll_areas(self):
        """
        Initialize the scroll areas for criteria, investigational drug, control drug, and disease tabs.
        Only setup when data is available.
        """
        # Only setup if data is loaded
        if (hasattr(self.model_clinical, 'model') and 
            self.model_clinical.model and 
            self.model_clinical.model.df is not None):
            
            # Setup criteria scroll area
            self._update_tab_criteria()
            
            # Setup investigational drug scroll area
            self._update_tab_investigational()
            
            # Setup control drug scroll area
            self._update_tab_control()
            
            # Setup disease scroll area
            self._update_tab_disease()

    def _back_to_start(self):
        self.controller.change_page(0)
        
    def _next_tab(self):
        """Increments the tab index and enables the next tab."""
        self.tab = self.tabWidget_clinical.currentIndex() + 1
        self.tabWidget_clinical.setTabEnabled(self.tab, True)
        self.tabWidget_clinical.setCurrentIndex(self.tab)

    def _ok(self):
        self.tab = self.tabWidget_clinical.currentIndex()
        
        # Tab 1: Primary variable
        if self.tab == 1:
            if self._set_primary_variable():
                try:
                    self.model_clinical.model.autoconfig()
                    # After autoconfig, update all ScrollAreas with Ludwig data
                    self._setup_scroll_areas()
                    self._next_tab()
                except Exception as e:
                    self.controller.popup_message(self.ui, "Configuration Error", 
                                                f"Error configuring the model: {str(e)}")
            return

        # Tab 2: Inclusion/Exclusion criteria
        if self.tab == 2:
            self._set_criteria()
            self._next_tab()
            return
        
        # Tab 3: Investigational drug
        if self.tab == 3:
            if self._set_investigational_drug():
                self._next_tab()
            return
        
        # Tab 4: Control drug
        if self.tab == 4:
            if self._set_control_drug():
                self._next_tab()
            return
            
        # Tab 5: Disease/Disorder
        if self.tab == 5:
            self._set_disease()
            self._next_tab()
            return
        
        # Tab 6: Process
        if self.tab == 6:
            self._update_process_summary()
            if self.model_clinical.is_ready_for_analysis():
                try:
                    self.model_clinical.model.auto_train() # Train the model
                    self._next_tab() # Switch to outcome tab
                except Exception as e:
                    self.controller.popup_message(self.ui, "Training Error", 
                                                f"Error training the model: {str(e)}")
            else:
                self.controller.popup_message(self.ui, "Incomplete Information", 
                                            "Please provide at least Primary Endpoint, Experimental Treatment, and Control Group information.")
            return
    
    def update_page(self):
        """Initialize the clinical trial page."""
        self._update_tab_variable()
        # Update ScrollAreas when dataset is loaded
        if hasattr(self.model_clinical, 'model') and self.model_clinical.model and self.model_clinical.model.df is not None:
            self._update_tab_criteria()
            self._update_tab_investigational()
            self._update_tab_control()
            self._update_tab_disease()
        
    def _update_tab_variable(self):
        """Shows the variables in the dataset."""
        variables = self.model_clinical.model.acceptable_stratify_variables()
        self.listWidget_clinical_variable.clear()
        for variable in variables:
            self.listWidget_clinical_variable.addItem(variable)
        
    def _set_primary_variable(self):
        """Set the primary endpoint variable."""
        selected_item = self.listWidget_clinical_variable.currentItem()
        if selected_item:
            primary_variable = selected_item.text()
            self.model_clinical.primary_variable = primary_variable
            self.model_clinical.model.primary_variable = primary_variable
            return True
        else:
            self.controller.popup_message(self.ui, "Missing Selection", 
                                        "Please select a primary endpoint variable from the list.")
            return False
    
    def _set_criteria(self):
        """Set inclusion/exclusion criteria."""
        self._read_updated_criteria()
        return True
    
    def _set_investigational_drug(self):
        """Set investigational drug information."""
        self._read_updated_investigational()
        if self.model_clinical.investigational_drug and "No investigational drug" not in self.model_clinical.investigational_drug:
            return True
        else:
            self.controller.popup_message(self.ui, "Missing Information", 
                                        "Please configure the experimental treatment information.")
            return False
    
    def _set_control_drug(self):
        """Set control drug information."""
        self._read_updated_control()
        if self.model_clinical.control_drug and "No control group" not in self.model_clinical.control_drug:
            return True
        else:
            self.controller.popup_message(self.ui, "Missing Information", 
                                        "Please configure the control group information.")
            return False
    
    def _set_disease(self):
        """Set disease/disorder information."""
        self._read_updated_disease()
        # Disease is optional, so always return True
        return True
    
    def _update_process_summary(self):
        """Update the process summary with collected information."""
        summary = []
        
        if self.model_clinical.primary_variable:
            summary.append(f"Primary Endpoint: {self.model_clinical.primary_variable}")
        
        if self.model_clinical.inclusion_criteria:
            summary.append(f"Selection Criteria: {self.model_clinical.inclusion_criteria}")
        
        if self.model_clinical.investigational_drug:
            summary.append(f"Experimental Treatment: {self.model_clinical.investigational_drug}")
        
        if self.model_clinical.control_drug:
            summary.append(f"Control Group: {self.model_clinical.control_drug}")
        
        if self.model_clinical.disease:
            summary.append(f"Target Condition: {self.model_clinical.disease}")
        
        summary_text = "\n\n".join(summary) if summary else "No information collected yet."
        self.textEdit_4.setPlainText(summary_text)

    def _update_tab_criteria(self):
        """Setup the criteria tab with dynamic feature selection widgets."""
        if not hasattr(self.model_clinical, 'model') or not self.model_clinical.model or self.model_clinical.model.df is None:
            return

        # Exact same logic as Patient Registry
        criteria = self.model_clinical.model.ludwig.input_features | self.model_clinical.model.ludwig.target
        io = ["", "input", "output"]

        # Clear existing widgets - identical to Patient Registry
        while self.layout_clinical_criteria.count():
            item = self.layout_clinical_criteria.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add rows to the layout - identical to Patient Registry
        for name, type in criteria.items():
            row = QWidget()
            row_layout = QHBoxLayout(row)

            label_criterium = QLabel(name)
            combo_io = QComboBox()
            combo_type = QComboBox()
            ift = [""] + input_feature_types # Empty string for the first item
            if name != self.model_clinical.model.primary_variable:
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
            self.layout_clinical_criteria.addWidget(row)

    def _update_tab_investigational(self):
        """Setup the investigational drug tab with dynamic feature selection widgets."""
        if not hasattr(self.model_clinical, 'model') or not self.model_clinical.model or self.model_clinical.model.df is None:
            return

        columns = self.model_clinical.model.df.columns.tolist()
        scroll_widget = self.scrollArea_clinical_investigational.widget()
        layout = scroll_widget.layout()

        # Clear existing widgets
        for i in reversed(range(layout.count())):
            child = layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Add investigational drug selection widgets
        for column in columns:
            h_layout = QHBoxLayout()
            
            # Column name label
            label = QLabel(column)
            label.setMinimumWidth(150)
            h_layout.addWidget(label)
            
            # Feature type selection
            feature_combo = QComboBox()
            feature_combo.addItems(["ignore", "treatment_group", "drug_name", "dosage", "administration_route"])
            feature_combo.setObjectName(f"investigational_combo_{column}")
            h_layout.addWidget(feature_combo)
            
            # Add horizontal layout to main layout
            widget = QWidget()
            widget.setLayout(h_layout)
            layout.addWidget(widget)

    def _update_tab_control(self):
        """Setup the control drug tab with dynamic feature selection widgets."""
        if not hasattr(self.model_clinical, 'model') or not self.model_clinical.model or self.model_clinical.model.df is None:
            return

        columns = self.model_clinical.model.df.columns.tolist()
        scroll_widget = self.scrollArea_clinical_control.widget()
        layout = scroll_widget.layout()

        # Clear existing widgets
        for i in reversed(range(layout.count())):
            child = layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Add control drug selection widgets
        for column in columns:
            h_layout = QHBoxLayout()
            
            # Column name label
            label = QLabel(column)
            label.setMinimumWidth(150)
            h_layout.addWidget(label)
            
            # Feature type selection
            feature_combo = QComboBox()
            feature_combo.addItems(["ignore", "control_group", "control_treatment", "placebo", "standard_care"])
            feature_combo.setObjectName(f"control_combo_{column}")
            h_layout.addWidget(feature_combo)
            
            # Add horizontal layout to main layout
            widget = QWidget()
            widget.setLayout(h_layout)
            layout.addWidget(widget)

    def _update_tab_disease(self):
        """Setup the disease tab with dynamic feature selection widgets."""
        if not hasattr(self.model_clinical, 'model') or not self.model_clinical.model or self.model_clinical.model.df is None:
            return

        columns = self.model_clinical.model.df.columns.tolist()
        scroll_widget = self.scrollArea_clinical_disease.widget()
        layout = scroll_widget.layout()

        # Clear existing widgets
        for i in reversed(range(layout.count())):
            child = layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Add disease selection widgets
        for column in columns:
            h_layout = QHBoxLayout()
            
            # Column name label
            label = QLabel(column)
            label.setMinimumWidth(150)
            h_layout.addWidget(label)
            
            # Feature type selection
            feature_combo = QComboBox()
            feature_combo.addItems(["ignore", "disease_stage", "severity", "subtype", "diagnosis_code"])
            feature_combo.setObjectName(f"disease_combo_{column}")
            h_layout.addWidget(feature_combo)
            
            # Add horizontal layout to main layout
            widget = QWidget()
            widget.setLayout(h_layout)
            layout.addWidget(widget)

    def _read_updated_criteria(self):
        """Reads the user-modified criteria from the layout."""
        if not hasattr(self.model_clinical, 'model') or not self.model_clinical.model or self.model_clinical.model.df is None:
            return

        for i in range(self.layout_clinical_criteria.count()):
            row_widget = self.layout_clinical_criteria.itemAt(i).widget()
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
                self.model_clinical.model.ludwig.input_features[name] = type_value
            else:
                self.model_clinical.model.ludwig.target[name] = type_value

    def _read_updated_investigational(self):
        """Read the updated investigational drug configuration from the UI."""
        if not hasattr(self.model_clinical, 'model') or not self.model_clinical.model or self.model_clinical.model.df is None:
            return

        columns = self.model_clinical.model.df.columns.tolist()
        scroll_widget = self.scrollArea_clinical_investigational.widget()
        
        drug_info = []
        
        for column in columns:
            combo = scroll_widget.findChild(QComboBox, f"investigational_combo_{column}")
            if combo:
                selection = combo.currentText()
                if selection != "ignore":
                    drug_info.append(f"{selection}: {column}")
        
        self.model_clinical.investigational_drug = "; ".join(drug_info) if drug_info else "No investigational drug information specified"

    def _read_updated_control(self):
        """Read the updated control configuration from the UI."""
        if not hasattr(self.model_clinical, 'model') or not self.model_clinical.model or self.model_clinical.model.df is None:
            return

        columns = self.model_clinical.model.df.columns.tolist()
        scroll_widget = self.scrollArea_clinical_control.widget()
        
        control_info = []
        
        for column in columns:
            combo = scroll_widget.findChild(QComboBox, f"control_combo_{column}")
            if combo:
                selection = combo.currentText()
                if selection != "ignore":
                    control_info.append(f"{selection}: {column}")
        
        self.model_clinical.control_drug = "; ".join(control_info) if control_info else "No control group information specified"

    def _read_updated_disease(self):
        """Read the updated disease configuration from the UI."""
        if not hasattr(self.model_clinical, 'model') or not self.model_clinical.model or self.model_clinical.model.df is None:
            return

        columns = self.model_clinical.model.df.columns.tolist()
        scroll_widget = self.scrollArea_clinical_disease.widget()
        
        disease_info = []
        
        for column in columns:
            combo = scroll_widget.findChild(QComboBox, f"disease_combo_{column}")
            if combo:
                selection = combo.currentText()
                if selection != "ignore":
                    disease_info.append(f"{selection}: {column}")
        
        self.model_clinical.disease = "; ".join(disease_info) if disease_info else "No disease information specified"
