"""
i18n Strings
~~~~~~~~~~~~

English (EN) and Spanish (ES) translations for HAMELIN UI.

Design:
- Plain dicts: no nesting, easy to extend
- Naming: "section.component.label" (max 3 levels)
- Fallback: missing keys return the key itself (safe for development)
"""

EN: dict[str, str] = {
    # Navigation
    "nav.home": "Home",
    "nav.project": "Projects",
    "nav.data": "Data",
    "nav.table1": "Table 1",
    "nav.forecasting": "Recruitment",
    "nav.training": "Training",
    "nav.dashboard": "Dashboard",
    "nav.models": "Models",
    "nav.help": "Manual",
    "nav.settings": "Settings",

    # Home Page
    "home.title": "HAMELIN",
    "home.subtitle": "Clinical Research AutoML Platform",
    "home.help": (
        "This is the starting screen. From here you can open an existing "
        "project or create a new one, and see a quick summary of your "
        "projects. Once a project is open, use the menu on the left to "
        "move between Data, Table 1, Training, and the other pages."
    ),
    "home.welcome.title": "Welcome to HAMELIN",
    "home.welcome.text": "Start by creating or opening a project to begin your analysis journey.",
    "home.welcome.description": (
        "HAMELIN is a comprehensive platform for clinical research automation.\n\n"
        "Features:\n"
        "• Table 1 Generation - Automated baseline characteristics tables\n"
        "• Project Metadata - Track study information and recruitment\n"
        "• Recruitment Forecasting - Predict enrollment timelines\n"
        "• AutoML Integration - Automated machine learning with Ludwig\n\n"
        "Use the navigation menu on the left to get started."
    ),
    "home.stat.projects": "Projects",
    "home.stat.datasets": "Datasets",
    "home.stat.models": "Models",
    "home.stat.forecasts": "Forecasts",

    # Metadata/Projects Page
    "metadata.title": "Projects",
    "metadata.subtitle": "Open an existing project or start a new one",
    "metadata.help": (
        "This page holds your project's basic information: study name, "
        "principal investigator, target number of patients, and "
        "recruitment dates. Filling it in accurately is what powers the "
        "KPIs and recruitment forecast shown elsewhere in the app."
    ),
    "metadata.btn.new": "New Project",
    "metadata.btn.select": "Select",
    "metadata.btn.selected": "Selected",
    "metadata.no.projects": "No projects yet. Create one to get started.",
    "metadata.detail.title": "Project Metadata",
    "metadata.detail.subtitle": "Manage clinical study information",
    "metadata.btn.back": "← Back to Projects",
    "metadata.btn.open": "Open",
    "metadata.section.basic": "Basic Information",
    "metadata.section.ethics": "Ethics Approval",
    "metadata.section.recruitment": "Recruitment Information",
    "metadata.section.objectives": "Study Objectives",
    "metadata.label.name": "Project Name",
    "metadata.label.shortname": "Short Name",
    "metadata.label.protocol": "Protocol Number",
    "metadata.label.pi": "Principal Investigator",
    "metadata.label.email": "Contact Email",
    "metadata.label.institution": "Institution",
    "metadata.label.studytype": "Study Type",
    "metadata.label.description": "Study Description",
    "metadata.label.primaryobjective": "Primary Objective *",
    "metadata.label.secondaryobjectives": "Secondary Objectives (one per line)",
    "metadata.label.ethicscommittee": "Ethics Committee:",
    "metadata.label.ethicsapprovalnumber": "Approval Number:",
    "metadata.label.approvaldate": "Approval Date:",
    "metadata.placeholder.name": "Full project name…",
    "metadata.placeholder.shortname": "Short acronym, e.g. UPS",
    "metadata.placeholder.protocol": "Protocol number, e.g. UPS-2024-001",
    "metadata.placeholder.pi": "Principal Investigator name…",
    "metadata.placeholder.email": "contact@hospital.org",
    "metadata.placeholder.institution": "Institution or hospital name…",
    "metadata.placeholder.description": "The single main clinical question this study answers…",
    "metadata.placeholder.secondaryobjectives": "One additional objective per line, if any…",
    "metadata.placeholder.ethicscommittee": "e.g. Comité de Ética de la Investigación…",
    "metadata.placeholder.ethicsapprovalnumber": "e.g. CEIm-2024-015…",
    "metadata.btn.save": "Save Project",
    "metadata.btn.reset": "Reset",

    # Data Page
    "data.title": "Data Management",
    "data.subtitle": "Load, inspect, and manage your research data",
    "data.help": (
        "Load your dataset here (CSV, Excel, and other common formats). "
        "Hamelin automatically detects each column's type (categorical, "
        "numeric, etc.) and shows how much data is missing. You can "
        "exclude columns or rows you don't want to use, and export a "
        "quality report before moving on to analysis."
    ),
    "data.section.source": "Data Source",
    "data.section.metrics": "Data Quality Metrics",
    "data.section.inspection": "Data Inspection",
    "data.section.variables": "Variables & Types",
    "data.section.table1": "Table 1: Baseline Characteristics",
    "data.placeholder.filepath": "No file selected",
    "data.btn.browse": "Browse",
    "data.btn.load": "Load",
    "data.btn.reload": "Reload",
    "data.btn.reset.types": "Reset Types to Inferred",
    "data.btn.quality": "Generate Quality Report",
    "data.btn.remove_duplicates": "Remove Duplicates",
    "data.btn.export": "Export Cleaned Data",
    "data.btn.exclude": "Exclude Outliers",
    "data.btn.restore": "Restore Excluded",
    "data.label.formats": "Supported: CSV, TSV, Excel (.xlsx/.xls), Parquet, JSON/JSONL, Feather, HDF5, HTML, SPSS (.sav), Stata (.dta), SAS (.xpt/.sas7bdat), Fixed Width (.fwf), Pickled DataFrame (.pkl/.pickle)",
    "data.label.rows": "Rows",
    "data.label.cols": "Columns",
    "data.label.missing": "Missing %",
    "data.label.memory": "Memory",
    "data.label.excluded": "Excluded Rows",
    "data.help.formats": (
        "Load your research data from common formats supported by Ludwig.\n\n"
        "Supported formats:\n"
        "• CSV (.csv): comma- or semicolon-separated text files.\n"
        "• TSV (.tsv): tab-separated values.\n"
        "• Excel (.xlsx, .xls): Microsoft Excel workbooks (first sheet used).\n"
        "• Parquet (.parquet): columnar storage for large datasets.\n"
        "• JSON / JSONL (.json, .jsonl): structured JSON files (JSONL = one JSON object per line).\n"
        "• Feather (.feather): fast binary format for dataframes.\n"
        "• HDF5 (.h5, .hdf5): hierarchical binary format for big arrays.\n"
        "• HTML (.html, .htm): single-table HTML files (limited support).\n"
        "• SPSS (.sav): SPSS binary files (preserves labels).\n"
        "• Stata (.dta): Stata data files.\n"
        "• SAS (.xpt, .sas7bdat): SAS datasets.\n\n"
        "Tips:\n  • Ensure the first row contains column headers (variable names).\n  • One row per patient.\n  • If you see encoding errors, try saving CSV as UTF-8.\n  • Some formats require optional libraries. Install with:\n      pip install -r requirements.txt\n  • Parquet/Feather: pyarrow or fastparquet\n  • SPSS/SAS/Stata: pyreadstat or pandas built-in readers\n  • HDF5: tables (PyTables)"
    ),

    # Table 1 Page
    "table1.title": "Table 1: Descriptive Statistics",
    "table1.subtitle": "Patient characteristics and baseline variables",
    "table1.help": (
        "Generates the standard \"Table 1\" clinical papers require: a "
        "summary of your patients' characteristics, optionally split into "
        "groups (e.g. by outcome) with statistical comparisons between "
        "them. Choose which variables to include and, if you want group "
        "comparisons, which variable to group by."
    ),
    "table1.btn.generate": "Generate Table",
    "table1.btn.export": "Export",
    "table1.status.ready": "Ready to generate",
    "table1.status.generating": "Generating…",
    "table1.status.complete": "Complete",
    "table1.msg.loading": "Load a dataset first",
    "table1.msg.vars": "Select variables to include",

    # Forecasting Page
    "forecasting.title": "Recruitment Forecasting",
    "forecasting.subtitle": "Predict recruitment timeline and target achievement",
    "forecasting.help": (
        "Estimates when your study will reach its target number of "
        "patients, based on how recruitment has gone so far. Uses the "
        "recruitment events (patient enrollment dates) recorded for this "
        "project - the more history you have, the more reliable the "
        "estimate."
    ),
    "forecasting.section.status": "Current Recruitment Status",
    "forecasting.section.parameters": "Forecast Parameters",
    "forecasting.section.results": "Forecast Results",
    "forecasting.section.chart": "Recruitment Chart",
    "forecasting.section.timeline": "Projected Monthly Timeline",
    "forecasting.label.recruited": "Currently Enrolled",
    "forecasting.label.target": "Enrollment Target",
    "forecasting.label.remaining": "Remaining",
    "forecasting.label.rate": "Enrollment Rate",
    "forecasting.label.start": "Start Date",
    "forecasting.label.date.col": "Date Column",
    "forecasting.label.completion": "Predicted Completion",
    "forecasting.label.days.remaining": "Days Remaining",
    "forecasting.label.confidence": "Confidence Interval",
    "forecasting.label.r2": "R² (Model Fit)",
    "forecasting.label.on.track": "On Track",
    "forecasting.btn.generate": "Generate Forecast",
    "forecasting.btn.export.chart": "Export Chart (PNG)",
    "forecasting.btn.export.csv": "Export Timeline CSV",
    "forecasting.placeholder.date.col": "Load a dataset first…",
    "forecasting.status.not.calculated": "Not calculated",

    # Training Page
    "training.title": "Model Training",
    "training.subtitle": "Configure and train AutoML models",
    "training.help": (
        "This is where you build a predictive model. Choose the outcome "
        "you want to predict (your primary objective) and which patient "
        "data can be used to predict it, optionally narrow down which "
        "patients to include, then start training - Hamelin handles the "
        "machine learning automatically. Once done, you can see how well "
        "the model performed and export it."
    ),
    "training.section.variables": "1. Outcome Variable and Predictors",
    "training.section.criteria": "2. Patient Selection Criteria",
    "training.section.config": "3. Model Configuration",
    "training.section.control": "4. Training Control",
    "training.section.advanced": "Advanced Options",
    "training.section.hyperopt": "Advanced Configuration",
    "training.label.outcome": "Outcome Variable",
    "training.label.predictors": "Predictor variables (select one or more):",
    "training.btn.select_all_predictors": "Select all",
    "training.label.secondary_outcomes": "Secondary outcomes (optional):",
    "training.help.secondary_outcomes": "Map preset secondary outcomes or select dataset columns to mark as secondary endpoints.",
    "training.label.inclusion": "Inclusion Criteria:",
    "training.label.exclusion": "Exclusion Criteria:",
    "training.label.patients": "Patients after filtering",
    "training.label.problem": "Problem Type",
    "training.label.metric": "Optimization Metric",
    "training.label.strategy": "Search Strategy",
    "training.label.timebudget": "Time Budget (min)",
    "training.label.trials": "Max Trials",
    "training.label.imbalance": "Handle Class Imbalance",
    "training.label.meanimpute": "Missing numeric values strategy:",
    "training.label.modelname": "Model name:",
    "training.label.predictiontype": "Prediction type:",
    "training.label.evaluationmetric": "Evaluation metric:",
    "training.label.testsplit": "Final evaluation holdout:",
    "training.label.randomseed": "Random Seed:",
    "training.label.maxiterations": "Max. iterations:",
    "training.label.paralleltrials": "Parallel trials:",
    "training.label.earlystop": "Early stopping (rounds, -1 = off):",
    "training.missingstrategy.default": "Ludwig default (fill with 0)",
    "training.missingstrategy.mean": "Fill with column mean",
    "training.missingstrategy.mode": "Fill with most frequent value",
    "training.missingstrategy.ffill": "Forward fill (previous row's value)",
    "training.missingstrategy.bfill": "Backward fill (next row's value)",
    "training.missingstrategy.droprow": "Drop rows with missing value",
    "training.btn.select.all": "Select All",
    "training.btn.deselect.all": "Deselect All",
    "training.btn.show.options": "▶ Advanced options",
    "training.btn.hide.options": "▼ Advanced options",
    "training.btn.start": "Start Training",
    "training.btn.stop": "Stop",
    "training.btn.export": "Export Trained Model",
    "training.btn.import_config": "Train from Config File…",
    "training.placeholder.outcome": "e.g., Diagnosis, Treatment_response, Mortality…",
    "training.placeholder.inclusion": "e.g., Age ≥ 18, Confirmed diagnosis",
    "training.placeholder.exclusion": "e.g., Pregnancy, Active infection",
    "training.status.nodata": "Load a dataset first to enable training",
    "training.status.ready": "Ready to train",
    "training.status.training": "Training in progress…",
    "training.status.training.from_config": "Training from duplicated config…",
    "training.status.done": "Training complete",
    "training.status.error": "An error occurred during training",
    "training.status.cancelled": "Training cancelled",
    "training.status.duplicate_loaded": "Duplicated settings loaded: load its dataset in the Data tab if needed, then press Start Training",
    "training.duplicate.infobar.title": "Duplicated settings loaded",
    "training.duplicate.infobar.body": "Target and predictor variables are pre-filled from the original model.",
    "training.duplicate.banner": "The next run trains a fixed configuration from the duplicated model. The model configuration section below is ignored.",
    "training.duplicate.banner.cancel": "Use AutoML instead",

    # Dashboard Page
    "dashboard.title": "Project Dashboard",
    "dashboard.btn.refresh": "Refresh",
    "dashboard.subtitle": "Real-time project status and recruitment KPIs",
    "dashboard.help": (
        "A one-page overview of your project: how recruitment is "
        "progressing against your target, the quality of your dataset, "
        "and a history of every model you've trained. Use the shortcuts "
        "at the bottom to jump straight into Data or Training."
    ),
    "dashboard.section.kpi": "Key Performance Indicators",
    "dashboard.section.progress": "Recruitment Progress",
    "dashboard.section.chart": "Gráfica de Reclutamiento",
    "dashboard.section.history": "Model Training History",
    "dashboard.section.actions": "Quick Actions",
    "dashboard.label.quality": "Data Quality",
    "dashboard.label.variables": "Variables",
    "dashboard.label.samples": "Samples",
    "dashboard.label.enrollment": "Enrollment %",
    "dashboard.label.recruited": "Enrolled",
    "dashboard.label.target": "Target",
    "dashboard.msg.no.data": "No recruitment data available",

    # Settings Page
    "settings.title": "Settings",
    "settings.subtitle": "Configure application preferences",
    "settings.help": (
        "App-wide preferences: light/dark appearance, interface language, "
        "default export options, and (for troubleshooting) logging detail. "
        "These don't affect your data or models - just how Hamelin looks "
        "and behaves."
    ),
    "settings.section.appearance": "Appearance",
    "settings.section.language": "Language",
    "settings.section.export": "Export Preferences",
    "settings.section.advanced": "Advanced",
    "settings.section.about": "About HAMELIN",
    "settings.section.authors": "Authors",
    "settings.label.theme": "Theme",
    "settings.label.language": "Language",
    "settings.label.format": "Export Format",
    "settings.label.loglevel": "Log Level",
    "settings.label.debug": "Debug Info",
    "settings.label.version": "Version",
    "settings.label.description": "HAMELIN is a machine learning platform designed for clinical research teams.",
    "settings.label.contact": "Repository: https://github.com/diegotxegp/hamelin",
    "settings.about.license": "License: GNU General Public License v3.0 (GPLv3). This program is free software: you can redistribute it and/or modify it under the terms of the GPLv3 as published by the Free Software Foundation. It is distributed WITHOUT ANY WARRANTY, without even the implied warranty of merchantability or fitness for a particular purpose. Full text in the LICENSE file at the root of the repository, or at gnu.org/licenses/gpl-3.0.html.",
    "settings.btn.reset": "Reset to Defaults",
    "settings.btn.apply": "Apply Settings",
    "settings.msg.language.changed": "Language Changed",
    "settings.msg.language.restart": "Restart HAMELIN to apply the new language.",

    # Help/Manual Page
    "help.title": "User Manual",
    "help.subtitle": "Complete reference guide for HAMELIN",
    "help.btn.expand": "Expand All",
    "help.btn.collapse": "Collapse All",

    # Help Texts
    "help.data.formats": (
        "HAMELIN reads data from the most common file formats (see list).\n\n"
        "Supported formats:\n"
        "• CSV (.csv): text files with comma/semicolon separators.\n"
        "• TSV (.tsv): tab-separated values.\n"
        "• Excel (.xlsx, .xls): workbooks (first sheet used).\n"
        "• Parquet (.parquet): efficient columnar storage.\n"
        "• JSON / JSONL (.json, .jsonl): structured JSON files.\n"
        "• Feather (.feather): fast binary dataframe format.\n"
        "• HDF5 (.h5, .hdf5): hierarchical binary format.\n"
        "• HTML (.html): single-table HTML files (limited).\n"
        "• SPSS (.sav), Stata (.dta), SAS (.xpt/.sas7bdat): statistical package files.\n\n"
        "Make sure your file has a header row (variable names) and one row per patient. If loading fails, see the Data tab help for troubleshooting."
    ),
    "help.data.preview": "Preview all rows and columns of your loaded dataset.\n\n• Check that data loaded correctly\n• Verify column names and data types\n• Identify potential data quality issues\n• Scroll horizontally to see all variables\n\nCommon special values you may encounter:\n  NaN : Not a Number. Indicates a missing or unknown value in a\n         numeric or text column.\n  NaT : Not a Time. The date/time equivalent of NaN: the cell\n         should contain a date or time but no value was recorded.\n  None: Same meaning as NaN in most contexts.\n  inf : Infinity. A numeric result that overflowed (e.g., division\n         by zero). Treat it as a data quality issue.\n\nTip: Rows or columns with many NaN/NaT values may need to be\ncleaned or excluded before analysis.",
    "help.data.variables": "Overview of all variables (columns) in your dataset.\n\nVariable types:\n• 🔢 Numeric: Continuous or discrete numbers (age, lab values)\n• 📝 Categorical: Groups or categories (gender, diagnosis)\n• 📅 Date/Time: Temporal data (visit dates, timestamps)\n• 📄 Text: Free text fields (notes, comments)\n\nHAMELIN auto-detects types but you can change them if needed.",
    "help.data.table1": "Generate the standard \"baseline characteristics\" table used in clinical papers.\n\n• Pick a grouping variable to compare two groups (e.g. Treatment vs Control) with p-values, or leave it as 'None' for overall descriptive statistics only.\n• Smart Recommendations suggests which variables to exclude (identifiers, free text, zero-variance columns) and a likely grouping variable.\n• Export the result as CSV, Excel (.xlsx), or Word (.docx).",
    "help.metadata.basic": "Enter basic information about your clinical study. These details\nhelp document the study and are included in exported reports.",
    "help.settings.appearance": "Customize the visual appearance of HAMELIN.\n\n• Theme: Light (day mode), Dark (night mode), or Auto (follows system)\n• Font Size: Adjust text size for better readability (8-16)\n\nChanges apply immediately without restart.",
    "help.settings.language": "Choose your preferred language for the application.\n\nAvailable languages:\n• English: Interface in English\n• Español: Interface in Spanish\n\nRestart required for changes to take effect.",
    "help.settings.export": "Configure default settings for exporting results.\n\n• Default Format: CSV (simple), Excel (formatted), or Word (publication-ready)\n• Decimal Places: Number precision for statistical results (0-6)\n\nThese are defaults - you can change format when exporting.",
    "help.forecasting.params": "Configure the inputs needed to generate a forecast.\n\n• Enrollment Date Column: Column containing patient enrollment dates\n• Target Sample Size: Total patients needed to complete the study\n• Historical Period: Days of history used for velocity estimation\n• Confidence Level: Statistical confidence for the interval (0.95 = 95%)\n\nPress 'Generate Forecast' to run the analysis.",
    "help.training.variables": "Select what you want to predict and which clinical variables to use.\n\n• Outcome variable: the clinical endpoint to predict (diagnosis, treatment response, mortality…).\n• Predictor variables: patient characteristics the model will learn from (age, lab results, symptoms…). Click to select: hold Ctrl or Shift for several; there is no 'Select All' shortcut here.\n• Secondary outcomes (optional): other clinical endpoints you also want the model to predict alongside the main one: this trains a real multi-output model, it is not just kept for your own reference.",
    "help.training.criteria": "Define which patients should be INCLUDED or EXCLUDED from the analysis.\n\n• Inclusion: patients who meet eligibility criteria (e.g., Age >= 18, ConfirmedDiagnosis == True).\n• Exclusion: patients to remove (e.g., MissingData > 50%, ProtocolViolation == True).\n\nYou can also exclude cases with poor data quality identified in the dataset Quality Report.\n\nThese criteria filter the dataset before training.",
    "help.training.config": "Configure how the model should learn.\n\n• Model name: short identifier for this run: required; becomes the checkpoint folder name.\n• Prediction type: forces the model type: binary, multi-class, or regression: make sure it matches your outcome column.\n• Evaluation metric: how to measure whether the model is good (AUC is the most common in clinical settings).\n\nClick \"Advanced options\" for more control (the defaults are fine for most cases):\n• Time budget: maximum time to spend searching for the best model (in minutes).\n• Final evaluation holdout: percentage of patients reserved for the final test, never used in training. Recommended: 20%.\n• Random seed: fixes the randomness so a run can be reproduced exactly.\n• Search strategy: method for finding the best model configuration (Bayesian optimisation is most efficient; random search is faster but less precise).\n• Max. iterations: how many different configurations to try.\n• Parallel trials: use more CPU cores to speed up the search.\n• Handle class imbalance: enable when one outcome category is much rarer than the other.\n• Fill Missing Numeric Values with the Column Mean: when on, missing numeric values are imputed with the column mean instead of Ludwig's own default (which silently fills with 0).\n\nHAMELIN uses AutoML to automatically find the best model for your dataset.",
    "help.training.hyperopt": "Advanced options to automatically optimise the model.\n\n• Strategy: search method for finding the best model configuration.\n  • Bayesian optimisation: most efficient (recommended).\n  • Random search: faster but less precise.\n• Max. iterations: how many different configurations to try (more = better, more time).\n• Time budget: maximum search time (in minutes).\n• Parallel trials: use more CPU cores to speed up the search.\n\nIn most cases, the default values are sufficient. Only change this if you need maximum performance.",
    "help.training.control": "Start, monitor and control the model training process.\n\n• Start training: launches the AutoML process with your configuration.\n• Progress bar: shows progress in real time.\n• Results: performance metrics for the best model found.\n• Export model: saves the trained model for future use or deployment.\n\nTraining can take from minutes to hours depending on dataset size and configuration.",

    # Additional UI Strings
    # Data Page
    "data.btn.load.selected": "Load Selected",
    "data.btn.remove.selected": "Remove Selected",
    "data.btn.restore.all": "Restore All",
    "data.placeholder.datasets": "No datasets yet",

    # Metadata Page  
    "metadata.btn.new.project": "New Project",
    "metadata.btn.back": "← Back to Projects",
    "metadata.placeholder.name": "Full project name…",
    "metadata.placeholder.shortname": "Short acronym, e.g. UPS",
    "metadata.placeholder.protocol": "Protocol number, e.g. UPS-2024-001",
    "metadata.placeholder.pi": "Principal Investigator name…",
    "metadata.placeholder.email": "contact@hospital.org",
    "metadata.placeholder.institution": "Institution or hospital name…",
    "metadata.placeholder.description": "The single main clinical question this study answers…",
    "metadata.studytype.registry": "Patient Registry",
    "metadata.studytype.observational": "Observational Study",
    "metadata.studytype.clinical": "Clinical Trial",
    "metadata.btn.new.generic": "Quick Project",
    "metadata.btn.delete.all": "Delete All Projects",
    "metadata.msg.deleteall.title": "Delete All Projects?",
    "metadata.msg.deleteall.confirm": "This will permanently delete all {n} project(s) and everything inside them (datasets, results, models). This cannot be undone.",
    "metadata.msg.deleteall.success": "Deleted {n} project(s).",
    "metadata.msg.generic.success": "'{short_name}' created with placeholder details — open it anytime to fill in the real information.",

    # Settings Page
    "settings.theme.light": "Light",
    "settings.theme.dark": "Dark",
    "settings.label.uitheme": "Theme",
    "settings.label.uilanguage": "UI Language",

    # Table 1 Page
    "table1.placeholder.file": "Select dataset file (CSV or Excel)…",
    "table1.btn.generate": "Generate Table 1",
    "table1.btn.export.html": "Export HTML",
    "table1.btn.export.csv": "Export CSV",

    # Training Page - Problem Types
    "training.problemtype.classification.binary": "Binary classification (Yes/No, Positive/Negative)",
    "training.problemtype.classification.multi": "Multi-class classification (several categories)",
    "training.problemtype.regression": "Regression (continuous numeric value)",

    # Training Page - Metrics
    "training.metric.accuracy": "Accuracy (overall correctness)",
    "training.metric.auc": "AUC (area under ROC curve)",
    "training.metric.f1": "F1-score (balanced precision/recall)",
    "training.metric.recall": "Recall (sensitivity, true positive rate)",
    "training.metric.precision": "Precision (positive predictive value)",
    "training.metric.rmse": "RMSE (root mean squared error)",
    "training.metric.mae": "MAE (mean absolute error)",
    "training.metric.mse": "MSE (mean squared error)",
    "training.metric.rmspe": "RMSPE (root mean squared percentage error)",
    "training.metric.specificity": "Specificity (true negative rate)",
    "training.metric.hitsatk": "Hits at K (true category in top-K predictions)",

    # Training Page - Hyperopt Strategies
    "training.strategy.none": "No optimisation (default values)",
    "training.strategy.random": "Random search",
    "training.strategy.bayesian": "Bayesian optimization (recommended)",
    "training.strategy.hyperband": "Hyperband",
    "training.strategy.exhaustive": "Exhaustive search (Grid Search)",

    # Help Page
    "help.btn.expand.all": "Expand All",
    "help.btn.collapse.all": "Collapse All",

    # Additional UI Strings - Settings Page
    "settings.theme.light": "Light",
    "settings.theme.dark": "Dark",
    "settings.theme.auto": "Auto (System)",
    "settings.label.theme.label": "Theme:",
    "settings.label.font.size": "Font Size:",
    "settings.label.ui.language": "UI Language:",
    "settings.label.format.label": "Default Format:",
    "settings.label.decimals": "Decimal Places:",
    "settings.label.log.level": "Log Level:",
    "settings.msg.language.restart": "Restart HAMELIN to apply the new language.",
    "settings.btn.debug": "Debug mode can be enabled via command line: python main.py --debug",
    "settings.label.version.label": "Version:",
    "settings.msg.reset.title": "Reset Settings",
    "settings.msg.reset.confirm": "This will restore all settings to their original values.",
    "settings.msg.reset.success": "All settings have been restored to defaults.",
    "settings.msg.saved.success": "Your preferences have been saved.",

    # Table 1 Page
    "table1.heading.results": "Results",
    "table1.placeholder.results": "Table 1 will appear here after generation...",
    "table1.dialog.export.html": "Export Table 1 as HTML",
    "table1.dialog.export.csv": "Export Table 1 as CSV",
    "table1.msg.exported": "Exported",
    "table1.msg.export.error": "Export Error",
    "table1.msg.load.error": "Load Error",
    "table1.msg.generation.error": "Table 1 Generation Error",
    "table1.dialog.file.default": "Table1.html",
    "table1.dialog.file.csv": "Table1.csv",

    # Data Page
    "data.dialog.select": "Select Data File",
    "data.dialog.filters": "All Supported (*.csv *.tsv *.xlsx *.parquet *.json *.jsonl *.feather *.h5 *.hdf5 *.html *.sav *.dta *.xpt *.sas7bdat *.fwf *.pkl *.pickle);;CSV (*.csv);;TSV (*.tsv);;Excel (*.xlsx);;Parquet (*.parquet);;JSON/JSONL (*.json *.jsonl);;Feather (*.feather);;HDF5 (*.h5 *.hdf5);;HTML (*.html *.htm);;SPSS (*.sav);;Stata (*.dta);;SAS (*.xpt *.sas7bdat);;Fixed Width Format (*.fwf);;Pickled DataFrame (*.pkl *.pickle)",

    # Main Window - Navigation
    "nav.forecasting": "Forecasting",
    "nav.help": "Help",

    # Home Page
    "home.stat.forecasts": "Forecasts",
    
    # Help Page - Header and Controls
    "help.btn.expand": "Expand All",
    "help.btn.collapse": "Collapse All",
    
    # Settings - About Section
    "settings.about.description":
        "HAMELIN (Human-guided Automated Machine Learning for Clinical Studies) "
        "is a platform that automates the machine learning pipeline for clinical "
        "research professionals, enabling robust statistical analysis and predictive "
        "modelling without requiring programming expertise.",
    
    "settings.about.university": "University of Cantabria",
    
    "settings.about.repository": "Repository: https://github.com/diegotxegp/hamelin",

    # Help Page - Section Titles and Summaries
    "help.section.0.title": "1 · Introduction",
    "help.section.0.summary": "What is HAMELIN and who is it for?",
    "help.section.0.block.0.heading": "What is HAMELIN?",
    "help.section.0.block.1.heading": "Who is HAMELIN for?",
    "help.section.0.block.2.heading": "Typical workflow",
    "help.section.0.block.3.heading": "What does HAMELIN NOT do?",

    "help.section.1.title": "2 · Getting Started",
    "help.section.1.summary": "Installation, first launch, and creating your first project.",
    "help.section.1.block.0.heading": "System requirements",
    "help.section.1.block.1.heading": "First launch",
    "help.section.1.block.2.heading": "Creating your first project",
    "help.section.1.block.3.heading": "Opening an existing project",
    "help.section.1.block.4.heading": "Where are my files?",

    "help.section.2.title": "3 · Projects",
    "help.section.2.summary": "Every metadata field explained: what to fill in and why it matters.",
    "help.section.2.block.0.heading": "Basic Information",
    "help.section.2.block.1.heading": "Recruitment Information",
    "help.section.2.block.2.heading": "Study Description",
    "help.section.2.block.3.heading": "Tips and common mistakes",

    "help.section.3.title": "4 · Data",
    "help.section.3.summary": "Loading files, variable types, data quality, and Table 1 (baseline characteristics).",
    "help.section.3.block.0.heading": "Supported file formats",
    "help.section.3.block.1.heading": "Loading a dataset",
    "help.section.3.block.2.heading": "Data Preview",
    "help.section.3.block.3.heading": "Removing and restoring columns/rows",
    "help.section.3.block.4.heading": "Variable List and Ludwig type inference",
    "help.section.3.block.5.heading": "Quality Report",
    "help.section.3.block.6.heading": "Common data problems and solutions",
    "help.section.3.block.7.heading": "Data Summary and missingness chart",
    "help.section.3.block.8.heading": "Table 1: what it is and how to generate it",
    "help.section.3.block.9.heading": "Table 1: grouping variable, missing data, and variable selection",
    "help.section.3.block.10.heading": "Table 1: interpreting and exporting the table",

    "help.section.6.title": "7 · Forecasting",
    "help.section.6.summary": "Predicting when your study will reach its enrollment target.",
    "help.section.6.block.0.heading": "What does the Forecasting page do?",
    "help.section.6.block.1.heading": "Required inputs",
    "help.section.6.block.2.heading": "Forecast parameters explained",
    "help.section.6.block.3.heading": "Reading the forecast chart",
    "help.section.6.block.4.heading": "Current Recruitment Status panel",
    "help.section.6.block.5.heading": "Exporting the timeline",

    "help.section.4.title": "5 · Training",
    "help.section.4.summary": "Building a predictive model with AutoML: no programming required.",
    "help.section.4.block.0.heading": "What is model training?",
    "help.section.4.block.1.heading": "Step 1: Outcome variable and predictors",
    "help.section.4.block.2.heading": "Step 2: Patient selection criteria",
    "help.section.4.block.3.heading": "Step 3: Model configuration",
    "help.section.4.block.4.heading": "Advanced options (inside Model Configuration, click to expand)",
    "help.section.4.block.5.heading": "Starting and monitoring training",
    "help.section.4.block.6.heading": "Understanding results",
    "help.section.4.block.7.heading": "Exporting the trained model",



    "help.section.7.title": "8 · Glossary",
    "help.section.7.summary": "Definitions of clinical and machine learning terms used in HAMELIN.",
    "help.section.7.block.0.heading": "Clinical terms",
    "help.section.7.block.1.heading": "Machine Learning / Statistics terms",
    "help.section.7.block.2.heading": "File formats",
    
    # Training Page - Additional labels
    "training.label.outcome.full": "Outcome variable:",
    "training.label.patients.count": "Patients after filtering: 0",

    # Help Page - Section 0: Introduction Block Texts
    "help.section.0.block.0.text": "HAMELIN (Human-guided Automated Machine Learning for Clinical Studies) is a desktop application designed for Clinical Research Professionals (CRPs) who need to manage clinical studies, analyse patient data, and build predictive models: without requiring programming skills or knowledge of Machine Learning.\n\nThe application was built following the HGML-2025 methodology, a set of validated best practices for applying Artificial Intelligence in clinical settings.",
    "help.section.0.block.1.text": "• Principal Investigators (PIs) who need to monitor recruitment and forecast when a study will reach its target.\n• Data Managers who prepare and clean datasets for analysis.\n• Biostatisticians who generate descriptive tables (Table 1) and predictive models.\n• Research Nurses and Coordinators who need a simple interface to check study status.",
    "help.section.0.block.2.text": "The recommended order of steps is:\n\n  1. PROJECT: create or open a project and fill in the study metadata.\n  2. DATA: load the patient dataset (CSV, Excel or SPSS).  Table 1 (baseline characteristics) is generated right there too, as the last section of the Data tab.\n  3. TRAINING: train an AutoML predictive model.\n  4. MODELS: a dedicated page (right after Training in the nav bar) to inspect and compare every model you've trained in this project.\n\nFORECASTING is optional: it predicts when you will reach your enrollment target and sits in the nav bar right after Models; use it if that is relevant to your study, it is not part of the core flow above.\n\nEach step is a tab in the left navigation bar (Help and Settings are pinned at the bottom; everything else, including Models and Forecasting, is in the main list).  You can go back and forward at any time.",
    "help.section.0.block.3.text": "• It does not replace a statistician or a data scientist for complex analyses.\n• It does not manage patient consent or regulatory documentation.\n• It is not a clinical data management system (CDMS): use it alongside your existing EDC (REDCap, OpenClinica, etc.).\n• It does not send data to any cloud service; everything runs locally on your computer.",

    # Help Page - Section 1: Getting Started Block Texts
    "help.section.1.block.0.text": "• Operating system: Windows 10/11 (64-bit), macOS 12+, or Ubuntu 20.04+.\n• Python 3.10 or newer (already bundled if you received the installer).\n• RAM: 8 GB minimum; 16 GB recommended for large datasets (> 10 000 rows).\n• Disk: 500 MB free for the application + space for your datasets.",
    "help.section.1.block.1.text": "Run the application from the terminal:\n\n    cd hamelin/\nuv run hamelin\n\nOn first launch the Home page is displayed with zero projects. No configuration is required.",
    "help.section.1.block.2.text": "1. Click 'Project' in the left navigation bar.\n2. Click the 'New Project' button.\n3. Fill in at least the required fields (marked with *): Project Name, Acronym, Protocol Number, Principal Investigator, Contact Email, and Institution.\n4. Click 'Save Project'.\n\nA folder named after your acronym will be created inside the Projects/ directory. All files related to this project will be saved there automatically.\n\nQuick Project:\n  Skips the form entirely and creates a project immediately with auto-generated placeholder details (name, acronym, protocol number). Useful to start loading data right away; open the project later from this same page to fill in the real study information.\n\nDelete All Projects:\n  Permanently deletes every saved project and everything inside them (datasets, results, models), after a confirmation prompt. This cannot be undone.",
    "help.section.1.block.3.text": "1. Click 'Project' in the navigation bar.\n2. The project list shows all previously saved projects with their details.\n3. Click 'Open' on the project card you want to work on.\n\nThe project is loaded into all pages simultaneously: the Data, Training and Forecasting pages are all updated with the project context.",
    "help.section.1.block.4.text": "All project data is stored locally in:\n\n    workspace/Projects/<ACRONYM>/ (inside the hamelin repo)\n        metadata.json    : project metadata\n        data/            : datasets linked to this project\n        data/dataset_index.json : registry of datasets\n        results/         : training results and exports\n\nYou can back up the entire Projects/ folder to any location.\n\nOutside a specific project, two more folders live in workspace/:\n    workspace/logs/hamelin_YYYY-MM-DD.log : the technical application log (one file per day).\n    workspace/logs/usage_log.csv          : a record of what you click and fill in across the app (button clicks, form fields, navigation, with a timestamp for each), kept for usability-study purposes. It's a plain CSV, easy to open in Excel or any spreadsheet tool.",

    # Help Page - Section 5: Training Block Texts (Most Important)
    "help.section.4.block.0.text": "Training a model means teaching a computer programme to recognise patterns in your data that are associated with a clinical outcome of interest.\n\nExample: given a patient's age, BMI, blood pressure, and cholesterol, can the model predict whether that patient will develop hypertension?\n\nHAMELIN uses AutoML (Automated Machine Learning via Ludwig) to automatically select and configure the best algorithm for your data: you do NOT need to know what a Random Forest or a Neural Network is.",
    "help.section.4.block.1.text": "Outcome variable (what you want to predict):\n    Select the column that contains the clinical result you want to model.\n    Examples: Diagnosis (Yes/No), Treatment_response (Complete/Partial/None), HbA1c_at_12months (numeric).\n\nPredictor variables (what the model learns from):\n    Click to select the columns you believe are clinically relevant: hold Ctrl or Shift to select several; there is no 'Select All' shortcut here, pick them one by one.\n    Rules of thumb:\n      • Include variables that are available BEFORE the outcome is known.\n      • Exclude patient ID, administrative codes, and the date column.\n      • Exclude variables with > 50% missing values unless you plan to impute them.\n\nSecondary outcomes (optional):\n    Other clinical endpoints you also want the model to learn to predict alongside the main one: this trains a real multi-output model, it is not just kept for your own reference.\n    Example: main outcome 'Mortality', with 'Length_of_stay' and 'Readmission_30d' also ticked here: the model is then trained to predict all three.\n    A column ticked as both a predictor and a secondary outcome is treated as a predictor only.",
    "help.section.4.block.2.text": "Here you can define inclusion and exclusion rules to filter the dataset before training, using the visual rule builder: pick a Column, an Operator, and a Value for each rule (there is no free-text expression box):\n    Age    >=   18\n    Sex    ==   Female\n\nAdd as many rows as you need, separately for Inclusion and Exclusion.  Click each builder's own 'Preview' button to see how many rows match and a sample of them, before you commit to training.\n\nIf a patient does NOT meet all inclusion criteria, they are excluded.\nIf a patient meets ANY exclusion criterion, they are also excluded.\n\n'Save preset' / 'Reset preset' save or clear these criteria (and the outcome variable) as a reusable JSON file for this project, under training_schemas/.",
    "help.section.4.block.3.text": "Only three settings are shown here by default: the rest live behind the '▶ Advanced options' toggle described just below, since they're more ML-technical than something a non-technical user needs to reason about day to day.\n\nModel name:\n  A short name for this training run: required.  It becomes the name of the folder where the trained model is saved, and is what you'll see later in the Model Training History and in the 'Models' page, so pick something you'll recognise (e.g. 'Mortality_v1').\n\nPrediction type:\n  Binary classification: the outcome has exactly two values (Yes/No, 0/1).\n  Multi-class classification: the outcome has 3 or more categories.\n  Regression: the outcome is a continuous number (e.g., weight loss in kg).\n  This is not just a hint: it forces Ludwig to train that kind of model, so make sure it actually matches your outcome column.\n\nEvaluation metric (how to measure model quality):\n  The list of choices changes depending on the Prediction type picked above - Ludwig only supports certain metrics per type:\n  Binary: AUC-ROC (most common in clinical settings), Accuracy, Precision, Recall, Specificity.\n  Multi-class: Accuracy, Hits at K (is the true category among the top-K predictions?).\n  Regression: RMSE, MAE, MSE, RMSPE - all measure average prediction error, lower is better.",
    "help.section.4.block.4.text": "Click '▶ Advanced options' in the Model Configuration card to reveal the rest of the settings.  Defaults are fine for most studies.\n\nTime budget (minutes):\n  Hard limit on search time.  Training stops when this is reached even if the max iterations have not been completed.\n\nFinal evaluation holdout (%):\n  A fixed percentage of patients is set aside BEFORE training begins and NEVER used for training: only for the final performance evaluation.  Default: 20%.\n\nRandom Seed:\n  Ensures that splits and random operations produce the same result every time you re-run the training.  Use the same seed to reproduce a result exactly.\n\nSearch strategy (hyperparameter optimisation):\n  No optimisation: use Ludwig's defaults (fastest, good starting point).\n  Random search: try random combinations.  Fast but less thorough.\n  Bayesian optimisation: uses results from previous trials to choose the next configuration to test.  Most efficient.  Recommended.\n  Grid Search (Exhaustive search): tries ALL combinations.  Very slow.  Not recommended for large spaces.\n\nMax. iterations:\n  Maximum number of different configurations to try, once a search strategy other than 'No optimisation' is selected.  More iterations → better model, more time.  Recommended: 50–100.\n\nParallel trials:\n  Number of CPU cores to use simultaneously.  Increase for faster search; decrease if the computer becomes unresponsive.\n\nEarly stopping (rounds):\n  How many consecutive evaluation rounds can pass with no improvement before training stops automatically.  Default: 5.  Set to -1 to disable it and always run the full time budget/iterations.\n\nHandle Class Imbalance:\n  On/off switch: enable it when one outcome category is much rarer than the other.  Only available for Binary classification - Ludwig doesn't support this for multi-class or regression, so the switch is disabled (and greyed out) for those.\n\nFill Missing Numeric Values with the Column Mean:\n  On/off switch.  Off (default): missing values in numeric columns are left for Ludwig to handle with its own default, which silently fills them with 0.  On: missing values are filled with that column's mean instead, before training: usually a better default than 0 for a clinical measurement.",
    "help.section.4.block.5.text": "1. Click 'Start Training'.  The button is only enabled once a dataset is loaded.\n2. The progress bar updates as training proceeds.  Do not close the application during training.\n3. Training log messages appear in real time.\n4. When finished, the Results panel's 4 highlighted cards adapt to what you actually trained:\n     • Classification: AUC-ROC, Accuracy, Sensitivity, Specificity.\n     • Regression: R², RMSE, MAE, Loss.\n   Any other metric Ludwig reports appears in a smaller line just below the cards.  A confusion matrix and ROC curve are also shown for classification tasks, when available.\n5. Click 'Stop' at any time to cancel.  Partial results up to the last completed trial are displayed.",
    "help.section.4.block.6.text": "AUC-ROC (Area Under the Curve): classification tasks:\n  0.5 = random guessing (useless model).\n  0.7 = acceptable discriminative ability.\n  0.8 = good.\n  0.9 = excellent (rare; verify there is no data leakage).\n  1.0 = perfect (almost always indicates a data leak: check your variables).\n\nR² (goodness of fit): regression tasks:\n  1.0 = perfect fit.\n  0.7–0.9 = good to excellent fit.\n  0.5–0.7 = moderate fit.\n  0–0.5 = weak fit: the model barely captures the pattern.\n  Below 0 = worse than simply predicting the average every time: the model isn't finding a real relationship between the predictors and this outcome.  This can happen; it usually means the chosen target isn't actually predictable from the chosen predictors, not that something is broken.\n\nRMSE / MAE (regression):\n  Both measure average prediction error, in the same units as the outcome variable: smaller is better.  MAE is easier to interpret directly ('predictions are off by X on average'); RMSE penalises large errors more.\n\nConfusion matrix (classification):\n  A 2×2 table (binary) counting:\n    True Positives (TP) / True Negatives (TN): correct predictions.\n    False Positives (FP): predicted positive, actually negative.\n    False Negatives (FN): predicted negative, actually positive.\n  In clinical settings, FN (missed cases) is usually more costly than FP.\n\nThe green box below the charts is an automatically generated one-line summary in plain language: it always adapts to whichever of the two result types you're looking at.",
    "help.section.4.block.7.text": "Click 'Export Trained Model' to save the model artefacts to a ZIP file.\nThis archive can be used to:\n  • Make predictions on new patients in the future.\n  • Share the model with collaborators.\n  • Archive the model for audit / reproducibility purposes.\n\nTraining results (metrics, charts) are also saved automatically in the project's results/ folder every time training completes.",
    "help.section.2.block.0.text": "Project Name *\n    The full official name of the study as it appears in the protocol.\n    Example: 'Impact of Ultra-Processed Foods on Metabolic Health'\n\nAcronym *\n    A short uppercase code used as the folder name for all project files.\n    Must be unique and contain only letters and numbers (no spaces).\n    Example: 'UPS' or 'METAB2025'.  Cannot be changed after saving.\n\nProtocol Number *\n    The official identifier assigned by your institution or sponsor.\n    Example: 'UPS-2024-001' or 'EudraCT 2024-000123-45'\n\nPrincipal Investigator *\n    Full name (and title) of the lead researcher.\n\nContact Email *\n    Primary contact for queries about this study.\n\nInstitution *\n    Hospital, university, or research centre running the study.\n\nStudy Type\n    Select the closest match:\n    • Patient Registry: ongoing data collection without intervention\n    • Observational Study: prospective or retrospective, no randomisation\n    • Clinical Trial: intervention with randomised allocation",
    "help.section.2.block.1.text": "Target Sample Size *\n    Number of patients you need to enroll to achieve the study's statistical power.\n    This value is used by the Forecasting page to calculate the estimated end date.\n    If you are unsure, consult your biostatistician.\n\nStart Date\n    The date when patient enrollment officially started.\n    Used in Forecasting to compute elapsed time and recruitment velocity.\n\nExpected End Date\n    The date by which you plan to complete enrollment.\n    Compared against the model's estimated end date to assess delay risk.",
    "help.section.2.block.2.text": "A free-text description of the study's primary objective, inclusion/exclusion criteria, interventions, and endpoints.\n\nThis text is included verbatim in automatically generated reports, so writing a clear, complete description here will save time later.",
    "help.section.2.block.3.text": "• The Acronym cannot be changed after the project is saved for the first time. Choose it carefully.\n• All required fields (*) must be filled to save.  The application will highlight the missing ones.\n• If you leave the form without saving, your changes are lost.  Use 'Save Project' before navigating away.\n• You can edit metadata at any time by opening the project card and clicking 'Open'.",
    "help.section.3.block.0.text": (
        "HAMELIN supports the following formats (readable by Ludwig):\n\n"
        "• CSV (.csv): plain text, values separated by commas or semicolons.\n"
        "  ✔ Most common format. Use this when exporting from REDCap or Excel.\n"
        "• TSV (.tsv): tab-separated values.\n"
        "• Excel (.xlsx): Microsoft Excel workbook (first sheet is used).\n"
        "• Parquet (.parquet): columnar storage, useful for large datasets.\n"
        "• JSON / JSONL (.json, .jsonl): structured data, JSON Lines for one-object-per-line.\n"
        "• Feather (.feather): fast binary dataframe format.\n"
        "• HDF5 (.h5, .hdf5): hierarchical binary format for large arrays.\n"
        "• HTML (.html): single-table HTML files (limited support).\n"
        "• SPSS (.sav): IBM SPSS binary format (preserves labels).\n"
        "• Stata (.dta): Stata data file.\n"
        "• SAS (.xpt, .sas7bdat): SAS datasets.\n"
        "• Fixed Width Format (.fwf): columns aligned by character position, no delimiter.\n"
        "• Pickled DataFrame (.pkl, .pickle): a pandas DataFrame saved with Python's pickle — only open files you trust.\n\n"
        "Requirements:\n  • First row must contain column headers (variable names).\n  • One row per patient.\n  • Avoid merged cells or decorative formatting (Excel)."
    ),
    "help.section.3.block.1.text": "1. Go to the Data tab.\n2. Click 'Browse' and select your file.\n3. Click 'Load'.\n\nWhen a project is active, the file is automatically copied into the project's data/ folder and registered so you can reload it later from the 'Project datasets' selector: no need to browse for the file again.\n\nHAMELIN also auto-detects column types (numeric, date, text…) and runs a background analysis with Ludwig AI to infer the most appropriate machine-learning type for each variable.",
    "help.section.3.block.2.text": "After loading, the Data Preview table shows ALL rows and columns of the dataset.\n\nColumn headers show the variable name; you can scroll horizontally to see all variables.\n\nSpecial values you may encounter:\n  NaN  : 'Not a Number'.  Indicates a missing or unknown value in a numeric column.\n  NaT  : 'Not a Time'.  Missing value in a date/time column.\n  (empty cell): same as NaN/NaT in most contexts.\n  inf  : Infinity.  A numeric overflow: treat as a data quality problem.\n\nYou can select columns by clicking the column header (highlighted in blue) and then click 'Remove Selected' to hide them from the analysis. They are NOT permanently deleted: use 'Restore All' to bring them back.",
    "help.section.3.block.3.text": "Select mode:\n  • Click a column header → enters 'column selection' mode.\n  • Click a row number   → enters 'row selection' mode.\n  • Hold Ctrl or Shift to select multiple items.\n\nRemoving:\n  Click 'Remove Selected'.  Removed items are hidden from the preview and from all analyses (Table 1, Training) until restored.\n\nRestoring:\n  Click 'Restore All' to bring back all previously removed columns and rows.\n\nExporting:\n  Pick a format from the dropdown next to the 'Export Cleaned Data' button: CSV, Excel (.xlsx), or Word (.docx): then click it.  It saves the dataset with any columns or rows you've removed left out.",
    "help.section.3.block.4.text": 'The Variable List shows every column with its inferred data type.\n\nWhile HAMELIN runs the analysis a progress bar is shown. This can take up to 30 seconds on large datasets.\n\nType icons:\n  🔢 number   : continuous or discrete numeric value (age, BMI, lab result)\n  ⭕ binary   : exactly two values (Yes/No, 0/1, Male/Female)\n  📝 category : a small number of discrete categories (diagnosis, treatment group)\n  📅 date     : calendar date or datetime\n  📄 text     : free-text (notes, comments) : usually excluded from models\n  📈 sequence : ordered sequence of values\n  ⏱ timeseries: values measured over time\n  ➡ vector   : multi-dimensional numeric feature\n\nThe type determines which statistical tests and model features HAMELIN uses. If a type is wrong, it is usually because the column contains unexpected values; check the Data Preview for encoding inconsistencies.\n\nYou can override any column\'s type yourself using the \'Set type\' dropdown next to it: the row highlights to show it\'s a manual override.  Changed your mind about several of them?  Click \'Reset Types to Inferred\' (just below the table) to revert every column back to what Ludwig originally inferred: this only touches type overrides, it never changes the dataset\'s actual values.',
    "help.section.3.block.5.text": "Click 'Generate Quality Report' to save a CSV file with one row per variable, listing: type, non-null count, missing count and missing %, number of unique values, and: for numeric columns: min, max, and mean.\n\nYou choose where to save it (default filename: quality_report.csv); it is not written automatically into the project folder and does not open on its own: open it afterwards in Excel or any spreadsheet programme.\n\nFor a quick visual check instead, see 'Data Summary and missingness chart' below.",
    "help.section.3.block.6.text": "Problem: 'Load failed: encoding error'\n  → Open the CSV in a text editor and save it as UTF-8.\n\nProblem: Date column shown as 'text' type\n  → Ensure all dates use the same format (DD/MM/YYYY or YYYY-MM-DD). Mixed formats prevent automatic detection.\n\nProblem: A numeric column shows as 'category'\n  → There may be non-numeric characters in some cells (e.g., '12 mg', '>100'). Open the file and clean those cells.\n\nProblem: Empty rows at the end of the file\n  → HAMELIN filters out fully-empty rows automatically. If the row count seems too low, check for rows with only a few values.",
    "help.section.3.block.7.text": "Once a dataset is loaded, HAMELIN also builds two things automatically, just below the Export / Reset Types / Generate Quality Report buttons:\n\n• A chart of the variables with the most missing data (top 10), so you can spot problem columns at a glance without opening the Quality Report.\n• A 'Data Summary' card: a plain-text overview of the loaded dataset you can read directly on the page.  Click 'Export Data Summary' to save that text to a .txt or .md file, e.g. to paste into an email or a methods section.\n\nBoth refresh automatically whenever you load a different dataset.",
    "help.section.3.block.8.text": "Table 1 is the standard first table in a clinical research paper.  It describes the demographic and clinical characteristics of the study population: usually things like age, sex, comorbidities, lab values: so readers can assess how representative the sample is.  It lives at the bottom of this Data tab and is built from whatever dataset is already loaded above: there is no separate 'Browse' button of its own.\n\nHAMELIN generates it automatically, using the correct statistical test for each variable type:\n  • Numeric → mean ± SD and median (IQR).\n  • Categorical / binary → count (n) and percentage (%).\n\nStep by step:\n  1. Scroll to the 'Select Variables for Table 1' card, further down this same tab.  Every column is listed and ticked by default.\n  2. Columns HAMELIN thinks should probably be excluded (identifiers, free text, zero-variance columns…) or that look like a good grouping variable are flagged right on their own row, so there's no separate list to cross-reference.\n  3. Click 'Apply All Recommendations' to act on those flags automatically, or tick/untick variables yourself.\n  4. Under 'Table Settings', configure the options described in the next block, then click 'Generate Table 1'.\n  5. Review the table in the preview panel, then export it: see below.",
    "help.section.3.block.9.text": "Grouping Variable (optional):\n  A categorical column used to split the table into groups and run a between-group statistical test: numeric variables get a t-test (2 groups) or ANOVA (3+ groups); categorical variables get a Chi-square test or Fisher's exact test.  A common choice in randomised trials is the treatment allocation; in observational studies it's often 'Cases vs Controls' or a diagnosis category.\n\nMissing data:\n  Choose whether rows with missing values are kept (shown as missing in the table) or dropped entirely before the table is built.\n\nShow p-values:\n  Only applies when a grouping variable is selected; untick it to hide the p-value column, e.g. for a purely descriptive Table 1.\n\nSelecting variables:\n  • 'Select All' / 'Deselect All': tick or untick everything at once.\n  • Individual ticks: choose per variable.\n  • 'Apply All Recommendations': unticks every variable flagged '(recommendation: exclude: reason)' and pre-selects the suggested grouping variable, if one was found.\n\nTip: exclude patient ID columns, free-text notes, and any column with > 50% missing values before generating the table: this is exactly what the recommendations are flagging for you.",
    "help.section.3.block.10.text": "Continuous variables:\n  Mean ± SD: shown when the distribution is approximately normal.\n  Median (IQR): shown when the distribution is skewed.\n\nCategorical variables:\n  n (%): count and percentage of patients in each category.\n\np-value column (when a grouping variable is used and 'Show p-values' is ticked):\n  < 0.05  → the groups differ significantly on this variable.\n  ≥ 0.05  → no statistically significant difference detected.\n\nMissing column:\n  Shows the number/% of patients with missing values for each variable (most relevant when missing data is kept rather than dropped).\n\nExporting:\n  Pick CSV, Excel (.xlsx), or Word (.docx) from the format dropdown next to the Export button, then click Export.\n  CSV: a plain-text table you can open in Excel for further formatting; numbers keep full precision.\n  Excel (.xlsx): a ready-to-use workbook.\n  Word (.docx): a styled table you can drop straight into a manuscript or send to your statistician.",
    "help.section.6.block.0.text": 'Given how patients have been enrolled so far, HAMELIN fits a statistical model to estimate the date when you will reach your Target Sample Size.\n\nIt also shows:\n  • The current enrollment velocity (patients per month).\n  • A confidence interval: a range of dates within which the target is likely to be reached (default: 95% confidence).\n  • A monthly milestone table (how many patients you will have enrolled at each future month).\n  • A chart showing historical enrollment (solid line) and the forecast (dashed line with confidence band).',
    "help.section.6.block.1.text": "1. A loaded dataset with a date column recording enrollment dates (one row per patient, one cell per enrollment date).\n2. A Target Sample Size (pre-filled from Project metadata).\n\nThe enrollment date column is any column where each value is the date the corresponding patient was included in the study.  In REDCap this is often called 'enrollment_date' or 'inclusion_date'.",
    "help.section.6.block.2.text": 'Enrollment Date Column\n    Select the column that contains the date each patient was enrolled.\n    Only date-type columns are shown here.\n\nTarget Sample Size\n    The total number of patients you need to enroll.\n    Pre-filled from the Project metadata.  You can override it here.\n\nHistorical Period (days)\n    How many days of past data to use for estimating recruitment velocity.\n    Default: 90 days.  Increase this for more stable estimates; decrease for more sensitivity to recent trends.\n\nConfidence Level\n    Statistical confidence for the estimated date interval.\n    0.95 = 95% confidence interval.      A narrower interval (0.80) is more optimistic;     a wider one (0.99) is more conservative.',
    "help.section.6.block.3.text": 'Solid coloured line: actual cumulative enrollment (historical data).\nDashed line: projected enrollment based on fitted regression.\nShaded band: confidence interval for the projection.\nHorizontal dashed line: target sample size.\nVertical dashed line: estimated date when the target will be met.\n\nIf the shaded band is very wide, your enrollment has been irregular (e.g., periods of high and low activity).  Consider reviewing whether a site just opened or closed.',
    "help.section.6.block.4.text": 'This panel updates automatically after running the forecast.\n\nCurrently Recruited: patients extracted from the date column (rows with a valid date).\nTarget Sample Size : as configured in the parameters.\nRemaining          : how many more patients you still need.\nAvg. Rate          : mean patients enrolled per month over the whole study period.\nStudy Start Date   : date of the first enrollment found in the dataset.',
    "help.section.6.block.5.text": "Click 'Export Timeline CSV' to save the monthly milestone table as a CSV file.\nEach row shows: Month, Expected enrolled, Lower bound, Upper bound.\nThis table is useful for progress reports and sponsor updates.",
    "help.section.7.block.0.text": 'CRP: Clinical Research Professional. Any trained person involved in conducting clinical research (coordinator, nurse, monitor, etc.).\n\nEDC: Electronic Data Capture. Software used to enter and manage clinical trial data (e.g., REDCap, OpenClinica, Medidata Rave).\n\nEnrollment / Recruitment: the process of identifying, consenting, and including a patient in a clinical study.\n\nEthics Approval: formal permission from an Institutional Review Board (IRB) or Ethics Committee (EC) to conduct a study involving human participants.\n\nInclusion / Exclusion Criteria: conditions that a patient must satisfy (inclusion) or must not have (exclusion) to be eligible for a study.\n\nPrincipal Investigator (PI): the lead researcher responsible for the overall conduct of the study.\n\nProtocol Number: a unique alphanumeric code assigned to the study, used in all regulatory and administrative communications.\n\nSample Size: the number of patients required to give the study enough statistical power to detect the effect of interest.\n\nTable 1: the baseline characteristics table in a clinical paper describing the study population.\n\nTarget Sample Size: the minimum number of patients needed; determined by a power calculation.',
    "help.section.7.block.1.text": "Algorithm: a mathematical procedure that learns patterns from data.\n\nAUC-ROC (Area Under the Receiver Operating Characteristic Curve): a metric between 0 and 1 measuring how well a binary classifier separates positive from negative cases.  AUC = 0.5 is random; AUC = 1.0 is perfect.\n\nAutoML: Automated Machine Learning.  Software that automatically selects and configures the best algorithm for a given dataset.\n\nBinary classification: a task where the outcome has exactly two possible values (e.g., diseased / healthy, responder / non-responder).\n\nConfusion matrix: a table showing Correct and incorrect predictions broken down by True/False Positive/Negative.\n\nCross-validation: a technique that divides the dataset into folds to estimate model performance more reliably than a single train/test split.\n\nData leakage: when information from the future or from the outcome variable accidentally enters the training data, causing unrealistically high performance.\n\nF1 score: the harmonic mean of Precision and Recall.  Useful when classes are imbalanced.\n\nFeature: a predictor variable used as input to the model.\n\nFeature importance: a measure of how much each predictor contributed to the model's decisions.\n\nHoldout set: a portion of the data kept completely separate from training and used only for the final performance evaluation.\n\nHyperparameter: a setting that controls how the algorithm learns (e.g., learning rate, number of trees).  Distinct from model parameters, which are learned from data.\n\nHyperparameter optimisation (HPO): automatic search for the best hyperparameter combination.\n\nLudwig: an open-source AutoML framework from Uber AI used by HAMELIN for model training and variable type inference.\n\nMulti-class classification: a task where the outcome has three or more categories.\n\nNaN (Not a Number): missing or undefined numeric value in a dataset.\n\nNaT (Not a Time): missing value in a date/time column.\n\nOverfitting: when a model learns the training data too well and fails to generalise to new patients.\n\nPrecision: of all patients the model predicted as positive, what fraction actually were positive?\n\nRandom seed: a number that initialises the random number generator, ensuring that random splits and initialisations are reproducible.\n\nRecall (Sensitivity): of all truly positive patients, what fraction did the model correctly identify?\n\nRegression: a task where the outcome is a continuous numeric value.\n\nStandard Deviation (SD): a measure of how spread out the values are around the mean.\n\nTrain / Test split: dividing the dataset into a training set (used to build the model) and a test set (used to evaluate it).",
    "help.section.7.block.2.text": 'CSV (.csv): Comma-Separated Values.  Plain text file where each row is an observation and columns are separated by commas.\n\nStata (.dta): Stata proprietary binary format for statistical datasets.\n\nSPSS (.sav): IBM SPSS Statistics binary format.  Preserves variable labels and value labels.\n\nXLSX (.xlsx): Microsoft Excel Open XML format.  Supports multiple sheets; HAMELIN reads only the first sheet.\n\nHTML (.html): HyperText Markup Language.  Used for formatted Table 1 and Quality Report exports.\n\nJSON (.json): JavaScript Object Notation.  Used internally by HAMELIN for project metadata and dataset registry.',


    "help.section.5.title": "6 · Models",
    "help.section.5.summary": "Compare and inspect every model you've trained in this project.",
    "help.section.5.block.0.heading": "What is the Models page?",
    "help.section.5.block.0.text": "The 'Models' item in the navigation bar (between Training and Forecasting) opens a dedicated view for everything you've trained in this project so far, not just the most recent run.  It is a normal page in the nav bar, not a separate window — leaving it is just clicking any other nav item.  Open a project first: this page needs one to know where to look for trained models.",
    "help.section.5.block.1.heading": "What you can do here",
    "help.section.5.block.1.text": "• Compare several trained models side by side on the metric of your choice.\n• Inspect a single model in depth (confusion matrix, ROC curve, hyperparameters used).\n• Duplicate a model with slightly different settings to try a variation without starting from scratch — this pre-fills the Training page with that configuration and switches you to it; nothing is saved until you actually start training.\n• Mark favourites and clean up models you no longer need.",
}

ES: dict[str, str] = {
    # Navigation
    "nav.home": "Inicio",
    "nav.project": "Proyectos",
    "nav.data": "Datos",
    "nav.table1": "Tabla 1",
    "nav.forecasting": "Reclutamiento",
    "nav.training": "Entrenamiento",
    "nav.dashboard": "Panel",
    "nav.models": "Modelos",
    "nav.help": "Manual",
    "nav.settings": "Configuración",

    # Home Page
    "home.title": "HAMELIN",
    "home.subtitle": "Plataforma AutoML para Investigación Clínica",
    "home.help": (
        "Esta es la pantalla de inicio. Desde aquí puedes abrir un "
        "proyecto existente o crear uno nuevo, y ver un resumen rápido "
        "de tus proyectos. Una vez abierto un proyecto, usa el menú de "
        "la izquierda para moverte entre Datos, Tabla 1, Entrenamiento "
        "y las demás páginas."
    ),
    "home.welcome.title": "Bienvenido a HAMELIN",
    "home.welcome.text": "Comienza creando o abriendo un proyecto para iniciar tu viaje de análisis.",
    "home.welcome.description": (
        "HAMELIN es una plataforma integral para la automatización de investigación clínica.\n\n"
        "Características principales:\n"
        "• Generación Tabla 1 - Tablas de características demográficas automatizadas\n"
        "• Metadatos del Proyecto - Seguimiento de información y reclutamiento de estudios\n"
        "• Pronóstico de Reclutamiento - Predicción de cronogramas de inscripción\n"
        "• Integración de AutoML - Aprendizaje automático automatizado con Ludwig\n\n"
        "Utiliza el menú de navegación a la izquierda para comenzar."
    ),
    "home.stat.projects": "Proyectos",
    "home.stat.datasets": "Conjuntos de Datos",
    "home.stat.models": "Modelos",
    "home.stat.forecasts": "Pronósticos",

    # Metadata/Projects Page
    "metadata.title": "Proyectos",
    "metadata.subtitle": "Abre un proyecto existente o crea uno nuevo",
    "metadata.help": (
        "Esta página contiene la información básica de tu proyecto: "
        "nombre del estudio, investigador principal, número objetivo de "
        "pacientes y fechas de reclutamiento. Completarla correctamente "
        "es lo que alimenta los indicadores (KPI) y la predicción de "
        "reclutamiento que se muestran en el resto de la aplicación."
    ),
    "metadata.btn.new": "Nuevo Proyecto",
    "metadata.no.projects": "Sin proyectos aún. Crea uno para comenzar.",
    "metadata.detail.title": "Metadatos del Proyecto",
    "metadata.detail.subtitle": "Gestiona información del estudio clínico",
    "metadata.btn.back": "← Volver a Proyectos",
    "metadata.btn.open": "Abrir",
    "metadata.section.basic": "Información Básica",
    "metadata.section.ethics": "Aprobación Ética",
    "metadata.section.recruitment": "Información de Reclutamiento",
    "metadata.section.objectives": "Objetivos del Estudio",
    "metadata.label.name": "Nombre del Proyecto",
    "metadata.label.shortname": "Nombre Corto",
    "metadata.label.protocol": "Número de Protocolo",
    "metadata.label.pi": "Investigador Principal",
    "metadata.label.email": "Email de Contacto",
    "metadata.label.institution": "Institución",
    "metadata.label.studytype": "Tipo de Estudio",
    "metadata.label.description": "Descripción del Estudio",
    "metadata.label.primaryobjective": "Objetivo Principal *",
    "metadata.label.secondaryobjectives": "Objetivos Secundarios (uno por línea)",
    "metadata.label.ethicscommittee": "Comité de Ética:",
    "metadata.label.ethicsapprovalnumber": "Número de Aprobación:",
    "metadata.label.approvaldate": "Fecha de Aprobación:",
    "metadata.placeholder.name": "Nombre completo del proyecto…",
    "metadata.placeholder.shortname": "Acrónimo corto, p.ej. UPS",
    "metadata.placeholder.protocol": "Número de protocolo, p.ej. UPS-2024-001",
    "metadata.placeholder.pi": "Nombre del Investigador Principal…",
    "metadata.placeholder.email": "contacto@hospital.org",
    "metadata.placeholder.institution": "Nombre de la institución u hospital…",
    "metadata.placeholder.description": "La pregunta clínica principal que responde este estudio…",
    "metadata.placeholder.secondaryobjectives": "Un objetivo adicional por línea, si los hay…",
    "metadata.placeholder.ethicscommittee": "p.ej. Comité de Ética de la Investigación…",
    "metadata.placeholder.ethicsapprovalnumber": "p.ej. CEIm-2024-015…",
    "metadata.btn.save": "Guardar Proyecto",
    "metadata.btn.reset": "Reiniciar",

    # Data Page
    "data.title": "Gestión de Datos",
    "data.subtitle": "Carga, inspecciona y gestiona tus datos de investigación",
    "data.help": (
        "Carga tu conjunto de datos aquí (CSV, Excel y otros formatos "
        "habituales). Hamelin detecta automáticamente el tipo de cada "
        "columna (categórica, numérica, etc.) y muestra cuántos datos "
        "faltan. Puedes excluir columnas o filas que no quieras usar, y "
        "exportar un informe de calidad antes de pasar al análisis."
    ),
    "data.section.source": "Fuente de Datos",
    "data.section.metrics": "Métricas de Calidad de Datos",
    "data.section.inspection": "Inspección de Datos",
    "data.section.variables": "Variables y Tipos",
    "data.section.table1": "Tabla 1: Características Basales",
    "data.placeholder.filepath": "No hay archivo seleccionado",
    "data.btn.browse": "Examinar",
    "data.btn.load": "Cargar",
    "data.btn.reload": "Recargar",
    "data.btn.reset.types": "Restablecer Tipos Inferidos",
    "data.btn.quality": "Generar Informe de Calidad",
    "data.btn.remove_duplicates": "Eliminar Duplicados",
    "data.btn.export": "Exportar Datos Limpios",
    "data.btn.exclude": "Excluir Valores Atípicos",
    "data.btn.restore": "Restaurar Excluidos",
    "data.label.formats": "Soportados: CSV, TSV, Excel (.xlsx/.xls), Parquet, JSON/JSONL, Feather, HDF5, HTML, SPSS (.sav), Stata (.dta), SAS (.xpt/.sas7bdat), Ancho Fijo (.fwf), DataFrame Serializado (.pkl/.pickle)",
    "data.label.rows": "Filas",
    "data.label.cols": "Columnas",
    "data.label.missing": "Faltantes %",
    "data.label.memory": "Memoria",
    "data.label.excluded": "Filas Excluidas",
    "data.help.formats": (
        "Ludwig puede leer datos codificados en UTF-8 desde 14 formatos de archivo.\n\n"
        "Formatos soportados:\n"
        "• Comma Separated Values (csv)\n"
        "• Excel Workbooks (excel)\n"
        "• Feather (feather)\n"
        "• Fixed Width Format (fwf)\n"
        "• Hierarchical Data Format 5 (hdf5)\n"
        "• Hypertext Markup Language (html): limitado a una única tabla en el archivo.\n"
        "• JavaScript Object Notation (json, jsonl)\n"
        "• Parquet (parquet)\n"
        "• Pickled Pandas DataFrame (pickle)\n"
        "• SAS data sets (xport / sas7bdat)\n"
        "• SPSS file (spss)\n"
        "• Stata file (stata)\n"
        "• Tab Separated Values (tsv)\n\n"
        "Consejos:\n  • Asegúrate de que la primera fila contiene los encabezados de columna (nombres de variables).\n  • Una fila por paciente.\n  • Los archivos deben estar codificados en UTF-8.\n  • Algunos formatos requieren bibliotecas opcionales. Instala con:\n      pip install -r requirements.txt\n  • Parquet/Feather: pyarrow o fastparquet\n  • SPSS/SAS/Stata: pyreadstat o los lectores integrados de pandas\n  • HDF5: tables (PyTables)"
    ),
    

    # Table 1 Page
    "table1.title": "Tabla 1: Estadísticas Descriptivas",
    "table1.subtitle": "Características de los pacientes y variables basales",
    "table1.help": (
        "Genera la \"Tabla 1\" estándar que exigen los artículos clínicos: "
        "un resumen de las características de tus pacientes, "
        "opcionalmente dividido en grupos (por ejemplo, según el "
        "resultado) con comparaciones estadísticas entre ellos. Elige qué "
        "variables incluir y, si quieres comparar grupos, qué variable "
        "usar para agruparlos."
    ),
    "table1.btn.generate": "Generar Tabla",
    "table1.btn.export": "Exportar",
    "table1.status.ready": "Listo para generar",
    "table1.status.generating": "Generando…",
    "table1.status.complete": "Completado",
    "table1.msg.loading": "Carga un conjunto de datos primero",
    "table1.msg.vars": "Selecciona variables para incluir",

    # Forecasting Page
    "forecasting.title": "Predicción de Reclutamiento",
    "forecasting.subtitle": "Predice la línea de tiempo de reclutamiento y logro de objetivos",
    "forecasting.help": (
        "Estima cuándo tu estudio alcanzará el número objetivo de "
        "pacientes, según cómo ha ido el reclutamiento hasta ahora. Usa "
        "los eventos de reclutamiento (fechas de inscripción de "
        "pacientes) registrados para este proyecto - cuanto más "
        "historial tengas, más fiable será la estimación."
    ),
    "forecasting.section.status": "Estado Actual de Reclutamiento",
    "forecasting.section.parameters": "Parámetros de Pronóstico",
    "forecasting.section.results": "Resultados del Pronóstico",
    "forecasting.section.chart": "Gráfica de Reclutamiento",
    "forecasting.section.timeline": "Línea de Tiempo Proyectada Mensual",
    "forecasting.label.recruited": "Inscritos Actualmente",
    "forecasting.label.target": "Objetivo de Inscripción",
    "forecasting.label.remaining": "Restante",
    "forecasting.label.rate": "Tasa de Inscripción",
    "forecasting.label.start": "Fecha de Inicio",
    "forecasting.label.date.col": "Columna de Fecha",
    "forecasting.label.completion": "Finalización Predicha",
    "forecasting.label.days.remaining": "Días Restantes",
    "forecasting.label.confidence": "Intervalo de Confianza",
    "forecasting.label.r2": "R² (Ajuste del Modelo)",
    "forecasting.label.on.track": "En Marcha",
    "forecasting.btn.generate": "Generar Pronóstico",
    "forecasting.btn.export.chart": "Exportar Gráfica (PNG)",
    "forecasting.btn.export.csv": "Exportar Línea de Tiempo CSV",
    "forecasting.placeholder.date.col": "Carga un conjunto de datos primero…",
    "forecasting.status.not.calculated": "No calculado",

    # Training Page
    "training.title": "Entrenamiento de Modelos",
    "training.subtitle": "Configura y entrena modelos AutoML",
    "training.help": (
        "Aquí construyes un modelo predictivo. Elige el resultado que "
        "quieres predecir (tu objetivo principal) y qué datos del "
        "paciente se pueden usar para predecirlo, opcionalmente filtra "
        "qué pacientes incluir, y luego inicia el entrenamiento - "
        "Hamelin se encarga del aprendizaje automático. Al terminar, "
        "puedes ver qué tan bien funcionó el modelo y exportarlo."
    ),
    "training.section.variables": "1. Variable de Resultado y Predictores",
    "training.section.criteria": "2. Criterios de Selección de Pacientes",
    "training.section.config": "3. Configuración del Modelo",
    "training.section.control": "4. Control del Entrenamiento",
    "training.section.advanced": "Opciones Avanzadas",
    "training.section.hyperopt": "Configuración Avanzada",
    "training.label.outcome": "Variable de Resultado",
    "training.label.predictors": "Variables predictoras (selecciona una o más):",
    "training.btn.select_all_predictors": "Seleccionar todo",
    "training.label.secondary_outcomes": "Resultados Secundarios (opcionales):",
    "training.help.secondary_outcomes": "Mapea endpoints secundarios del preset o selecciona columnas del conjunto de datos para marcarlos como secundarios.",
    "training.label.inclusion": "Criterios de Inclusión:",
    "training.label.exclusion": "Criterios de Exclusión:",
    "training.label.patients": "Pacientes después del filtrado",
    "training.label.problem": "Tipo de Problema",
    "training.label.metric": "Métrica de Optimización",
    "training.label.strategy": "Estrategia de Búsqueda",
    "training.label.timebudget": "Presupuesto de Tiempo (min)",
    "training.label.trials": "Máximo de Ensayos",
    "training.label.imbalance": "Manejar Desbalance de Clases",
    "training.label.meanimpute": "Estrategia para valores numéricos faltantes:",
    "training.label.modelname": "Nombre del modelo:",
    "training.label.predictiontype": "Tipo de predicción:",
    "training.label.evaluationmetric": "Métrica de evaluación:",
    "training.label.testsplit": "Retención de evaluación final:",
    "training.label.randomseed": "Semilla Aleatoria:",
    "training.label.maxiterations": "Máx. iteraciones:",
    "training.label.paralleltrials": "Ensayos paralelos:",
    "training.label.earlystop": "Parada temprana (rondas, -1 = desactivada):",
    "training.missingstrategy.default": "Por defecto de Ludwig (rellena con 0)",
    "training.missingstrategy.mean": "Rellenar con la media de la columna",
    "training.missingstrategy.mode": "Rellenar con el valor más frecuente",
    "training.missingstrategy.ffill": "Relleno hacia adelante (valor de la fila anterior)",
    "training.missingstrategy.bfill": "Relleno hacia atrás (valor de la fila siguiente)",
    "training.missingstrategy.droprow": "Descartar filas con valor faltante",
    "training.btn.select.all": "Seleccionar Todo",
    "training.btn.deselect.all": "Deseleccionar Todo",
    "training.btn.show.options": "▶ Opciones avanzadas",
    "training.btn.hide.options": "▼ Opciones avanzadas",
    "training.btn.start": "Iniciar Entrenamiento",
    "training.btn.stop": "Detener",
    "training.btn.export": "Exportar Modelo Entrenado",
    "training.btn.import_config": "Entrenar desde archivo de config…",
    "training.placeholder.outcome": "p.ej. Diagnóstico, Respuesta_Tratamiento, Mortalidad…",
    "training.placeholder.inclusion": "p.ej. Edad ≥ 18, Diagnóstico confirmado",
    "training.placeholder.exclusion": "p.ej. Embarazo, Infección activa",
    "training.status.nodata": "Carga un conjunto de datos primero para habilitar el entrenamiento",
    "training.status.ready": "Listo para entrenar",
    "training.status.training": "Entrenamiento en curso…",
    "training.status.training.from_config": "Entrenando desde configuración duplicada…",
    "training.status.done": "Entrenamiento completado",
    "training.status.error": "Ocurrió un error durante el entrenamiento",
    "training.status.cancelled": "Entrenamiento cancelado",
    "training.status.duplicate_loaded": "Configuración duplicada cargada: carga su conjunto de datos en la pestaña Datos si es necesario, luego pulsa Iniciar Entrenamiento",
    "training.duplicate.infobar.title": "Configuración duplicada cargada",
    "training.duplicate.infobar.body": "Las variables objetivo y predictoras se rellenan a partir del modelo original.",
    "training.duplicate.banner": "La próxima ejecución entrena una configuración fija del modelo duplicado. La sección de configuración del modelo de abajo se ignora.",
    "training.duplicate.banner.cancel": "Usar AutoML en su lugar",

    # Dashboard Page
    "dashboard.title": "Panel del Proyecto",
    "dashboard.btn.refresh": "Actualizar",
    "dashboard.subtitle": "Estado del proyecto en tiempo real e indicadores de reclutamiento",
    "dashboard.help": (
        "Una vista general de tu proyecto en una sola página: cómo va el "
        "reclutamiento respecto a tu objetivo, la calidad de tu conjunto "
        "de datos y un historial de todos los modelos que has entrenado. "
        "Usa los accesos directos de abajo para ir directamente a Datos "
        "o Entrenamiento."
    ),
    "dashboard.section.kpi": "Indicadores Clave de Rendimiento",
    "dashboard.section.progress": "Progreso de Reclutamiento",
    "dashboard.section.chart": "Gráfica de Reclutamiento",
    "dashboard.section.history": "Historial de Entrenamiento de Modelos",
    "dashboard.section.actions": "Acciones Rápidas",
    "dashboard.label.quality": "Calidad de Datos",
    "dashboard.label.variables": "Variables",
    "dashboard.label.samples": "Muestras",
    "dashboard.label.enrollment": "Inscripción %",
    "dashboard.label.recruited": "Inscritos",
    "dashboard.label.target": "Objetivo",
    "dashboard.msg.no.data": "No hay datos de reclutamiento disponibles",

    # Settings Page
    "settings.title": "Configuración",
    "settings.subtitle": "Configura las preferencias de la aplicación",
    "settings.help": (
        "Preferencias generales de la aplicación: apariencia clara/oscura, "
        "idioma de la interfaz, opciones de exportación por defecto y "
        "(para solucionar problemas) el nivel de registro. No afectan a "
        "tus datos ni a tus modelos - solo a cómo se ve y se comporta "
        "Hamelin."
    ),
    "settings.section.appearance": "Apariencia",
    "settings.section.language": "Idioma",
    "settings.section.export": "Preferencias de Exportación",
    "settings.section.advanced": "Avanzado",
    "settings.section.about": "Acerca de HAMELIN",
    "settings.section.authors": "Autores",
    "settings.label.theme": "Tema",
    "settings.label.language": "Idioma",
    "settings.label.format": "Formato de Exportación",
    "settings.label.loglevel": "Nivel de Registro",
    "settings.label.debug": "Información de Depuración",
    "settings.label.version": "Versión",
    "settings.label.description": "HAMELIN es una plataforma de aprendizaje automático diseñada para equipos de investigación clínica.",
    "settings.label.contact": "Repositorio: https://github.com/diegotxegp/hamelin",
    "settings.about.license": "Licencia: GNU General Public License v3.0 (GPLv3). Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo los términos de la GPLv3 publicada por la Free Software Foundation. Se distribuye SIN NINGUNA GARANTÍA, ni siquiera la garantía implícita de comerciabilidad o idoneidad para un propósito particular. Texto completo en el fichero LICENSE en la raíz del repositorio, o en gnu.org/licenses/gpl-3.0.html.",
    "settings.btn.reset": "Restablecer Valores Predeterminados",
    "settings.btn.apply": "Aplicar Configuración",
    "settings.msg.language.changed": "Idioma Cambiado",
    "settings.msg.language.restart": "Reinicia HAMELIN para aplicar el nuevo idioma.",

    # Help/Manual Page
    "help.title": "Manual del Usuario",
    "help.subtitle": "Guía de referencia completa para HAMELIN",
    "help.btn.expand": "Expandir Todo",
    "help.btn.collapse": "Contraer Todo",

    # Help Texts
    "help.data.formats": (
        "HAMELIN lee los formatos de archivo más comunes (ver lista).\n\n"
        "Formatos soportados:\n"
        "• CSV (.csv): archivos de texto con separadores (coma/punto y coma).\n"
        "• TSV (.tsv): valores separados por tabulaciones.\n"
        "• Excel (.xlsx, .xls): libros de Excel (se utiliza la primera hoja).\n"
        "• Parquet (.parquet): almacenamiento columnar eficiente.\n"
        "• JSON / JSONL (.json, .jsonl): archivos JSON estructurados.\n"
        "• Feather (.feather): formato binario rápido para dataframes.\n"
        "• HDF5 (.h5, .hdf5): formato binario jerárquico.\n"
        "• HTML (.html): archivos HTML con una sola tabla (soporte limitado).\n"
        "• SPSS (.sav), Stata (.dta), SAS (.xpt/.sas7bdat): archivos de paquetes estadísticos.\n\n"
        "Asegúrate de que el archivo tenga una fila de encabezado (nombres de variables) y una fila por paciente. Si falla la carga, consulta la ayuda de la pestaña Datos para solución de problemas."
    ),
    "help.data.preview": "Visualiza todas las filas y columnas de tu conjunto de datos cargado.\n\n• Verifica que los datos se cargaron correctamente\n• Confirma nombres de columnas y tipos de datos\n• Identifica posibles problemas de calidad de datos\n• Desplázate horizontalmente para ver todas las variables\n\nValores especiales que podrías encontrar:\n  NaN : Not a Number (no es un número). Indica un valor faltante\n         o desconocido en una columna numérica o de texto.\n  NaT : Not a Time (no es hora). El equivalente de NaN para\n         fechas/horas: la celda debería contener un valor temporal.\n  None: Mismo significado que NaN en la mayoría de contextos.\n  inf : Infinito. Un resultado numérico que se desbordó\n         (p.ej. división por cero). Trata como problema de calidad.\n\nConsejo: Filas o columnas con muchos NaN/NaT pueden necesitar\nlimpieza o exclusión antes del análisis.",
    "help.data.variables": "Vista general de todas las variables (columnas) en tu conjunto de datos.\n\nTipos de variables:\n• 🔢 Numérica: Números continuos o discretos (edad, valores de lab)\n• 📝 Categórica: Grupos o categorías (sexo, diagnóstico)\n• 📅 Fecha/Hora: Datos temporales (fechas de visitas, timestamps)\n• 📄 Texto: Campos de texto libre (notas, comentarios)\n\nHAMELIN detecta automáticamente los tipos pero puedes cambiarlos si es necesario.",
    "help.data.table1": "Genera la tabla estándar de \"características basales\" usada en artículos clínicos.\n\n• Elige una variable de agrupación para comparar dos grupos (p.ej. Tratamiento vs Control) con p-values, o déjala en 'None' para estadísticas descriptivas generales.\n• Las Recomendaciones Inteligentes sugieren qué variables excluir (identificadores, texto libre, columnas sin varianza) y una posible variable de agrupación.\n• Exporta el resultado en CSV, Excel (.xlsx) o Word (.docx).",
    "help.metadata.basic": "Ingresa información básica sobre tu estudio clínico. Estos detalles\nayudan a documentar el estudio e se incluyen en reportes exportados.",
    "help.settings.appearance": "Personaliza la apariencia visual de HAMELIN.\n\n• Tema: Claro (modo día), Oscuro (modo noche), o Auto (sigue al sistema)\n• Tamaño de Fuente: Ajusta el tamaño del texto para mejor legibilidad (8-16)\n\nLos cambios se aplican inmediatamente sin requerir reinicio.",
    "help.settings.language": "Elige tu idioma preferido para la aplicación.\n\nIdiomas disponibles:\n• English: Interfaz en inglés\n• Español: Interfaz en español\n\nSe requiere reinicio para que los cambios surtan efecto.",
    "help.settings.export": "Configura ajustes predeterminados para exportar resultados.\n\n• Formato Predeterminado: CSV (simple), Excel (formateado), o Word (listo para publicación)\n• Decimales: Precisión de números para resultados estadísticos (0-6)\n\nEstos son los predeterminados - puedes cambiar el formato al exportar.",
    "help.training.variables": "Selecciona la variable de resultado que quieres predecir y las\nvariables predictoras a usar en el modelo.\n\n• Resultado: La variable Y objetivo (diagnóstico, respuesta al tratamiento, etc.)\n• Predictoras: Una o más variables X que ayudan a predecir el resultado\n\nUsa los botones para seleccionar o deseleccionar rápidamente todos los predictores.",
    "help.training.criteria": "Define criterios de selección de pacientes para tu análisis.\n\n• Inclusión: Define quién debe ser incluido (edad, diagnóstico, etc.)\n• Exclusión: Define quién debe ser excluido (embarazo, contraindicaciones, etc.)\n\nLos valores se aplican como filtros al dataset antes del entrenamiento.",
    "help.training.config": "Configura el tipo de modelo de aprendizaje automático y la métrica de optimización.\n\n• Tipo de Problema: Clasificación (binaria/multiclase) o Regresión\n• Métrica: Qué optimizar (exactitud, AUC, RMSE, etc.)\n\nLudwig ajustará hiperparámetros para maximizar esta métrica.",
    "help.forecasting.params": "Configura las entradas necesarias para generar el pronóstico.\n\n• Columna de Fecha de Inscripción: Columna que contiene fechas de inscripción de pacientes\n• Objetivo de Tamaño de Muestra: Total de pacientes necesarios para completar el estudio\n• Período Histórico: Días de historia usados para estimación de velocidad\n• Nivel de Confianza: Confianza estadística para el intervalo (0.95 = 95%)\n\nPresiona 'Generar Pronóstico' para ejecutar el análisis.",
    "help.training.variables": "Selecciona qué quieres predecir y qué variables clínicas usar.\n\n• Variable de resultado: el punto final clínico a predecir (diagnóstico, respuesta al tratamiento, mortalidad…).\n• Variables predictoras: características del paciente que el modelo aprenderá (edad, resultados de lab, síntomas…). Haz clic para seleccionar: mantén Ctrl o Mayús para varias; aquí no hay un atajo 'Seleccionar Todo'.\n• Resultados secundarios (opcional): otros puntos finales clínicos que también quieres que el modelo aprenda a predecir junto al principal: esto entrena un modelo real multi-resultado, no es solo para tu referencia.",
    "help.training.criteria": "Define qué pacientes deben ser INCLUIDOS o EXCLUIDOS del análisis.\n\n• Inclusión: pacientes que cumplen con criterios de elegibilidad (p.ej. Edad >= 18, DiagnósticoConfirmado == True).\n• Exclusión: pacientes a remover (p.ej. DatosAusentes > 50%, ViolacióndeProtocolo == True).\n\nTambién puedes excluir casos con pobre calidad de datos identificados en el Informe de Calidad del dataset.\n\nEstos criterios filtran el dataset antes del entrenamiento.",
    "help.training.config": "Configura cómo el modelo debe aprender.\n\n• Nombre del modelo: identificador corto para esta ejecución: obligatorio; se convierte en el nombre de la carpeta del checkpoint.\n• Tipo de predicción: fuerza el tipo de modelo: binaria, multiclase o regresión: asegúrate de que coincide con tu variable de resultado.\n• Métrica de evaluación: cómo medir si el modelo es bueno (AUC es la más común en contextos clínicos).\n\nPulsa \"Opciones avanzadas\" para más control (los valores por defecto son suficientes en la mayoría de los casos):\n• Presupuesto de tiempo: tiempo máximo de búsqueda del mejor modelo (en minutos).\n• Retención de evaluación final: porcentaje de pacientes reservados para la prueba final, nunca usado en entrenamiento. Recomendado: 20%.\n• Semilla aleatoria: fija la aleatoriedad para poder reproducir exactamente una ejecución.\n• Estrategia de búsqueda: método para encontrar la mejor configuración (la optimización Bayesiana es la más eficiente; la búsqueda aleatoria es más rápida pero menos precisa).\n• Máx. iteraciones: cuántas configuraciones diferentes probar.\n• Ensayos paralelos: usa más núcleos de CPU para acelerar la búsqueda.\n• Manejar desbalance de clases: actívalo cuando una categoría de resultado es mucho más rara que la otra.\n• Rellenar Valores Numéricos Faltantes con la Media: si está activado, los valores numéricos faltantes se imputan con la media de la columna en lugar del valor por defecto de Ludwig (que los rellena con 0 en silencio).\n\nHAMELIN usa AutoML para encontrar automáticamente el mejor modelo para tu dataset.",
    "help.training.hyperopt": "Opciones avanzadas para optimizar automáticamente el modelo.\n\n• Estrategia: método de búsqueda para encontrar la mejor configuración del modelo.\n  • Optimización Bayesiana: más eficiente (recomendado).\n  • Búsqueda aleatoria: más rápido pero menos preciso.\n• Máx. iteraciones: cuántas configuraciones diferentes probar (más = mejor, más tiempo).\n• Presupuesto de tiempo: tiempo máximo de búsqueda (en minutos).\n• Ensayos paralelos: usa más núcleos de CPU para acelerar la búsqueda.\n\nEn la mayoría de los casos, los valores predeterminados son suficientes. Cambia esto solo si necesitas máximo rendimiento.",
    "help.training.control": "Inicia, monitorea y controla el proceso de entrenamiento del modelo.\n\n• Iniciar entrenamiento: lanza el proceso AutoML con tu configuración.\n• Barra de progreso: muestra el progreso en tiempo real.\n• Resultados: métricas de rendimiento para el mejor modelo encontrado.\n• Exportar modelo: guarda el modelo entrenado para uso futuro o despliegue.\n\nEl entrenamiento puede tomar desde minutos a horas dependiendo del tamaño del dataset y configuración.",

    # Additional UI Strings
    # Data Page
    "data.btn.load.selected": "Cargar Seleccionados",
    "data.btn.remove.selected": "Eliminar Seleccionados",
    "data.btn.restore.all": "Restaurar Todo",
    "data.placeholder.datasets": "Sin conjuntos de datos aún",

    # Metadata Page
    "metadata.btn.new.project": "Nuevo Proyecto",
    "metadata.btn.select": "Seleccionar",
    "metadata.btn.selected": "✓ Seleccionado",
    "metadata.btn.back": "← Volver a Proyectos",
    "metadata.placeholder.name": "Nombre completo del proyecto…",
    "metadata.placeholder.shortname": "Acrónimo corto, p.ej. UPS",
    "metadata.placeholder.protocol": "Número de protocolo, p.ej. UPS-2024-001",
    "metadata.placeholder.pi": "Nombre del Investigador Principal…",
    "metadata.placeholder.email": "contacto@hospital.org",
    "metadata.placeholder.institution": "Nombre de la institución u hospital…",
    "metadata.placeholder.description": "La pregunta clínica principal que responde este estudio…",
    "metadata.studytype.registry": "Registro de Pacientes",
    "metadata.studytype.observational": "Estudio Observacional",
    "metadata.studytype.clinical": "Ensayo Clínico",
    "metadata.btn.new.generic": "Proyecto Rápido",
    "metadata.btn.delete.all": "Borrar Todos los Proyectos",
    "metadata.msg.deleteall.title": "¿Borrar todos los proyectos?",
    "metadata.msg.deleteall.confirm": "Esto eliminará permanentemente los {n} proyecto(s) y todo su contenido (datasets, resultados, modelos). No se puede deshacer.",
    "metadata.msg.deleteall.success": "Se eliminaron {n} proyecto(s).",
    "metadata.msg.generic.success": "'{short_name}' creado con datos de marcador de posición — ábrelo cuando quieras para rellenar la información real.",

    # Settings Page
    "settings.theme.light": "Claro",
    "settings.theme.dark": "Oscuro",
    "settings.label.uitheme": "Tema",
    "settings.label.uilanguage": "Idioma de la Interfaz",

    # Table 1 Page
    "table1.placeholder.file": "Selecciona archivo de datos (CSV o Excel)…",
    "table1.btn.generate": "Generar Tabla 1",
    "table1.btn.export.html": "Exportar HTML",
    "table1.btn.export.csv": "Exportar CSV",

    # Training Page - Problem Types
    "training.problemtype.classification.binary": "Clasificación binaria (Sí/No, Positivo/Negativo)",
    "training.problemtype.classification.multi": "Clasificación multiclase (varias categorías)",
    "training.problemtype.regression": "Regresión (valor numérico continuo)",

    # Training Page - Metrics
    "training.metric.accuracy": "Exactitud (corrección general)",
    "training.metric.auc": "AUC (área bajo la curva ROC)",
    "training.metric.f1": "F1-score (balance entre precisión y recuerdo)",
    "training.metric.recall": "Recuerdo (sensibilidad, tasa de verdaderos positivos)",
    "training.metric.precision": "Precisión (valor predictivo positivo)",
    "training.metric.rmse": "RMSE (raíz del error cuadrático medio)",
    "training.metric.mae": "MAE (error absoluto medio)",
    "training.metric.mse": "MSE (error cuadrático medio)",
    "training.metric.rmspe": "RMSPE (raíz del error porcentual cuadrático medio)",
    "training.metric.specificity": "Especificidad (tasa de verdaderos negativos)",
    "training.metric.hitsatk": "Hits at K (categoría real entre las K mejores predicciones)",

    # Training Page - Hyperopt Strategies
    "training.strategy.none": "Sin optimización (valores predeterminados)",
    "training.strategy.random": "Búsqueda aleatoria",
    "training.strategy.bayesian": "Optimización Bayesiana (recomendado)",
    "training.strategy.hyperband": "Hyperband",
    "training.strategy.exhaustive": "Búsqueda exhaustiva (Grid Search)",

    # Help Page
    "help.btn.expand.all": "Expandir Todo",
    "help.btn.collapse.all": "Contraer Todo",

    # Additional UI Strings - Settings Page
    "settings.theme.light": "Claro",
    "settings.theme.dark": "Oscuro",
    "settings.theme.auto": "Auto (Sistema)",
    "settings.label.theme.label": "Tema:",
    "settings.label.font.size": "Tamaño de Fuente:",
    "settings.label.ui.language": "Idioma de la Interfaz:",
    "settings.label.format.label": "Formato Predeterminado:",
    "settings.label.decimals": "Decimales:",
    "settings.label.log.level": "Nivel de Registro:",
    "settings.msg.language.restart": "Reinicia HAMELIN para aplicar el nuevo idioma.",
    "settings.btn.debug": "El modo de depuración se puede habilitar por línea de comandos: python main.py --debug",
    "settings.label.version.label": "Versión:",
    "settings.msg.reset.title": "Restablecer Configuración",
    "settings.msg.reset.confirm": "Esto restaurará toda la configuración a los valores originales.",
    "settings.msg.reset.success": "Toda la configuración ha sido restaurada a los valores predeterminados.",
    "settings.msg.saved.success": "Tus preferencias han sido guardadas.",

    # Table 1 Page
    "table1.heading.results": "Resultados",
    "table1.placeholder.results": "Tabla 1 aparecerá aquí después de la generación...",
    "table1.dialog.export.html": "Exportar Tabla 1 como HTML",
    "table1.dialog.export.csv": "Exportar Tabla 1 como CSV",
    "table1.msg.exported": "Exportado",
    "table1.msg.export.error": "Error de Exportación",
    "table1.msg.load.error": "Error de Carga",
    "table1.msg.generation.error": "Error de Generación de la Tabla 1",
    "table1.dialog.file.default": "Tabla1.html",
    "table1.dialog.file.csv": "Tabla1.csv",

    # Data Page
    "data.dialog.select": "Seleccionar Archivo de Datos",
    "data.dialog.filters": "Soportados (*.csv *.tsv *.xlsx *.parquet *.json *.jsonl *.feather *.h5 *.hdf5 *.html *.sav *.dta *.xpt *.sas7bdat *.fwf *.pkl *.pickle);;CSV (*.csv);;TSV (*.tsv);;Excel (*.xlsx);;Parquet (*.parquet);;JSON/JSONL (*.json *.jsonl);;Feather (*.feather);;HDF5 (*.h5 *.hdf5);;HTML (*.html *.htm);;SPSS (*.sav);;Stata (*.dta);;SAS (*.xpt *.sas7bdat);;Formato de Ancho Fijo (*.fwf);;DataFrame Serializado (*.pkl *.pickle)",

    # Main Window - Navigation
    "nav.forecasting": "Pronóstico",
    "nav.help": "Manual",

    # Home Page
    "home.stat.forecasts": "Pronósticos",

    # Training Page - Additional labels
    "training.label.outcome.full": "Variable de Resultado:",
    "training.label.patients.count": "Pacientes después del filtrado: 0",

    # Help Page - Header and Controls
    "help.title": "Manual del Usuario",
    "help.subtitle": "Guía de referencia completa para HAMELIN",
    "help.btn.expand": "Expandir Todo",
    "help.btn.collapse": "Contraer Todo",

    # Settings - About Section
    "settings.about.description": 
        "HAMELIN (Aprendizaje Automático Guiado por Humanos para Estudios Clínicos) "
        "es una plataforma que automatiza el procesamiento de IA para profesionales "
        "de investigación clínica, permitiendo análisis estadísticos robustos y "
        "modelado predictivo sin requerir habilidades de programación.",
    
    "settings.about.university": "Universidad de Cantabria (España)",
    
    "settings.about.repository": "Repositorio: https://github.com/diegotxegp/hamelin",

    # Help Page - Section Titles and Summaries
    "help.section.0.title": "1 · Introducción",
    "help.section.0.summary": "Qué es HAMELIN y para quién está diseñado?",
    "help.section.0.block.0.heading": "Qué es HAMELIN?",
    "help.section.0.block.1.heading": "¿Para quién es HAMELIN?",
    "help.section.0.block.2.heading": "Flujo de trabajo típico",
    "help.section.0.block.3.heading": "Qué NO hace HAMELIN?",

    "help.section.1.title": "2 · Primeros Pasos",
    "help.section.1.summary": "Instalación, primer lanzamiento y creación de tu primer proyecto.",
    "help.section.1.block.0.heading": "Requisitos del sistema",
    "help.section.1.block.1.heading": "Primer lanzamiento",
    "help.section.1.block.2.heading": "Creando tu primer proyecto",
    "help.section.1.block.3.heading": "Abrir un proyecto existente",
    "help.section.1.block.4.heading": "¿Dónde están mis archivos?",

    "help.section.2.title": "3 · Proyectos",
    "help.section.2.summary": "Explicación de cada campo de metadatos: qué rellenar y por qué importa.",
    "help.section.2.block.0.heading": "Información Básica",
    "help.section.2.block.1.heading": "Información de Reclutamiento",
    "help.section.2.block.2.heading": "Descripción del Estudio",
    "help.section.2.block.3.heading": "Consejos y errores comunes",

    "help.section.3.title": "4 · Datos",
    "help.section.3.summary": "Cargando archivos, tipos de variables, calidad de datos y Tabla 1 (características basales).",
    "help.section.3.block.0.heading": "Formatos de archivo soportados",
    "help.section.3.block.1.heading": "Cargando un dataset",
    "help.section.3.block.2.heading": "Vista Previa de Datos",
    "help.section.3.block.3.heading": "Removiendo y restaurando columnas/filas",
    "help.section.3.block.4.heading": "Lista de Variables e inferencia de tipos Ludwig",
    "help.section.3.block.5.heading": "Reporte de Calidad",
    "help.section.3.block.6.heading": "Problemas comunes de datos y soluciones",
    "help.section.3.block.7.heading": "Resumen de Datos y gráfico de valores faltantes",
    "help.section.3.block.8.heading": "Tabla 1: qué es y cómo generarla",
    "help.section.3.block.9.heading": "Tabla 1: variable de agrupación, datos faltantes y selección de variables",
    "help.section.3.block.10.heading": "Tabla 1: interpretando y exportando la tabla",

    "help.section.6.title": "7 · Pronóstico",
    "help.section.6.summary": "Prediciendo cuándo tu estudio alcanzará su objetivo de reclutamiento.",
    "help.section.6.block.0.heading": "Qué hace la página de Pronóstico?",
    "help.section.6.block.1.heading": "Entradas requeridas",
    "help.section.6.block.2.heading": "Parámetros de pronóstico explicados",
    "help.section.6.block.3.heading": "Leyendo el gráfico de pronóstico",
    "help.section.6.block.4.heading": "Panel de Estado de Reclutamiento Actual",
    "help.section.6.block.5.heading": "Exportando la línea de tiempo",

    "help.section.4.title": "5 · Entrenamiento",
    "help.section.4.summary": "Construyendo un modelo predictivo con AutoML: sin programación requerida.",
    "help.section.4.block.0.heading": "Qué es el entrenamiento de modelos?",
    "help.section.4.block.1.heading": "Paso 1: Variable de resultado y predictores",
    "help.section.4.block.2.heading": "Paso 2: Criterios de selección de pacientes",
    "help.section.4.block.3.heading": "Paso 3: Configuración del modelo",
    "help.section.4.block.4.heading": "Opciones avanzadas (dentro de Configuración del Modelo, clic para expandir)",
    "help.section.4.block.5.heading": "Iniciando y monitoreando el entrenamiento",
    "help.section.4.block.6.heading": "Entendiendo los resultados",
    "help.section.4.block.7.heading": "Exportando el modelo entrenado",



    "help.section.7.title": "8 · Glosario",
    "help.section.7.summary": "Definiciones de términos clínicos y de aprendizaje automático utilizados en HAMELIN.",
    "help.section.7.block.0.heading": "Términos clínicos",
    "help.section.7.block.1.heading": "Términos de Aprendizaje Automático / Estadística",
    "help.section.7.block.2.heading": "Formatos de archivo",

    # Help Page - Section 0: Introduction Block Texts (Spanish)
    "help.section.0.block.0.text": "HAMELIN (Aprendizaje Automático Guiado por Humanos para Estudios Clínicos) es una aplicación de escritorio diseñada para Profesionales de Investigación Clínica (PIC) que necesitan gestionar estudios clínicos, analizar datos de pacientes y construir modelos predictivos, sin requerir habilidades de programación o conocimiento de Aprendizaje Automático.\n\nLa aplicación fue construida siguiendo la metodología HGML-2025, un conjunto de mejores prácticas validadas para aplicar Inteligencia Artificial en ámbitos clínicos.",
    "help.section.0.block.1.text": "• Investigadores Principales (IP) que necesitan monitorear el reclutamiento y pronosticar cuándo un estudio alcanzará su objetivo.\n• Gestores de Datos que preparan y limpian conjuntos de datos para análisis.\n• Bioestadísticos que generan tablas descriptivas (Tabla 1) y modelos predictivos.\n• Enfermeras de Investigación y Coordinadores que necesitan una interfaz simple para verificar el estado del estudio.",
    "help.section.0.block.2.text": "El orden recomendado de pasos es:\n\n  1. PROYECTO: crear o abrir un proyecto y completar los metadatos del estudio.\n  2. DATOS: cargar el conjunto de datos de pacientes (CSV, Excel o SPSS).  Tabla 1 (características basales) también se genera ahí mismo, como la última sección de la pestaña Datos.\n  3. ENTRENAMIENTO: entrenar un modelo predictivo AutoML.\n  4. MODELOS: una página dedicada (justo después de Entrenamiento en la barra de navegación) para inspeccionar y comparar cada modelo que hayas entrenado en este proyecto.\n\nPRONÓSTICO es opcional: predice cuándo alcanzarás tu objetivo de reclutamiento y se encuentra en la barra de navegación justo después de Modelos; úsalo si es relevante para tu estudio, no forma parte del flujo principal anterior.\n\nCada paso es una pestaña en la barra de navegación izquierda (Ayuda y Configuración están fijadas abajo; todo lo demás, incluyendo Modelos y Pronóstico, está en la lista principal).  Puedes avanzar y retroceder en cualquier momento.",
    "help.section.0.block.3.text": "• No reemplaza a un estadístico o científico de datos para análisis complejos.\n• No maneja consentimiento de pacientes o documentación regulatoria.\n• No es un sistema de gestión de datos clínicos (CDMS): úsalo junto a tu sistema EDC existente (REDCap, OpenClinica, etc.).\n• No envía datos a ningún servicio en la nube; todo se ejecuta localmente en tu computadora.",

    # Help Page - Section 1: Getting Started Block Texts (Spanish)
    "help.section.1.block.0.text": "• Sistema operativo: Windows 10/11 (64-bit), macOS 12+, o Ubuntu 20.04+.\n• Python 3.10 o más reciente (ya incluido si recibiste el instalador).\n• RAM: 8 GB mínimo; 16 GB recomendado para grandes conjuntos de datos (> 10 000 filas).\n• Disco: 500 MB libres para la aplicación + espacio para tus conjuntos de datos.",
    "help.section.1.block.1.text": "Ejecuta la aplicación desde la terminal:\n\n    cd hamelin/\nuv run hamelin\n\nAl iniciar por primera vez, se muestra la página Inicio con cero proyectos. No se requiere configuración.",
    "help.section.1.block.2.text": "1. Haz clic en 'Proyectos' en la barra de navegación izquierda.\n2. Haz clic en el botón 'Nuevo Proyecto'.\n3. Completa al menos los campos obligatorios (marcados con *): Nombre del Proyecto, Acrónimo, Número de Protocolo, Investigador Principal, Email de Contacto, e Institución.\n4. Haz clic en 'Guardar Proyecto'.\n\nSe creará una carpeta con el nombre de tu acrónimo dentro del directorio Projects/ (el nombre de la carpeta en disco es siempre en inglés, aunque la interfaz esté en español). Todos los archivos relacionados con este proyecto se guardarán allí automáticamente.\n\nProyecto Rápido:\n  Se salta el formulario por completo y crea un proyecto al instante con datos de marcador de posición generados automáticamente (nombre, acrónimo, número de protocolo). Útil para empezar a cargar datos de inmediato; abre el proyecto más tarde desde esta misma página para rellenar la información real del estudio.\n\nBorrar Todos los Proyectos:\n  Elimina permanentemente todos los proyectos guardados y todo su contenido (datasets, resultados, modelos), tras una confirmación. No se puede deshacer.",
    "help.section.1.block.3.text": "1. Haz clic en 'Proyectos' en la barra de navegación.\n2. La lista de proyectos muestra todos los proyectos guardados previamente con sus detalles.\n3. Haz clic en 'Abrir' en la tarjeta del proyecto con el que deseas trabajar.\n\nEl proyecto se carga en todas las páginas simultáneamente: las páginas Datos, Entrenamiento y Pronóstico se actualizan con el contexto del proyecto.",
    "help.section.1.block.4.text": "Todos los datos del proyecto se almacenan localmente en:\n\n    workspace/Projects/<ACRÓNIMO>/ (dentro del repositorio hamelin; el nombre de la carpeta es siempre en inglés)\n        metadata.json    : metadatos del proyecto\n        data/            : conjuntos de datos vinculados a este proyecto\n        data/dataset_index.json : registro de conjuntos de datos\n        results/         : resultados de entrenamiento y exportaciones\n\nPuedes hacer una copia de seguridad de toda la carpeta Projects/ en cualquier ubicación.\n\nFuera de un proyecto concreto, hay dos carpetas más en workspace/:\n    workspace/logs/hamelin_YYYY-MM-DD.log : el log técnico de la aplicación (un fichero por día).\n    workspace/logs/usage_log.csv          : un registro de qué pulsas y qué rellenas en la app (clics en botones, campos de formulario, navegación, cada uno con su hora), guardado para estudios de usabilidad. Es un CSV normal, fácil de abrir en Excel o cualquier hoja de cálculo.",

    # Help Page - Section 5: Training Block Texts (Spanish - Most Important)
    "help.section.4.block.0.text": "Entrenar un modelo significa enseñar a un programa informático a reconocer patrones en tus datos que están asociados con un resultado clínico de interés.\n\nEjemplo: dado la edad, IMC, presión arterial y colesterol de un paciente, ¿puede el modelo predecir si ese paciente desarrollará hipertensión?\n\nHAMELIN utiliza AutoML (Aprendizaje Automático Automatizado a través de Ludwig) para seleccionar y configurar automáticamente el mejor algoritmo para tus datos: NO necesitas saber qué es un Bosque Aleatorio o una Red Neuronal.",
    "help.section.4.block.1.text": "Variable de resultado (lo que quieres predecir):\n    Selecciona la columna que contiene el resultado clínico que deseas modelar.\n    Ejemplos: Diagnóstico (Sí/No), Respuesta_Tratamiento (Completa/Parcial/Ninguna), HbA1c_a_12meses (numérico).\n\nVariables predictoras (lo que el modelo aprende):\n    Haz clic para seleccionar las columnas que creas que son clínicamente relevantes: mantén Ctrl o Mayús para seleccionar varias; aquí no hay un atajo 'Seleccionar Todo', elígelas una por una.\n    Reglas prácticas:\n      • Incluye variables que estén disponibles ANTES de que se conozca el resultado.\n      • Excluye el ID del paciente, códigos administrativos y la columna de fecha.\n      • Excluye variables con > 50% de valores faltantes a menos que planees imputarlos.\n\nResultados secundarios (opcional):\n    Otros puntos finales clínicos que también quieres que el modelo aprenda a predecir junto al principal: esto entrena un modelo real multi-resultado, no es solo para tu referencia.\n    Ejemplo: resultado principal 'Mortalidad', con 'Duración_estancia' y 'Reingreso_30d' también marcados aquí: el modelo se entrena entonces para predecir los tres.\n    Una columna marcada tanto como predictora como resultado secundario se trata solo como predictora.",
    "help.section.4.block.2.text": "Aquí puedes definir reglas de inclusión y exclusión para filtrar el conjunto de datos antes del entrenamiento, usando el generador visual de reglas: elige una Columna, un Operador y un Valor para cada regla (no hay un cuadro de expresión de texto libre):\n    Edad    >=   18\n    Sexo    ==   Femenino\n\nAgrega tantas filas como necesites, por separado en Inclusión y Exclusión.  Haz clic en el botón 'Preview' de cada generador para ver cuántas filas coinciden y una muestra de ellas, antes de comprometerte al entrenamiento.\n\nSi un paciente NO cumple con todos los criterios de inclusión, se excluye.\nSi un paciente cumple con CUALQUIER criterio de exclusión, también se excluye.\n\n'Save preset' / 'Reset preset' guardan o borran estos criterios (y la variable de resultado) como un archivo JSON reutilizable para este proyecto, en training_schemas/.",
    "help.section.4.block.3.text": "Solo se muestran tres configuraciones aquí por defecto: el resto vive detrás del interruptor '▶ Opciones avanzadas' descrito justo abajo, ya que son más técnicas de ML de lo que un usuario no técnico necesita razonar día a día.\n\nNombre del modelo:\n  Un nombre corto para esta ejecución de entrenamiento: obligatorio.  Se convierte en el nombre de la carpeta donde se guarda el modelo entrenado, y es lo que verás después en el Historial de Entrenamiento del Modelo y en la página 'Modelos', así que elige algo que reconozcas (p.ej. 'Mortalidad_v1').\n\nTipo de predicción:\n  Clasificación binaria: el resultado tiene exactamente dos valores (Sí/No, 0/1).\n  Clasificación multiclase: el resultado tiene 3 o más categorías.\n  Regresión: el resultado es un número continuo (p.ej., pérdida de peso en kg).\n  Esto no es solo una sugerencia: fuerza a Ludwig a entrenar ese tipo de modelo, así que asegúrate de que realmente coincide con tu variable de resultado.\n\nMétrica de evaluación (cómo medir la calidad del modelo):\n  La lista de opciones cambia según el Tipo de predicción elegido arriba - Ludwig solo soporta ciertas métricas por tipo:\n  Binaria: AUC-ROC (más común en ámbitos clínicos), Exactitud, Precisión, Recuerdo, Especificidad.\n  Multiclase: Exactitud, Hits at K (¿está la categoría real entre las K mejores predicciones?).\n  Regresión: RMSE, MAE, MSE, RMSPE - todas miden el error promedio de predicción, cuanto más bajo, mejor.",
    "help.section.4.block.4.text": "Haz clic en '▶ Opciones avanzadas' en la tarjeta Configuración del Modelo para revelar el resto de los ajustes.  Los valores predeterminados son adecuados para la mayoría de los estudios.\n\nPresupuesto de tiempo (minutos):\n  Límite duro en el tiempo de búsqueda.  El entrenamiento se detiene cuando se alcanza esto incluso si no se han completado las iteraciones máximas.\n\nRetención de evaluación final (%):\n  Un porcentaje fijo de pacientes se aparta ANTES de que comience el entrenamiento y NUNCA se usa para entrenar: solo para la evaluación final del desempeño.  Predeterminado: 20%.\n\nSemilla Aleatoria:\n  Asegura que las divisiones y operaciones aleatorias produzcan el mismo resultado cada vez que reejecutas el entrenamiento.  Usa la misma semilla para reproducir un resultado exactamente.\n\nEstrategia de búsqueda (optimización de hiperparámetros):\n  Sin optimización: usa los valores predeterminados de Ludwig (más rápido, buen punto de partida).\n  Búsqueda aleatoria: intenta combinaciones aleatorias.  Rápido pero menos exhaustivo.\n  Optimización bayesiana: utiliza resultados de ensayos anteriores para elegir la siguiente configuración a probar.  Más eficiente.  Recomendado.\n  Grid Search (búsqueda exhaustiva): intenta TODAS las combinaciones.  Muy lento.  No recomendado para espacios grandes.\n\nMáx. iteraciones:\n  Número máximo de configuraciones diferentes a probar, una vez que se selecciona una estrategia de búsqueda distinta de 'Sin optimización'.  Más iteraciones → mejor modelo, más tiempo.  Recomendado: 50–100.\n\nEnsayos paralelos:\n  Número de núcleos de CPU a usar simultáneamente.  Aumenta para búsqueda más rápida; disminuye si la computadora se vuelve sin respuesta.\n\nParada temprana (rondas):\n  Cuántas rondas de evaluación consecutivas pueden pasar sin mejora antes de que el entrenamiento se detenga automáticamente.  Predeterminado: 5.  Ponlo en -1 para desactivarla y ejecutar siempre el presupuesto de tiempo/iteraciones completo.\n\nManejar Desbalance de Clases:\n  Interruptor: actívalo cuando una categoría de resultado es mucho más rara que la otra.  Solo disponible para Clasificación binaria - Ludwig no soporta esto para multiclase o regresión, así que el interruptor aparece desactivado (en gris) en esos casos.\n\nRellenar Valores Numéricos Faltantes con la Media:\n  Interruptor.  Desactivado (predeterminado): los valores numéricos faltantes se dejan para que Ludwig los maneje con su propio valor predeterminado, que los rellena con 0 en silencio.  Activado: los valores faltantes se rellenan con la media de esa columna en su lugar, antes del entrenamiento: normalmente un mejor valor predeterminado que 0 para una medición clínica.",
    "help.section.4.block.5.text": "1. Haz clic en 'Iniciar Entrenamiento'.  El botón solo está habilitado una vez que has cargado un conjunto de datos.\n2. La barra de progreso se actualiza mientras el entrenamiento procede.  No cierres la aplicación durante el entrenamiento.\n3. Los mensajes del registro de entrenamiento aparecen en tiempo real.\n4. Cuando termina, las 4 tarjetas destacadas del panel de Resultados se adaptan a lo que realmente entrenaste:\n     • Clasificación: AUC-ROC, Exactitud, Sensibilidad, Especificidad.\n     • Regresión: R², RMSE, MAE, Loss.\n   Cualquier otra métrica que reporte Ludwig aparece en una línea más pequeña justo debajo de las tarjetas.  También se muestran una matriz de confusión y una curva ROC para tareas de clasificación, cuando están disponibles.\n5. Haz clic en 'Detener' en cualquier momento para cancelar.  Se muestran resultados parciales hasta el último ensayo completado.",
    "help.section.4.block.6.text": "AUC-ROC (Área Bajo la Curva): tareas de clasificación:\n  0.5 = adivinanza aleatoria (modelo inútil).\n  0.7 = habilidad discriminativa aceptable.\n  0.8 = bueno.\n  0.9 = excelente (raro; verifica que no haya fuga de datos).\n  1.0 = perfecto (casi siempre indica una fuga de datos: verifica tus variables).\n\nR² (bondad de ajuste): tareas de regresión:\n  1.0 = ajuste perfecto.\n  0.7–0.9 = ajuste bueno a excelente.\n  0.5–0.7 = ajuste moderado.\n  0–0.5 = ajuste débil: el modelo apenas captura el patrón.\n  Menos de 0 = peor que simplemente predecir el promedio todo el tiempo: el modelo no está encontrando una relación real entre los predictores y este resultado.  Esto puede suceder; generalmente significa que la variable objetivo elegida no es realmente predecible a partir de los predictores elegidos, no que algo esté roto.\n\nRMSE / MAE (regresión):\n  Ambos miden el error promedio de predicción, en las mismas unidades que la variable de resultado: menor es mejor.  MAE es más fácil de interpretar directamente ('las predicciones se desvían X en promedio'); RMSE penaliza más los errores grandes.\n\nMatriz de confusión (clasificación):\n  Una tabla 2×2 (binaria) contando:\n    Verdaderos Positivos (VP) / Verdaderos Negativos (VN): predicciones correctas.\n    Falsos Positivos (FP): predicho positivo, realmente negativo.\n    Falsos Negativos (FN): predicho negativo, realmente positivo.\n  En ámbitos clínicos, FN (casos perdidos) suele ser más costoso que FP.\n\nEl recuadro verde debajo de los gráficos es un resumen de una línea generado automáticamente en lenguaje sencillo: siempre se adapta a cuál de los dos tipos de resultado estés viendo.",
    "help.section.4.block.7.text": "Haz clic en 'Exportar Modelo Entrenado' para guardar los artefactos del modelo en un archivo ZIP.\nEste archivo puede usarse para:\n  • Hacer predicciones en nuevos pacientes en el futuro.\n  • Compartir el modelo con colaboradores.\n  • Archivar el modelo para fines de auditoría / reproducibilidad.\n\nLos resultados del entrenamiento (métricas, gráficos) también se guardan automáticamente en la carpeta resultados/ del proyecto cada vez que se completa el entrenamiento.",

    # Help Page - Section 2: Project Block Texts (Spanish)
    "help.section.2.block.0.text": "Nombre del Proyecto *\n    El nombre oficial completo del estudio tal como aparece en el protocolo.\n    Ejemplo: 'Impacto de los Alimentos Ultraprocesados ​​en la Salud Metabólica'\n\nAcrónimo *\n    Un código corto en mayúsculas utilizado como nombre de carpeta para todos los archivos del proyecto.\n    Debe ser único y contener solo letras y números (sin espacios).\n    Ejemplo: 'UPS' o 'METAB2025'. No puede cambiar después de guardar.\n\nNúmero de Protocolo *\n    El identificador oficial asignado por tu institución o patrocinador.\n    Ejemplo: 'UPS-2024-001' o 'EudraCT 2024-000123-45'\n\nInvestigador Principal *\n    Nombre completo (y título) del investigador principal.\n\nEmail de Contacto *\n    Contacto principal para consultas sobre este estudio.\n\nInstitución *\n    Hospital, universidad o centro de investigación que realiza el estudio.\n\nTipo de Estudio\n    Selecciona la opción que mejor se ajuste:\n    • Registro de Pacientes: recopilación de datos continua sin intervención\n    • Estudio Observacional: prospectivo o retrospectivo, sin aleatorización\n    • Ensayo Clínico: intervención con asignación aleatorizada",

    "help.section.2.block.1.text": "Tamaño de Muestra Objetivo *\n    Número de pacientes que necesitas reclutar para lograr el poder estadístico del estudio.\n    Este valor se utiliza en la página Pronóstico para calcular la fecha de finalización estimada.\n    Si no estás seguro, consulta tu bioestadístico.\n\nFecha de Inicio\n    La fecha en que comenzó oficialmente el reclutamiento de pacientes.\n    Se utiliza en Pronóstico para calcular el tiempo transcurrido y la velocidad de reclutamiento.\n\nFecha de Finalización Esperada\n    La fecha en la que planeas completar el reclutamiento.\n    Se compara con la fecha de finalización estimada del modelo para evaluar el riesgo de retraso.",

    "help.section.2.block.2.text": "Una descripción de texto libre del objetivo principal del estudio, criterios de inclusión/exclusión, intervenciones y puntos finales.\n\nEste texto se incluye textualmente en los informes generados automáticamente, por lo que escribir una descripción clara y completa aquí te ahorrará tiempo más adelante.",

    "help.section.2.block.3.text": "• El Acrónimo no puede cambiar después de que el proyecto se guarde por primera vez. Elige con cuidado.\n• Todos los campos obligatorios (*) deben completarse para guardar. La aplicación resaltará los que falten.\n• Si abandonas el formulario sin guardar, tus cambios se pierden. Usa 'Guardar Proyecto' antes de navegar.\n• Puedes editar metadatos en cualquier momento abriendo la tarjeta del proyecto y haciendo clic en 'Abrir'.",

    # Help Page - Section 3: Data Block Texts (Spanish)
    "help.section.3.block.0.text": (
        "HAMELIN admite los siguientes formatos (compatibles con Ludwig):\n\n"
        "• CSV (.csv): texto plano, valores separados por comas o tabuladores.\n"
        "  ✔ Formato más común. Úsalo al exportar desde REDCap o Excel.\n"
        "• TSV (.tsv): valores separados por tabulaciones.\n"
        "• Excel (.xlsx): libro de Microsoft Excel (se usa la primera hoja).\n"
        "• Parquet (.parquet): formato columnar, útil para conjuntos de datos grandes.\n"
        "• JSON / JSONL (.json, .jsonl): datos estructurados; JSONL es un objeto por línea.\n"
        "• Feather (.feather): formato binario rápido para dataframes.\n"
        "• HDF5 (.h5, .hdf5): formato binario jerárquico para matrices grandes.\n"
        "• HTML (.html): tablas HTML de una sola tabla (soporte limitado).\n"
        "• SPSS (.sav): formato binario de IBM SPSS (preserva etiquetas).\n"
        "• Stata (.dta): archivo de datos Stata.\n"
        "• SAS (.xpt, .sas7bdat): conjuntos de datos SAS.\n"
        "• Formato de Ancho Fijo (.fwf): columnas alineadas por posición de carácter, sin delimitador.\n"
        "• DataFrame Serializado (.pkl, .pickle): un DataFrame de pandas guardado con pickle de Python — abre solo archivos de confianza.\n\n"
        "Requisitos:\n  • La primera fila debe contener encabezados de columna (nombres de variables).\n  • Una fila por paciente.\n  • Evita celdas combinadas o formato decorativo (Excel)."
    ),

    "help.section.3.block.1.text": "1. Ve a la pestaña Datos.\n2. Haz clic en 'Examinar' y selecciona tu archivo.\n3. Haz clic en 'Cargar'.\n\nCuando un proyecto está activo, el archivo se copia automáticamente en la carpeta datos/ del proyecto y se registra para que puedas recargarlo más tarde desde el selector 'Conjuntos de datos del proyecto': no necesitas examinar el archivo nuevamente.\n\nHAMELIN también detecta automáticamente los tipos de columna (numérico, fecha, texto...) y ejecuta un análisis de fondo con Ludwig AI para inferir el tipo más apropiado de aprendizaje automático para cada variable.",

    "help.section.3.block.2.text": "Después de cargar, la tabla Vista Previa de Datos muestra TODAS las filas y columnas del conjunto de datos.\n\nLos encabezados de columna muestran el nombre de la variable; puedes desplazarte horizontalmente para ver todas las variables.\n\nValores especiales que puedes encontrar:\n  NaN  : 'No es un Número'. Indica un valor faltante o desconocido en una columna numérica.\n  NaT  : 'No es una Hora'. Valor faltante en una columna de fecha/hora.\n  (celda vacía): lo mismo que NaN/NaT en la mayoría de contextos.\n  inf  : Infinito. Un desbordamiento numérico: trata como un problema de calidad de datos.\n\nPuedes seleccionar columnas haciendo clic en el encabezado de columna (resaltado en azul) y luego hacer clic en 'Eliminar Seleccionados' para ocultarlas del análisis. NO se eliminan permanentemente: usa 'Restaurar Todo' para recuperarlas.",

    "help.section.3.block.3.text": "Modo de selección:\n  • Haz clic en un encabezado de columna → entra en modo 'selección de columna'.\n  • Haz clic en un número de fila → entra en modo 'selección de fila'.\n  • Mantén presionado Ctrl o Mayús para seleccionar múltiples elementos.\n\nEliminación:\n  Haz clic en 'Eliminar Seleccionados'. Los elementos eliminados se ocultan de la vista previa y de todos los análisis (Tabla 1, Entrenamiento) hasta que se restauren.\n\nRestauración:\n  Haz clic en 'Restaurar Todo' para recuperar todas las columnas y filas eliminadas previamente.\n\nExportación:\n  Elige un formato en el desplegable junto al botón 'Exportar Datos Limpios': CSV, Excel (.xlsx) o Word (.docx): y luego haz clic en él.  Guarda el conjunto de datos dejando fuera cualquier columna o fila que hayas eliminado.",

    "help.section.3.block.4.text": "La Lista de Variables muestra cada columna con su tipo de dato inferido.\n\nMientras HAMELIN ejecuta el análisis se muestra una barra de progreso. Esto puede tomar hasta 30 segundos en grandes conjuntos de datos.\n\nIconos de tipo:\n  🔢 número   : valor numérico continuo o discreto (edad, IMC, resultado de lab)\n  ⭕ binario   : exactamente dos valores (Sí/No, 0/1, Masculino/Femenino)\n  📝 categoría : un pequeño número de categorías discretas (diagnóstico, grupo de tratamiento)\n  📅 fecha     : fecha de calendario o datetime\n  📄 texto     : texto libre (notas, comentarios): generalmente excluido de modelos\n  📈 secuencia : secuencia ordenada de valores\n  ⏱ serie temporal: valores medidos a lo largo del tiempo\n  ➡ vector   : característica numérica multidimensional\n\nEl tipo determina qué pruebas estadísticas y características de modelo utiliza HAMELIN. Si un tipo es incorrecto, generalmente es porque la columna contiene valores inesperados; comprueba la Vista Previa de Datos para detectar inconsistencias de codificación.\n\nPuedes anular el tipo de cualquier columna tú mismo usando el desplegable 'Set type' junto a ella: la fila se resalta para mostrar que es una anulación manual.  ¿Cambiaste de opinión sobre varias de ellas?  Haz clic en 'Restablecer Tipos Inferidos' (justo debajo de la tabla) para revertir cada columna a lo que Ludwig infirió originalmente: esto solo afecta las anulaciones de tipo, nunca cambia los valores reales del conjunto de datos.",

    "help.section.3.block.5.text": "Haz clic en 'Generar Informe de Calidad' para guardar un archivo CSV con una fila por variable, listando: tipo, conteo de no nulos, conteo y porcentaje de faltantes, número de valores únicos, y: para columnas numéricas: mínimo, máximo y media.\n\nTú eliges dónde guardarlo (nombre de archivo predeterminado: quality_report.csv); no se escribe automáticamente en la carpeta del proyecto y no se abre por sí solo: ábrelo después en Excel o cualquier programa de hojas de cálculo.\n\nPara una revisión visual rápida en su lugar, consulta 'Resumen de Datos y gráfico de valores faltantes' más abajo.",

    "help.section.3.block.6.text": "Problema: 'Error de carga: error de codificación'\n  → Abre el CSV en un editor de texto y guárdalo como UTF-8.\n\nProblema: Columna de fecha mostrada como tipo 'texto'\n  → Asegúrate de que todas las fechas usen el mismo formato (DD/MM/YYYY o YYYY-MM-DD). Los formatos mixtos previenen la detección automática.\n\nProblema: Una columna numérica aparece como 'categoría'\n  → Puede haber caracteres no numéricos en algunas celdas (p.ej., '12 mg', '>100'). Abre el archivo y limpia esas celdas.\n\nProblema: Filas vacías al final del archivo\n  → HAMELIN filtra automáticamente las filas completamente vacías. Si el recuento de filas parece muy bajo, comprueba si hay filas con solo pocos valores.",

    "help.section.3.block.7.text": "Una vez cargado un conjunto de datos, HAMELIN también construye dos cosas automáticamente, justo debajo de los botones Exportar / Restablecer Tipos / Generar Informe de Calidad:\n\n• Un gráfico de las variables con más datos faltantes (top 10), para que puedas detectar columnas problemáticas de un vistazo sin abrir el Informe de Calidad.\n• Una tarjeta 'Resumen de Datos': una descripción en texto plano del conjunto de datos cargado que puedes leer directamente en la página.  Haz clic en 'Export Data Summary' para guardar ese texto en un archivo .txt o .md, p.ej. para pegarlo en un correo o una sección de métodos.\n\nAmbos se actualizan automáticamente cada vez que cargas un conjunto de datos diferente.",

    "help.section.3.block.8.text": "Tabla 1 es la tabla estándar al inicio de un documento de investigación clínica.  Describe las características demográficas y clínicas de la población estudiada: generalmente elementos como edad, sexo, comorbilidades, valores de laboratorio: para que los lectores puedan evaluar cuán representativa es la muestra.  Vive al final de esta pestaña Datos y se construye a partir de lo que ya esté cargado arriba: no tiene un botón 'Examinar' propio.\n\nHAMELIN la genera automáticamente, utilizando la prueba estadística correcta para cada tipo de variable:\n  • Numérico → media ± DE y mediana (RIC).\n  • Categórico / binario → conteo (n) y porcentaje (%).\n\nPaso a paso:\n  1. Desplázate hasta la tarjeta 'Select Variables for Table 1', más abajo en esta misma pestaña.  Cada columna aparece listada y marcada por defecto.\n  2. Las columnas que HAMELIN cree que probablemente deberían excluirse (identificadores, texto libre, columnas sin varianza…) o que parecen una buena variable de agrupación se marcan directamente en su propia fila, así que no hay una lista separada que consultar.\n  3. Haz clic en 'Apply All Recommendations' para actuar sobre esas marcas automáticamente, o marca/desmarca variables tú mismo.\n  4. En 'Table Settings', configura las opciones descritas en el siguiente bloque, luego haz clic en 'Generar Tabla 1'.\n  5. Revisa la tabla en el panel de vista previa y luego expórtala: ver abajo.",

    "help.section.3.block.9.text": "Variable de Agrupación (opcional):\n  Una columna categórica usada para dividir la tabla en grupos y ejecutar una prueba estadística entre grupos: las variables numéricas reciben una prueba t (2 grupos) o ANOVA (3+ grupos); las variables categóricas reciben una prueba de chi-cuadrado o una prueba exacta de Fisher.  Una elección común en ensayos aleatorizados es la asignación de tratamiento; en estudios observacionales suele ser 'Casos vs Controles' o una categoría de diagnóstico.\n\nDatos faltantes:\n  Elige si las filas con valores faltantes se mantienen (mostradas como faltantes en la tabla) o se descartan por completo antes de construir la tabla.\n\nMostrar p-values:\n  Solo aplica cuando se selecciona una variable de agrupación; desmárcalo para ocultar la columna de valor p, p.ej. para una Tabla 1 puramente descriptiva.\n\nSeleccionando variables:\n  • 'Select All' / 'Deselect All': marca o desmarca todo a la vez.\n  • Marcas individuales: elige por variable.\n  • 'Apply All Recommendations': desmarca cada variable marcada con '(recommendation: exclude: reason)' y preselecciona la variable de agrupación sugerida, si se encontró alguna.\n\nConsejo: excluye columnas de ID de paciente, notas de texto libre y cualquier columna con > 50% de valores faltantes antes de generar la tabla: esto es exactamente lo que las recomendaciones te están señalando.",

    "help.section.3.block.10.text": "Variables continuas:\n  Media ± DE: se muestra cuando la distribución es aproximadamente normal.\n  Mediana (RIC): se muestra cuando la distribución está sesgada.\n\nVariables categóricas:\n  n (%): conteo y porcentaje de pacientes en cada categoría.\n\nColumna de valor p (cuando se usa una variable de agrupación y 'Show p-values' está marcado):\n  < 0.05  → los grupos difieren significativamente en esta variable.\n  ≥ 0.05  → no se detectó diferencia estadística significativa.\n\nColumna Faltante:\n  Muestra el número/% de pacientes con valores faltantes para cada variable (más relevante cuando los datos faltantes se mantienen en lugar de descartarse).\n\nExportación:\n  Elige CSV, Excel (.xlsx) o Word (.docx) en el desplegable de formato junto al botón Exportar, luego haz clic en Exportar.\n  CSV: una tabla de texto plano que puedes abrir en Excel para formato adicional; los números mantienen precisión completa.\n  Excel (.xlsx): un libro listo para usar.\n  Word (.docx): una tabla estilizada que puedes colocar directamente en un manuscrito o enviar a tu estadístico.",

    # Help Page - Section 4: Forecasting Block Texts (Spanish)
    "help.section.6.block.0.text": "Dado cómo se han inscrito los pacientes hasta ahora, HAMELIN ajusta un modelo estadístico para estimar la fecha en que alcanzarás tu Tamaño de Muestra Objetivo.\n\nTambién muestra:\n  • La velocidad de reclutamiento actual (pacientes por mes).\n  • Un intervalo de confianza: un rango de fechas dentro del cual es probable que se alcance el objetivo (predeterminado: confianza del 95%).\n  • Una tabla de hitos mensuales (cuántos pacientes habrás inscrito en cada mes futuro).\n  • Un gráfico que muestra el reclutamiento histórico (línea sólida) y el pronóstico (línea punteada con banda de confianza).",

    "help.section.6.block.1.text": "1. Un conjunto de datos cargado con una columna de fecha que registra fechas de inscripción (una fila por paciente, una celda por fecha de inscripción).\n2. Un Tamaño de Muestra Objetivo (rellenado previamente desde los metadatos del proyecto).\n\nLa columna de fecha de inscripción es cualquier columna donde cada valor es la fecha en que se incluyó al paciente correspondiente en el estudio. En REDCap esto a menudo se llama 'fecha_inscripción' o 'fecha_inclusión'.",

    "help.section.6.block.2.text": "Columna de Fecha de Inscripción\n    Selecciona la columna que contiene la fecha en que se inscribió cada paciente.\n    Solo se muestran aquí las columnas de tipo fecha.\n\nTamaño de Muestra Objetivo\n    El número total de pacientes que necesitas reclutar.\n    Prellenado desde los metadatos del Proyecto. Puedes anularlo aquí.\n\nPeríodo Histórico (días)\n    Cuántos días de datos pasados usar para estimar la velocidad de reclutamiento.\n    Predeterminado: 90 días. Aumenta para estimaciones más estables; disminuye para mayor sensibilidad a tendencias recientes.\n\nNivel de Confianza\n    Confianza estadística para el intervalo de fecha estimado.\n    0.95 = intervalo de confianza del 95%. Un intervalo más estrecho (0.80) es más optimista; uno más amplio (0.99) es más conservador.",

    "help.section.6.block.3.text": "Línea de color sólido: inscripción acumulada real (datos históricos).\nLínea punteada: inscripción proyectada basada en regresión ajustada.\nBanda sombreada: intervalo de confianza para la proyección.\nLínea punteada horizontal: tamaño de muestra objetivo.\nLínea punteada vertical: fecha estimada en que se alcanzará el objetivo.\n\nSi la banda sombreada es muy ancha, tu reclutamiento ha sido irregular (p.ej., períodos de actividad alta y baja). Considera revisar si un sitio acaba de abrir o cerrar.",

    "help.section.6.block.4.text": "Este panel se actualiza automáticamente después de ejecutar el pronóstico.\n\nReclutados Actualmente: pacientes extraídos de la columna de fecha (filas con una fecha válida).\nTamaño de Muestra Objetivo: según está configurado en los parámetros.\nRestante: cuántos pacientes más aún necesitas.\nTasa Promedio: pacientes inscritos promedio por mes durante todo el período del estudio.\nFecha de Inicio del Estudio: fecha de la primera inscripción encontrada en el conjunto de datos.",

    "help.section.6.block.5.text": "Haz clic en 'Exportar Línea de Tiempo CSV' para guardar la tabla de hitos mensuales como un archivo CSV.\nCada fila muestra: Mes, Inscritos esperados, Límite inferior, Límite superior.\nEsta tabla es útil para informes de progreso y actualizaciones para patrocinadores.",

    # Help Page - Section 6: Settings Block Texts (Spanish)





    # Help Page - Section 7: Glossary Block Texts (Spanish)
    "help.section.7.block.0.text": "PIC: Profesional de Investigación Clínica. Cualquier persona capacitada involucrada en la realización de investigación clínica (coordinador, enfermero, monitor, etc.).\n\nEDC: Captura de Datos Electrónica. Software utilizado para ingresar y gestionar datos de ensayos clínicos (p.ej., REDCap, OpenClinica, Medidata Rave).\n\nInscrip ción / Reclutamiento: el proceso de identificar, obtener consentimiento e incluir a un paciente en un estudio clínico.\n\nAprobación Ética: permiso formal de una Junta de Revisión Institucional (IRB) o Comité de Ética (EC) para realizar un estudio que involucre participantes humanos.\n\nCriterios de Inclusión / Exclusión: condiciones que un paciente debe cumplir (inclusión) o no tener (exclusión) para ser elegible para un estudio.\n\nInvestigador Principal (IP): el investigador principal responsable de la conducción general del estudio.\n\nNúmero de Protocolo: un código alfanumérico único asignado al estudio, utilizado en todas las comunicaciones regulatorias y administrativas.\n\nTamaño de Muestra: el número de pacientes requerido para dar al estudio suficiente poder estadístico para detectar el efecto de interés.\n\nTabla 1: la tabla de características demográficas en un documento de investigación clínica que describe la población estudiada.\n\nTamaño de Muestra Objetivo: el número mínimo de pacientes requerido; determinado por un cálculo de potencia.",

    "help.section.7.block.1.text": "Algoritmo: un procedimiento matemático que aprende patrones de datos.\n\nAUC-ROC (Área Bajo la Curva de Características Operativas del Receptor): una métrica entre 0 y 1 que mide qué tan bien un clasificador binario separa casos positivos de negativos. AUC = 0.5 es aleatorio; AUC = 1.0 es perfecto.\n\nAutoML: Aprendizaje Automático Automatizado. Software que selecciona y configura automáticamente el mejor algoritmo para un conjunto de datos dado.\n\nClasificación Binaria: una tarea donde el resultado tiene exactamente dos valores posibles (p.ej., enfermo / saludable, respondedor / no respondedor).\n\nMatriz de Confusión: una tabla que muestra predicciones Correctas e incorrectas desglosadas por Verdadero/Falso Positivo/Negativo.\n\nValidación Cruzada: una técnica que divide el conjunto de datos en folds para estimar el desempeño del modelo de manera más confiable que una única división tren/prueba.\n\nFuga de Datos: cuando información del futuro o de la variable de resultado accidentalmente entra en los datos de entrenamiento, causando un desempeño irrealistamente alto.\n\nPuntuación F1: la media armónica de Precisión y Recall. Útil cuando las clases están desequilibradas.\n\nCaracterística: una variable predictora utilizada como entrada al modelo.\n\nImportancia de Características: una medida de cuánto cada predictor contribuyó a las decisiones del modelo.\n\nConjunto de Retención: una porción de datos mantenida completamente separada del entrenamiento y utilizada solo para la evaluación final del desempeño.\n\nHiperparámetro: una configuración que controla cómo aprende el algoritmo (p.ej., tasa de aprendizaje, número de árboles). Distinto de los parámetros del modelo, que se aprenden de los datos.\n\nOptimización de Hiperparámetros (HPO): búsqueda automática de la mejor combinación de hiperparámetros.\n\nLudwig: un marco AutoML de código abierto de Uber AI utilizado por HAMELIN para entrenamiento de modelos e inferencia de tipos de variables.\n\nClasificación Multiclase: una tarea donde el resultado tiene tres o más categorías.\n\nNaN (No es un Número): valor numérico faltante o indefinido en un conjunto de datos.\n\nNaT (No es una Hora): valor faltante en una columna de fecha/hora.\n\nSobreajuste: cuando un modelo aprende demasiado bien los datos de entrenamiento y no generaliza a nuevos pacientes.\n\nPrecisión: de todos los pacientes que el modelo predijo como positivos, ¿qué fracción realmente eran positivos?\n\nSemilla Aleatoria: un número que inicializa el generador de números aleatorios, asegurando que las divisiones aleatorias e inicializaciones sean reproducibles.\n\nRecall (Sensibilidad): de todos los pacientes verdaderamente positivos, ¿qué fracción identificó correctamente el modelo?\n\nRegresión: una tarea donde el resultado es un valor numérico continuo.\n\nDesviación Estándar (DE): una medida de cuán dispersos están los valores alrededor de la media.\n\nDivisión Tren / Prueba: división del conjunto de datos en un conjunto de entrenamiento (utilizado para construir el modelo) y un conjunto de prueba (utilizado para evaluarlo).",

    "help.section.7.block.2.text": "CSV (.csv): Valores Separados por Comas. Archivo de texto plano donde cada fila es una observación y las columnas están separadas por comas.\n\nStata (.dta): Formato binario propietario de Stata para conjuntos de datos estadísticos.\n\nSPSS (.sav): Formato binario de IBM SPSS Statistics. Preserva etiquetas de variables y valores.\n\nXLSX (.xlsx): Formato Open XML de Microsoft Excel. Soporta múltiples hojas; HAMELIN lee solo la primera hoja.\n\nHTML (.html): Lenguaje de Marcado de Hipertexto. Utilizado para exportaciones de Tabla 1 y Informe de Calidad formateadas.\n\nJSON (.json): Notación de Objetos JavaScript. Utilizado internamente por HAMELIN para metadatos del proyecto y registro de conjuntos de datos.",


    "help.section.5.title": "6 · Modelos",
    "help.section.5.summary": "Compara e inspecciona todos los modelos entrenados en este proyecto.",
    "help.section.5.block.0.heading": "¿Qué es la página Modelos?",
    "help.section.5.block.0.text": "El elemento 'Models' en la barra de navegación (entre Entrenamiento y Pronóstico) abre una vista dedicada a todo lo que has entrenado en este proyecto hasta ahora, no solo la ejecución más reciente. Es una página normal de la barra de navegación, no una ventana aparte — salir de ella es simplemente hacer clic en cualquier otro elemento del menú. Abre primero un proyecto: esta página necesita uno para saber dónde buscar los modelos entrenados.",
    "help.section.5.block.1.heading": "Qué puedes hacer aquí",
    "help.section.5.block.1.text": "• Comparar varios modelos entrenados lado a lado según la métrica que elijas.\n• Inspeccionar un modelo en profundidad (matriz de confusión, curva ROC, hiperparámetros usados).\n• Duplicar un modelo con ligeros cambios para probar una variación sin empezar de cero — esto precarga la página Entrenamiento con esa configuración y te lleva allí; nada se guarda hasta que realmente inicies el entrenamiento.\n• Marcar favoritos y eliminar modelos que ya no necesites.",
}