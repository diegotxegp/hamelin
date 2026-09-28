"""
Project Metadata Model
~~~~~~~~~~~~~~~~~~~~~

Model for storing clinical research project metadata.

Includes:
- Study information (name, PI, institution)
- Study dates (start, end, data cutoff)
- Patient information (target, recruited)
- Study type and phase
- IRB/Ethics information
- Contact information

This metadata is used for:
- Table 1 generation
- Recruitment forecasting
- Status dashboard
- Report generation
"""

from datetime import datetime, date
from typing import Dict, Any, Optional
from pathlib import Path

from hamelin.model.base_model import BaseModel
from hamelin.utils.logger import log


class ProjectMetadata(BaseModel):
    """
    Clinical research project metadata.
    
    Essential information about the research study that will be used
    throughout the application for analysis, reporting, and tracking.
    """
    
    def __init__(self):
        """Initialize project metadata with default values."""
        super().__init__()
        
        # Study Information
        self.study_name: str = ""
        self.study_acronym: str = ""
        self.principal_investigator: str = ""
        self.institution: str = ""
        self.department: str = ""
        
        # Study Classification
        self.study_type: str = ""  # e.g., "Observational", "Interventional"
        self.study_phase: str = ""  # e.g., "Phase I", "Phase II", etc.
        self.study_design: str = ""  # e.g., "Retrospective", "Prospective"
        
        # Dates
        self.start_date: Optional[date] = None
        self.end_date: Optional[date] = None
        self.data_cutoff_date: Optional[date] = None
        
        # Patient Information
        self.target_patients: Optional[int] = None
        self.recruited_patients: int = 0
        
        # Ethics & Regulatory
        self.irb_approval_number: str = ""
        self.irb_approval_date: Optional[date] = None
        self.ethics_committee: str = ""
        
        # Contact Information
        self.contact_email: str = ""
        self.contact_phone: str = ""
        
        # Additional Information
        self.description: str = ""
        self.keywords: str = ""  # Comma-separated
        self.funding_source: str = ""
        
        # Clinical Trial Registry
        self.registry_id: str = ""  # e.g., NCT number
        self.registry_name: str = ""  # e.g., "ClinicalTrials.gov"
    
    def validate(self) -> bool:
        """
        Validate project metadata.
        
        Returns:
            True if all required fields are valid
        """
        self.clear_errors()
        
        # Required fields
        self.validate_required("study_name", self.study_name)
        self.validate_required("principal_investigator", self.principal_investigator)
        self.validate_required("institution", self.institution)
        
        # Type validations
        self.validate_type("target_patients", self.target_patients, int)
        self.validate_type("recruited_patients", self.recruited_patients, int)
        
        # Range validations
        if self.target_patients is not None:
            self.validate_range("target_patients", self.target_patients, min_value=1)
        
        self.validate_range("recruited_patients", self.recruited_patients, min_value=0)
        
        # Date validations
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                self.add_error("Study end date must be after start date")
        
        if self.start_date and self.data_cutoff_date:
            if self.data_cutoff_date < self.start_date:
                self.add_error("Data cutoff date cannot be before study start date")
        
        # Patient count validation
        if self.target_patients and self.recruited_patients > self.target_patients:
            self.add_error("Recruited patients cannot exceed target")
        
        # String length validations
        self.validate_length("study_name", self.study_name, min_length=3, max_length=200)
        self.validate_length("study_acronym", self.study_acronym, max_length=20)
        
        return not self.has_errors()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metadata to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'study_name': self.study_name,
            'study_acronym': self.study_acronym,
            'principal_investigator': self.principal_investigator,
            'institution': self.institution,
            'department': self.department,
            'study_type': self.study_type,
            'study_phase': self.study_phase,
            'study_design': self.study_design,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'data_cutoff_date': self.data_cutoff_date.isoformat() if self.data_cutoff_date else None,
            'target_patients': self.target_patients,
            'recruited_patients': self.recruited_patients,
            'irb_approval_number': self.irb_approval_number,
            'irb_approval_date': self.irb_approval_date.isoformat() if self.irb_approval_date else None,
            'ethics_committee': self.ethics_committee,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'description': self.description,
            'keywords': self.keywords,
            'funding_source': self.funding_source,
            'registry_id': self.registry_id,
            'registry_name': self.registry_name
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load metadata from dictionary.
        
        Args:
            data: Dictionary with metadata
        """
        self.study_name = data.get('study_name', '')
        self.study_acronym = data.get('study_acronym', '')
        self.principal_investigator = data.get('principal_investigator', '')
        self.institution = data.get('institution', '')
        self.department = data.get('department', '')
        self.study_type = data.get('study_type', '')
        self.study_phase = data.get('study_phase', '')
        self.study_design = data.get('study_design', '')
        
        # Parse dates
        if data.get('start_date'):
            self.start_date = date.fromisoformat(data['start_date'])
        if data.get('end_date'):
            self.end_date = date.fromisoformat(data['end_date'])
        if data.get('data_cutoff_date'):
            self.data_cutoff_date = date.fromisoformat(data['data_cutoff_date'])
        if data.get('irb_approval_date'):
            self.irb_approval_date = date.fromisoformat(data['irb_approval_date'])
        
        self.target_patients = data.get('target_patients')
        self.recruited_patients = data.get('recruited_patients', 0)
        self.irb_approval_number = data.get('irb_approval_number', '')
        self.ethics_committee = data.get('ethics_committee', '')
        self.contact_email = data.get('contact_email', '')
        self.contact_phone = data.get('contact_phone', '')
        self.description = data.get('description', '')
        self.keywords = data.get('keywords', '')
        self.funding_source = data.get('funding_source', '')
        self.registry_id = data.get('registry_id', '')
        self.registry_name = data.get('registry_name', '')
        
        self.mark_clean()
    
    def get_recruitment_status(self) -> Dict[str, Any]:
        """
        Get recruitment status summary.
        
        Returns:
            Dictionary with recruitment statistics
        """
        status = {
            'recruited': self.recruited_patients,
            'target': self.target_patients,
            'remaining': None,
            'percentage': None,
            'status': 'Unknown'
        }
        
        if self.target_patients:
            status['remaining'] = self.target_patients - self.recruited_patients
            status['percentage'] = (self.recruited_patients / self.target_patients) * 100
            
            if self.recruited_patients >= self.target_patients:
                status['status'] = 'Completed'
            elif self.recruited_patients >= self.target_patients * 0.75:
                status['status'] = 'Nearly Complete'
            elif self.recruited_patients >= self.target_patients * 0.5:
                status['status'] = 'On Track'
            elif self.recruited_patients >= self.target_patients * 0.25:
                status['status'] = 'In Progress'
            else:
                status['status'] = 'Early Stage'
        
        return status
    
    def get_study_duration_days(self) -> Optional[int]:
        """
        Calculate study duration in days.
        
        Returns:
            Number of days, or None if dates not set
        """
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None
    
    def is_active(self) -> bool:
        """
        Check if study is currently active.
        
        Returns:
            True if study is active based on dates
        """
        today = date.today()
        
        if self.start_date and self.start_date > today:
            return False  # Not started yet
        
        if self.end_date and self.end_date < today:
            return False  # Already ended
        
        return True
    
    def get_summary(self) -> str:
        """
        Get a brief summary of the project.
        
        Returns:
            Human-readable summary string
        """
        summary = f"{self.study_name}"
        
        if self.study_acronym:
            summary += f" ({self.study_acronym})"
        
        summary += f"\nPI: {self.principal_investigator}"
        summary += f"\nInstitution: {self.institution}"
        
        if self.target_patients:
            recruitment = self.get_recruitment_status()
            summary += f"\nRecruitment: {recruitment['recruited']}/{recruitment['target']} "
            summary += f"({recruitment['percentage']:.1f}%) - {recruitment['status']}"
        
        if self.start_date:
            summary += f"\nStart Date: {self.start_date.strftime('%Y-%m-%d')}"
        
        return summary


if __name__ == "__main__":
    # Test ProjectMetadata
    print("Testing ProjectMetadata...\n")
    
    # Create metadata
    metadata = ProjectMetadata()
    metadata.study_name = "Urological Prosthetic Surgery Study"
    metadata.study_acronym = "UPS"
    metadata.principal_investigator = "Dr. Diego"
    metadata.institution = "University Hospital"
    metadata.department = "Urology"
    metadata.study_type = "Observational"
    metadata.study_design = "Retrospective"
    metadata.start_date = date(2020, 1, 1)
    metadata.end_date = date(2025, 12, 31)
    metadata.target_patients = 100
    metadata.recruited_patients = 95
    metadata.irb_approval_number = "IRB-2019-12345"
    metadata.contact_email = "diego@hospital.com"
    metadata.description = "Study on prosthetic urological surgeries"
    
    # Validate
    if metadata.validate():
        print("✓ Metadata is valid\n")
    else:
        print("✗ Validation errors:")
        for error in metadata.get_errors():
            print(f"  - {error}")
    
    # Get summary
    print(metadata.get_summary())
    
    # Get recruitment status
    print(f"\nRecruitment Status:")
    status = metadata.get_recruitment_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Test serialization
    json_str = metadata.to_json()
    print(f"\n✓ Serialized to JSON ({len(json_str)} chars)")
    
    # Test deserialization
    metadata2 = ProjectMetadata()
    metadata2.from_json(json_str)
    print(f"✓ Deserialized: {metadata2.study_name}")
    
    # Test file save/load
    test_file = Path("/tmp/test_metadata.json")
    metadata.to_json(filepath=test_file)
    
    metadata3 = ProjectMetadata()
    metadata3.from_json(filepath=test_file)
    print(f"✓ Saved and loaded from file: {metadata3.study_acronym}")
    
    print("\n✓ ProjectMetadata test complete")
