# model/model_clinical_trial.py
class ModelClinicalTrial:
    def __init__(self, model):
        self.model = model
        self.primary_variable = None
        self.inclusion_criteria = None
        self.investigational_drug = None
        self.control_drug = None
        self.disease = None
        
    def get_summary(self):
        """Return a summary of all collected clinical trial information."""
        summary = {
            "Primary Endpoint": self.primary_variable,
            "Selection Criteria": self.inclusion_criteria,
            "Experimental Treatment": self.investigational_drug,
            "Control Group": self.control_drug,
            "Target Condition": self.disease
        }
        return {k: v for k, v in summary.items() if v is not None}
    
    def is_ready_for_analysis(self):
        """Check if minimum required information is available for analysis."""
        return (self.primary_variable is not None and 
                self.investigational_drug is not None and 
                self.control_drug is not None)