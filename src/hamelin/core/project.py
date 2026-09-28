"""
Project Metadata System for HAMELIN

This module manages clinical research project metadata, including:
- Study identification and ethics approval
- Team information (investigators, contacts)
- Temporal data (dates, timelines)
- Study design and objectives
- Population criteria and sample size
- Project persistence and directory management

Author: AI Assistant
Date: February 18, 2026
Version: 2.0
"""

from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import re
import shutil

from hamelin.utils.logger import log
from hamelin.utils.exceptions import (
    ValidationError,
    DataLoadError,
    DataSaveError
)


@dataclass
class ProjectMetadata:
    """
    Complete metadata for a clinical research project.
    
    This dataclass stores all essential information about a clinical study,
    including identification, team, timeline, objectives, and population criteria.
    
    Example:
        >>> metadata = ProjectMetadata(
        ...     name="Ultra-Processed Foods Study",
        ...     short_name="UPS",
        ...     protocol_number="UPS-2024-001",
        ...     principal_investigator="Dr. Jane Smith",
        ...     contact_email="j.smith@hospital.edu",
        ...     institution="General Hospital",
        ...     target_sample_size=100,
        ...     study_type="Observational Study",
        ...     primary_objective="Assess UPF consumption patterns"
        ... )
        >>> metadata.validate_all()
        []  # No errors
    """
    
    # Identification
    name: str                                       # Full project name
    short_name: str                                 # Abbreviated name (for files)
    protocol_number: str                            # Study protocol ID
    
    # Ethics & Approval
    ethics_approval_number: str = ""
    ethics_committee: str = ""
    approval_date: Optional[date] = None
    approved_by: List[str] = field(default_factory=list)
    
    # Team
    principal_investigator: str = ""
    co_investigators: List[str] = field(default_factory=list)
    contact_email: str = ""
    institution: str = ""
    
    # Temporal
    first_patient_date: Optional[date] = None
    estimated_completion_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    
    # Study Design
    study_type: str = "Observational Study"          # Patient Registry, Observational Study, Clinical Trial
    primary_objective: str = ""
    secondary_objectives: List[str] = field(default_factory=list)
    
    # Population
    target_sample_size: int = 0
    inclusion_criteria_summary: str = ""
    exclusion_criteria_summary: str = ""
    
    # Description
    background: str = ""
    hypothesis: str = ""
    
    # Metadata
    version: str = "1.0"
    hamelin_version: str = "0.1.0"
    
    def __post_init__(self):
        """Validate required fields immediately after initialization."""
        errors = self.validate_required_fields()
        if errors:
            raise ValidationError(
                '; '.join(errors)
            )
    
    def validate_required_fields(self) -> List[str]:
        """
        Validate that all required fields are present and non-empty.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Required string fields
        if not self.name or not self.name.strip():
            errors.append("Project name is required")
        elif len(self.name) > 200:
            errors.append("Project name must be ≤ 200 characters")
        
        if not self.short_name or not self.short_name.strip():
            errors.append("Short name is required")
        elif len(self.short_name) > 50:
            errors.append("Short name must be ≤ 50 characters")
        
        if not self.protocol_number or not self.protocol_number.strip():
            errors.append("Protocol number is required")
        
        if not self.principal_investigator or not self.principal_investigator.strip():
            errors.append("Principal investigator is required")
        
        if not self.contact_email or not self.contact_email.strip():
            errors.append("Contact email is required")
        
        if not self.institution or not self.institution.strip():
            errors.append("Institution is required")
        
        # Validate target sample size
        if self.target_sample_size <= 0:
            errors.append("Target sample size must be positive")
        
        return errors
    
    def validate_email(self) -> List[str]:
        """
        Validate email format.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        if self.contact_email:
            # Basic email validation regex
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, self.contact_email):
                errors.append(f"Invalid email format: {self.contact_email}")
        
        return errors
    
    def validate_dates(self) -> List[str]:
        """
        Validate date chronology and logic.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Approval before first patient
        if self.approval_date and self.first_patient_date:
            if self.approval_date > self.first_patient_date:
                errors.append(
                    "Approval date cannot be after first patient date"
                )
        
        # First patient before estimated completion
        if self.first_patient_date and self.estimated_completion_date:
            if self.first_patient_date > self.estimated_completion_date:
                errors.append(
                    "First patient date cannot be after estimated completion"
                )
        
        # First patient before actual completion
        if self.first_patient_date and self.actual_completion_date:
            if self.first_patient_date > self.actual_completion_date:
                errors.append(
                    "First patient date cannot be after actual completion"
                )
        
        # Actual completion should be after estimated (warning, not error)
        # This is acceptable - studies often extend beyond estimates
        
        return errors
    
    def validate_sample_size(self) -> List[str]:
        """
        Validate sample size is reasonable.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        if self.target_sample_size < 0:
            errors.append("Sample size cannot be negative")
        elif self.target_sample_size == 0:
            errors.append("Sample size must be specified")
        elif self.target_sample_size > 1000000:
            errors.append("Sample size seems unreasonably large (> 1 million)")
        
        return errors
    
    def validate_study_type(self) -> List[str]:
        """
        Validate study type is from accepted list.
        
        Returns:
            List of error messages (empty if valid)
        """
        valid_types = [
            "Patient Registry",
            "Observational Study",
            "Clinical Trial",
        ]
        
        errors = []
        
        if self.study_type and self.study_type not in valid_types:
            # Not a hard error - allow custom types but log warning
            log.warning(
                f"Study type '{self.study_type}' not in standard list. "
                f"Valid types: {', '.join(valid_types)}"
            )
        
        return errors
    
    def validate_all(self) -> List[str]:
        """
        Run all validation checks.
        
        Returns:
            List of all error messages (empty if fully valid)
        """
        errors = []
        errors.extend(self.validate_required_fields())
        errors.extend(self.validate_email())
        errors.extend(self.validate_dates())
        errors.extend(self.validate_sample_size())
        errors.extend(self.validate_study_type())
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metadata to JSON-serializable dictionary.
        
        Returns:
            Dictionary with all fields, dates as ISO strings
        """
        data = asdict(self)
        
        # Convert date objects to ISO strings
        if self.approval_date:
            data['approval_date'] = self.approval_date.isoformat()
        
        if self.first_patient_date:
            data['first_patient_date'] = self.first_patient_date.isoformat()
        
        if self.estimated_completion_date:
            data['estimated_completion_date'] = self.estimated_completion_date.isoformat()
        
        if self.actual_completion_date:
            data['actual_completion_date'] = self.actual_completion_date.isoformat()
        
        # Convert datetime objects to ISO strings
        data['created_at'] = self.created_at.isoformat()
        data['last_modified'] = self.last_modified.isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectMetadata':
        """
        Create ProjectMetadata from dictionary.
        
        Args:
            data: Dictionary with metadata fields
            
        Returns:
            ProjectMetadata instance
        """
        # Convert ISO strings back to date objects
        if data.get('approval_date'):
            data['approval_date'] = date.fromisoformat(data['approval_date'])
        
        if data.get('first_patient_date'):
            data['first_patient_date'] = date.fromisoformat(data['first_patient_date'])
        
        if data.get('estimated_completion_date'):
            data['estimated_completion_date'] = date.fromisoformat(data['estimated_completion_date'])
        
        if data.get('actual_completion_date'):
            data['actual_completion_date'] = date.fromisoformat(data['actual_completion_date'])
        
        # Convert ISO strings back to datetime objects
        if data.get('created_at'):
            if isinstance(data['created_at'], str):
                data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if data.get('last_modified'):
            if isinstance(data['last_modified'], str):
                data['last_modified'] = datetime.fromisoformat(data['last_modified'])
        
        return cls(**data)
    
    def summary(self) -> str:
        """
        Generate human-readable summary of project metadata.
        
        Returns:
            Multi-line string with key information
        """
        lines = [
            f"{'=' * 60}",
            f"PROJECT: {self.name} ({self.short_name})",
            f"{'=' * 60}",
            "",
            f"Protocol Number: {self.protocol_number}",
            f"Study Type: {self.study_type}",
            f"Principal Investigator: {self.principal_investigator}",
            f"Institution: {self.institution}",
            "",
            f"Target Sample Size: {self.target_sample_size} patients",
            "",
        ]
        
        if self.first_patient_date:
            lines.append(f"First Patient: {self.first_patient_date.isoformat()}")
        
        if self.estimated_completion_date:
            lines.append(f"Estimated Completion: {self.estimated_completion_date.isoformat()}")
        
        if self.actual_completion_date:
            lines.append(f"Actual Completion: {self.actual_completion_date.isoformat()}")
        
        if self.first_patient_date or self.estimated_completion_date or self.actual_completion_date:
            lines.append("")
        
        if self.primary_objective:
            lines.append(f"Primary Objective: {self.primary_objective}")
        
        if self.secondary_objectives:
            lines.append(f"Secondary Objectives: {len(self.secondary_objectives)}")
        
        lines.append("")
        lines.append(f"Created: {self.created_at.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"Last Modified: {self.last_modified.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"{'=' * 60}")
        
        return "\n".join(lines)
    
    def update_timestamp(self):
        """Update the last_modified timestamp to now."""
        self.last_modified = datetime.now()


class ProjectRepository:
    """
    Manages project metadata persistence and organization.
    
    This class handles:
    - Creating new projects with directory structure
    - Saving/loading project metadata to/from JSON
    - Listing and managing multiple projects
    - Validating project data
    
    Directory structure created for each project:
        Projects/
        └── {project_short_name}/
            ├── metadata.json          # Project metadata
            ├── data/                  # Project-specific datasets
            ├── results/               # Analysis results
            │   ├── table1/           # Table 1 outputs
            │   ├── models/           # Trained models
            │   └── reports/          # Generated reports
            └── recruitment_log.json   # Recruitment tracking data
    
    Example:
        >>> repo = ProjectRepository()
        >>> metadata = ProjectMetadata(name="My Study", ...)
        >>> project_path = repo.create_project(metadata)
        >>> repo.save(metadata)
        >>> loaded = repo.load("My Study")
        >>> projects = repo.list_projects()
    """
    
    # Default Projects/ directory: always anchored to the repo root regardless of CWD.
    # src/hamelin/core/project.py → parent.parent.parent.parent == repo root
    _DEFAULT_BASE = Path(__file__).resolve().parent.parent.parent.parent / "workspace" / "Projects"

    def __init__(self, base_path: Path = None):
        """
        Initialize repository with base path.
        
        Args:
            base_path: Root directory for all projects.
                       Defaults to <repo_root>/Projects/ so the location
                       is independent of the working directory.
        """
        self.base_path = Path(base_path) if base_path is not None else ProjectRepository._DEFAULT_BASE
        
        # Create base Projects directory if it doesn't exist
        if not self.base_path.exists():
            self.base_path.mkdir(parents=True, exist_ok=True)
            log.info(f"Created Projects directory at {self.base_path}")
    
    def create_project(self, metadata: ProjectMetadata) -> Path:
        """
        Create a new project with complete directory structure.
        
        Args:
            metadata: Project metadata to save
            
        Returns:
            Path to created project directory
            
        Raises:
            ValidationError: If metadata is invalid
            DataSaveError: If directory creation fails
        """
        # Validate metadata first
        errors = metadata.validate_all()
        if errors:
            raise ValidationError(
                f"Cannot create project with invalid metadata: {'; '.join(errors)}"
            )
        
        # Get project path
        project_path = self.get_project_path(metadata.short_name)
        
        # Check if project already exists
        if project_path.exists():
            raise DataSaveError(
                f"Project '{metadata.short_name}' already exists at {project_path}"
            )
        
        try:
            # Create directory structure
            self._create_directory_structure(project_path)
            log.info(f"Created project directory structure at {project_path}")
            
            # Save metadata
            self.save(metadata)
            log.info(f"Created project '{metadata.name}' ({metadata.short_name})")
            
            return project_path
            
        except Exception as e:
            # Clean up on failure
            if project_path.exists():
                shutil.rmtree(project_path)
            raise DataSaveError(f"Failed to create project: {e}") from e
    
    def save(self, metadata: ProjectMetadata) -> None:
        """
        Save project metadata to JSON file.
        
        Args:
            metadata: Project metadata to save
            
        Raises:
            ValidationError: If metadata is invalid
            DataSaveError: If save operation fails
        """
        # Validate before saving
        errors = metadata.validate_all()
        if errors:
            raise ValidationError(
                f"Cannot save invalid metadata: {'; '.join(errors)}"
            )
        
        # Update timestamp
        metadata.update_timestamp()
        
        # Get project path
        project_path = self.get_project_path(metadata.short_name)
        metadata_file = project_path / "metadata.json"
        
        # Create project directory if it doesn't exist
        if not project_path.exists():
            self._create_directory_structure(project_path)
        
        try:
            # Serialize to JSON
            data = metadata.to_dict()
            
            # Write to file with pretty formatting
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            log.info(f"Saved metadata for project '{metadata.short_name}' to {metadata_file}")
            
        except Exception as e:
            raise DataSaveError(f"Failed to save metadata: {e}") from e
    
    def load(self, project_name: str) -> ProjectMetadata:
        """
        Load project metadata from JSON file.
        
        Args:
            project_name: Short name of the project to load
            
        Returns:
            ProjectMetadata instance
            
        Raises:
            DataLoadError: If project doesn't exist or file is corrupted
        """
        if not self.exists(project_name):
            raise DataLoadError(f"Project '{project_name}' does not exist")
        
        project_path = self.get_project_path(project_name)
        metadata_file = project_path / "metadata.json"
        
        try:
            # Read JSON file
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Deserialize to ProjectMetadata
            metadata = ProjectMetadata.from_dict(data)
            
            log.info(f"Loaded metadata for project '{project_name}'")
            return metadata
            
        except json.JSONDecodeError as e:
            raise DataLoadError(
                f"Corrupted metadata file for project '{project_name}': {e}"
            ) from e
        except Exception as e:
            raise DataLoadError(
                f"Failed to load metadata for project '{project_name}': {e}"
            ) from e
    
    def list_projects(self) -> List[str]:
        """
        List all available projects.
        
        Returns:
            List of project short names
        """
        if not self.base_path.exists():
            return []
        
        projects = []
        
        for item in self.base_path.iterdir():
            # Check if it's a directory with metadata.json
            if item.is_dir():
                metadata_file = item / "metadata.json"
                if metadata_file.exists():
                    projects.append(item.name)
        
        return sorted(projects)
    
    def exists(self, project_name: str) -> bool:
        """
        Check if a project exists.
        
        Args:
            project_name: Short name of the project
            
        Returns:
            True if project exists, False otherwise
        """
        project_path = self.get_project_path(project_name)
        metadata_file = project_path / "metadata.json"
        
        return project_path.exists() and metadata_file.exists()
    
    def delete_project(self, project_name: str, confirm: bool = False) -> None:
        """
        Delete a project and all its data.
        
        Args:
            project_name: Short name of the project to delete
            confirm: Must be True to actually delete (safety measure)
            
        Raises:
            ValueError: If confirm is not True
            DataLoadError: If project doesn't exist
        """
        if not confirm:
            raise ValueError(
                "Must set confirm=True to delete project. This operation cannot be undone."
            )
        
        if not self.exists(project_name):
            raise DataLoadError(f"Project '{project_name}' does not exist")
        
        project_path = self.get_project_path(project_name)
        
        try:
            shutil.rmtree(project_path)
            log.warning(f"Deleted project '{project_name}' and all data at {project_path}")
            
        except Exception as e:
            raise DataSaveError(f"Failed to delete project: {e}") from e
    
    def get_project_path(self, project_name: str) -> Path:
        """
        Get path to project directory.
        
        Args:
            project_name: Short name of the project
            
        Returns:
            Path to project directory
        """
        return self.base_path / project_name
    
    def validate_metadata(self, metadata: ProjectMetadata) -> List[str]:
        """
        Validate project metadata.
        
        Args:
            metadata: Metadata to validate
            
        Returns:
            List of error messages (empty if valid)
        """
        return metadata.validate_all()
    
    def _create_directory_structure(self, project_path: Path) -> None:
        """
        Create standard directory structure for a project.
        
        Args:
            project_path: Path where project will be created
        """
        # Create main project directory
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (project_path / "data").mkdir(exist_ok=True)
        (project_path / "results").mkdir(exist_ok=True)
        (project_path / "results" / "table1").mkdir(exist_ok=True)
        (project_path / "results" / "models").mkdir(exist_ok=True)
        (project_path / "results" / "reports").mkdir(exist_ok=True)
        
        log.debug(f"Created directory structure for project at {project_path}")


# Convenience function for quick project creation
def create_sample_project() -> ProjectMetadata:
    """
    Create a sample project metadata for demonstration/testing.
    
    Returns:
        Sample ProjectMetadata instance
    """
    sample = ProjectMetadata(
        name="Ultra-Processed Foods Study",
        short_name="UPS",
        protocol_number="UPS-2024-001",
        ethics_approval_number="ETH-2024-123",
        ethics_committee="Hospital Ethics Committee",
        approval_date=date(2024, 1, 15),
        principal_investigator="Dr. Jane Smith",
        co_investigators=["Dr. John Doe", "Dr. Maria Garcia"],
        contact_email="jane.smith@hospital.edu",
        institution="General Hospital Research Institute",
        first_patient_date=date(2024, 2, 1),
        estimated_completion_date=date(2025, 12, 31),
        study_type="Observational Study",
        primary_objective="To assess the relationship between ultra-processed food consumption and metabolic outcomes in adults",
        secondary_objectives=[
            "Characterize dietary patterns in the study population",
            "Identify barriers to healthy eating",
            "Evaluate socioeconomic factors influencing food choices"
        ],
        target_sample_size=100,
        inclusion_criteria_summary="Adults aged 18-65, able to provide informed consent",
        exclusion_criteria_summary="Pregnancy, eating disorders, inability to complete questionnaires",
        background="Ultra-processed foods (UPF) are industrially manufactured products with multiple ingredients. Recent evidence suggests UPF consumption is associated with adverse health outcomes.",
        hypothesis="Higher UPF consumption is associated with increased prevalence of metabolic syndrome."
    )
    
    return sample
