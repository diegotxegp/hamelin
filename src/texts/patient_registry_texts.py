# texts/patient_registry_texts.py

"""
Centralized texts for the Patient Registry tab
Here you can easily modify all explanatory texts without touching the code
"""

PATIENT_REGISTRY_TEXTS = {
    "primary_variable": {
        "title": "Primary Variable (Target)",
        "content": """
        <p style="font-size: 14pt; font-weight: bold; margin-bottom: 15px; text-align: center;">
            Primary Variable Selection
        </p>
        
        <p style="margin-bottom: 15px; text-align: justify;">
            The <strong>primary variable</strong> is the main characteristic you want to understand or predict 
            from your patient registry. This variable will be the focus of your analysis.
        </p>
        
        <p style="font-weight: bold; margin-bottom: 10px;">
            What is a Patient Registry?
        </p>
        
        <p style="margin-bottom: 15px; text-align: justify;">
            A patient registry systematically collects health data from patients with specific conditions or 
            characteristics. It helps track outcomes, identify patterns, and improve healthcare quality over time.
        </p>
        
        <p style="font-weight: bold; margin-bottom: 10px;">
            HAMELIN supports both Classification and Regression:
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>Categorical Outcomes (Classification):</strong><br/>
            Disease progression stages, treatment response categories, mortality risk levels, 
            remission status (complete/partial/none)
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>Binary Outcomes (Classification):</strong><br/>
            Survival (yes/no), hospital readmission (yes/no), adverse events (present/absent), 
            treatment adherence (compliant/non-compliant)
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>Continuous Numerical Outcomes (Regression):</strong><br/>
            Quality of life scores (0-100), pain intensity (0.0-10.0), lab values (glucose, cholesterol), 
            functional capacity measurements, survival time (in months)
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 15px;">
            <strong>Discrete Numerical Outcomes:</strong><br/>
            Number of hospitalizations, number of complications, disease recurrence count
        </p>
        
        <p style="font-weight: bold; margin-bottom: 10px; background-color: #e8f4f8; padding: 10px;">
            ✓ Intelligent Variable Detection:
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            The system automatically identifies:
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            • <strong>Categorical variables</strong>: Text labels or limited distinct values (2-10 categories)
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            • <strong>Continuous variables</strong>: Numbers with significant decimal places (e.g., 7.2, 98.6, 145.3)
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 15px;">
            • <strong>Discrete variables</strong>: Integers with repeated values (treated appropriately for the task)
        </p>
        
        <p style="font-weight: bold; margin-bottom: 10px;">
            Selection Requirements:
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            • <strong>For categorical variables:</strong> Between 2 to 10 different categories
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            • <strong>For categorical variables:</strong> Each category must have at least 5 examples
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 15px;">
            • <strong>For continuous variables:</strong> Sufficient variation in values (not all identical)
        </p>
        
        <p style="margin-top: 15px; font-style: italic; background-color: #f0f8ff; padding: 10px; border-left: 4px solid #4a90e2;">
            <strong>Tip:</strong> Choose a variable that represents a clinically meaningful outcome 
            or characteristic. HAMELIN will automatically determine if classification or regression 
            is more appropriate based on your variable type.
        </p>
        """
    },
    
    "criteria": {
        "title": "Variable Selection",
        "content": """
        <p style="font-size: 14pt; font-weight: bold; margin-bottom: 15px; text-align: center;">
            Variable Selection and Configuration
        </p>
        
        <p style="margin-bottom: 15px; text-align: justify;">
            For each variable (column) in your patient registry, you need to specify <strong>two things</strong>:
        </p>
        
        <p style="font-weight: bold; margin-bottom: 10px; font-size: 12pt;">
            [1] Role in Analysis
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 10px; text-align: justify;">
            Choose whether the variable will be used as:
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            <strong>input:</strong> Variables used to make predictions (patient characteristics, clinical measurements, demographics)
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            <strong>output:</strong> The outcome you want to predict (only your primary variable)
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 15px;">
            <strong>(blank):</strong> Leave empty to exclude variables you don't want to use
        </p>
        
        <p style="font-weight: bold; margin-bottom: 10px; font-size: 12pt;">
            [2] Data Type
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 10px; text-align: justify;">
            Specify what kind of data the variable contains:
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            <strong>binary:</strong> Yes/No, True/False, 0/1 (e.g., Event occurred/not occurred)
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            <strong>category:</strong> Multiple distinct groups (e.g., Disease severity: Mild, Moderate, Severe)
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            <strong>number:</strong> Numerical measurements (e.g., Age, lab values, questionnaire scores)
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            <strong>text:</strong> Free text descriptions or medical notes
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            <strong>date:</strong> Date or time information (e.g., Visit dates, diagnosis dates)
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 15px;">
            <strong>Other types:</strong> bag, set, sequence, vector, audio, h3, image, timeseries (for specialized data)
        </p>
        
        <p style="margin-top: 15px; font-style: italic; background-color: #fff3cd; padding: 10px; border-left: 4px solid #f0ad4e;">
            <strong>Example:</strong> For "Patient Status" with values Alive/Deceased, select <strong>input</strong> + <strong>binary</strong>. 
            For "Hospital Admissions" with a count, use <strong>input</strong> + <strong>number</strong>. Your primary variable should be <strong>output</strong> + its type.
        </p>
        
        <p style="margin-top: 15px; font-style: italic; background-color: #d1ecf1; padding: 10px; border-left: 4px solid #0c5460;">
            <strong>Tip:</strong> Include all clinical variables that might influence the outcome. Patient identifiers or administrative codes can be left blank.
        </p>
        """
    },
    
    "settings": {
        "title": "Analysis Settings",
        "content": """
        <p style="font-size: 14pt; font-weight: bold; margin-bottom: 15px; text-align: center;">
            Analysis Settings Configuration
        </p>
        
        <p style="margin-bottom: 15px; text-align: justify;">
            Configure the analysis parameters for your patient registry. These settings control how Ludwig processes 
            your data and trains the predictive model.
        </p>
        
        <p style="font-weight: bold; margin-bottom: 10px; font-size: 12pt;">
            [*] Separator
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 15px; text-align: justify;">
            Choose the character that separates values in your dataset file. Common separators:
            <br/>• <strong>Comma (,)</strong> - Most common for CSV files
            <br/>• <strong>Tab</strong> - Used in TSV files
            <br/>• <strong>Semicolon (;)</strong> - Common in European datasets
        </p>
        
        <p style="font-weight: bold; margin-bottom: 10px; font-size: 12pt;">
            [*] Missing-data Strategy
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 10px; text-align: justify;">
            How Ludwig handles missing values in your dataset:
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            <strong>fill_with_const:</strong> Replaces missing values with a specific value you define
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            <strong>fill_with_mode:</strong> Uses the most frequent value in that column
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            <strong>fill_with_mean:</strong> Uses the average value (only for numerical data)
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            <strong>fill_with_false:</strong> Replaces with 'false' (only for yes/no data)
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            <strong>bfill:</strong> Uses the next valid value from subsequent rows
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            <strong>ffill:</strong> Uses the previous valid value from preceding rows
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 15px;">
            <strong>drop_row:</strong> Removes the entire row if any value is missing
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 15px; font-style: italic; background-color: #fff3cd; padding: 8px;">
            <strong>Note:</strong> For the outcome variable, 'drop_row' is always used to ensure real predictions, 
            not made-up values.
        </p>
        
        <p style="font-weight: bold; margin-bottom: 10px; font-size: 12pt;">
            [*] Metric
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 10px; text-align: justify;">
            The primary measure to evaluate model performance. Common metrics:
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            <strong>Accuracy:</strong> Percentage of correct predictions (good for balanced datasets)
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            <strong>ROC AUC:</strong> Ability to distinguish between outcomes (0.5 = random, 1.0 = perfect)
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 15px;">
            <strong>Loss:</strong> Error measure (lower is better)
        </p>
        
        <p style="font-weight: bold; margin-bottom: 10px; font-size: 12pt;">
            [*] Goal
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 15px; text-align: justify;">
            Optimization objective:
            <br/>• <strong>Maximize:</strong> For metrics like accuracy or ROC AUC (higher = better)
            <br/>• <strong>Minimize:</strong> For metrics like loss or error (lower = better)
        </p>
        
        <p style="font-weight: bold; margin-bottom: 10px; font-size: 12pt;">
            [*] Time-dependable
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 15px; text-align: justify;">
            Whether the analysis should consider the order of data over time. Set to <strong>True</strong> if your 
            registry includes longitudinal data with follow-up visits or time-series measurements where the order matters.
        </p>
        
        <p style="font-weight: bold; margin-bottom: 10px; font-size: 12pt;">
            [*] Runtime (seconds)
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 15px; text-align: justify;">
            Maximum training time in seconds. Default is 7200 (2 hours). Longer times allow more thorough 
            model optimization but take more time to complete. Recommended: 3600-10800 seconds.
        </p>
        
        <p style="margin-top: 15px; font-style: italic; background-color: #d1ecf1; padding: 10px; border-left: 4px solid #0c5460;">
            <strong>Tip:</strong> Start with default settings. If results are poor, try 'fill_with_mean' 
            for missing data and increase runtime to 10800 seconds for better optimization.
        </p>
        """
    }
}