# controller/controller_start.py

from PySide6.QtWidgets import QPushButton, QComboBox, QTabWidget, QInputDialog, QListWidget, QTextEdit, QFileDialog, QMessageBox, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import pandas as pd
import os

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
        
        # Tab: Welcome - Get the textEdit widget
        self.textEdit_start_welcome = self.ui.findChild(QTextEdit, "textEdit_start_welcome")
        
        self._setup_signals()
        self._set_tabs_disabled()
        self._add_logo_to_welcome()

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

    def _add_logo_to_welcome(self):
        """
        Adds the Hamelin logo to the Welcome tab.
        """
        # Get the path to the logo
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        logo_path = os.path.join(project_root, "assets", "Hamelin icono.png")
        
        if not os.path.exists(logo_path):
            print(f"Warning: Logo not found at {logo_path}")
            return
        
        # Create the HTML content with the logo
        html_content = f"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /><style type="text/css">
p, li {{ white-space: pre-wrap; }}
hr {{ height: 1px; border-width: 0; }}
li.unchecked::marker {{ content: "\\2610"; }}
li.checked::marker {{ content: "\\2612"; }}
</style></head><body style=" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;">
<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
<img src="{logo_path}" width="150" height="150" /></p>
<p align="center" style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:14pt; font-weight:600;">Welcome to Hamelin!</span></p>
<p align="center" style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:11pt;">Hamelin is a user-friendly tool designed for clinical research professionals who want to create predictive models using artificial intelligence.</span></p>
<p align="center" style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>
<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:11pt;">With this application, you can analyze medical data and obtain predictions to help with clinical decision-making, without needing advanced programming knowledge.</span></p></body></html>"""
        
        # Set the HTML content to the QTextEdit
        self.textEdit_start_welcome.setHtml(html_content)


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
                    self.controller.window,
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
                    self.controller.window,
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
                    self.controller.window,
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
                self.controller.window,
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
                    self.controller.window,
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
                self.controller.window,
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
        origin_path, _ = QFileDialog.getOpenFileName(self.controller.window, "Open CSV File", "", "CSV Files (*.csv)")
        if origin_path:
            try:
                self.model_start.load_dataset(origin_path)
                self._update_tab_data()
            except Exception as e:
                QMessageBox.critical(
                    self.controller.window,
                    "Error Loading Dataset",
                    f"Failed to load the selected CSV file.\n\nError: {str(e)}\n\nPlease ensure the file is a valid CSV format."
                )
        else:
            QMessageBox.information(
                self.controller.window,
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
            
            # Generate comprehensive dataset statistics in plain language
            status_info = []
            status_info.append("=== DATASET SUMMARY ===\n")
            
            # Basic information
            status_info.append(f"[*] Size: {df.shape[0]:,} patients/records with {df.shape[1]} characteristics")
            status_info.append(f"[*] File size: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            if self.model_start.model.dataset_name:
                status_info.append(f"[*] Name: {self.model_start.model.dataset_name}")
            
            # Data types analysis - simplified for non-experts
            status_info.append("\n--- TYPES OF INFORMATION ---")
            numeric_count = len(df.select_dtypes(include=['int64', 'float64']).columns)
            categorical_count = len(df.select_dtypes(include=['object', 'category']).columns)
            
            if numeric_count > 0:
                status_info.append(f"  > {numeric_count} numerical variables (measurements, counts, values)")
            if categorical_count > 0:
                status_info.append(f"  > {categorical_count} categorical variables (categories, labels, groups)")
            
            # Missing data analysis
            missing_data = df.isnull().sum()
            total_missing = missing_data.sum()
            total_cells = df.shape[0] * df.shape[1]
            missing_percentage = (total_missing / total_cells) * 100
            
            status_info.append("\n--- DATA COMPLETENESS ---")
            if total_missing > 0:
                status_info.append(f"  [!] {total_missing:,} missing values found ({missing_percentage:.1f}% of all data)")
                missing_cols = missing_data[missing_data > 0]
                status_info.append(f"  > {len(missing_cols)} variables have incomplete information")
                
                # Show columns with most missing data
                top_missing = missing_cols.nlargest(3)
                if len(top_missing) > 0:
                    status_info.append("\n  Most affected variables:")
                    for col, missing_count in top_missing.items():
                        percentage = (missing_count / len(df)) * 100
                        status_info.append(f"    - {col}: {percentage:.1f}% missing")
            else:
                status_info.append("  [OK] Complete dataset - no missing values")
            
            # Numeric columns statistics - simplified
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) > 0:
                status_info.append(f"\n--- NUMERICAL VARIABLES ({len(numeric_cols)} total) ---")
                status_info.append("  Examples of measured values:")
                for col in numeric_cols[:3]:  # Show first 3
                    min_val = df[col].min()
                    max_val = df[col].max()
                    mean_val = df[col].mean()
                    status_info.append(f"    > {col}")
                    status_info.append(f"      Range: {min_val:.2f} to {max_val:.2f} (average: {mean_val:.2f})")
                if len(numeric_cols) > 3:
                    status_info.append(f"    ... and {len(numeric_cols) - 3} more")
            
            # Categorical columns analysis - simplified
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            if len(categorical_cols) > 0:
                status_info.append(f"\n--- CATEGORICAL VARIABLES ({len(categorical_cols)} total) ---")
                status_info.append("  Examples of categories:")
                for col in categorical_cols[:3]:  # Show first 3
                    unique_count = df[col].nunique()
                    status_info.append(f"    > {col}: {unique_count} different categories")
                    # Show most common category
                    if len(df[col].value_counts()) > 0:
                        top_category = df[col].value_counts().index[0]
                        top_count = df[col].value_counts().iloc[0]
                        top_percent = (top_count / len(df)) * 100
                        status_info.append(f"      Most common: '{top_category}' ({top_percent:.1f}%)")
                if len(categorical_cols) > 3:
                    status_info.append(f"    ... and {len(categorical_cols) - 3} more")
            
            # Potential target variables
            status_info.append("\n--- SUITABLE OUTCOME VARIABLES ---")
            status_info.append("  (Variables that could be predicted)")
            potential_categorical = []
            potential_numerical = []
            potential_boolean = []
            
            total_rows = len(df)
            
            for col in df.columns:
                # Categorical variables for classification
                if pd.api.types.is_categorical_dtype(df[col]) or df[col].dtype == object:
                    counts = df[col].value_counts(dropna=True)
                    if len(counts) <= 10 and (counts >= 5).all():  # max_categories=10, min_samples=5
                        potential_categorical.append((col, len(counts)))
                
                # Numerical variables
                elif df[col].dtype in ['int64', 'float64']:
                    unique_count = df[col].nunique(dropna=True)
                    
                    # Check if variable has real decimal values (not just .0)
                    has_decimals = False
                    if df[col].dtype == 'float64':
                        has_decimals = (df[col].dropna() % 1 != 0).any()
                    
                    # Continuous variable: has real decimals OR >50% values are unique
                    if has_decimals or unique_count > total_rows * 0.5:
                        potential_numerical.append(col)
                    # Discrete numerical (treated as categorical): check min 2 samples per value
                    else:
                        counts = df[col].value_counts(dropna=True)
                        min_count = counts.min()
                        if min_count >= 2 and unique_count <= 10:
                            potential_categorical.append((col, unique_count))
                
                # Boolean variables for binary classification
                elif df[col].dtype == 'bool':
                    counts = df[col].value_counts(dropna=True)
                    if len(counts) == 2 and (counts >= 2).all():  # Both True and False with at least 2 samples
                        potential_boolean.append(col)
            
            if potential_categorical:
                status_info.append("  Classification (categorical outcomes):")
                for col, unique_count in sorted(potential_categorical, key=lambda x: x[1])[:3]:
                    status_info.append(f"    > {col} ({unique_count} categories)")
                if len(potential_categorical) > 3:
                    status_info.append(f"    ... and {len(potential_categorical) - 3} more")
            
            if potential_boolean:
                status_info.append("  Binary classification (boolean outcomes):")
                for col in potential_boolean[:3]:
                    status_info.append(f"    > {col} (True/False)")
                if len(potential_boolean) > 3:
                    status_info.append(f"    ... and {len(potential_boolean) - 3} more")
            
            if potential_numerical:
                status_info.append("  Regression (continuous numerical outcomes):")
                for col in potential_numerical[:3]:
                    min_val = df[col].min()
                    max_val = df[col].max()
                    status_info.append(f"    > {col} (range: {min_val:.2f} to {max_val:.2f})")
                if len(potential_numerical) > 3:
                    status_info.append(f"    ... and {len(potential_numerical) - 3} more")
            
            if not potential_categorical and not potential_numerical and not potential_boolean:
                status_info.append("    [!] No suitable outcome variables found")
                status_info.append("    Requirements:")
                status_info.append("      - Categorical: 2-10 categories, each with ≥5 examples")
                status_info.append("      - Numerical (continuous): >50% unique values or real decimals")
                status_info.append("      - Numerical (discrete): ≤10 unique values, each with ≥2 examples")
                status_info.append("      - Boolean: Both True and False with ≥2 examples")
            
            # Data quality assessment
            status_info.append("\n--- OVERALL DATA QUALITY ---")
            quality_score = 0
            
            # Check missing data
            if total_missing == 0:
                status_info.append("  [OK] Excellent: Complete dataset with no missing values")
                quality_score += 1
            elif missing_percentage < 5:
                status_info.append("  [OK] Good: Very few missing values (< 5%)")
                quality_score += 1
            elif missing_percentage < 15:
                status_info.append("  [!] Fair: Some missing data (5-15%) - may need attention")
            else:
                status_info.append("  [X] Poor: Significant missing data (> 15%) - preprocessing recommended")
            
            # Check sample size
            if len(df) >= 1000:
                status_info.append("  [OK] Good: Large sample size - reliable results expected")
                quality_score += 1
            elif len(df) >= 100:
                status_info.append("  [!] Fair: Moderate sample size - results may vary")
            else:
                status_info.append("  [X] Small: Limited data - results may be unreliable")
            
            # Check variable balance
            if len(numeric_cols) > 0 and len(categorical_cols) > 0:
                status_info.append("  [OK] Good: Balanced mix of numerical and categorical data")
                quality_score += 1
            
            # Overall recommendation
            status_info.append("\n--- RECOMMENDATION ---")
            if quality_score >= 3:
                status_info.append("  [OK] Dataset is ready for analysis!")
            elif quality_score >= 2:
                status_info.append("  [!] Dataset can be used but may benefit from preprocessing")
            else:
                status_info.append("  [X] Consider data cleaning before analysis")
            
            self.textEdit_start_status_text.setPlainText("\n".join(status_info))
        else:
            # Fallback to original behavior if no dataset loaded
            self.model_start.read_status_from_file()
            if self.model_start.model.status is not None:
                self.textEdit_start_status_text.setPlainText(self.model_start.model.status)
            else:
                self.textEdit_start_status_text.setPlainText("[*] No dataset loaded yet.\n\nPlease select a dataset from the Data tab to see its characteristics and quality assessment.")

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
