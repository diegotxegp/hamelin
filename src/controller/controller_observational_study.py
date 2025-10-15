# controller/controller_observational_study.py

from PySide6.QtWidgets import QPushButton, QTabWidget, QListWidget, QLabel, QComboBox, QWidget, QHBoxLayout, QScrollArea, QTextEdit, QLineEdit, QSizePolicy, QMessageBox
from datetime import datetime

from my_ludwig.ludwig_data import input_feature_types, output_feature_types, separators, missing_data_options, metrics, goals
from texts import text_manager

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
        self.textEdit_observational_outcome = self.ui.findChild(QTextEdit, "textEdit_observational_outcome")

        scroll_area = self.ui.findChild(QScrollArea, "scrollArea_observational_criteria")
        container = scroll_area.widget()
        self.layout_observational_criteria = container.layout()
        
        scroll_area = self.ui.findChild(QScrollArea, "scrollArea_observational_settings")
        container = scroll_area.widget()
        self.layout_observational_settings = container.layout()

        self._setup_signals()
        self._set_tabs_disabled()
        self._setup_texts()

        self.tabWidget_observational.setCurrentIndex(1)

    def _setup_signals(self):
        """ Connect UI elements (buttons, etc.) to their respective slots. """
        self.pushButton_observational_start.clicked.connect(self._back_to_start)
        self.pushButton_observational_variable.clicked.connect(self._ok)
        self.pushButton_observational_criteria.clicked.connect(self._ok)
        self.pushButton_observational_settings.clicked.connect(self._ok)
        self.pushButton_observational_process.clicked.connect(self._ok)

    def _setup_texts(self):
        """
        Inicializa todos los textos explicativos usando el sistema centralizado de textos.
        """
        # Configurar texto para la pestaña de variable primaria
        textEdit_variable = self.ui.findChild(QTextEdit, "textEdit_observational_variable")
        if textEdit_variable:
            textEdit_variable.setHtml(text_manager.get_html_content('observational_study', 'primary_variable'))

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
            if not self._set_primary_variable():
                return  # Don't proceed if validation failed
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
            self._update_tab_process() # Update the process tab
            self._update_tab_outcome() # Update the outcome tab with results
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
        current_item = self.listWidget_observational_variable.currentItem()
        if current_item is None:
            QMessageBox.warning(
                None, 
                "No Variable Selected", 
                "Please select a primary variable from the list before continuing."
            )
            return False
        
        selected_primary_variable = current_item.text()
        self.model_observational.model.primary_variable = selected_primary_variable
        return True

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

    def _update_tab_outcome(self):
        """Updates the outcome tab with training results."""
        if hasattr(self.model_observational.model, 'ludwig') and hasattr(self.model_observational.model.ludwig, 'model'):
            try:
                # Get evaluation metrics from the trained model
                eval_stats, predictions, output_directory = self.model_observational.model.ludwig.model.evaluate(dataset=self.model_observational.model.ludwig.df)
                
                # Format the results for display (excluding 'combined')
                results_text = "=== OBSERVATIONAL STUDY RESULTS ===\n\n"
                results_text += f"Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                results_text += f"Dataset: {self.model_observational.model.dataset_name}\n"
                results_text += f"Primary Variable: {self.model_observational.model.primary_variable}\n\n"
                
                # Display evaluation metrics (skip 'combined')
                results_text += "EVALUATION METRICS:\n"
                results_text += "-" * 40 + "\n"
                
                explanation_text = "\n=== RESULTS EXPLANATION FOR NON-EXPERTS ===\n\n"
                
                for feature_name, metrics in eval_stats.items():
                    if isinstance(metrics, dict) and feature_name != 'combined':
                        results_text += f"\n{feature_name.upper()}:\n"
                        
                        for metric_name, value in metrics.items():
                            if isinstance(value, float):
                                results_text += f"  {metric_name}: {value:.4f}\n"
                            else:
                                results_text += f"  {metric_name}: {value}\n"
                        
                        # Add user-friendly explanations
                        explanation_text += f"[RESULTS] {feature_name.upper()} Analysis:\n"
                        
                        if 'accuracy' in metrics:
                            acc_value = metrics['accuracy']
                            explanation_text += f"- Accuracy: {acc_value:.1%} - This shows how often our analysis correctly identifies patterns.\n"
                            if acc_value >= 0.9:
                                explanation_text += "  → Excellent! The analysis is very reliable for this outcome.\n"
                            elif acc_value >= 0.8:
                                explanation_text += "  → Good reliability for observational conclusions.\n"
                            elif acc_value >= 0.7:
                                explanation_text += "  → Moderate reliability. Consider additional data collection.\n"
                            else:
                                explanation_text += "  → Low reliability. Results should be interpreted with caution.\n"
                        
                        if 'roc_auc' in metrics:
                            auc_value = metrics['roc_auc']
                            explanation_text += f"• ROC AUC: {auc_value:.3f} - Measures how well we can distinguish between different study outcomes.\n"
                            if auc_value >= 0.9:
                                explanation_text += "  → Outstanding discrimination between groups.\n"
                            elif auc_value >= 0.8:
                                explanation_text += "  → Good ability to distinguish between study groups.\n"
                            elif auc_value >= 0.7:
                                explanation_text += "  → Fair discrimination ability.\n"
                            else:
                                explanation_text += "  → Poor discrimination. Groups may be too similar to distinguish.\n"
                        
                        if 'loss' in metrics:
                            loss_value = metrics['loss']
                            explanation_text += f"• Loss: {loss_value:.4f} - Lower values indicate better pattern recognition.\n"
                            if loss_value <= 0.3:
                                explanation_text += "  → Excellent pattern recognition in the data.\n"
                            elif loss_value <= 0.5:
                                explanation_text += "  → Good pattern recognition.\n"
                            elif loss_value <= 0.7:
                                explanation_text += "  → Acceptable pattern recognition.\n"
                            else:
                                explanation_text += "  → Poor pattern recognition. May need more data or different approach.\n"
                        
                        explanation_text += "\n"
                
                # Add model configuration summary
                results_text += f"\nSTUDY CONFIGURATION:\n"
                results_text += "-" * 40 + "\n"
                results_text += f"Input Features: {len(self.model_observational.model.ludwig.input_features)}\n"
                results_text += f"Target Features: {len(self.model_observational.model.ludwig.target)}\n"
                results_text += f"Study Samples: {len(self.model_observational.model.ludwig.df)}\n"
                
                # Add training time and number of models
                if hasattr(self.model_observational.model.ludwig, 'training_time') and self.model_observational.model.ludwig.training_time:
                    training_time = self.model_observational.model.ludwig.training_time
                    hours = int(training_time // 3600)
                    minutes = int((training_time % 3600) // 60)
                    seconds = int(training_time % 60)
                    if hours > 0:
                        time_str = f"{hours}h {minutes}m {seconds}s"
                    elif minutes > 0:
                        time_str = f"{minutes}m {seconds}s"
                    else:
                        time_str = f"{seconds}s"
                    results_text += f"Analysis Time: {time_str}\n"
                
                if hasattr(self.model_observational.model.ludwig, 'num_trials') and self.model_observational.model.ludwig.num_trials:
                    results_text += f"Models Tested: {self.model_observational.model.ludwig.num_trials}\n"
                
                # Combine results and explanations
                full_text = results_text + explanation_text
                
                # Add study interpretation
                full_text += "🔬 STUDY INTERPRETATION:\n"
                full_text += "-" * 40 + "\n"
                
                # Get primary metric for interpretation
                primary_metrics = None
                for feature_name, metrics in eval_stats.items():
                    if isinstance(metrics, dict) and feature_name != 'combined':
                        primary_metrics = metrics
                        break
                
                if primary_metrics and 'accuracy' in primary_metrics:
                    acc = primary_metrics['accuracy']
                    if acc >= 0.85:
                        full_text += "[OK] Strong evidence found in the observational data. Results can inform decision-making.\n"
                    elif acc >= 0.75:
                        full_text += "[WARNING] Moderate evidence found. Consider collecting additional data for confirmation.\n"
                    else:
                        full_text += "[ERROR] Weak evidence in current data. Results should be interpreted cautiously.\n"
                else:
                    full_text += "[INFO] Review the metrics above to interpret the strength of observational findings.\n"
                
                full_text += "\n* Note: Observational studies show associations, not causation. Consider controlled studies for causal conclusions.\n"
                
                # Set the results in the outcome tab
                self.textEdit_observational_outcome.setText(full_text)
                
            except Exception as e:
                error_text = f"Error displaying results:\n{str(e)}\n\nPlease ensure the model has been trained successfully."
                self.textEdit_observational_outcome.setText(error_text)
        else:
            self.textEdit_observational_outcome.setText("No trained model available. Please complete the training process first.")