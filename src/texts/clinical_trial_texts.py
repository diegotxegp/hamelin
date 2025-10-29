# texts/clinical_trial_texts.py

"""
Centralized texts for the Clinical Trial tab
Here you can easily modify all explanatory texts without touching the code
"""

CLINICAL_TRIAL_TEXTS = {
    "primary_variable": {
        "title": "Primary Outcome Variable Selection",
        "content": """
        <p style="font-size: 14pt; font-weight: bold; margin-bottom: 15px; text-align: center;">
            Primary Outcome Variable Selection
        </p>
        
        <p style="margin-bottom: 15px; text-align: justify;">
            Select the <strong>primary outcome variable</strong> from your clinical trial dataset. 
            This is the main variable that measures the effectiveness of the treatment being studied.
        </p>
        
        <p style="font-weight: bold; margin-bottom: 10px;">
            HAMELIN supports both Classification and Regression tasks:
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>• Binary outcomes (Classification):</strong> Treatment success/failure, presence/absence of disease, cure/no cure
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>• Categorical outcomes (Classification):</strong> Disease severity levels, treatment response categories (mild/moderate/severe)
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>• Continuous numerical outcomes (Regression):</strong> Blood pressure levels, pain scores (0-10), quality of life indices, lab values
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 15px;">
            <strong>• Time-related outcomes (Regression):</strong> Survival time, time to recovery, duration of symptoms (in days/weeks)
        </p>
        
        <p style="font-weight: bold; margin-top: 15px; margin-bottom: 10px; background-color: #e8f4f8; padding: 10px;">
            ✓ Intelligent Variable Detection:
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            The system automatically detects:
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            • <strong>Categorical variables</strong>: Text categories, limited distinct values
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 5px;">
            • <strong>Continuous variables</strong>: Real numbers with decimals (e.g., 72.5, 98.6)
        </p>
        
        <p style="margin-left: 40px; margin-bottom: 15px;">
            • <strong>Discrete numerical variables</strong>: Integers with repeated values (treated as categorical if appropriate)
        </p>
        
        <p style="margin-top: 15px; font-style: italic; background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107;">
            <strong>Note:</strong> Variables with insufficient sample distribution are automatically filtered out. 
            For classification, each category needs at least 5 samples. For regression with discrete values, 
            at least 2 samples per value are required.
        </p>
        """
    },
    
    "criteria": {
        "title": "Inclusion/Exclusion Criteria",
        "content": """
        <p style="margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            <span style="font-size:16pt; font-weight:600;">Patient Selection Criteria</span>
        </p>
        <p style="margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            Define the <span style="font-weight:600;">inclusion and exclusion criteria</span> used to select patients for your clinical trial. 
            This helps ensure the analysis focuses on the appropriate patient population.
        </p>
        <p style="margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            <span style="font-weight:600;">Common criteria types:</span>
        </p>
        <ul style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;">
            <li style="margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style="font-weight:600;">Demographic:</span> Age ranges, gender, geographic location
            </li>
            <li style="margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style="font-weight:600;">Clinical:</span> Disease stage, symptom severity, previous treatments
            </li>
            <li style="margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style="font-weight:600;">Laboratory:</span> Biomarker levels, test results, vital signs
            </li>
            <li style="margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style="font-weight:600;">Exclusion:</span> Contraindications, comorbidities, inability to comply
            </li>
        </ul>
        <p style="margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            <span style="font-style:italic;">Clear criteria definition ensures reproducible and valid study results.</span>
        </p>
        """
    },
    
    "investigational_drug": {
        "title": "Experimental Treatment Group",
        "content": """
        <p style="margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            <span style="font-size:16pt; font-weight:600;">Experimental Treatment Group</span>
        </p>
        <p style="margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            Identify the <span style="font-weight:600;">experimental treatment group</span> in your clinical trial dataset. 
            This represents patients who received the new treatment being tested.
        </p>
        <p style="margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            <span style="font-weight:600;">What to specify:</span>
        </p>
        <ul style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;">
            <li style="margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style="font-weight:600;">Treatment group identifier:</span> Column name or values that identify experimental arm
            </li>
            <li style="margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style="font-weight:600;">Drug name/code:</span> Name or code of the investigational treatment
            </li>
            <li style="margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style="font-weight:600;">Dosage information:</span> Dose levels or regimens if applicable
            </li>
            <li style="margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style="font-weight:600;">Administration route:</span> How the treatment was given (oral, IV, etc.)
            </li>
        </ul>
        <p style="margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            <span style="font-style:italic;">This information helps the AI identify which patients received the experimental treatment for comparison analysis.</span>
        </p>
        """
    },
    
    "control_drug": {
        "title": "Control Group Identification",
        "content": """
        <p style="margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            <span style="font-size:16pt; font-weight:600;">Control Group Identification</span>
        </p>
        <p style="margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            Identify the <span style="font-weight:600;">control group</span> in your clinical trial dataset. 
            This is the comparison group used to evaluate the effectiveness of the experimental treatment.
        </p>
        <p style="margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            <span style="font-weight:600;">Types of control groups:</span>
        </p>
        <ul style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;">
            <li style="margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style="font-weight:600;">Placebo:</span> Inactive treatment that looks identical to the experimental drug
            </li>
            <li style="margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style="font-weight:600;">Active control:</span> Standard treatment or existing approved medication
            </li>
            <li style="margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style="font-weight:600;">No treatment:</span> Natural course of disease without intervention
            </li>
            <li style="margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style="font-weight:600;">Historical control:</span> Comparison with past patient data
            </li>
        </ul>
        <p style="margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            <span style="font-weight:600;">What to specify:</span> Control group identifier, treatment name/code, and any relevant dosage information.
        </p>
        <p style="margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            <span style="font-style:italic;">Accurate control group identification is essential for meaningful treatment comparisons.</span>
        </p>
        """
    },
    
    "disease": {
        "title": "Target Condition Specification",
        "content": """
        <p style="margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            <span style="font-size:16pt; font-weight:600;">Target Condition Specification</span>
        </p>
        <p style="margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            Specify the <span style="font-weight:600;">medical condition</span> that was studied in your clinical trial. 
            This helps contextualize the treatment effects and analysis results.
        </p>
        <p style="margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            <span style="font-weight:600;">Information to include:</span>
        </p>
        <ul style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;">
            <li style="margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style="font-weight:600;">Disease name:</span> Primary condition being treated (e.g., diabetes, hypertension, cancer)
            </li>
            <li style="margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style="font-weight:600;">Disease stage/severity:</span> Early stage, advanced, mild, moderate, severe
            </li>
            <li style="margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style="font-weight:600;">Medical classification:</span> ICD codes, disease subtypes, specific variants
            </li>
            <li style="margin-top:6px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style="font-weight:600;">Study population:</span> Specific patient characteristics or demographics
            </li>
        </ul>
        <p style="margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
            <span style="font-style:italic;">Clear disease specification helps ensure the analysis focuses on relevant clinical outcomes and safety considerations.</span>
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
            Configure the analysis parameters for your clinical trial. These settings control how Ludwig processes 
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
            data includes time-series measurements or follow-up visits where the order matters.
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