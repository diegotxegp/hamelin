# texts/text_manager.py

"""
Centralized text manager for the HAMELIN application
This module allows loading and managing all user interface texts
"""

from .clinical_trial_texts import CLINICAL_TRIAL_TEXTS
from .patient_registry_texts import PATIENT_REGISTRY_TEXTS
from .observational_study_texts import OBSERVATIONAL_STUDY_TEXTS

class TextManager:
    """
    Class to manage all application texts in a centralized way
    """
    
    def __init__(self):
        self.texts = {
            'clinical_trial': CLINICAL_TRIAL_TEXTS,
            'patient_registry': PATIENT_REGISTRY_TEXTS,
            'observational_study': OBSERVATIONAL_STUDY_TEXTS
        }
    
    def get_text(self, section, subsection, key='content'):
        """
        Gets a specific text from the application
        
        Args:
            section (str): Main section (clinical_trial, patient_registry, observational_study)
            subsection (str): Specific subsection (primary_variable, criteria, etc.)
            key (str): Specific key (content, title)
        
        Returns:
            str: The requested text or a default text if not found
        """
        try:
            return self.texts[section][subsection][key]
        except KeyError:
            return f"Text not found: {section}.{subsection}.{key}"
    
    def get_html_content(self, section, subsection):
        """
        Gets the complete HTML content for a QTextEdit
        
        Args:
            section (str): Main section
            subsection (str): Specific subsection
            
        Returns:
            str: Complete HTML to display in QTextEdit
        """
        content = self.get_text(section, subsection, 'content')
        
        # HTML wrapper with base styles
        html_template = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /><style type="text/css">
p, li {{ white-space: pre-wrap; }}
hr {{ height: 1px; border-width: 0; }}
li.unchecked::marker {{ content: "\\2610"; }}
li.checked::marker {{ content: "\\2612"; }}
</style></head><body style=" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;">
{content}
</body></html>'''
        
        return html_template.format(content=content)
    
    def update_text(self, section, subsection, key, new_text):
        """
        Updates a specific text (useful for dynamic modifications)
        
        Args:
            section (str): Main section
            subsection (str): Specific subsection
            key (str): Specific key
            new_text (str): New text
        """
        if section in self.texts and subsection in self.texts[section]:
            self.texts[section][subsection][key] = new_text
    
    def get_all_sections(self):
        """
        Returns all available sections
        
        Returns:
            list: List of section names
        """
        return list(self.texts.keys())
    
    def get_subsections(self, section):
        """
        Returns all subsections of a specific section
        
        Args:
            section (str): Section name
            
        Returns:
            list: List of subsection names
        """
        return list(self.texts.get(section, {}).keys())

# Global instance of the text manager
text_manager = TextManager()