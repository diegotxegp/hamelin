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
            Common Primary Variables in Registries:
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>Clinical Outcomes:</strong><br/>
            Disease progression, treatment response, mortality, complications, remission status
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>Patient Status:</strong><br/>
            Disease severity levels, risk categories, functional status, quality of life scores
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>Healthcare Events:</strong><br/>
            Hospital admissions, emergency visits, surgical interventions, adverse events
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 15px;">
            <strong>Long-term Follow-up:</strong><br/>
            Survival status, disease recurrence, treatment adherence, patient-reported outcomes
        </p>
        
        <p style="font-weight: bold; margin-bottom: 10px;">
            Selection Requirements:
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            • The variable must be <strong>categorical</strong> (represents categories or groups)
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            • Should have between <strong>2 to 10 different categories</strong>
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 15px;">
            • Each category must have <strong>at least 5 examples</strong> in your data
        </p>
        
        <p style="margin-top: 15px; font-style: italic; background-color: #f0f8ff; padding: 10px; border-left: 4px solid #4a90e2;">
            <strong>Tip:</strong> Choose a variable that represents a clinically meaningful outcome 
            or characteristic that you want to predict or better understand in your patient population.
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