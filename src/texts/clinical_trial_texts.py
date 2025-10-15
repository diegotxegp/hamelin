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
            Examples of primary outcome variables:
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>• Binary outcomes:</strong> Treatment success/failure, presence/absence of disease, cure/no cure
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>• Continuous outcomes:</strong> Blood pressure levels, pain scores, quality of life indices
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>• Categorical outcomes:</strong> Disease severity levels, treatment response categories
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 15px;">
            <strong>• Time-related outcomes:</strong> Survival time, time to recovery, duration of symptoms
        </p>
        
        <p style="margin-top: 15px; font-style: italic;">
            Note: This variable will be used as the target for all predictive analyses and treatment effect comparisons.
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
            Analysis Settings
        </p>
        
        <p style="margin-bottom: 15px; text-align: justify;">
            Configure the analysis parameters for your clinical trial. These settings control how the data is processed and analyzed.
        </p>
        
        <p style="font-weight: bold; margin-bottom: 10px;">
            Configuration options:
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>• Separator:</strong> Choose the data separator used in your dataset
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>• Missing-data:</strong> How to handle missing values in the dataset
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>• Metric:</strong> Primary evaluation metric for model performance
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>• Goal:</strong> Optimization objective (minimize or maximize)
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>• Time-dependable:</strong> Whether the analysis considers temporal relationships
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 15px;">
            <strong>• Runtime:</strong> Maximum training time in seconds (default: 7200)
        </p>
        
        <p style="margin-top: 15px; font-style: italic;">
            Note: These settings directly impact the quality and duration of the analysis.
        </p>
        """
    }
}