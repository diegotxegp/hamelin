# controller/controller_registro.py

from PySide6.QtWidgets import QPushButton, QTabWidget, QListWidget, QLabel, QComboBox, QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QTextEdit, QLineEdit, QSizePolicy, QMessageBox, QProgressDialog, QFrame
from PySide6.QtCore import Qt, QThread, Signal
from datetime import datetime

from my_ludwig.ludwig_data import input_feature_types, output_feature_types, separators, missing_data_options, metrics, goals
from texts import text_manager

class AutoconfigWorker(QThread):
    """Worker thread for autoconfig."""
    finished = Signal()
    error = Signal(str)
    cancelled = Signal()
    
    def __init__(self, model, parent_window=None):
        super().__init__()
        self.model = model
        self.parent_window = parent_window
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
    
    def __init__(self, model, parent_window=None):
        super().__init__()
        self.model = model
        self.parent_window = parent_window
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
        self.pushButton_registry_settings = self.ui.findChild(QPushButton, "pushButton_registry_settings")
        self.textEdit_registry_process_summary = self.ui.findChild(QTextEdit, "textEdit_registry_process_summary")
        self.pushButton_registry_process = self.ui.findChild(QPushButton, "pushButton_registry_process")
        self.textEdit_registry_outcome = self.ui.findChild(QTextEdit, "textEdit_registry_outcome")
        self.pushButton_registry_performance = self.ui.findChild(QPushButton, "pushButton_registry_performance")
        self.pushButton_registry_confusion_matrix = self.ui.findChild(QPushButton, "pushButton_registry_confusion_matrix")

        scroll_area = self.ui.findChild(QScrollArea, "scrollArea_registry_criteria")
        container = scroll_area.widget()
        self.layout_registry_criteria = container.layout()
        
        scroll_area = self.ui.findChild(QScrollArea, "scrollArea_registry_settings")
        container = scroll_area.widget()
        self.layout_registry_settings = container.layout()


        self._setup_signals()
        self._set_tabs_disabled()
        self._setup_texts()

    def _setup_signals(self):
        """ Connect UI elements (buttons, etc.) to their respective slots. """

        self.pushButton_registry_start.clicked.connect(self._back_to_start)
        self.pushButton_registry_variable.clicked.connect(self._ok)
        self.pushButton_registry_criteria.clicked.connect(self._ok)
        self.pushButton_registry_settings.clicked.connect(self._ok)
        self.pushButton_registry_process.clicked.connect(self._ok)
        
        # Connect visualization buttons
        self.pushButton_registry_performance.clicked.connect(self._show_performance_chart)
        self.pushButton_registry_confusion_matrix.clicked.connect(self._show_confusion_matrix)

    def _setup_texts(self):
        """
        Inicializa todos los textos explicativos usando el sistema centralizado de textos.
        """
        # Configurar texto para la pestaña de variable primaria
        textEdit_variable = self.ui.findChild(QTextEdit, "textEdit_registry_variable")
        if textEdit_variable:
            textEdit_variable.setHtml(text_manager.get_html_content('patient_registry', 'primary_variable'))
        
        # Configurar texto para la pestaña de criteria
        textEdit_criteria = self.ui.findChild(QTextEdit, "textEdit_registry_criteria")
        if textEdit_criteria:
            textEdit_criteria.setHtml(text_manager.get_html_content('patient_registry', 'criteria'))
        
        # Configurar texto para la pestaña de settings
        textEdit_settings = self.ui.findChild(QTextEdit, "textEdit_registry_settings")
        if textEdit_settings:
            textEdit_settings.setHtml(text_manager.get_html_content('patient_registry', 'settings'))

    def _set_tabs_disabled(self):
        """ Disables all tabs except the first two."""
        tabs = self.tabWidget_registry.count()

        for i in range(2, tabs):
            self.tabWidget_registry.setTabEnabled(i, False)

    def _back_to_start(self):
        self.controller.change_page(0)

    def _next_tab(self):
        """ Increments the tab index and enables the next tab."""
        self.tab = self.tabWidget_registry.currentIndex() + 1
        self.tabWidget_registry.setTabEnabled(self.tab, True)
        self.tabWidget_registry.setCurrentIndex(self.tab)

    def _ok(self):
        self.tab = self.tabWidget_registry.currentIndex()
        
        # Tab 1: Primary variable
        if self.tab == 1:
            if not self._set_primary_variable():
                return  # Don't proceed if validation failed
            
            # Store current tab before async operation
            self.config_source_tab = self.tab
            
            # Create progress dialog
            self.config_progress = QProgressDialog("Configuring model, please wait...", "Cancel", 0, 0, self.controller.window)
            self.config_progress.setWindowTitle("Auto Configuration")
            self.config_progress.setWindowModality(Qt.WindowModal)
            self.config_progress.setMinimumDuration(0)
            
            # Create worker
            self.config_worker = AutoconfigWorker(self.model_registry.model, self.controller.window)
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
            # Apply criteria and validate
            if not self._read_updated_criteria():
                return  # Stay on criteria tab if validation failed
            
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
                self.controller.window,
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
            self.training_progress = QProgressDialog("Training model, please wait...", "Cancel", 0, 0, self.controller.window)
            self.training_progress.setWindowTitle("Model Training")
            self.training_progress.setWindowModality(Qt.WindowModal)
            self.training_progress.setMinimumDuration(0)
            
            # Create worker
            self.training_worker = TrainingWorker(self.model_registry.model, self.controller.window)
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
        variables = self.model_registry.model.acceptable_stratify_variables()
        self.listWidget_registry_variable.clear()
        for variable in variables:
            self.listWidget_registry_variable.addItem(variable)

    def _set_primary_variable(self):
        """ Reads the selected project from the list widget. """
        current_item = self.listWidget_registry_variable.currentItem()
        if current_item is None:
            QMessageBox.warning(
                self.controller.window, 
                "No Variable Selected", 
                "Please select a primary variable from the list before continuing."
            )
            return False
        
        selected_primary_variable = current_item.text()
        self.model_registry.model.primary_variable = selected_primary_variable
        return True

    def _update_tab_criteria(self):
        """
        Updates the criteria tab with variable type selection and instance filtering.
        Combines original functionality with [IS2] Select subpopulations and [IS3] Remove specific instances.
        """
        # Get criteria from Ludwig
        criteria = self.model_registry.model.ludwig.input_features | self.model_registry.model.ludwig.target
        io = ["", "input", "output"]
        
        # Clear the layout
        while self.layout_registry_criteria.count():
            item = self.layout_registry_criteria.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # SECTION 1: Variable Type Selection (Original Functionality)
        # Add rows for each variable to select input/output types
        for name, type_value in criteria.items():
            row = QWidget()
            row_layout = QHBoxLayout(row)

            label_criterium = QLabel(name)
            combo_io = QComboBox()
            combo_type = QComboBox()
            ift = [""] + input_feature_types  # Empty string for the first item
            
            if name != self.model_registry.model.primary_variable:
                combo_io.addItems(io)
                combo_io.setCurrentText("input")
                combo_type.addItems(ift)
            else:
                combo_io.addItems(io)
                combo_io.setCurrentText("output")
                combo_type.addItems(output_feature_types)
                
            combo_type.setCurrentText(type_value)

            row_layout.addWidget(label_criterium)
            row_layout.addWidget(combo_io)
            row_layout.addWidget(combo_type)
            self.layout_registry_criteria.addWidget(row)
        
        # SECTION 2: Instance Filtering (New Functionality - [IS2] and [IS3])
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.layout_registry_criteria.addWidget(separator)
        
        # Add header with instructions
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        
        instructions = QLabel(
            "<b>Instance Selection Criteria (Optional)</b><br>"
            "<i>Inclusion rules:</i> Select specific subpopulations (patients meeting certain conditions)<br>"
            "<i>Exclusion rules:</i> Remove specific instances (outliers, invalid data, etc.)"
        )
        instructions.setWordWrap(True)
        header_layout.addWidget(instructions)
        
        # Add buttons to add new rules
        button_row = QWidget()
        button_layout = QHBoxLayout(button_row)
        
        btn_add_inclusion = QPushButton("➕ Add Inclusion Rule")
        btn_add_inclusion.clicked.connect(lambda: self._add_criteria_rule('inclusion'))
        button_layout.addWidget(btn_add_inclusion)
        
        btn_add_exclusion = QPushButton("➖ Add Exclusion Rule")
        btn_add_exclusion.clicked.connect(lambda: self._add_criteria_rule('exclusion'))
        button_layout.addWidget(btn_add_exclusion)
        
        btn_clear_all = QPushButton("🗑️ Clear All")
        btn_clear_all.clicked.connect(self._clear_all_criteria)
        button_layout.addWidget(btn_clear_all)
        
        button_layout.addStretch()
        header_layout.addWidget(button_row)
        
        self.layout_registry_criteria.addWidget(header_widget)
        
        # Display existing filtering rules
        self._display_criteria_rules()
        
        # Add summary at the bottom
        self._update_criteria_summary()
    
    def _add_criteria_rule(self, rule_type='inclusion'):
        """Add a new criteria rule row to the interface."""
        if self.model_registry.model.df is None:
            QMessageBox.warning(
                self.controller.window,
                "No Dataset",
                "Please load a dataset first before defining criteria."
            )
            return
        
        rule_widget = QWidget()
        rule_layout = QHBoxLayout(rule_widget)
        rule_layout.setContentsMargins(5, 2, 5, 2)
        
        # Rule type indicator
        rule_type_label = QLabel("✓ Include:" if rule_type == 'inclusion' else "✗ Exclude:")
        rule_type_label.setMinimumWidth(70)
        rule_type_label.setStyleSheet("font-weight: bold; color: green;" if rule_type == 'inclusion' else "font-weight: bold; color: red;")
        rule_layout.addWidget(rule_type_label)
        
        # Variable selection
        combo_variable = QComboBox()
        combo_variable.addItems([''] + list(self.model_registry.model.df.columns))
        combo_variable.setMinimumWidth(150)
        rule_layout.addWidget(combo_variable)
        
        # Operator selection
        combo_operator = QComboBox()
        combo_operator.addItems(['equals', 'not equals', 'greater than', 'less than', 
                                  'greater or equal', 'less or equal', 'between', 'contains', 'not contains'])
        combo_operator.setMinimumWidth(120)
        rule_layout.addWidget(combo_operator)
        
        # Value input
        line_value = QLineEdit()
        line_value.setPlaceholderText("value (for 'between' use: min,max)")
        line_value.setMinimumWidth(150)
        rule_layout.addWidget(line_value)
        
        # Remove button
        btn_remove = QPushButton("✕")
        btn_remove.setMaximumWidth(30)
        btn_remove.setToolTip("Remove this rule")
        btn_remove.clicked.connect(lambda: self._remove_criteria_rule(rule_widget))
        rule_layout.addWidget(btn_remove)
        
        rule_layout.addStretch()
        
        # Store rule type as widget property
        rule_widget.setProperty('rule_type', rule_type)
        
        # Add to layout (QGridLayout adds to next available row)
        self.layout_registry_criteria.addWidget(rule_widget)
    
    def _remove_criteria_rule(self, rule_widget):
        """Remove a criteria rule from the interface."""
        self.layout_registry_criteria.removeWidget(rule_widget)
        rule_widget.deleteLater()
        self._update_criteria_summary()
    
    def _clear_all_criteria(self):
        """Remove all criteria rules."""
        reply = QMessageBox.question(
            self.controller.window,
            "Clear All Criteria",
            "Are you sure you want to remove all inclusion/exclusion criteria?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.model_registry.model.criteria_manager.clear_rules()
            self._update_tab_criteria()
    
    def _display_criteria_rules(self):
        """Display existing rules from the criteria manager."""
        for i, rule in enumerate(self.model_registry.model.criteria_manager.rules):
            self._add_criteria_rule(rule.rule_type)
            
            # Find the last added rule widget
            rule_widget = self.layout_registry_criteria.itemAt(self.layout_registry_criteria.count() - 3).widget()
            rule_layout = rule_widget.layout()
            
            # Set the values
            combo_variable = rule_layout.itemAt(1).widget()
            combo_operator = rule_layout.itemAt(2).widget()
            line_value = rule_layout.itemAt(3).widget()
            
            combo_variable.setCurrentText(rule.variable)
            combo_operator.setCurrentText(rule.operator)
            line_value.setText(str(rule.value))
    
    def _update_criteria_summary(self):
        """Update the summary label showing filtering statistics."""
        # Remove existing summary if present
        for i in range(self.layout_registry_criteria.count()):
            item = self.layout_registry_criteria.itemAt(i)
            if item and item.widget() and item.widget().property('is_summary'):
                item.widget().deleteLater()
                break
        
        summary_widget = QWidget()
        summary_widget.setProperty('is_summary', True)
        summary_layout = QVBoxLayout(summary_widget)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        summary_layout.addWidget(separator)
        
        summary_label = QLabel()
        summary_label.setWordWrap(True)
        
        if self.model_registry.model.df is not None:
            rules_count = sum(1 for i in range(self.layout_registry_criteria.count())
                             if self.layout_registry_criteria.itemAt(i).widget() and
                             self.layout_registry_criteria.itemAt(i).widget().property('rule_type'))
            
            text = f"<b>Current Status:</b><br>"
            text += f"Original dataset: {len(self.model_registry.model.df):,} rows<br>"
            text += f"Rules defined: {rules_count}<br>"
            
            if self.model_registry.model.filtered_df is not None:
                filtered_count = len(self.model_registry.model.filtered_df)
                removed = len(self.model_registry.model.df) - filtered_count
                percentage = (removed / len(self.model_registry.model.df) * 100) if len(self.model_registry.model.df) > 0 else 0
                text += f"<span style='color: blue;'>Filtered dataset: {filtered_count:,} rows</span><br>"
                text += f"<span style='color: red;'>Removed: {removed:,} rows ({percentage:.1f}%)</span>"
            else:
                text += "<i>Click 'Continue' to apply criteria</i>"
            
            summary_label.setText(text)
        else:
            summary_label.setText("<i>No dataset loaded</i>")
        
        summary_layout.addWidget(summary_label)
        self.layout_registry_criteria.addWidget(summary_widget)

    def _read_updated_criteria(self):
        """
        Reads both variable types and instance filtering criteria.
        Returns True if all validations pass, False otherwise.
        """
        # SECTION 1: Read variable type selections (input/output)
        for i in range(self.layout_registry_criteria.count()):
            row_widget = self.layout_registry_criteria.itemAt(i).widget()
            if not row_widget:
                continue
            
            # Check if this is a variable type row (has exactly 3 widgets: label, combo_io, combo_type)
            row_layout = row_widget.layout()
            if not row_layout or row_layout.count() != 3:
                continue
            
            # Check if first widget is a QLabel (variable name)
            first_widget = row_layout.itemAt(0).widget()
            if not isinstance(first_widget, QLabel):
                continue
            
            # This is a variable type row
            label = first_widget
            combo_io = row_layout.itemAt(1).widget()
            combo_type = row_layout.itemAt(2).widget()
            
            if not isinstance(combo_io, QComboBox) or not isinstance(combo_type, QComboBox):
                continue
            
            name = label.text()
            io_value = combo_io.currentText()
            type_value = combo_type.currentText()

            # Update Ludwig features
            if io_value == "input":
                self.model_registry.model.ludwig.input_features[name] = type_value
            else:
                self.model_registry.model.ludwig.target[name] = type_value
        
        # SECTION 2: Read instance filtering rules ([IS2] and [IS3])
        # Clear existing filtering rules
        self.model_registry.model.criteria_manager.rules.clear()
        
        # Read filtering rules from the interface
        incomplete_rules = []
        for i in range(self.layout_registry_criteria.count()):
            item = self.layout_registry_criteria.itemAt(i)
            if not item or not item.widget():
                continue
            
            rule_widget = item.widget()
            rule_type = rule_widget.property('rule_type')
            
            if rule_type not in ['inclusion', 'exclusion']:
                continue  # Not a filtering rule widget
            
            rule_layout = rule_widget.layout()
            if not rule_layout or rule_layout.count() < 4:
                continue
            
            # Extract rule components (skip first widget which is the label)
            combo_variable = rule_layout.itemAt(1).widget()
            combo_operator = rule_layout.itemAt(2).widget()
            line_value = rule_layout.itemAt(3).widget()
            
            if not isinstance(combo_variable, QComboBox) or not isinstance(combo_operator, QComboBox) or not isinstance(line_value, QLineEdit):
                continue
            
            variable = combo_variable.currentText()
            operator = combo_operator.currentText()
            value_text = line_value.text().strip()
            
            # Validate rule completeness
            if not value_text:
                incomplete_rules.append(f"{rule_type.title()}: {variable} {operator} [empty value]")
                continue
            
            # Try to convert value to appropriate type
            try:
                # Special handling for 'between' operator
                if operator == 'between':
                    # Parse value as "min,max" or "min-max"
                    if ',' in value_text:
                        parts = value_text.split(',')
                    elif '-' in value_text and value_text.count('-') == 1:
                        parts = value_text.split('-')
                    else:
                        incomplete_rules.append(f"{rule_type.title()}: {variable} between [invalid format, use: min,max]")
                        continue
                    
                    if len(parts) != 2:
                        incomplete_rules.append(f"{rule_type.title()}: {variable} between [invalid format, use: min,max]")
                        continue
                    
                    try:
                        min_val = float(parts[0].strip())
                        max_val = float(parts[1].strip())
                        value = (min_val, max_val)
                    except ValueError:
                        incomplete_rules.append(f"{rule_type.title()}: {variable} between [values must be numeric]")
                        continue
                else:
                    # Check if the column is numeric
                    if variable in self.model_registry.model.df.columns:
                        col_dtype = self.model_registry.model.df[variable].dtype
                        if col_dtype in ['int64', 'float64']:
                            value = float(value_text)
                        else:
                            value = value_text
                    else:
                        value = value_text
            except ValueError:
                value = value_text
            
            # Add rule to criteria manager
            self.model_registry.model.criteria_manager.add_rule(
                variable=variable,
                operator=operator,
                value=value,
                rule_type=rule_type
            )
        
        # Check for incomplete rules
        if incomplete_rules:
            QMessageBox.warning(
                self.controller.window,
                "Incomplete Rules",
                f"The following rules have empty values and will be ignored:\n\n" + "\n".join(incomplete_rules),
                QMessageBox.Ok
            )
        
        # Apply filtering criteria if there are any rules
        if len(self.model_registry.model.criteria_manager.rules) > 0:
            try:
                stats = self.model_registry.model.apply_criteria()
                
                # Show statistics dialog
                QMessageBox.information(
                    self.controller.window,
                    "Criteria Applied",
                    f"Instance selection criteria applied successfully:\n\n"
                    f"Original dataset: {stats['original_count']} instances\n"
                    f"Filtered dataset: {stats['filtered_count']} instances\n"
                    f"Removed: {stats['removed_count']} instances ({stats['removed_percent']:.1f}%)\n\n"
                    f"The filtered dataset will be used for training.",
                    QMessageBox.Ok
                )
                
                # Validate minimum sample size
                if stats['filtered_count'] < 10:
                    QMessageBox.warning(
                        self.controller.window,
                        "Low Sample Size",
                        f"Warning: Only {stats['filtered_count']} instances remain after filtering.\n\n"
                        f"This may not be sufficient for reliable model training.\n"
                        f"Consider relaxing your criteria.",
                        QMessageBox.Ok
                    )
                
            except Exception as e:
                QMessageBox.critical(
                    self.controller.window,
                    "Error Applying Criteria",
                    f"An error occurred while applying the selection criteria:\n\n{str(e)}",
                    QMessageBox.Ok
                )
                return False
        else:
            # No filtering rules defined - use full dataset
            self.model_registry.model.filtered_df = None
        
        return True

    def _update_tab_settings(self):
        """Updates the settings tab with predefined configuration options depending on primary variable type."""
        target_type = next(iter(self.model_registry.model.ludwig.target.values()))

        settings = {
            "Separator": [""] + separators,
            "Missing-data": [""] + missing_data_options,
            "Metric": metrics.get(target_type, []),
            "Goal":  goals,
            "Time-dependable": ["False", "True"]
        }

        while self.layout_registry_settings.count():
            item = self.layout_registry_settings.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get current values from ludwig config (after autoconfig)
        current_metric = list(self.model_registry.model.ludwig.metric.keys())[0] if self.model_registry.model.ludwig.metric else ""
        current_goal = list(self.model_registry.model.ludwig.metric.values())[0] if self.model_registry.model.ludwig.metric else ""

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
            self.layout_registry_settings.addWidget(row)

        row = QWidget()
        row_layout = QHBoxLayout(row)

        label = QLabel("Runtime")
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Enter max runtime in seconds (Default: 7200)")
        line_edit.setMaximumWidth(700)

        row_layout.addWidget(label)
        row_layout.addWidget(line_edit)
        self.layout_registry_settings.addWidget(row)

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

        for i in range(self.layout_registry_settings.count()):
            row_widget = self.layout_registry_settings.itemAt(i).widget()
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

            setattr(self.model_registry.model.ludwig, key, value)

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
        
        self.textEdit_registry_process_summary.setText(summary_text)

    def _update_tab_outcome(self):
        """Updates the outcome tab with training results."""
        if hasattr(self.model_registry.model, 'ludwig') and hasattr(self.model_registry.model.ludwig, 'model'):
            try:
                # Get evaluation metrics from the trained model
                eval_stats, predictions, output_directory = self.model_registry.model.ludwig.model.evaluate(dataset=self.model_registry.model.ludwig.df)
                
                # Format the results for display (excluding 'combined')
                results_text = "=== MODEL TRAINING RESULTS ===\n\n"
                results_text += f"Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                results_text += f"Dataset: {self.model_registry.model.dataset_name}\n"
                results_text += f"Primary Variable: {self.model_registry.model.primary_variable}\n\n"
                
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
                        explanation_text += f"📊 {feature_name.upper()} Performance:\n"
                        
                        if 'accuracy' in metrics:
                            acc_value = metrics['accuracy']
                            correct_predictions = int(acc_value * 100)
                            explanation_text += f"• Accuracy: {acc_value:.1%}\n"
                            explanation_text += f"  → Out of 100 predictions, the model gets {correct_predictions} right.\n"
                            if acc_value >= 0.9:
                                explanation_text += "  ✓ Excellent! The model is very reliable for clinical decision support.\n"
                                explanation_text += "  → Recommendation: Can be used with confidence, but always validate with new data.\n"
                            elif acc_value >= 0.8:
                                explanation_text += "  ✓ Good performance for most practical applications.\n"
                                explanation_text += "  → Recommendation: Suitable for clinical use with expert supervision.\n"
                            elif acc_value >= 0.7:
                                explanation_text += "  ⚠ Moderate performance. The model shows some predictive ability.\n"
                                explanation_text += "  → Recommendation: Use as support tool only. Review data quality and consider adding more relevant variables.\n"
                            else:
                                explanation_text += "  ✗ Low performance. The model struggles with predictions.\n"
                                explanation_text += "  → Recommendation: DO NOT use for clinical decisions. Collect more data or review feature selection.\n"
                        
                        if 'roc_auc' in metrics:
                            auc_value = metrics['roc_auc']
                            explanation_text += f"• ROC AUC: {auc_value:.3f}\n"
                            explanation_text += f"  → Measures the model's ability to distinguish between different patient outcomes.\n"
                            explanation_text += f"  → Score ranges from 0.5 (random/no discrimination) to 1.0 (perfect discrimination).\n"
                            if auc_value >= 0.9:
                                explanation_text += "  ✓ Outstanding discrimination ability. The model clearly separates different outcome groups.\n"
                            elif auc_value >= 0.8:
                                explanation_text += "  ✓ Good discrimination. The model reliably distinguishes between outcomes.\n"
                            elif auc_value >= 0.7:
                                explanation_text += "  ⚠ Fair discrimination. The model shows some ability to separate outcomes.\n"
                            else:
                                explanation_text += "  ✗ Poor discrimination. The model barely performs better than random guessing.\n"
                        
                        if 'loss' in metrics:
                            loss_value = metrics['loss']
                            explanation_text += f"• Loss: {loss_value:.4f}\n"
                            explanation_text += f"  → Measures prediction errors. Lower values mean better model fit.\n"
                            if loss_value <= 0.3:
                                explanation_text += "  ✓ Excellent model fit. Predictions are very close to actual outcomes.\n"
                                explanation_text += "  → Recommendation: Model is well-calibrated for this dataset.\n"
                            elif loss_value <= 0.5:
                                explanation_text += "  ✓ Good model fit. Acceptable prediction accuracy.\n"
                                explanation_text += "  → Recommendation: Model performs well, minor improvements possible.\n"
                            elif loss_value <= 0.7:
                                explanation_text += "  ⚠ Acceptable fit, but predictions show noticeable errors.\n"
                                explanation_text += "  → Recommendation: Consider model tuning or adding more informative features.\n"
                            else:
                                explanation_text += "  ✗ Poor fit. Large prediction errors detected.\n"
                                explanation_text += "  → Recommendation: Review data quality, outliers, or try different modeling approach.\n"
                        
                        explanation_text += "\n"
                
                # Add model configuration summary
                results_text += f"\nMODEL CONFIGURATION:\n"
                results_text += "-" * 40 + "\n"
                results_text += f"Input Features: {len(self.model_registry.model.ludwig.input_features)}\n"
                results_text += f"Target Features: {len(self.model_registry.model.ludwig.target)}\n"
                results_text += f"Training Samples: {len(self.model_registry.model.ludwig.df)}\n"
                
                # Add training time and number of models
                if hasattr(self.model_registry.model.ludwig, 'training_time') and self.model_registry.model.ludwig.training_time:
                    training_time = self.model_registry.model.ludwig.training_time
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
                
                if hasattr(self.model_registry.model.ludwig, 'num_trials') and self.model_registry.model.ludwig.num_trials:
                    results_text += f"Models Tested: {self.model_registry.model.ludwig.num_trials}\n"
                
                # Combine results and explanations
                full_text = results_text + explanation_text
                
                # Add overall recommendation
                full_text += "[RECOMMENDATION]:\n"
                full_text += "-" * 40 + "\n"
                
                # Get primary metric for recommendation
                primary_metrics = None
                for feature_name, metrics in eval_stats.items():
                    if isinstance(metrics, dict) and feature_name != 'combined':
                        primary_metrics = metrics
                        break
                
                if primary_metrics and 'accuracy' in primary_metrics:
                    acc = primary_metrics['accuracy']
                    if acc >= 0.85:
                        full_text += "[OK] This model shows strong performance and can be used with confidence.\n"
                    elif acc >= 0.75:
                        full_text += "[WARNING] This model shows decent performance but consider validating with new data.\n"
                    else:
                        full_text += "[ERROR] This model shows poor performance. Consider collecting more data or reviewing features.\n"
                else:
                    full_text += "[INFO] Review the metrics above to assess model performance.\n"
                
                # Generate visualizations automatically after training
                try:
                    import os
                    project_dir = self.model_registry.model.project_dir
                    output_dir = os.path.join(project_dir, "visualizations")
                    
                    # Generate performance chart
                    self.model_registry.model.ludwig.compare_performance(output_dir=output_dir)
                    
                    # Generate confusion matrix
                    self.model_registry.model.ludwig.confusion_matrix(output_dir=output_dir)
                    
                    full_text += "\n[VISUALIZATIONS] Performance chart and confusion matrix generated successfully.\n"
                except Exception as viz_error:
                    full_text += f"\n[WARNING] Could not generate visualizations: {str(viz_error)}\n"
                
                # Set the results in the outcome tab
                self.textEdit_registry_outcome.setText(full_text)
                
            except Exception as e:
                error_text = f"Error displaying results:\n{str(e)}\n\nPlease ensure the model has been trained successfully."
                self.textEdit_registry_outcome.setText(error_text)
        else:
            self.textEdit_registry_outcome.setText("No trained model available. Please complete the training process first.")

    def _open_image_file(self, image_path, title="Visualization"):
        """
        Open an image file in a Qt dialog.
        """
        from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton
        from PySide6.QtGui import QPixmap
        from PySide6.QtCore import Qt
        import os
        
        if not os.path.exists(image_path):
            QMessageBox.warning(self.controller.window, "File Not Found", 
                              f"Image file not found:\n{image_path}")
            return
        
        # Show image in Qt dialog
        try:
            dialog = QDialog(self.controller.window)
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
            QMessageBox.critical(self.controller.window, "Error", 
                               f"Unable to display image.\nError: {str(e)}\n\nFile location:\n{image_path}")

    def _show_performance_chart(self):
        """Display the performance chart generated by Ludwig."""
        if hasattr(self.model_registry.model, 'ludwig') and hasattr(self.model_registry.model.ludwig, 'model'):
            try:
                from PySide6.QtWidgets import QMessageBox
                import os
                
                # Get the project directory and construct the path to the pre-generated chart
                project_dir = self.model_registry.model.project_dir
                output_dir = os.path.join(project_dir, "visualizations")
                
                # Get target name to construct the expected file path
                target_name = list(self.model_registry.model.ludwig.target.keys())[0] if isinstance(self.model_registry.model.ludwig.target, dict) else self.model_registry.model.ludwig.target
                chart_path = os.path.join(output_dir, f"compare_performance_{target_name}.png")
                
                # Open the pre-generated image
                self._open_image_file(chart_path, "Performance Chart")
                
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self.controller.window, "Error", 
                                   f"Error generating performance chart:\n{str(e)}")
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self.controller.window, "No Model", 
                              "No trained model available. Please complete the training process first.")

    # Signal handlers for auto-configuration
    def _on_config_finished(self):
        """Handle successful auto-configuration completion."""
        self.config_progress.close()
        self._update_tab_criteria()
        # Navigate to Inclusion/Exclusion (tab 2), NOT Settings (tab 3)
        next_tab = self.config_source_tab + 1
        self.tabWidget_registry.setTabEnabled(next_tab, True)
        self.tabWidget_registry.setCurrentIndex(next_tab)
    
    def _on_config_error(self, error_msg):
        """Handle auto-configuration error."""
        self.config_progress.close()
        QMessageBox.critical(self.controller.window, "Configuration Error", 
                           f"Error during model configuration:\n{error_msg}")
    
    def _on_config_cancelled(self):
        """Handle auto-configuration cancellation."""
        self.config_progress.close()
        QMessageBox.information(self.controller.window, "Cancelled", 
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
        self.tabWidget_registry.setTabEnabled(next_tab, True)
        self.tabWidget_registry.setCurrentIndex(next_tab)
    
    def _on_training_error(self, error_msg):
        """Handle training error."""
        # Wait for worker to fully finish
        if hasattr(self, 'training_worker'):
            self.training_worker.wait()
        
        self.training_progress.close()
        QMessageBox.critical(self.controller.window, "Training Error", 
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
        QMessageBox.information(self.controller.window, "Cancelled", 
                              "Model training was cancelled. The process may take a moment to fully stop.")
    
    def _on_progress_update(self, message):
        """Update progress dialog with current step."""
        self.training_progress.setLabelText(message)

    def _show_confusion_matrix(self):
        """Display the confusion matrix generated by Ludwig."""
        if hasattr(self.model_registry.model, 'ludwig') and hasattr(self.model_registry.model.ludwig, 'model'):
            try:
                from PySide6.QtWidgets import QMessageBox
                import os
                import glob
                
                # Get the project directory and construct the path to the pre-generated matrix
                project_dir = self.model_registry.model.project_dir
                output_dir = os.path.join(project_dir, "visualizations")
                
                # Get target name to search for the confusion matrix file
                target_name = list(self.model_registry.model.ludwig.target.keys())[0] if isinstance(self.model_registry.model.ludwig.target, dict) else self.model_registry.model.ludwig.target
                
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
                QMessageBox.critical(self.controller.window, "Error", 
                                   f"Error generating confusion matrix:\n{str(e)}")
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self.controller.window, "No Model", 
                              "No trained model available. Please complete the training process first.")