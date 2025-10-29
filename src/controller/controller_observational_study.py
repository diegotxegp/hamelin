# controller/controller_observational_study.py

from PySide6.QtWidgets import QPushButton, QTabWidget, QListWidget, QLabel, QComboBox, QWidget, QHBoxLayout, QScrollArea, QTextEdit, QLineEdit, QSizePolicy, QMessageBox, QProgressDialog
from PySide6.QtCore import Qt, QThread, Signal
from datetime import datetime

from my_ludwig.ludwig_data import input_feature_types, output_feature_types, separators, missing_data_options, metrics, goals
from texts import text_manager

class AutoConfigWorker(QThread):
    """Worker thread for model auto-configuration."""
    finished = Signal()
    error = Signal(str)
    cancelled = Signal()
    
    def __init__(self, model):
        super().__init__()
        self.model = model
        self._is_cancelled = False
        
    def cancel(self):
        """Cancel the operation."""
        self._is_cancelled = True
        
    def run(self):
        """Execute autoconfig in background."""
        try:
            if self._is_cancelled:
                self.cancelled.emit()
                return
            
            self.model.autoconfig()
            
            if self._is_cancelled:
                self.cancelled.emit()
                return
            
            self.finished.emit()
        except Exception as e:
            if not self._is_cancelled:
                self.error.emit(str(e))

class TrainingWorker(QThread):
    """Worker thread for model training and visualization generation."""
    finished = Signal()
    error = Signal(str)
    cancelled = Signal()
    progress_update = Signal(str)
    
    def __init__(self, model):
        super().__init__()
        self.model = model
        self._is_cancelled = False
        
    def cancel(self):
        """Cancel the operation immediately by killing Ray processes."""
        self._is_cancelled = True
        self.requestInterruption()
        
        # Kill Ray processes immediately
        import subprocess
        import signal
        import os
        
        try:
            # First, try graceful Ray shutdown
            import ray
            if ray.is_initialized():
                ray.shutdown()
        except Exception:
            pass
        
        try:
            # Kill all Ray-related processes forcefully
            if os.name == 'posix':  # Linux/Mac
                # Find and kill raylet processes
                subprocess.run(['pkill', '-9', '-f', 'raylet'], 
                             stderr=subprocess.DEVNULL, 
                             stdout=subprocess.DEVNULL)
                # Find and kill ray processes
                subprocess.run(['pkill', '-9', '-f', 'ray::'], 
                             stderr=subprocess.DEVNULL, 
                             stdout=subprocess.DEVNULL)
                # Find and kill GCS server
                subprocess.run(['pkill', '-9', '-f', 'gcs_server'], 
                             stderr=subprocess.DEVNULL, 
                             stdout=subprocess.DEVNULL)
        except Exception:
            pass
        
    def run(self):
        """Execute training and visualizations in background."""
        try:
            if self.isInterruptionRequested() or self._is_cancelled:
                self._cleanup_ray()
                self.cancelled.emit()
                return
            
            # Step 1: Train the model
            self.progress_update.emit("Training model...")
            
            try:
                self.model.auto_train()
            except Exception as train_error:
                # If cancelled during training, treat as cancellation
                if self._is_cancelled or self.isInterruptionRequested():
                    self._cleanup_ray()
                    self.cancelled.emit()
                    return
                raise  # Re-raise if it's a real error
            
            # Check for cancellation after training
            if self.isInterruptionRequested() or self._is_cancelled:
                self._cleanup_ray()
                self.cancelled.emit()
                return
            
            # Step 2: Generate performance visualization
            self.progress_update.emit("Generating performance chart...")
            
            if self.isInterruptionRequested() or self._is_cancelled:
                self._cleanup_ray()
                self.cancelled.emit()
                return
            
            try:
                self.model.ludwig.compare_performance()
            except Exception:
                if self._is_cancelled or self.isInterruptionRequested():
                    self._cleanup_ray()
                    self.cancelled.emit()
                    return
                raise
            
            if self.isInterruptionRequested() or self._is_cancelled:
                self._cleanup_ray()
                self.cancelled.emit()
                return
            
            # Step 3: Generate confusion matrix (only for classification tasks)
            if self.model.ludwig.is_classification():
                self.progress_update.emit("Generating confusion matrix...")
                
                if self.isInterruptionRequested() or self._is_cancelled:
                    self._cleanup_ray()
                    self.cancelled.emit()
                    return
                
                try:
                    target_name = self.model.primary_variable
                    self.model.ludwig.confusion_matrix(target_name)
                except Exception:
                    if self._is_cancelled or self.isInterruptionRequested():
                        self._cleanup_ray()
                        self.cancelled.emit()
                        return
                    raise
            else:
                print("DEBUG: Skipping confusion matrix - regression task")
            
            if self.isInterruptionRequested() or self._is_cancelled:
                self._cleanup_ray()
                self.cancelled.emit()
                return
            
            self._cleanup_ray()
            self.finished.emit()
        except Exception as e:
            self._cleanup_ray()
            if not (self.isInterruptionRequested() or self._is_cancelled):
                self.error.emit(str(e))
            else:
                self.cancelled.emit()
    
    def _cleanup_ray(self):
        """Clean up Ray resources."""
        try:
            import ray
            if ray.is_initialized():
                ray.shutdown()
        except Exception:
            pass

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
        self.pushButton_observational_performance = self.ui.findChild(QPushButton, "pushButton_observational_performance")
        self.pushButton_observational_confusion_matrix = self.ui.findChild(QPushButton, "pushButton_observational_confusion_matrix")

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
        
        # Connect visualization buttons
        self.pushButton_observational_performance.clicked.connect(self._show_performance_chart)
        self.pushButton_observational_confusion_matrix.clicked.connect(self._show_confusion_matrix)

    def _setup_texts(self):
        """
        Inicializa todos los textos explicativos usando el sistema centralizado de textos.
        """
        # Configurar texto para la pestaña de variable primaria
        textEdit_variable = self.ui.findChild(QTextEdit, "textEdit_observational_variable")
        if textEdit_variable:
            textEdit_variable.setHtml(text_manager.get_html_content('observational_study', 'primary_variable'))
        
        # Configurar texto para la pestaña de criteria
        textEdit_criteria = self.ui.findChild(QTextEdit, "textEdit_observational_criteria")
        if textEdit_criteria:
            textEdit_criteria.setHtml(text_manager.get_html_content('observational_study', 'criteria'))
        
        # Configurar texto para la pestaña de settings
        textEdit_settings = self.ui.findChild(QTextEdit, "textEdit_observational_settings")
        if textEdit_settings:
            textEdit_settings.setHtml(text_manager.get_html_content('observational_study', 'settings'))

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
            
            # Store current tab before async operation
            self.config_source_tab = self.tab
            
            # Create progress dialog
            self.config_progress = QProgressDialog("Configuring model, please wait...", "Cancel", 0, 0, None)
            self.config_progress.setWindowTitle("Auto Configuration")
            self.config_progress.setWindowModality(Qt.WindowModal)
            self.config_progress.setMinimumDuration(0)
            
            # Create worker
            self.config_worker = AutoConfigWorker(self.model_observational.model)
            self.config_worker.finished.connect(self._on_config_finished)
            self.config_worker.error.connect(self._on_config_error)
            self.config_worker.cancelled.connect(self._on_config_cancelled)
            self.config_progress.canceled.connect(self.config_worker.cancel)
            
            # Start worker and show dialog
            self.config_worker.start()
            self.config_progress.exec()
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
            # Show confirmation dialog before training
            reply = QMessageBox.question(
                None,
                "Confirm Training",
                "Are you sure you want to start the model training?\n\n"
                "This process may take several minutes depending on your data size and settings.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return  # User cancelled, don't proceed
            
            # Store current tab before async operation
            self.training_source_tab = self.tab
            
            # Create progress dialog
            self.training_progress = QProgressDialog("Training model, please wait...", "Cancel", 0, 0, None)
            self.training_progress.setWindowTitle("Model Training")
            self.training_progress.setWindowModality(Qt.WindowModal)
            self.training_progress.setMinimumDuration(0)
            
            # Create worker
            self.training_worker = TrainingWorker(self.model_observational.model)
            self.training_worker.finished.connect(self._on_training_finished)
            self.training_worker.error.connect(self._on_training_error)
            self.training_worker.cancelled.connect(self._on_training_cancelled)
            self.training_worker.progress_update.connect(self._on_progress_update)
            self.training_progress.canceled.connect(self.training_worker.cancel)
            
            # Start worker and show dialog
            self.training_worker.start()
            self.training_progress.exec()
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
        # Check if autoconfig completed successfully
        if self.model_observational.model.ludwig.input_features is None or self.model_observational.model.ludwig.target is None:
            print("WARNING: Cannot update criteria tab - autoconfig not completed successfully")
            return
            
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

        # Get current values from ludwig config (after autoconfig)
        current_metric = list(self.model_observational.model.ludwig.metric.keys())[0] if self.model_observational.model.ludwig.metric else ""
        current_goal = list(self.model_observational.model.ludwig.metric.values())[0] if self.model_observational.model.ludwig.metric else ""

        for label_text, options in settings.items():
            row = QWidget()
            row_layout = QHBoxLayout(row)

            label = QLabel(label_text)
            combo = QComboBox()
            combo.addItems(options)
            
            # Set current value from config
            if label_text == "Metric" and current_metric:
                index = combo.findText(current_metric)
                if index >= 0:
                    combo.setCurrentIndex(index)
            elif label_text == "Goal" and current_goal:
                index = combo.findText(current_goal)
                if index >= 0:
                    combo.setCurrentIndex(index)

            row_layout.addWidget(label)
            row_layout.addWidget(combo)
            self.layout_observational_settings.addWidget(row)

        row = QWidget()
        row_layout = QHBoxLayout(row)

        label = QLabel("Runtime")
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Enter max runtime in seconds (Default: 7200)")
        line_edit.setMaximumWidth(700)

        row_layout.addWidget(label)
        row_layout.addWidget(line_edit)
        self.layout_observational_settings.addWidget(row)

    def _read_updated_settings(self):
        """Reads the user-modified settings from the layout."""
        
        # Map UI label text to ludwig attribute names
        label_to_attr = {
            "Separator": "separator",
            "Missing-data": "missing_data",
            "Metric": "metric",
            "Goal": "goal",
            "Time-dependable": "timedependable",
            "Runtime": "runtime"
        }

        for i in range(self.layout_observational_settings.count()):
            row_widget = self.layout_observational_settings.itemAt(i).widget()
            if not row_widget:
                continue
            row_layout = row_widget.layout()
            if not row_layout or row_layout.count() < 2:
                continue

            label = row_layout.itemAt(0).widget()
            input_widget = row_layout.itemAt(1).widget()

            label_text = label.text()
            # Use mapping to get the correct attribute name
            key = label_to_attr.get(label_text, label_text.lower())

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
                
                explanation_text = "\n=== RESULTS INTERPRETATION ===\n\n"
                
                for feature_name, metrics in eval_stats.items():
                    if isinstance(metrics, dict) and feature_name != 'combined':
                        results_text += f"\n{feature_name.upper()}:\n"
                        
                        for metric_name, value in metrics.items():
                            if isinstance(value, float):
                                results_text += f"  {metric_name}: {value:.4f}\n"
                            else:
                                results_text += f"  {metric_name}: {value}\n"
                        
                        # Add user-friendly explanations
                        explanation_text += f"📊 {feature_name.upper()} Analysis:\n"
                        
                        if 'accuracy' in metrics:
                            acc_value = metrics['accuracy']
                            correct_predictions = int(acc_value * 100)
                            explanation_text += f"• Accuracy: {acc_value:.1%}\n"
                            explanation_text += f"  → Out of 100 observations, the model correctly identifies patterns in {correct_predictions} cases.\n"
                            if acc_value >= 0.9:
                                explanation_text += "  ✓ Excellent! The analysis shows strong predictive patterns in your observational data.\n"
                                explanation_text += "  → Recommendation: Results are reliable for hypothesis generation and further research.\n"
                            elif acc_value >= 0.8:
                                explanation_text += "  ✓ Good reliability for observational conclusions.\n"
                                explanation_text += "  → Recommendation: Patterns detected can inform clinical practice with appropriate validation.\n"
                            elif acc_value >= 0.7:
                                explanation_text += "  ⚠ Moderate reliability. Some predictive patterns detected.\n"
                                explanation_text += "  → Recommendation: Consider additional data collection or confounding variables.\n"
                            else:
                                explanation_text += "  ✗ Low reliability. Weak or inconsistent patterns.\n"
                                explanation_text += "  → Recommendation: Results should be interpreted with caution. May need larger sample or better controls.\n"
                        
                        if 'roc_auc' in metrics:
                            auc_value = metrics['roc_auc']
                            explanation_text += f"• ROC AUC: {auc_value:.3f}\n"
                            explanation_text += f"  → Measures ability to distinguish between different observed outcomes or groups.\n"
                            explanation_text += f"  → Score ranges from 0.5 (random/no discrimination) to 1.0 (perfect discrimination).\n"
                            if auc_value >= 0.9:
                                explanation_text += "  ✓ Outstanding discrimination. Clear separation between study groups or outcomes.\n"
                            elif auc_value >= 0.8:
                                explanation_text += "  ✓ Good discrimination ability between observed groups.\n"
                            elif auc_value >= 0.7:
                                explanation_text += "  ⚠ Fair discrimination. Some overlap between groups exists.\n"
                            else:
                                explanation_text += "  ✗ Poor discrimination. Groups may be too similar or confounded.\n"
                        
                        if 'loss' in metrics:
                            loss_value = metrics['loss']
                            explanation_text += f"• Loss: {loss_value:.4f}\n"
                            explanation_text += f"  → Measures prediction errors. Lower values mean better pattern recognition.\n"
                            if loss_value <= 0.3:
                                explanation_text += "  ✓ Excellent pattern fit. The model captures observational patterns very well.\n"
                                explanation_text += "  → Recommendation: Strong evidence of meaningful associations in the data.\n"
                            elif loss_value <= 0.5:
                                explanation_text += "  ✓ Good pattern fit. Acceptable prediction accuracy.\n"
                                explanation_text += "  → Recommendation: Reliable patterns detected, suitable for further investigation.\n"
                            elif loss_value <= 0.7:
                                explanation_text += "  ⚠ Acceptable fit with some prediction noise.\n"
                                explanation_text += "  → Recommendation: Consider adjusting for confounders or collecting more variables.\n"
                            else:
                                explanation_text += "  ✗ Poor fit. High prediction errors suggest weak associations.\n"
                                explanation_text += "  → Recommendation: Review study design, data quality, or variable selection.\n"
                        
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
                
                # Generate visualizations automatically after training
                try:
                    import os
                    project_dir = self.model_observational.model.project_dir
                    output_dir = os.path.join(project_dir, "visualizations")
                    
                    # Generate performance chart
                    self.model_observational.model.ludwig.compare_performance(output_dir=output_dir)
                    
                    # Generate confusion matrix
                    self.model_observational.model.ludwig.confusion_matrix(output_dir=output_dir)
                    
                    full_text += "\n[VISUALIZATIONS] Performance chart and confusion matrix generated successfully.\n"
                except Exception as viz_error:
                    full_text += f"\n[WARNING] Could not generate visualizations: {str(viz_error)}\n"
                
                # Set the results in the outcome tab
                self.textEdit_observational_outcome.setText(full_text)
                
            except Exception as e:
                error_text = f"Error displaying results:\n{str(e)}\n\nPlease ensure the analysis has been completed successfully."
                self.textEdit_observational_outcome.setText(error_text)
        else:
            self.textEdit_observational_outcome.setText("No trained model available. Please complete the training process first.")

    def _open_image_file(self, image_path, title="Visualization"):
        """
        Open an image file in a Qt dialog.
        """
        from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton
        from PySide6.QtGui import QPixmap
        from PySide6.QtCore import Qt
        import os
        
        if not os.path.exists(image_path):
            QMessageBox.warning(None, "File Not Found", 
                              f"Image file not found:\n{image_path}")
            return
        
        # Show image in Qt dialog
        try:
            dialog = QDialog()
            dialog.setWindowTitle(title)
            dialog.setMinimumSize(900, 700)
            
            layout = QVBoxLayout()
            
            # Load and display image
            label = QLabel()
            pixmap = QPixmap(image_path)
            
            # Scale image to fit dialog while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(880, 650, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(scaled_pixmap)
            label.setAlignment(Qt.AlignCenter)
            
            layout.addWidget(label)
            
            # Add close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.setLayout(layout)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(None, "Error", 
                               f"Unable to display image.\nError: {str(e)}\n\nFile location:\n{image_path}")

    def _show_performance_chart(self):
        """Display the performance chart generated by Ludwig."""
        if hasattr(self.model_observational.model, 'ludwig') and hasattr(self.model_observational.model.ludwig, 'model'):
            try:
                from PySide6.QtWidgets import QMessageBox
                import os
                
                # Get the project directory and construct the path to the pre-generated chart
                project_dir = self.model_observational.model.project_dir
                output_dir = os.path.join(project_dir, "visualizations")
                
                # Get target name to construct the expected file path
                target_name = list(self.model_observational.model.ludwig.target.keys())[0] if isinstance(self.model_observational.model.ludwig.target, dict) else self.model_observational.model.ludwig.target
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

    # Signal handlers for auto-configuration
    def _on_config_finished(self):
        """Handle successful auto-configuration completion."""
        self.config_progress.close()
        self._update_tab_criteria()
        # Navigate to Inclusion/Exclusion (tab 2), NOT Settings (tab 3)
        next_tab = self.config_source_tab + 1
        self.tabWidget_observational.setTabEnabled(next_tab, True)
        self.tabWidget_observational.setCurrentIndex(next_tab)
    
    def _on_config_error(self, error_msg):
        """Handle auto-configuration error."""
        self.config_progress.close()
        QMessageBox.critical(None, "Configuration Error", 
                           f"Error during model configuration:\n{error_msg}")
    
    def _on_config_cancelled(self):
        """Handle auto-configuration cancellation."""
        self.config_progress.close()
        QMessageBox.information(None, "Cancelled", 
                              "Model configuration was cancelled.")
    
    # Signal handlers for training
    def _on_training_finished(self):
        """Handle successful training completion."""
        # Wait for worker to fully finish
        if hasattr(self, 'training_worker'):
            self.training_worker.wait()
        
        self.training_progress.close()
        self._update_tab_process()
        self._update_tab_outcome()
        # Navigate to Outcome tab
        next_tab = self.training_source_tab + 1
        self.tabWidget_observational.setTabEnabled(next_tab, True)
        self.tabWidget_observational.setCurrentIndex(next_tab)
    
    def _on_training_error(self, error_msg):
        """Handle training error."""
        # Wait for worker to fully finish
        if hasattr(self, 'training_worker'):
            self.training_worker.wait()
        
        self.training_progress.close()
        QMessageBox.critical(None, "Training Error", 
                           f"Error during model training:\n{error_msg}")
    
    def _on_training_cancelled(self):
        """Handle training cancellation."""
        # Wait for worker to finish with timeout
        if hasattr(self, 'training_worker'):
            # Try to wait for 2 seconds
            if not self.training_worker.wait(2000):  # 2000 ms = 2 seconds
                # If still running after 2 seconds, terminate forcefully
                self.training_worker.terminate()
                self.training_worker.wait()
        
        self.training_progress.close()
        QMessageBox.information(None, "Cancelled", 
                              "Model training was cancelled. The process may take a moment to fully stop.")
    
    def _on_progress_update(self, message):
        """Update progress dialog with current step."""
        self.training_progress.setLabelText(message)

    def _show_confusion_matrix(self):
        """Display the confusion matrix generated by Ludwig."""
        if hasattr(self.model_observational.model, 'ludwig') and hasattr(self.model_observational.model.ludwig, 'model'):
            try:
                from PySide6.QtWidgets import QMessageBox
                import os
                import glob
                
                # Get the project directory and construct the path to the pre-generated matrix
                project_dir = self.model_observational.model.project_dir
                output_dir = os.path.join(project_dir, "visualizations")
                
                # Get target name to search for the confusion matrix file
                target_name = list(self.model_observational.model.ludwig.target.keys())[0] if isinstance(self.model_observational.model.ludwig.target, dict) else self.model_observational.model.ludwig.target
                
                # Search for the pre-generated confusion matrix file
                pattern = os.path.join(output_dir, f"confusion_matrix__{target_name}_top*.png")
                matching_files = glob.glob(pattern)
                
                if matching_files:
                    matrix_path = matching_files[0]
                else:
                    # Fallback to standard name
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