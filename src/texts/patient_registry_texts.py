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
            Primary Variable (Target)
        </p>
        
        <p style="margin-bottom: 15px; text-align: justify;">
            Select the <strong>primary variable of interest</strong> from your patient registry dataset. 
            This is the main outcome or characteristic you want to predict or analyze.
        </p>
        
        <p style="font-weight: bold; margin-bottom: 10px;">
            Examples for patient registries:
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>• Clinical outcomes:</strong> Disease progression, treatment response, complications
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>• Patient characteristics:</strong> Risk categories, disease severity, phenotypes
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 8px;">
            <strong>• Healthcare utilization:</strong> Hospital readmissions, length of stay, costs
        </p>
        
        <p style="margin-left: 20px; margin-bottom: 15px;">
            <strong>• Quality measures:</strong> Patient satisfaction, adherence, quality of life
        </p>
        
        <p style="margin-top: 15px; font-style: italic;">
            Note: This variable will serve as the target for predictive modeling and pattern analysis.
        </p>
        """
    }
}