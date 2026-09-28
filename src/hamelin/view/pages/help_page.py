"""
Help & User Manual Page
~~~~~~~~~~~~~~~~~~~~~~~

Full in-app reference manual for HAMELIN.

Sections
--------
  1. Introduction — what is HAMELIN and the clinical research workflow
  2. Getting Started — first steps, creating a project
  3. Projects (Metadata) — every field explained
  4. Data — loading files, supported formats, variable types, quality report,
     and Table 1 (baseline characteristics), which lives at the bottom of
     this same page rather than as its own tab or its own Help section
  5. Training — outcome, predictors, model types, metrics, hyperopt
  6. Models — comparing and inspecting every trained model, own section
     kept right after Training to match the nav bar's own ordering
  7. Forecasting — date column, parameters, reading the chart
  8. Glossary — technical and clinical terms

  Settings and Dashboard aren't documented here on purpose: Settings is
  self-explanatory on screen (toggles/dropdowns, nothing to explain), and
  Dashboard isn't linked from the nav sidebar, so there's nothing a user
  can actually do with it right now (see main_window.py's
  _init_navigation).

Design principles
-----------------
- Every section is a collapsible card so the page is not overwhelming.
- Text is written for a Clinical Research Professional who is NOT a data
  scientist.  Technical terms are explained in plain language on first use.
- Icons from FluentIcon keep the page visually consistent with the rest
  of the application.

Author: GitHub Copilot
Sprint: 4, Day 36
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QFont, QPixmap
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, StrongBodyLabel, BodyLabel, CaptionLabel,
    CardWidget, PushButton, FluentIcon, IconWidget,
    TransparentToolButton,
)

from hamelin.utils.logger import log
from hamelin.utils.usage_logger import usage_log
from hamelin.view.widgets.theme_colors import apply_scroll_area_theme, bind_style
from hamelin.i18n import t

# Real app screenshots referenced by a few blocks below (see the "image"
# key on individual block dicts) - same resources/ location as the logo,
# see home_page.py's own _logo_path for the matching path computation.
_HELP_IMAGES_DIR = Path(__file__).resolve().parent.parent.parent / "resources" / "help_images"


# Section content — strings are intentionally long; they ARE the manual.
# ──────────────────────────────────────────────────────────────────────────────

_SECTIONS: list[dict] = [
    # ── 1. Introduction ────────────────────────────────────────────────────────
    {
        "icon": FluentIcon.HOME,
        "title": "1 · Introduction",
        "summary": "What is HAMELIN and who is it for?",
        "blocks": [
            {
                "heading": "What is HAMELIN?",
                "text": (
                    "HAMELIN (Human-guided Automated Machine Learning for Clinical Studies) "
                    "is a desktop application designed for Clinical Research Professionals (CRPs) "
                    "who need to manage clinical studies, analyse patient data, and build predictive "
                    "models — without requiring programming skills or knowledge of Machine Learning.\n\n"
                    "The application was built following the HGML-2025 methodology, a set of validated "
                    "best practices for applying Artificial Intelligence in clinical settings."
                ),
            },
            {
                "heading": "Who is HAMELIN for?",
                "text": (
                    "• Principal Investigators (PIs) who need to monitor recruitment and forecast "
                    "when a study will reach its target.\n"
                    "• Data Managers who prepare and clean datasets for analysis.\n"
                    "• Biostatisticians who generate descriptive tables (Table 1) and predictive models.\n"
                    "• Research Nurses and Coordinators who need a simple interface to check study status."
                ),
            },
            {
                "heading": "Typical workflow",
                "text": (
                    "The recommended order of steps is:\n\n"
                    "  1. PROJECT — create or open a project and fill in the study metadata.\n"
                    "  2. DATA — load the patient dataset (CSV, Excel or SPSS). "
                    "Table 1 (baseline characteristics) is generated right there too, "
                    "as the last section of the Data tab — it is no longer a separate tab.\n"
                    "  3. TRAINING — train an AutoML predictive model.\n"
                    "  4. MODELS — a dedicated page (right after Training in the nav bar) "
                    "to inspect and compare every model you've trained in this project.\n\n"
                    "FORECASTING is optional — it predicts when you will reach your "
                    "enrollment target and sits in the nav bar right after Models; use it "
                    "if that is relevant to your study, it is not part of the core flow above.\n\n"
                    "Each step is a tab in the left navigation bar (Help and Settings are "
                    "pinned at the bottom; everything else, including Models and "
                    "Forecasting, is in the main list).  You can go back and forward at "
                    "any time."
                ),
                "image": "home_page.png",
            },
            {
                "heading": "What does HAMELIN NOT do?",
                "text": (
                    "• It does not replace a statistician or a data scientist for complex analyses.\n"
                    "• It does not manage patient consent or regulatory documentation.\n"
                    "• It is not a clinical data management system (CDMS) — use it alongside your "
                    "existing EDC (REDCap, OpenClinica, etc.).\n"
                    "• It does not send data to any cloud service; everything runs locally on your computer."
                ),
            },
        ],
    },

    # ── 2. Getting Started ─────────────────────────────────────────────────────
    {
        "icon": FluentIcon.PLAY,
        "title": "2 · Getting Started",
        "summary": "Installation, first launch, and creating your first project.",
        "blocks": [
            {
                "heading": "System requirements",
                "text": (
                    "• Operating system: Windows 10/11 (64-bit), macOS 12+, or Ubuntu 20.04+.\n"
                    "• Python 3.10 or newer (already bundled if you received the installer).\n"
                    "• RAM: 8 GB minimum; 16 GB recommended for large datasets (> 10 000 rows).\n"
                    "• Disk: 500 MB free for the application + space for your datasets."
                ),
            },
            {
                "heading": "First launch",
                "text": (
                    "Run the application from the terminal:\n\n"
                    "    cd hamelin/\n"
                    "    uv run hamelin\n\n"
                    "On first launch the Home page is displayed with zero projects. "
                    "No configuration is required."
                ),
            },
            {
                "heading": "Creating your first project",
                "text": (
                    "1. Click 'Project' in the left navigation bar.\n"
                    "2. Click the 'New Project' button.\n"
                    "3. Fill in at least the required fields (marked with *): "
                    "Project Name, Acronym, Protocol Number, Principal Investigator, "
                    "Contact Email, and Institution.\n"
                    "4. Click 'Save Project'.\n\n"
                    "A folder named after your acronym will be created inside the Projects/ directory. "
                    "All files related to this project will be saved there automatically."
                ),
                "image": "project_page.png",
            },
            {
                "heading": "Opening an existing project",
                "text": (
                    "1. Click 'Project' in the navigation bar.\n"
                    "2. The project list shows all previously saved projects with their details.\n"
                    "3. Click 'Open' on the project card you want to work on.\n\n"
                    "The project is loaded into all pages simultaneously — the Data, Training "
                    "and Forecasting pages are all updated with the project context."
                ),
            },
            {
                "heading": "Where are my files?",
                "text": (
                    "All project data is stored locally in:\n\n"
                    "    workspace/Projects/<ACRONYM>/  (inside the hamelin repo)\n"
                    "        metadata.json     — project metadata\n"
                    "        data/             — datasets linked to this project\n"
                    "        data/dataset_index.json  — registry of datasets\n"
                    "        results/          — training results and exports\n\n"
                    "You can back up the entire Projects/ folder to any location."
                ),
            },
        ],
    },

    # ── 3. Projects ────────────────────────────────────────────────────────────
    {
        "icon": FluentIcon.FOLDER,
        "title": "3 · Projects",
        "summary": "Every metadata field explained — what to fill in and why it matters.",
        "blocks": [
            {
                "heading": "Basic Information",
                "text": (
                    "Project Name *\n"
                    "    The full official name of the study as it appears in the protocol.\n"
                    "    Example: 'Impact of Ultra-Processed Foods on Metabolic Health'\n\n"
                    "Acronym *\n"
                    "    A short uppercase code used as the folder name for all project files.\n"
                    "    Must be unique and contain only letters and numbers (no spaces).\n"
                    "    Example: 'UPS' or 'METAB2025'.  Cannot be changed after saving.\n\n"
                    "Protocol Number *\n"
                    "    The official identifier assigned by your institution or sponsor.\n"
                    "    Example: 'UPS-2024-001' or 'EudraCT 2024-000123-45'\n\n"
                    "Principal Investigator *\n"
                    "    Full name (and title) of the lead researcher.\n\n"
                    "Contact Email *\n"
                    "    Primary contact for queries about this study.\n\n"
                    "Institution *\n"
                    "    Hospital, university, or research centre running the study.\n\n"
                    "Study Type\n"
                    "    Select the closest match:\n"
                    "    • Patient Registry — ongoing data collection without intervention\n"
                    "    • Observational Study — prospective or retrospective, no randomisation\n"
                    "    • Clinical Trial — intervention with randomised allocation"
                ),
            },
            {
                "heading": "Recruitment Information",
                "text": (
                    "Target Sample Size *\n"
                    "    Number of patients you need to enroll to achieve the study's statistical power.\n"
                    "    This value is used by the Forecasting page to calculate the estimated end date.\n"
                    "    If you are unsure, consult your biostatistician.\n\n"
                    "Start Date\n"
                    "    The date when patient enrollment officially started.\n"
                    "    Used in Forecasting to compute elapsed time and recruitment velocity.\n\n"
                    "Expected End Date\n"
                    "    The date by which you plan to complete enrollment.\n"
                    "    Compared against the model's estimated end date to assess delay risk."
                ),
            },
            {
                "heading": "Study Description",
                "text": (
                    "A free-text description of the study's primary objective, "
                    "inclusion/exclusion criteria, interventions, and endpoints.\n\n"
                    "This text is included verbatim in automatically generated reports, "
                    "so writing a clear, complete description here will save time later."
                ),
            },
            {
                "heading": "Tips and common mistakes",
                "text": (
                    "• The Acronym cannot be changed after the project is saved for the first time. "
                    "Choose it carefully.\n"
                    "• All required fields (*) must be filled to save.  "
                    "The application will highlight the missing ones.\n"
                    "• If you leave the form without saving, your changes are lost.  "
                    "Use 'Save Project' before navigating away.\n"
                    "• You can edit metadata at any time by opening the project card and clicking 'Open'."
                ),
            },
        ],
    },

    # ── 4. Data ────────────────────────────────────────────────────────────────
    {
        "icon": FluentIcon.FOLDER_ADD,
        "title": "4 · Data",
        "summary": "Loading files, variable types, data quality, and the dataset registry.",
        "blocks": [
            {
                "heading": "Supported file formats",
                "text": (
                    "HAMELIN supports the following formats (readable by Ludwig):\n\n"
                    "• CSV (.csv) — plain text, values separated by commas or semicolons.\n"
                    "  ✔ Most common format.  Use this when exporting from REDCap or Excel.\n"
                    "• TSV (.tsv) — tab-separated values.\n"
                    "• Excel (.xlsx) — Microsoft Excel workbook (first sheet is used).\n"
                    "• Parquet (.parquet) — columnar storage, useful for large datasets.\n"
                    "• JSON / JSONL (.json, .jsonl) — structured data, JSON Lines for one-object-per-line.\n"
                    "• Feather (.feather) — fast binary dataframe format.\n"
                    "• HDF5 (.h5, .hdf5) — hierarchical binary format for large arrays.\n"
                    "• HTML (.html) — single-table HTML files (limited support).\n"
                    "• SPSS (.sav) — IBM SPSS Statistics native format.\n"
                    "  ✔ Variable labels and value labels are preserved.\n"
                    "• Stata (.dta) — Stata data file.\n"
                    "• SAS (.xpt, .sas7bdat) — SAS datasets.\n"
                    "• Fixed Width Format (.fwf) — columns aligned by character position, no delimiter.\n"
                    "• Pickled DataFrame (.pkl, .pickle) — a pandas DataFrame saved with Python's pickle "
                    "— only open files you trust.\n\n"
                    "Requirements:\n"
                    "  — First row must contain column headers (variable names).\n"
                    "  — One row per patient.\n"
                    "  — Avoid merged cells or decorative formatting (Excel)."
                ),
            },
            {
                "heading": "Loading a dataset",
                "text": (
                    "1. Go to the Data tab.\n"
                    "2. Click 'Browse' and select your file.\n"
                    "3. Click 'Load'.\n\n"
                    "When a project is active, the file is automatically copied into the project's "
                    "data/ folder and registered so you can reload it later from the 'Project datasets' "
                    "selector — no need to browse for the file again.\n\n"
                    "HAMELIN also auto-detects column types (numeric, date, text…) "
                    "and runs a background analysis with Ludwig AI to infer the most appropriate "
                    "machine-learning type for each variable."
                ),
                "image": "data_page.png",
            },
            {
                "heading": "Data Preview",
                "text": (
                    "After loading, the Data Preview table shows ALL rows and columns of the dataset.\n\n"
                    "Column headers show the variable name; you can scroll horizontally to see all variables.\n\n"
                    "Special values you may encounter:\n"
                    "  NaN   — 'Not a Number'.  Indicates a missing or unknown value in a numeric column.\n"
                    "  NaT   — 'Not a Time'.  Missing value in a date/time column.\n"
                    "  (empty cell) — same as NaN/NaT in most contexts.\n"
                    "  inf   — Infinity.  A numeric overflow — treat as a data quality problem.\n\n"
                    "You can select columns by clicking the column header (highlighted in blue) and "
                    "then click 'Remove Selected' to hide them from the analysis. "
                    "They are NOT permanently deleted — use 'Restore All' to bring them back."
                ),
            },
            {
                "heading": "Removing and restoring columns/rows",
                "text": (
                    "Select mode:\n"
                    "  • Click a column header → enters 'column selection' mode.\n"
                    "  • Click a row number   → enters 'row selection' mode.\n"
                    "  • Hold Ctrl or Shift to select multiple items.\n\n"
                    "Removing:\n"
                    "  Click 'Remove Selected'.  Removed items are hidden from the preview "
                    "and from all analyses (Table 1, Training) until restored.\n\n"
                    "Restoring:\n"
                    "  Click 'Restore All' to bring back all previously removed columns and rows.\n\n"
                    "Excluding outliers (just below Remove/Restore, same table):\n"
                    "  'Exclude Outliers' automatically hides any row where a numeric value is "
                    "more than 3 standard deviations from that column's mean.  Excluded rows are "
                    "hidden from training and Table 1 but never deleted from the file — "
                    "click 'Restore Excluded' to bring them all back.\n\n"
                    "Exporting:\n"
                    "  Pick a format from the dropdown next to the 'Export Cleaned Data' "
                    "button — CSV, Excel (.xlsx), or Word (.docx) — then click it.  It "
                    "saves the dataset with any columns or rows you've removed left out."
                ),
            },
            {
                "heading": "Variable List and Ludwig type inference",
                "text": (
                    "The Variable List shows every column with its inferred data type.\n\n"
                    "While HAMELIN runs the analysis a progress bar is shown. "
                    "This can take up to 30 seconds on large datasets.\n\n"
                    "Type icons:\n"
                    "  🔢 number    — continuous or discrete numeric value (age, BMI, lab result)\n"
                    "  ⭕ binary    — exactly two values (Yes/No, 0/1, Male/Female)\n"
                    "  📝 category  — a small number of discrete categories (diagnosis, treatment group)\n"
                    "  📅 date      — calendar date or datetime\n"
                    "  📄 text      — free-text (notes, comments)  — usually excluded from models\n"
                    "  📈 sequence  — ordered sequence of values\n"
                    "  ⏱ timeseries — values measured over time\n"
                    "  ➡ vector    — multi-dimensional numeric feature\n\n"
                    "The type determines which statistical tests and model features HAMELIN uses. "
                    "If a type is wrong, it is usually because the column contains unexpected values; "
                    "check the Data Preview for encoding inconsistencies.\n\n"
                    "You can override any column's type yourself using the 'Set type' dropdown "
                    "next to it — the row highlights to show it's a manual override.  Changed your "
                    "mind about several of them?  Click 'Reset Types to Inferred' (just below the "
                    "table) to revert every column back to what Ludwig originally inferred — this "
                    "only touches type overrides, it never changes the dataset's actual values."
                ),
            },
            {
                "heading": "Quality Report",
                "text": (
                    "Click 'Generate Quality Report' to save a CSV file with one row per "
                    "variable, listing: type, non-null count, missing count and missing %, "
                    "number of unique values, and — for numeric columns — min, max, and mean.\n\n"
                    "You choose where to save it (default filename: quality_report.csv); it "
                    "is not written automatically into the project folder and does not open "
                    "on its own — open it afterwards in Excel or any spreadsheet programme.\n\n"
                    "For a quick visual check instead, see 'Data Summary and missingness "
                    "chart' below."
                ),
            },
            {
                "heading": "Common data problems and solutions",
                "text": (
                    "Problem: 'Load failed — encoding error'\n"
                    "  → Open the CSV in a text editor and save it as UTF-8.\n\n"
                    "Problem: Date column shown as 'text' type\n"
                    "  → Ensure all dates use the same format (DD/MM/YYYY or YYYY-MM-DD). "
                    "Mixed formats prevent automatic detection.\n\n"
                    "Problem: A numeric column shows as 'category'\n"
                    "  → There may be non-numeric characters in some cells (e.g., '12 mg', '>100'). "
                    "Open the file and clean those cells.\n\n"
                    "Problem: Empty rows at the end of the file\n"
                    "  → HAMELIN filters out fully-empty rows automatically. "
                    "If the row count seems too low, check for rows with only a few values."
                ),
            },
            {
                "heading": "Data Summary and missingness chart",
                "text": (
                    "Once a dataset is loaded, HAMELIN also builds two things "
                    "automatically, just below the Export / Reset Types / Generate "
                    "Quality Report buttons:\n\n"
                    "• A chart of the variables with the most missing data (top 10), so "
                    "you can spot problem columns at a glance without opening the Quality "
                    "Report.\n"
                    "• A 'Data Summary' card — a plain-text overview of the loaded dataset "
                    "you can read directly on the page.  Click 'Export Data Summary' to "
                    "save that text to a .txt or .md file, e.g. to paste into an email or "
                    "a methods section.\n\n"
                    "Both refresh automatically whenever you load a different dataset."
                ),
            },
            {
                "heading": "Table 1: what it is and how to generate it",
                "text": (
                    "Table 1 is the standard first table in a clinical research paper.  "
                    "It describes the demographic and clinical characteristics of the "
                    "study population — usually things like age, sex, comorbidities, lab "
                    "values — so readers can assess how representative the sample is.  It "
                    "used to be its own tab; it now lives at the bottom of this Data tab "
                    "and is built from whatever dataset is already loaded above — there is "
                    "no separate 'Browse' button of its own.\n\n"
                    "HAMELIN generates it automatically, using the correct statistical "
                    "test for each variable type:\n"
                    "  • Numeric → mean ± SD and median (IQR).\n"
                    "  • Categorical / binary → count (n) and percentage (%).\n\n"
                    "Step by step:\n"
                    "  1. Scroll to the 'Select Variables for Table 1' card, further down "
                    "this same tab.  Every column is listed and ticked by default.\n"
                    "  2. Columns HAMELIN thinks should probably be excluded (identifiers, "
                    "free text, zero-variance columns…) or that look like a good grouping "
                    "variable are flagged right on their own row, so there's no separate "
                    "list to cross-reference.\n"
                    "  3. Click 'Apply All Recommendations' to act on those flags "
                    "automatically, or tick/untick variables yourself.\n"
                    "  4. Under 'Table Settings', configure the options described in the "
                    "next block, then click 'Generate Table 1'.\n"
                    "  5. Review the table in the preview panel, then export it — see "
                    "below."
                ),
            },
            {
                "heading": "Table 1: grouping variable, missing data, and variable selection",
                "text": (
                    "Grouping Variable (optional):\n"
                    "  A categorical column used to split the table into groups and run a "
                    "between-group statistical test — numeric variables get a t-test "
                    "(2 groups) or ANOVA (3+ groups); categorical variables get a "
                    "Chi-square test or Fisher's exact test.  A common choice in "
                    "randomised trials is the treatment allocation; in observational "
                    "studies it's often 'Cases vs Controls' or a diagnosis category.\n\n"
                    "Missing data:\n"
                    "  Choose whether rows with missing values are kept (shown as missing "
                    "in the table) or dropped entirely before the table is built.\n\n"
                    "Show p-values:\n"
                    "  Only applies when a grouping variable is selected; untick it to "
                    "hide the p-value column, e.g. for a purely descriptive Table 1.\n\n"
                    "Selecting variables:\n"
                    "  • 'Select All' / 'Deselect All' — tick or untick everything at "
                    "once.\n"
                    "  • Individual ticks — choose per variable.\n"
                    "  • 'Apply All Recommendations' — unticks every variable flagged "
                    "'(recommendation: exclude — reason)' and pre-selects the suggested "
                    "grouping variable, if one was found.\n\n"
                    "Tip: exclude patient ID columns, free-text notes, and any column "
                    "with > 50% missing values before generating the table — this is "
                    "exactly what the recommendations are flagging for you."
                ),
            },
            {
                "heading": "Table 1: interpreting and exporting the table",
                "text": (
                    "Continuous variables:\n"
                    "  Mean ± SD — shown when the distribution is approximately normal.\n"
                    "  Median (IQR) — shown when the distribution is skewed.\n\n"
                    "Categorical variables:\n"
                    "  n (%) — count and percentage of patients in each category.\n\n"
                    "p-value column (when a grouping variable is used and 'Show p-values' "
                    "is ticked):\n"
                    "  < 0.05  → the groups differ significantly on this variable.\n"
                    "  ≥ 0.05  → no statistically significant difference detected.\n\n"
                    "Missing column:\n"
                    "  Shows the number/% of patients with missing values for each "
                    "variable (most relevant when missing data is kept rather than "
                    "dropped).\n\n"
                    "Exporting:\n"
                    "  Pick CSV, Excel (.xlsx), or Word (.docx) from the format dropdown "
                    "next to the Export button, then click Export.\n"
                    "  CSV — a plain-text table you can open in Excel for further "
                    "formatting; numbers keep full precision.\n"
                    "  Excel (.xlsx) — a ready-to-use workbook.\n"
                    "  Word (.docx) — a styled table you can drop straight into a "
                    "manuscript or send to your statistician."
                ),
            },
        ],
    },

    # ── 5. Training ────────────────────────────────────────────────────────────
    {
        "icon": FluentIcon.ROBOT,
        "title": "5 · Training",
        "summary": "Building a predictive model with AutoML — no programming required.",
        "blocks": [
            {
                "heading": "What is model training?",
                "text": (
                    "Training a model means teaching a computer programme to recognise patterns "
                    "in your data that are associated with a clinical outcome of interest.\n\n"
                    "Example: given a patient's age, BMI, blood pressure, and cholesterol, "
                    "can the model predict whether that patient will develop hypertension?\n\n"
                    "HAMELIN uses AutoML (Automated Machine Learning via Ludwig) to automatically "
                    "select and configure the best algorithm for your data — you do NOT need to "
                    "know what a Random Forest or a Neural Network is."
                ),
            },
            {
                "heading": "Step 1 — Outcome variable and predictors",
                "text": (
                    "Outcome variable (what you want to predict):\n"
                    "    Select the column that contains the clinical result you want to model.\n"
                    "    Examples: Diagnosis (Yes/No), Treatment_response (Complete/Partial/None), "
                    "HbA1c_at_12months (numeric).\n\n"
                    "Predictor variables (what the model learns from):\n"
                    "    Click to select the columns you believe are clinically relevant — hold "
                    "Ctrl or Shift to select several; there is no 'Select All' shortcut here, "
                    "pick them one by one.\n"
                    "    Rules of thumb:\n"
                    "      — Include variables that are available BEFORE the outcome is known.\n"
                    "      — Exclude patient ID, administrative codes, and the date column.\n"
                    "      — Exclude variables with > 50% missing values unless you plan to impute them.\n\n"
                    "Secondary outcomes (optional):\n"
                    "    Other clinical endpoints you also want the model to learn to predict "
                    "alongside the main one — this trains a real multi-output model, it is not "
                    "just kept for your own reference.\n"
                    "    Example: main outcome 'Mortality', with 'Length_of_stay' and "
                    "'Readmission_30d' also ticked here — the model is then trained to predict "
                    "all three.\n"
                    "    A column ticked as both a predictor and a secondary outcome is treated "
                    "as a predictor only."
                ),
            },
            {
                "heading": "Step 2 — Patient selection criteria",
                "text": (
                    "Here you can define inclusion and exclusion rules to filter the dataset "
                    "before training, using the visual rule builder — pick a Column, an "
                    "Operator, and a Value for each rule (there is no free-text expression box):\n"
                    "    Age    >=   18\n"
                    "    Sex    ==   Female\n\n"
                    "Add as many rows as you need, separately for Inclusion and Exclusion.  "
                    "Click each builder's own 'Preview' button to see how many rows match and "
                    "a sample of them, before you commit to training.\n\n"
                    "If a patient does NOT meet all inclusion criteria, they are excluded.\n"
                    "If a patient meets ANY exclusion criterion, they are also excluded.\n\n"
                    "'Save preset' / 'Reset preset' save or clear these criteria (and the "
                    "outcome variable) as a reusable JSON file for this project, under "
                    "training_schemas/."
                ),
            },
            {
                "heading": "Step 3 — Model configuration",
                "text": (
                    "Only three settings are shown here by default — the rest live behind the "
                    "'▶ Advanced options' toggle described just below, since they're more "
                    "ML-technical than something a non-technical user needs to reason about "
                    "day to day.\n\n"
                    "Model name:\n"
                    "  A short name for this training run — required.  It becomes the name of "
                    "the folder where the trained model is saved, and is what you'll see later "
                    "in the Model Training History and in the 'Models' page, so pick something "
                    "you'll recognise (e.g. 'Mortality_v1').\n\n"
                    "Prediction type:\n"
                    "  Binary classification — the outcome has exactly two values (Yes/No, 0/1).\n"
                    "  Multi-class classification — the outcome has 3 or more categories.\n"
                    "  Regression — the outcome is a continuous number (e.g., weight loss in kg).\n"
                    "  This is not just a hint — it forces Ludwig to train that kind of model, "
                    "so make sure it actually matches your outcome column.\n\n"
                    "Evaluation metric (how to measure model quality):\n"
                    "  The list of choices changes depending on the Prediction type picked "
                    "above — Ludwig only supports certain metrics per type:\n"
                    "  Binary — AUC-ROC (most common in clinical settings), Accuracy, "
                    "Precision, Recall, Specificity.\n"
                    "  Multi-class — Accuracy, Hits at K (is the true category among the "
                    "top-K predictions?).\n"
                    "  Regression — RMSE, MAE, MSE, RMSPE — all measure average prediction "
                    "error, lower is better."
                ),
            },
            {
                "heading": "Advanced options (inside Model Configuration, click to expand)",
                "text": (
                    "Click '▶ Advanced options' in the Model Configuration card to reveal "
                    "the rest of the settings.  Defaults are fine for most studies.\n\n"
                    "Time budget (minutes):\n"
                    "  Hard limit on search time.  Training stops when this is reached "
                    "even if the max iterations have not been completed.  Typed directly "
                    "(no up/down arrows).\n\n"
                    "Final evaluation holdout (%):\n"
                    "  A fixed percentage of patients is set aside BEFORE training begins and "
                    "NEVER used for training — only for the final performance evaluation.  "
                    "Default: 0.20.  Typed directly, e.g. '0.2' (no up/down arrows).\n\n"
                    "Random Seed:\n"
                    "  Ensures that splits and random operations produce the same result every time "
                    "you re-run the training.  Use the same seed to reproduce a result exactly.\n\n"
                    "Search strategy (hyperparameter optimisation):\n"
                    "  No optimisation — use Ludwig's defaults (fastest, good starting point).\n"
                    "  Random search — try random combinations.  Fast but less thorough.\n"
                    "  Bayesian optimisation — uses results from previous trials to choose "
                    "the next configuration to test.  Most efficient.  Recommended.\n"
                    "  Grid Search (Exhaustive search) — tries ALL combinations.  Very slow.  "
                    "Not recommended for large spaces.\n\n"
                    "Max. iterations:\n"
                    "  Maximum number of different configurations to try, once a search "
                    "strategy other than 'No optimisation' is selected.  More iterations → "
                    "better model, more time.  Recommended: 50–100.\n\n"
                    "Parallel trials:\n"
                    "  Number of CPU cores to use simultaneously.  "
                    "Increase for faster search; decrease if the computer becomes unresponsive.\n\n"
                    "Early stopping (rounds):\n"
                    "  How many consecutive evaluation rounds can pass with no improvement "
                    "before training stops automatically.  Default: 5.  Set to -1 to disable "
                    "it and always run the full time budget/iterations.\n\n"
                    "Missing numeric values strategy:\n"
                    "  How Ludwig fills missing values in NUMBER columns: Ludwig default "
                    "(fills with 0), column mean, most frequent value, forward fill, "
                    "backward fill, or drop the row entirely.\n\n"
                    "Handle Class Imbalance:\n"
                    "  On/off switch — enable it when one outcome category is much rarer than "
                    "the other.  Only available for Binary classification — Ludwig doesn't "
                    "support this for multi-class or regression, so the switch is disabled "
                    "(greyed out) for those."
                ),
                "image": "training_page_advanced.png",
            },
            {
                "heading": "Starting and monitoring training",
                "text": (
                    "1. Click 'Start Training'.  The button is only enabled once a dataset is loaded.\n"
                    "2. The progress bar updates as training proceeds.  "
                    "Do not close the application during training.\n"
                    "3. Training log messages appear in real time.\n"
                    "4. When finished, the Results panel's 4 highlighted cards adapt to what "
                    "you actually trained:\n"
                    "     — Classification: AUC-ROC, Accuracy, Sensitivity, Specificity.\n"
                    "     — Regression: R², RMSE, MAE, Loss.\n"
                    "   Any other metric Ludwig reports appears in a smaller line just below "
                    "the cards.  A confusion matrix and ROC curve are also shown for "
                    "classification tasks, when available.\n"
                    "5. Click 'Stop' at any time to cancel.  "
                    "Partial results up to the last completed trial are displayed."
                ),
            },
            {
                "heading": "Understanding results",
                "text": (
                    "AUC-ROC (Area Under the Curve) — classification tasks:\n"
                    "  0.5 = random guessing (useless model).\n"
                    "  0.7 = acceptable discriminative ability.\n"
                    "  0.8 = good.\n"
                    "  0.9 = excellent (rare; verify there is no data leakage).\n"
                    "  1.0 = perfect (almost always indicates a data leak — check your variables).\n\n"
                    "R² (goodness of fit) — regression tasks:\n"
                    "  1.0 = perfect fit.\n"
                    "  0.7–0.9 = good to excellent fit.\n"
                    "  0.5–0.7 = moderate fit.\n"
                    "  0–0.5 = weak fit — the model barely captures the pattern.\n"
                    "  Below 0 = worse than simply predicting the average every time — the model "
                    "isn't finding a real relationship between the predictors and this outcome.  "
                    "This can happen; it usually means the chosen target isn't actually "
                    "predictable from the chosen predictors, not that something is broken.\n\n"
                    "RMSE / MAE (regression):\n"
                    "  Both measure average prediction error, in the same units as the outcome "
                    "variable — smaller is better.  MAE is easier to interpret directly "
                    "('predictions are off by X on average'); RMSE penalises large errors more.\n\n"
                    "Confusion matrix (classification):\n"
                    "  A 2×2 table (binary) counting:\n"
                    "    True Positives (TP) / True Negatives (TN) — correct predictions.\n"
                    "    False Positives (FP) — predicted positive, actually negative.\n"
                    "    False Negatives (FN) — predicted negative, actually positive.\n"
                    "  In clinical settings, FN (missed cases) is usually more costly than FP.\n\n"
                    "The green box below the charts is an automatically generated one-line "
                    "summary in plain language — it always adapts to whichever of the two "
                    "result types you're looking at."
                ),
            },
            {
                "heading": "Exporting the trained model",
                "text": (
                    "Click 'Export Trained Model' to save the model artefacts to a ZIP file.\n"
                    "This archive can be used to:\n"
                    "  — Make predictions on new patients in the future.\n"
                    "  — Share the model with collaborators.\n"
                    "  — Archive the model for audit / reproducibility purposes.\n\n"
                    "Training results (metrics, charts) are also saved automatically in the "
                    "project's results/ folder every time training completes."
                ),
            },
        ],
    },

    # ── 6. Models ──────────────────────────────────────────────────────────────
    # Training and Forecasting; see section 6, block 8 for the original
    # placement of this content) ───────────────────────────────────────
    {
        "icon": FluentIcon.ROBOT,
        "title": "6 · Models",
        "summary": "Compare and inspect every model you've trained in this project.",
        "blocks": [
            {
                "heading": "What is the Models page?",
                "text": (
                    "The 'Models' item in the navigation bar (between Training and "
                    "Forecasting) opens a dedicated view for everything you've trained in "
                    "this project so far, not just the most recent run.  It is a normal page "
                    "in the nav bar, not a separate window — leaving it is just clicking any "
                    "other nav item.  Open a project first: this page needs one to know where "
                    "to look for trained models."
                ),
            },
            {
                "heading": "What you can do here",
                "text": (
                    "• Compare several trained models side by side on the metric of your "
                    "choice.\n"
                    "• Inspect a single model in depth (confusion matrix, ROC curve, "
                    "hyperparameters used).\n"
                    "• Duplicate a model with slightly different settings to try a variation "
                    "without starting from scratch — this pre-fills the Training page with "
                    "that configuration and switches you to it; nothing is saved until you "
                    "actually start training.\n"
                    "• Mark favourites and clean up models you no longer need."
                ),
            },
        ],
    },
    # ── 7. Forecasting ─────────────────────────────────────────────────────────
    {
        "icon": FluentIcon.HISTORY,
        "title": "7 · Forecasting",
        "summary": "Predicting when your study will reach its enrollment target.",
        "blocks": [
            {
                "heading": "What does the Forecasting page do?",
                "text": (
                    "Given how patients have been enrolled so far, HAMELIN fits a statistical "
                    "model to estimate the date when you will reach your Target Sample Size.\n\n"
                    "It also shows:\n"
                    "  • The current enrollment velocity (patients per month).\n"
                    "  • A confidence interval — a range of dates within which the target is "
                    "likely to be reached (default: 95% confidence).\n"
                    "  • A monthly milestone table (how many patients you will have enrolled "
                    "at each future month).\n"
                    "  • A chart showing historical enrollment (solid line) and the forecast "
                    "(dashed line with confidence band)."
                ),
                "image": "forecasting_page.png",
            },
            {
                "heading": "Required inputs",
                "text": (
                    "1. A loaded dataset with a date column recording enrollment dates "
                    "(one row per patient, one cell per enrollment date).\n"
                    "2. A Target Sample Size (pre-filled from Project metadata).\n\n"
                    "The enrollment date column is any column where each value is the date "
                    "the corresponding patient was included in the study.  "
                    "In REDCap this is often called 'enrollment_date' or 'inclusion_date'."
                ),
            },
            {
                "heading": "Forecast parameters explained",
                "text": (
                    "Enrollment Date Column\n"
                    "    Select the column that contains the date each patient was enrolled.\n"
                    "    Only date-type columns are shown here.\n\n"
                    "Target Sample Size\n"
                    "    The total number of patients you need to enroll.\n"
                    "    Pre-filled from the Project metadata.  You can override it here.\n\n"
                    "Historical Period (days)\n"
                    "    How many days of past data to use for estimating recruitment velocity.\n"
                    "    Default: 90 days.  Increase this for more stable estimates; decrease for "
                    "more sensitivity to recent trends.\n\n"
                    "Confidence Level\n"
                    "    Statistical confidence for the estimated date interval.\n"
                    "    0.95 = 95% confidence interval.  "
                    "    A narrower interval (0.80) is more optimistic; "
                    "    a wider one (0.99) is more conservative."
                ),
            },
            {
                "heading": "Reading the forecast chart",
                "text": (
                    "Solid coloured line — actual cumulative enrollment (historical data).\n"
                    "Dashed line — projected enrollment based on fitted regression.\n"
                    "Shaded band — confidence interval for the projection.\n"
                    "Horizontal dashed line — target sample size.\n"
                    "Vertical dashed line — estimated date when the target will be met.\n\n"
                    "If the shaded band is very wide, your enrollment has been irregular "
                    "(e.g., periods of high and low activity).  "
                    "Consider reviewing whether a site just opened or closed."
                ),
            },
            {
                "heading": "Current Recruitment Status panel",
                "text": (
                    "This panel updates automatically after running the forecast.\n\n"
                    "Currently Recruited — patients extracted from the date column (rows with a valid date).\n"
                    "Target Sample Size  — as configured in the parameters.\n"
                    "Remaining           — how many more patients you still need.\n"
                    "Avg. Rate           — mean patients enrolled per month over the whole study period.\n"
                    "Study Start Date    — date of the first enrollment found in the dataset."
                ),
            },
            {
                "heading": "Exporting the timeline",
                "text": (
                    "Click 'Export Timeline CSV' to save the monthly milestone table as a CSV file.\n"
                    "Each row shows: Month, Expected enrolled, Lower bound, Upper bound.\n"
                    "This table is useful for progress reports and sponsor updates."
                ),
            },
        ],
    },

    # ── 8. Glossary ────────────────────────────────────────────────────────────
    {
        "icon": FluentIcon.BOOK_SHELF,
        "title": "8 · Glossary",
        "summary": "Definitions of clinical and machine learning terms used in HAMELIN.",
        "blocks": [
            {
                "heading": "Clinical terms",
                "text": (
                    "CRP — Clinical Research Professional. "
                    "Any trained person involved in conducting clinical research (coordinator, nurse, monitor, etc.).\n\n"
                    "EDC — Electronic Data Capture. Software used to enter and manage clinical trial data "
                    "(e.g., REDCap, OpenClinica, Medidata Rave).\n\n"
                    "Enrollment / Recruitment — the process of identifying, consenting, and including "
                    "a patient in a clinical study.\n\n"
                    "Ethics Approval — formal permission from an Institutional Review Board (IRB) or "
                    "Ethics Committee (EC) to conduct a study involving human participants.\n\n"
                    "Inclusion / Exclusion Criteria — conditions that a patient must satisfy (inclusion) "
                    "or must not have (exclusion) to be eligible for a study.\n\n"
                    "Principal Investigator (PI) — the lead researcher responsible for the overall conduct "
                    "of the study.\n\n"
                    "Protocol Number — a unique alphanumeric code assigned to the study, used in all "
                    "regulatory and administrative communications.\n\n"
                    "Sample Size — the number of patients required to give the study enough "
                    "statistical power to detect the effect of interest.\n\n"
                    "Table 1 — the baseline characteristics table in a clinical paper describing "
                    "the study population.\n\n"
                    "Target Sample Size — the minimum number of patients needed; determined by a "
                    "power calculation."
                ),
            },
            {
                "heading": "Machine Learning / Statistics terms",
                "text": (
                    "Algorithm — a mathematical procedure that learns patterns from data.\n\n"
                    "AUC-ROC (Area Under the Receiver Operating Characteristic Curve) — a metric "
                    "between 0 and 1 measuring how well a binary classifier separates positive from "
                    "negative cases.  AUC = 0.5 is random; AUC = 1.0 is perfect.\n\n"
                    "AutoML — Automated Machine Learning.  Software that automatically selects and "
                    "configures the best algorithm for a given dataset.\n\n"
                    "Binary classification — a task where the outcome has exactly two possible values "
                    "(e.g., diseased / healthy, responder / non-responder).\n\n"
                    "Confusion matrix — a table showing Correct and incorrect predictions broken down "
                    "by True/False Positive/Negative.\n\n"
                    "Cross-validation — a technique that divides the dataset into folds to estimate "
                    "model performance more reliably than a single train/test split.\n\n"
                    "Data leakage — when information from the future or from the outcome variable "
                    "accidentally enters the training data, causing unrealistically high performance.\n\n"
                    "F1 score — the harmonic mean of Precision and Recall.  Useful when classes are "
                    "imbalanced.\n\n"
                    "Feature — a predictor variable used as input to the model.\n\n"
                    "Holdout set — a portion of the data kept completely separate from training and "
                    "used only for the final performance evaluation.\n\n"
                    "Hyperparameter — a setting that controls how the algorithm learns "
                    "(e.g., learning rate, number of trees).  Distinct from model parameters, "
                    "which are learned from data.\n\n"
                    "Hyperparameter optimisation (HPO) — automatic search for the best hyperparameter "
                    "combination.\n\n"
                    "Loss — the raw value the training process is directly trying to minimise.  "
                    "Lower is better, but it's on an arbitrary scale, so it's mainly useful to "
                    "compare between trials of the SAME training run, not as a standalone number.\n\n"
                    "Ludwig — an open-source AutoML framework from Uber AI used by HAMELIN for "
                    "model training and variable type inference.\n\n"
                    "MAE (Mean Absolute Error) — regression metric: the average absolute difference "
                    "between predicted and actual values, in the same units as the outcome. "
                    "Smaller is better; 0 would be a perfect model.\n\n"
                    "Multi-class classification — a task where the outcome has three or more categories.\n\n"
                    "NaN (Not a Number) — missing or undefined numeric value in a dataset.\n\n"
                    "NaT (Not a Time) — missing value in a date/time column.\n\n"
                    "Overfitting — when a model learns the training data too well and fails to "
                    "generalise to new patients.\n\n"
                    "Precision — of all patients the model predicted as positive, what fraction "
                    "actually were positive?\n\n"
                    "R² (R-squared) — regression metric measuring goodness of fit, typically between "
                    "0 and 1 (1 = perfect fit).  Can go negative, which means the model performs "
                    "worse than simply predicting the average value every time.\n\n"
                    "Random seed — a number that initialises the random number generator, ensuring "
                    "that random splits and initialisations are reproducible.\n\n"
                    "Recall (Sensitivity) — of all truly positive patients, what fraction did the "
                    "model correctly identify?\n\n"
                    "Regression — a task where the outcome is a continuous numeric value.\n\n"
                    "RMSE (Root Mean Squared Error) — regression metric similar to MAE, but squares "
                    "errors before averaging, which penalises large individual errors more heavily. "
                    "Same units as the outcome variable; smaller is better.\n\n"
                    "Standard Deviation (SD) — a measure of how spread out the values are around "
                    "the mean.\n\n"
                    "Train / Test split — dividing the dataset into a training set (used to build "
                    "the model) and a test set (used to evaluate it)."
                ),
            },
            {
                "heading": "File formats",
                "text": (
                    "CSV (.csv) — Comma-Separated Values.  "
                    "Plain text file where each row is an observation and columns are separated by commas.\n\n"
                    "Stata (.dta) — Stata proprietary binary format for statistical datasets.\n\n"
                    "SPSS (.sav) — IBM SPSS Statistics binary format.  "
                    "Preserves variable labels and value labels.\n\n"
                    "XLSX (.xlsx) — Microsoft Excel Open XML format.  "
                    "Supports multiple sheets; HAMELIN reads only the first sheet.\n\n"
                    "HTML (.html) — HyperText Markup Language.  "
                    "Used for formatted Table 1 and Quality Report exports.\n\n"
                    "JSON (.json) — JavaScript Object Notation.  "
                    "Used internally by HAMELIN for project metadata and dataset registry."
                ),
            },
        ],
    },

]


def _get_translated_sections() -> list[dict]:
    """Apply i18n translations to section titles, summaries, block headings, and block text.
    
    If a translation key is not found, falls back to the English text in _SECTIONS.
    """
    sections = []
    for section_idx, section in enumerate(_SECTIONS):
        # Helper to check if translation exists (if result equals the key, it wasn't found)
        def get_text(key: str, fallback: str) -> str:
            result = t(key)
            return fallback if result == key else result
        
        translated = {
            "icon": section["icon"],
            "title": get_text(f"help.section.{section_idx}.title", section["title"]),
            "summary": get_text(f"help.section.{section_idx}.summary", section["summary"]),
            "blocks": [
                {
                    "heading": get_text(f"help.section.{section_idx}.block.{block_idx}.heading", block["heading"]),
                    "text": get_text(f"help.section.{section_idx}.block.{block_idx}.text", block["text"]),
                    # Screenshots aren't translated text - carried through
                    # as-is, not looked up in strings.py.
                    "image": block.get("image"),
                }
                for block_idx, block in enumerate(section["blocks"])
            ],
        }
        sections.append(translated)
    return sections


# ──────────────────────────────────────────────────────────────────────────────
# Helper widgets
# ──────────────────────────────────────────────────────────────────────────────

class _Block(QWidget):
    """A heading + body-text block inside a section card, with an optional
    real screenshot of the app shown underneath the text."""

    def __init__(self, heading: str, text: str, parent=None, image: str | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(4)

        h_lbl = StrongBodyLabel(heading, self)
        h_font = h_lbl.font()
        h_font.setWeight(QFont.Weight.DemiBold)
        h_lbl.setFont(h_font)
        layout.addWidget(h_lbl)

        t_lbl = BodyLabel(text, self)
        t_lbl.setWordWrap(True)
        t_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(t_lbl)

        if image:
            pixmap = QPixmap(str(_HELP_IMAGES_DIR / image))
            if not pixmap.isNull():
                img_lbl = QLabel(self)
                # Cap the width so a full-page screenshot doesn't blow out
                # this card's layout; keep it readable but not huge.
                scaled = pixmap.scaledToWidth(700, Qt.SmoothTransformation)
                img_lbl.setPixmap(scaled)
                img_lbl.setStyleSheet("border: 1px solid rgba(0, 0, 0, 40); margin-top: 6px;")
                layout.addWidget(img_lbl)
            else:
                log.warning(f"HelpPage: image not found or unreadable: {image}")


class _SectionCard(QWidget):
    """
    A collapsible card for one manual section.

    Header row:  [icon]  [title]  ────────────────  [▼/▶ toggle]
    Body:        [summary caption]
                 [block 0]  [block 1]  …
    """

    def __init__(self, spec: dict, parent=None) -> None:
        super().__init__(parent)
        self._title = spec["title"]

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._card = CardWidget(self)
        root.addWidget(self._card)

        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(0)

        # ── Header row ────────────────────────────────────────────────
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        icon_w = IconWidget(spec["icon"], self._card)
        icon_w.setFixedSize(22, 22)
        header_row.addWidget(icon_w, alignment=Qt.AlignVCenter)

        title_lbl = SubtitleLabel(spec["title"], self._card)
        t_font = title_lbl.font()
        t_font.setWeight(QFont.Weight.DemiBold)
        title_lbl.setFont(t_font)
        header_row.addWidget(title_lbl, stretch=1, alignment=Qt.AlignVCenter)

        self._toggle_btn = TransparentToolButton(FluentIcon.CARE_DOWN_SOLID, self._card)
        self._toggle_btn.setFixedSize(28, 28)
        self._toggle_btn.clicked.connect(self._toggle)
        header_row.addWidget(self._toggle_btn, alignment=Qt.AlignVCenter)

        card_layout.addLayout(header_row)

        # ── Summary caption (always visible) ─────────────────────────
        summary_lbl = CaptionLabel(spec["summary"], self._card)
        bind_style(summary_lbl, lambda c: f"color: {c.text_secondary};")
        summary_lbl.setWordWrap(True)
        card_layout.addSpacing(4)
        card_layout.addWidget(summary_lbl)

        # ── Collapsible body ──────────────────────────────────────────
        self._body = QWidget(self._card)
        body_layout = QVBoxLayout(self._body)
        body_layout.setContentsMargins(0, 12, 0, 0)
        body_layout.setSpacing(16)

        for block in spec["blocks"]:
            body_layout.addWidget(
                _Block(block["heading"], block["text"], self._body, image=block.get("image"))
            )

        card_layout.addWidget(self._body)
        self._body.setVisible(False)   # collapsed by default

    # ------------------------------------------------------------------
    def _toggle(self) -> None:
        expanded = not self._body.isVisible()
        usage_log.event("Help", "click", f"Section toggle: {self._title}", "expanded" if expanded else "collapsed")
        self._body.setVisible(expanded)
        self._toggle_btn.setIcon(
            FluentIcon.CARE_UP_SOLID if expanded else FluentIcon.CARE_DOWN_SOLID
        )

    def expand(self) -> None:
        """Expand the section programmatically."""
        self._body.setVisible(True)
        self._toggle_btn.setIcon(FluentIcon.CARE_UP_SOLID)

    def collapse(self) -> None:
        """Collapse the section programmatically."""
        self._body.setVisible(False)
        self._toggle_btn.setIcon(FluentIcon.CARE_DOWN_SOLID)


# ──────────────────────────────────────────────────────────────────────────────
# HelpPage
# ──────────────────────────────────────────────────────────────────────────────

class HelpPage(QWidget):
    """
    In-app user manual page.

    Displayed as the last item in the bottom navigation bar.
    All nine sections start collapsed; the user expands whichever one
    they need.  An 'Expand All' / 'Collapse All' convenience button pair
    is provided at the top.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("HelpPage")
        self._section_cards: list[_SectionCard] = []
        log.debug("Initialising Help Page")
        self._init_ui()

    # ------------------------------------------------------------------
    def _init_ui(self) -> None:
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        scroll.setWidget(container)
        apply_scroll_area_theme(scroll)
        container.setStyleSheet("background: transparent;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        # ── Page header ───────────────────────────────────────────────
        title = TitleLabel(t("help.title"))
        title.setAlignment(Qt.AlignLeft)
        layout.addWidget(title)

        subtitle = StrongBodyLabel(t("help.subtitle"))
        bind_style(subtitle, lambda c: f"color: {c.text_secondary};")
        layout.addWidget(subtitle)

        layout.addSpacing(4)

        # ── Expand / Collapse all ─────────────────────────────────────
        ctrl_row = QHBoxLayout()
        expand_btn = PushButton(t("help.btn.expand"), self)
        expand_btn.setIcon(FluentIcon.CARE_DOWN_SOLID)
        expand_btn.clicked.connect(self._expand_all)
        expand_btn.setFixedWidth(140)

        collapse_btn = PushButton(t("help.btn.collapse"), self)
        collapse_btn.setIcon(FluentIcon.CARE_UP_SOLID)
        collapse_btn.clicked.connect(self._collapse_all)
        collapse_btn.setFixedWidth(140)

        ctrl_row.addWidget(expand_btn)
        ctrl_row.addWidget(collapse_btn)
        ctrl_row.addStretch()
        layout.addLayout(ctrl_row)

        layout.addSpacing(4)

        # ── Section cards ─────────────────────────────────────────────
        translated_sections = _get_translated_sections()
        for spec in translated_sections:
            card = _SectionCard(spec, container)
            self._section_cards.append(card)
            layout.addWidget(card)

        layout.addStretch()

        log.debug(f"Help Page initialised with {len(translated_sections)} sections")

    # ------------------------------------------------------------------
    def _expand_all(self) -> None:
        usage_log.event("Help", "click", "Expand All button")
        for card in self._section_cards:
            card.expand()

    def _collapse_all(self) -> None:
        usage_log.event("Help", "click", "Collapse All button")
        for card in self._section_cards:
            card.collapse()
