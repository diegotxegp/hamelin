# controller/controller_start.py

from PySide6.QtWidgets import QPushButton, QComboBox, QTabWidget, QInputDialog, QListWidget, QTextEdit, QFileDialog, QMessageBox
import pandas as pd

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
        self.selected_option = None # Variable to store the selected option from Options tab

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
            self._next_tab() # Switches to the next tab (Options)
            return

        # Tab 1: Options
        if self.tab == 1:
            current_option = self.comboBox_start_options.currentText()
            if not current_option or current_option == "":
                QMessageBox.warning(
                    None,
                    "No Study Type Selected",
                    "Please select a study type from the dropdown menu before continuing."
                )
                return
            
            self._save_option() # Saves the selected option
            self._update_tab_project() # Updates the project tab
            self._next_tab() # Switches to the next tab
            return

        # Tab 2: Project
        if self.tab == 2:
            current_project = self.listWidget_start_project.currentItem()
            if current_project is None:
                QMessageBox.warning(
                    None,
                    "No Project Selected",
                    "Please select a project from the list or create a new one before continuing."
                )
                return
                
            if current_project.text() == "[New project]":
                self._new_project()
            else:
                self._set_project() # Selects the project
                self._update_tab_data() # Updates the data tab
                self._next_tab() # Switches to the next tab
                return

        # Tab 3: Data
        if self.tab == 3:
            current_data = self.listWidget_start_data.currentItem()
            if current_data is None:
                QMessageBox.warning(
                    None,
                    "No Dataset Selected",
                    "Please select a dataset from the list or upload a new one before continuing."
                )
                return
                
            if current_data.text() == "[New dataset]":
                self._load_dataset()
            else:
                self._set_dataset() # Selects the dataset
                self._update_tab_status() # Updates the status tab
                self._next_tab() # Switches to the next tab
                return

        # Tab 4: Status (now the last tab)
        if self.tab == 4:
            # Optional confirmation before proceeding to analysis
            reply = QMessageBox.question(
                None,
                "Ready to Begin Analysis",
                f"You are about to start a {self.comboBox_start_options.currentText()} analysis.\n\n"
                f"Project: {self.model_start.model.project_name if hasattr(self.model_start.model, 'project_name') else 'Unknown'}\n"
                f"Dataset: {self.model_start.model.dataset_name if hasattr(self.model_start.model, 'dataset_name') else 'Unknown'}\n\n"
                "Are you ready to proceed?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.No:
                return
                
            self._set_status() # Selects the status
            self._select_option() # Now executes the final option selection
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
        if ok and name.strip():  # Check for empty/whitespace names
            np = self.model_start.new_project(name.strip())
            if np == None:
                QMessageBox.warning(
                    None,
                    "Project Name Exists",
                    "This project name already exists. Please choose a different name."
                )
            else:
                self._update_tab_project()
                # Automatically select the new project
                for i in range(self.listWidget_start_project.count()):
                    if self.listWidget_start_project.item(i).text() == name.strip():
                        self.listWidget_start_project.setCurrentRow(i)
                        break
        elif ok and not name.strip():
            QMessageBox.warning(
                None,
                "Invalid Project Name",
                "Project name cannot be empty. Please enter a valid name."
            )

    def _set_project(self):
        """
        Reads the selected project from the list widget.
        """
        current_item = self.listWidget_start_project.currentItem()
        if current_item is None:
            return False
        
        selected_project = current_item.text()
        self.model_start.set_project(selected_project)
        return True

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
            try:
                self.model_start.load_dataset(origin_path)
                self._update_tab_data()
            except Exception as e:
                QMessageBox.critical(
                    None,
                    "Error Loading Dataset",
                    f"Failed to load the selected CSV file.\n\nError: {str(e)}\n\nPlease ensure the file is a valid CSV format."
                )
        else:
            QMessageBox.information(
                None,
                "No File Selected",
                "Please select a CSV file to upload or choose an existing dataset from the list."
            )

    def _set_dataset(self):
        """
        Reads the selected dataset from the list widget.
        """
        current_item = self.listWidget_start_data.currentItem()
        if current_item is None:
            return False
        
        selected_dataset = current_item.text()
        self.model_start.set_dataset(selected_dataset)
        return True

    def _update_tab_status(self):
        self.textEdit_start_status_text.clear()

        # Generate automatic dataset characteristics
        if hasattr(self.model_start.model, 'df') and self.model_start.model.df is not None:
            df = self.model_start.model.df
            
            # Generate comprehensive dataset statistics
            status_info = []
            status_info.append("=== DATASET CHARACTERISTICS ===\n")
            
            # Basic information
            status_info.append(f"* Dataset Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
            status_info.append(f"* Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            status_info.append(f"* Dataset Name: {self.model_start.model.dataset_name if self.model_start.model.dataset_name else 'Unknown'}")
            
            # Data types analysis
            status_info.append("\n+ DATA TYPES:")
            dtype_counts = df.dtypes.value_counts()
            for dtype, count in dtype_counts.items():
                status_info.append(f"  - {dtype}: {count} columns")
            
            # Missing data analysis
            missing_data = df.isnull().sum()
            total_missing = missing_data.sum()
            if total_missing > 0:
                status_info.append(f"\n! MISSING DATA: {total_missing:,} total missing values")
                missing_cols = missing_data[missing_data > 0]
                for col, missing_count in missing_cols.head(5).items():
                    percentage = (missing_count / len(df)) * 100
                    status_info.append(f"  - {col}: {missing_count:,} ({percentage:.1f}%)")
                if len(missing_cols) > 5:
                    status_info.append(f"  - ... and {len(missing_cols) - 5} more columns with missing data")
            else:
                status_info.append("\n+ MISSING DATA: No missing values detected")
            
            # Numeric columns statistics
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) > 0:
                status_info.append(f"\n+ NUMERIC COLUMNS ({len(numeric_cols)}):")
                for col in numeric_cols[:5]:  # Show first 5
                    min_val = df[col].min()
                    max_val = df[col].max()
                    mean_val = df[col].mean()
                    status_info.append(f"  - {col}: Range [{min_val:.2f} - {max_val:.2f}], Mean: {mean_val:.2f}")
                if len(numeric_cols) > 5:
                    status_info.append(f"  - ... and {len(numeric_cols) - 5} more numeric columns")
            
            # Categorical columns analysis
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            if len(categorical_cols) > 0:
                status_info.append(f"\n+ CATEGORICAL COLUMNS ({len(categorical_cols)}):")
                for col in categorical_cols[:5]:  # Show first 5
                    unique_count = df[col].nunique()
                    most_common = df[col].value_counts().iloc[0] if len(df[col].value_counts()) > 0 else 0
                    status_info.append(f"  - {col}: {unique_count} unique values, Most frequent: {most_common} occurrences")
                if len(categorical_cols) > 5:
                    status_info.append(f"  - ... and {len(categorical_cols) - 5} more categorical columns")
            
            # Potential target variables (same logic as acceptable_stratify_variables)
            status_info.append("\n+ POTENTIAL TARGET VARIABLES:")
            potential_targets = []
            for col in df.columns:
                # Only consider categorical variables (same as acceptable_stratify_variables)
                if pd.api.types.is_categorical_dtype(df[col]) or df[col].dtype == object:
                    counts = df[col].value_counts(dropna=True)
                    if len(counts) <= 10 and (counts >= 5).all():  # max_categories=10, min_samples=5
                        potential_targets.append((col, len(counts)))
            
            if potential_targets:
                for col, unique_count in sorted(potential_targets, key=lambda x: x[1])[:3]:
                    status_info.append(f"  - {col}: {unique_count} unique values")
            else:
                status_info.append("  - No suitable categorical target variables found")
            
            # Data quality assessment
            status_info.append("\n+ DATA QUALITY ASSESSMENT:")
            if total_missing == 0:
                status_info.append("  - + Complete dataset (no missing values)")
            elif total_missing / (df.shape[0] * df.shape[1]) < 0.05:
                status_info.append("  - + Good quality (< 5% missing data)")
            else:
                status_info.append("  - ! Needs attention (>= 5% missing data)")
            
            if len(df) >= 1000:
                status_info.append("  - + Sufficient sample size for analysis")
            else:
                status_info.append("  - ! Small sample size - results may be less reliable")
            
            self.textEdit_start_status_text.setPlainText("\n".join(status_info))
        else:
            # Fallback to original behavior if no dataset loaded
            self.model_start.read_status_from_file()
            if self.model_start.model.status is not None:
                self.textEdit_start_status_text.setPlainText(self.model_start.model.status)
            else:
                self.textEdit_start_status_text.setPlainText("No dataset loaded yet. Please select a dataset from the Data tab to see automatic characteristics.")

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

    def _save_option(self):
        """
        Saves the selected option from the combo box for later use.
        """
        self.selected_option = self.comboBox_start_options.currentText()

    def _select_option(self):
        """
        Uses the previously saved option to tell the main controller to switch pages.
        """
        pages = {
            "Start": 0,
            "Patient registry": 1,
            "Observational study": 2,
            "Clinical trial": 3,
        }
        option = self.selected_option if self.selected_option else self.comboBox_start_options.currentText()
        index = pages.get(option, 0)
        self.controller.change_page(index)
