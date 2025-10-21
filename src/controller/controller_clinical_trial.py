# controller/controller_clinical_trial.py

from PySide6.QtWidgets import QPushButton, QTabWidget, QListWidget, QLabel, QComboBox, QWidget, QHBoxLayout, QScrollArea, QTextEdit, QLineEdit, QSizePolicy, QMessageBox
from datetime import datetime
from datetime import datetime

from my_ludwig.ludwig_data import input_feature_types, output_feature_types, separators, missing_data_options, metrics, goals
from texts import text_manager

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
        
        # Settings tab
        self.pushButton_clinical_settings = self.ui.findChild(QPushButton, "pushButton_clinical_settings")
        scroll_area = self.ui.findChild(QScrollArea, "scrollArea_clinical_settings")
        self.layout_clinical_settings = None
        if scroll_area:
            container = scroll_area.widget()
            if container:
                self.layout_clinical_settings = container.layout()
        
        # Process tab
        self.textEdit_4 = self.ui.findChild(QTextEdit, "textEdit_4")
        self.pushButton_clinical_process = self.ui.findChild(QPushButton, "pushButton_clinical_process")
        
        # Outcome tab
        self.textEdit_clinical_outcome = self.ui.findChild(QTextEdit, "textEdit_clinical_outcome")
        self.pushButton_clinical_performance = self.ui.findChild(QPushButton, "pushButton_clinical_performance")
        self.pushButton_clinical_confusion_matrix = self.ui.findChild(QPushButton, "pushButton_clinical_confusion_matrix")

        self._setup_signals()
        self._set_tabs_disabled()
        self._setup_texts()
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
        if self.pushButton_clinical_settings:
            self.pushButton_clinical_settings.clicked.connect(self._ok)
        self.pushButton_clinical_process.clicked.connect(self._ok)
        
        # Connect visualization buttons
        self.pushButton_clinical_performance.clicked.connect(self._show_performance_chart)
        self.pushButton_clinical_confusion_matrix.clicked.connect(self._show_confusion_matrix)

    def _setup_texts(self):
        """
        Inicializa todos los textos explicativos usando el sistema centralizado de textos.
        """
        # Buscar y configurar los QTextEdit de cada pestaña
        textEdit_variable = self.ui.findChild(QTextEdit, "textEdit_clinical_variable")
        if textEdit_variable:
            textEdit_variable.setHtml(text_manager.get_html_content('clinical_trial', 'primary_variable'))
        
        textEdit_criteria = self.ui.findChild(QTextEdit, "textEdit_clinical_criteria")
        if textEdit_criteria:
            textEdit_criteria.setHtml(text_manager.get_html_content('clinical_trial', 'criteria'))
        
        textEdit_investigational = self.ui.findChild(QTextEdit, "textEdit_clinical_investigational")
        if textEdit_investigational:
            textEdit_investigational.setHtml(text_manager.get_html_content('clinical_trial', 'investigational_drug'))
        
        textEdit_control = self.ui.findChild(QTextEdit, "textEdit_clinical_control")
        if textEdit_control:
            textEdit_control.setHtml(text_manager.get_html_content('clinical_trial', 'control_drug'))
        
        textEdit_disease = self.ui.findChild(QTextEdit, "textEdit_clinical_disease")
        if textEdit_disease:
            textEdit_disease.setHtml(text_manager.get_html_content('clinical_trial', 'disease'))
            
        textEdit_settings = self.ui.findChild(QTextEdit, "textEdit_clinical_settings")
        if textEdit_settings:
            textEdit_settings.setHtml(text_manager.get_html_content('clinical_trial', 'settings'))

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
            
            # Setup settings area
            if self.layout_clinical_settings:
                self._update_tab_settings()

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
        
        # Tab 6: Settings
        if self.tab == 6:
            self._read_updated_settings()
            self._next_tab()
            return
        
        # Tab 7: Process
        if self.tab == 7:
            self._update_process_summary()
            if self.model_clinical.is_ready_for_analysis():
                try:
                    self.model_clinical.model.auto_train() # Train the model
                    self._update_tab_outcome() # Update the outcome tab with results
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
            if self.layout_clinical_settings:
                self._update_tab_settings()
        
    def _update_tab_variable(self):
        """Shows the variables in the dataset."""
        variables = self.model_clinical.model.acceptable_stratify_variables()
        self.listWidget_clinical_variable.clear()
        for variable in variables:
            self.listWidget_clinical_variable.addItem(variable)
        
    def _set_primary_variable(self):
        """Set the primary endpoint variable."""
        selected_item = self.listWidget_clinical_variable.currentItem()
        if selected_item is None:
            QMessageBox.warning(
                None, 
                "No Variable Selected", 
                "Please select a primary endpoint variable from the list before continuing."
            )
            return False
            
        primary_variable = selected_item.text()
        self.model_clinical.primary_variable = primary_variable
        self.model_clinical.model.primary_variable = primary_variable
        return True
    
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
        # Disease information is optional - always allow progression
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
        
        # Add settings information if available
        if hasattr(self.model_clinical, 'model') and self.model_clinical.model and hasattr(self.model_clinical.model, 'ludwig'):
            ludwig = self.model_clinical.model.ludwig
            settings_info = []
            
            if hasattr(ludwig, 'separator') and ludwig.separator:
                settings_info.append(f"Separator: {ludwig.separator}")
            if hasattr(ludwig, 'missing_data') and ludwig.missing_data:
                settings_info.append(f"Missing data handling: {ludwig.missing_data}")
            if hasattr(ludwig, 'metric') and ludwig.metric:
                settings_info.append(f"Evaluation metric: {ludwig.metric}")
            if hasattr(ludwig, 'goal') and ludwig.goal:
                settings_info.append(f"Optimization goal: {ludwig.goal}")
            if hasattr(ludwig, 'runtime') and ludwig.runtime:
                settings_info.append(f"Max runtime: {ludwig.runtime} seconds")
            
            if settings_info:
                summary.append("Analysis Settings:\n" + "\n".join(settings_info))
        
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
            feature_combo.addItems(["Ignore", "Investigational drug"])
            feature_combo.setCurrentText("Ignore")  # Default to Ignore
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
            feature_combo.addItems(["Ignore", "Control drug"])
            feature_combo.setCurrentText("Ignore")  # Default to Ignore
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
            feature_combo.addItems(["Ignore", "Disease/Disorder"])
            feature_combo.setCurrentText("Ignore")  # Default to Ignore
            feature_combo.setObjectName(f"disease_combo_{column}")
            h_layout.addWidget(feature_combo)
            
            # Add horizontal layout to main layout
            widget = QWidget()
            widget.setLayout(h_layout)
            layout.addWidget(widget)

    def _update_tab_settings(self):
        """Updates the settings tab with predefined configuration options depending on primary variable type."""
        if not hasattr(self.model_clinical, 'model') or not self.model_clinical.model or self.model_clinical.model.df is None:
            return
        
        if not self.layout_clinical_settings:
            return
            
        target_type = next(iter(self.model_clinical.model.ludwig.target.values()))

        settings = {
            "Separator": [""] + separators,
            "Missing-data": [""] + missing_data_options,
            "Metric": metrics.get(target_type, []),
            "Goal":  goals,
            "Time-dependable": ["False", "True"]
        }

        while self.layout_clinical_settings.count():
            item = self.layout_clinical_settings.takeAt(0)
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
            self.layout_clinical_settings.addWidget(row)

        row = QWidget()
        row_layout = QHBoxLayout(row)

        label = QLabel("runtime")
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Enter max runtime in seconds (Default: 7200)")
        line_edit.setMaximumWidth(700)

        row_layout.addWidget(label)
        row_layout.addWidget(line_edit)
        self.layout_clinical_settings.addWidget(row)

    def _read_updated_settings(self):
        """Reads the user-modified settings from the layout."""
        if not hasattr(self, 'layout_clinical_settings'):
            return

        for i in range(self.layout_clinical_settings.count()):
            row_widget = self.layout_clinical_settings.itemAt(i).widget()
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

            setattr(self.model_clinical.model.ludwig, key, value)

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
                if selection != "Ignore" and selection != "":
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
                if selection != "Ignore" and selection != "":
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
                if selection != "Ignore" and selection != "":
                    disease_info.append(f"{selection}: {column}")
        
        self.model_clinical.disease = "; ".join(disease_info) if disease_info else "No disease information specified"

    def _update_tab_outcome(self):
        """Updates the outcome tab with training results."""
        if hasattr(self.model_clinical.model, 'ludwig') and hasattr(self.model_clinical.model.ludwig, 'model'):
            try:
                # Get evaluation metrics from the trained model
                eval_stats, predictions, output_directory = self.model_clinical.model.ludwig.model.evaluate(dataset=self.model_clinical.model.ludwig.df)
                
                # Format the results for display (excluding 'combined')
                results_text = "=== CLINICAL TRIAL ANALYSIS RESULTS ===\n\n"
                results_text += f"Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                results_text += f"Dataset: {self.model_clinical.model.dataset_name}\n"
                results_text += f"Primary Endpoint: {self.model_clinical.model.primary_variable}\n"
                
                # Add clinical trial specific information
                if self.model_clinical.investigational_drug:
                    results_text += f"Experimental Treatment: {self.model_clinical.investigational_drug}\n"
                if self.model_clinical.control_drug:
                    results_text += f"Control Group: {self.model_clinical.control_drug}\n"
                if self.model_clinical.disease:
                    results_text += f"Target Condition: {self.model_clinical.disease}\n"
                
                results_text += "\n"
                
                # Display evaluation metrics (skip 'combined')
                results_text += "EVALUATION METRICS:\n"
                results_text += "-" * 40 + "\n"
                
                explanation_text = "\n=== CLINICAL RESULTS EXPLANATION ===\n\n"
                
                for feature_name, metrics in eval_stats.items():
                    if isinstance(metrics, dict) and feature_name != 'combined':
                        results_text += f"\n{feature_name.upper()}:\n"
                        
                        for metric_name, value in metrics.items():
                            if isinstance(value, float):
                                results_text += f"  {metric_name}: {value:.4f}\n"
                            else:
                                results_text += f"  {metric_name}: {value}\n"
                        
                        # Add clinical-specific explanations
                        explanation_text += f"🏥 {feature_name.upper()} Clinical Performance:\n"
                        
                        if 'accuracy' in metrics:
                            acc_value = metrics['accuracy']
                            explanation_text += f"• Accuracy: {acc_value:.1%} - This shows how often the trial analysis correctly predicts the primary endpoint.\n"
                            if acc_value >= 0.9:
                                explanation_text += "  → Excellent predictive power. Strong evidence for treatment efficacy.\n"
                            elif acc_value >= 0.8:
                                explanation_text += "  → Good predictive ability. Promising treatment results.\n"
                            elif acc_value >= 0.7:
                                explanation_text += "  → Moderate predictive ability. Further validation may be needed.\n"
                            else:
                                explanation_text += "  → Low predictive ability. Treatment effect may be limited.\n"
                        
                        if 'roc_auc' in metrics:
                            auc_value = metrics['roc_auc']
                            explanation_text += f"• ROC AUC: {auc_value:.3f} - Measures ability to distinguish between treatment responders and non-responders.\n"
                            if auc_value >= 0.9:
                                explanation_text += "  → Outstanding discrimination. Clear treatment benefit.\n"
                            elif auc_value >= 0.8:
                                explanation_text += "  → Good discrimination between treatment groups.\n"
                            elif auc_value >= 0.7:
                                explanation_text += "  → Fair discrimination. Moderate treatment effect.\n"
                            else:
                                explanation_text += "  → Poor discrimination. Treatment may not be significantly different from control.\n"
                        
                        if 'loss' in metrics:
                            loss_value = metrics['loss']
                            explanation_text += f"• Loss: {loss_value:.4f} - Lower values indicate better model fit to trial data.\n"
                            if loss_value <= 0.3:
                                explanation_text += "  → Excellent model fit. High confidence in results.\n"
                            elif loss_value <= 0.5:
                                explanation_text += "  → Good model fit. Reliable results.\n"
                            elif loss_value <= 0.7:
                                explanation_text += "  → Acceptable fit. Results should be validated.\n"
                            else:
                                explanation_text += "  → Poor fit. Consider additional data or analysis methods.\n"
                        
                        explanation_text += "\n"
                
                # Add model configuration summary
                results_text += f"\nTRIAL CONFIGURATION:\n"
                results_text += "-" * 40 + "\n"
                results_text += f"Input Features: {len(self.model_clinical.model.ludwig.input_features)}\n"
                results_text += f"Target Features: {len(self.model_clinical.model.ludwig.target)}\n"
                results_text += f"Patient Samples: {len(self.model_clinical.model.ludwig.df)}\n"
                
                # Add training time and number of models
                if hasattr(self.model_clinical.model.ludwig, 'training_time') and self.model_clinical.model.ludwig.training_time:
                    training_time = self.model_clinical.model.ludwig.training_time
                    hours = int(training_time // 3600)
                    minutes = int((training_time % 3600) // 60)
                    seconds = int(training_time % 60)
                    if hours > 0:
                        time_str = f"{hours}h {minutes}m {seconds}s"
                    elif minutes > 0:
                        time_str = f"{minutes}m {seconds}s"
                    else:
                        time_str = f"{seconds}s"
                    results_text += f"Training Time: {time_str}\n"
                
                if hasattr(self.model_clinical.model.ludwig, 'num_trials') and self.model_clinical.model.ludwig.num_trials:
                    results_text += f"Models Tested: {self.model_clinical.model.ludwig.num_trials}\n"
                
                # Combine results and explanations
                full_text = results_text + explanation_text
                
                # Add clinical recommendation
                full_text += "[CLINICAL] CLINICAL INTERPRETATION:\n"
                full_text += "-" * 40 + "\n"
                
                # Get primary metric for clinical interpretation
                primary_metrics = None
                for feature_name, metrics in eval_stats.items():
                    if isinstance(metrics, dict) and feature_name != 'combined':
                        primary_metrics = metrics
                        break
                
                if primary_metrics and 'accuracy' in primary_metrics:
                    acc = primary_metrics['accuracy']
                    if acc >= 0.85:
                        full_text += "[OK] Strong evidence of treatment efficacy. Results support clinical significance.\n"
                        full_text += "   Consider proceeding with regulatory submission or larger trials.\n"
                    elif acc >= 0.75:
                        full_text += "[WARNING] Moderate evidence of treatment benefit. Consider additional validation studies.\n"
                        full_text += "   Results show promise but may need confirmation in larger populations.\n"
                    else:
                        full_text += "[ERROR] Limited evidence of treatment benefit. Consider alternative approaches.\n"
                        full_text += "   Current data suggests treatment may not be significantly better than control.\n"
                else:
                    full_text += "[INFO] Review the metrics above to assess treatment efficacy and clinical significance.\n"
                
                # Add clinical trial summary
                if hasattr(self.model_clinical, 'get_summary'):
                    trial_summary = self.model_clinical.get_summary()
                    if trial_summary:
                        full_text += f"\n📋 TRIAL DETAILS:\n"
                        full_text += "-" * 40 + "\n"
                        for key, value in trial_summary.items():
                            full_text += f"{key}: {value}\n"
                
                full_text += "\n! Important: These results are based on computational analysis. Always consult with clinical experts and regulatory guidelines before making treatment decisions.\n"
                
                # Generate visualizations automatically after training
                try:
                    import os
                    project_dir = self.model_clinical.model.project_dir
                    output_dir = os.path.join(project_dir, "visualizations")
                    
                    # Generate performance chart
                    self.model_clinical.model.ludwig.compare_performance(output_dir=output_dir)
                    
                    # Generate confusion matrix
                    self.model_clinical.model.ludwig.confusion_matrix(output_dir=output_dir)
                    
                    full_text += "\n[VISUALIZATIONS] Performance chart and confusion matrix generated successfully.\n"
                except Exception as viz_error:
                    full_text += f"\n[WARNING] Could not generate visualizations: {str(viz_error)}\n"
                
                # Set the results in the outcome tab
                self.textEdit_clinical_outcome.setText(full_text)
                
            except Exception as e:
                error_text = f"Error displaying results:\n{str(e)}\n\nPlease ensure the trial analysis has been completed successfully."
                self.textEdit_clinical_outcome.setText(error_text)
        else:
            self.textEdit_clinical_outcome.setText("No trained model available. Please complete the training process first.")

    def _open_image_file(self, image_path, title="Visualization"):
        """
        Open an image file using multiple fallback methods.
        """
        from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton
        from PySide6.QtGui import QDesktopServices, QPixmap
        from PySide6.QtCore import QUrl, Qt
        import subprocess
        import os
        
        if not os.path.exists(image_path):
            QMessageBox.warning(None, "File Not Found", 
                              f"Image file not found:\n{image_path}")
            return
        
        # Method 1: Try QDesktopServices (default system viewer)
        try:
            if QDesktopServices.openUrl(QUrl.fromLocalFile(image_path)):
                return  # Success
        except:
            pass
        
        # Method 2: Try common Linux image viewers
        viewers = ['eog', 'feh', 'gwenview', 'gpicview', 'ristretto', 'display', 'xdg-open']
        for viewer in viewers:
            try:
                subprocess.Popen([viewer, image_path], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                return  # Success
            except FileNotFoundError:
                continue
        
        # Method 3: Show image in Qt dialog as fallback
        try:
            dialog = QDialog()
            dialog.setWindowTitle(title)
            dialog.setMinimumSize(800, 600)
            
            layout = QVBoxLayout()
            
            # Load and display image
            label = QLabel()
            pixmap = QPixmap(image_path)
            
            # Scale image to fit dialog while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(780, 550, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(scaled_pixmap)
            label.setAlignment(Qt.AlignCenter)
            
            layout.addWidget(label)
            
            # Add close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.setLayout(layout)
            dialog.exec()
            return  # Success
        except Exception as e:
            QMessageBox.critical(None, "Error", 
                               f"Unable to display image.\nError: {str(e)}\n\nFile location:\n{image_path}")

    def _show_performance_chart(self):
        """Display the performance chart generated by Ludwig."""
        if hasattr(self.model_clinical.model, 'ludwig') and hasattr(self.model_clinical.model.ludwig, 'model'):
            try:
                from PySide6.QtWidgets import QMessageBox
                import os
                
                # Get the project directory and target name
                project_dir = self.model_clinical.model.project_dir
                output_dir = os.path.join(project_dir, "visualizations")
                
                # Get target name from model config
                target = self.model_clinical.model.ludwig.model.config["output_features"]
                target_name = list(target[0].keys())[0] if isinstance(target, list) else list(target.keys())[0]
                
                # Construct path to pre-generated performance chart
                chart_path = os.path.join(output_dir, f"compare_performance_{target_name}.png")
                
                # Open the pre-generated image
                self._open_image_file(chart_path, "Performance Chart")
                
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(None, "Error", 
                                   f"Error opening performance chart:\n{str(e)}")
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(None, "No Model", 
                              "No trained model available. Please complete the training process first.")

    def _show_confusion_matrix(self):
        """Display the confusion matrix generated by Ludwig."""
        if hasattr(self.model_clinical.model, 'ludwig') and hasattr(self.model_clinical.model.ludwig, 'model'):
            try:
                from PySide6.QtWidgets import QMessageBox
                import os
                import glob
                
                # Get the project directory and target name
                project_dir = self.model_clinical.model.project_dir
                output_dir = os.path.join(project_dir, "visualizations")
                
                # Get target name from model config
                target = self.model_clinical.model.ludwig.model.config["output_features"]
                target_name = list(target[0].keys())[0] if isinstance(target, list) else list(target.keys())[0]
                
                # Find pre-generated confusion matrix using glob pattern
                pattern = os.path.join(output_dir, f"confusion_matrix__{target_name}_top*.png")
                matching_files = glob.glob(pattern)
                
                if matching_files:
                    matrix_path = matching_files[0]  # Use the first match
                else:
                    # Fallback to direct path
                    matrix_path = os.path.join(output_dir, f"confusion_matrix_{target_name}.png")
                
                # Open the pre-generated image
                self._open_image_file(matrix_path, "Confusion Matrix")
                
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(None, "Error", 
                                   f"Error opening confusion matrix:\n{str(e)}")
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(None, "No Model", 
                              "No trained model available. Please complete the training process first.")
