"""
Comprehensive tests for Project Metadata System

Tests ProjectMetadata dataclass and ProjectRepository persistence layer.

Author: AI Assistant
Date: February 18, 2026
"""

import pytest
from datetime import date, datetime
from pathlib import Path
import json
import shutil

from hamelin.core.project import (
    ProjectMetadata,
    ProjectRepository,
    create_sample_project
)
from hamelin.utils.exceptions import ValidationError, DataLoadError, DataSaveError


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def valid_metadata():
    """Create valid project metadata for testing."""
    return ProjectMetadata(
        name="Test Clinical Study",
        short_name="TCS",
        protocol_number="TCS-2026-001",
        principal_investigator="Dr. Test Investigator",
        contact_email="test@example.com",
        institution="Test Hospital",
        target_sample_size=50,
        study_type="RCT"
    )


@pytest.fixture
def complete_metadata():
    """Create metadata with all fields populated."""
    return ProjectMetadata(
        name="Complete Test Study",
        short_name="CTS",
        protocol_number="CTS-2026-001",
        ethics_approval_number="ETH-2026-001",
        ethics_committee="Research Ethics Board",
        approval_date=date(2026, 1, 1),
        approved_by=["Dr. Smith", "Dr. Jones"],
        principal_investigator="Dr. Lead Investigator",
        co_investigators=["Dr. Co-I 1", "Dr. Co-I 2"],
        contact_email="lead@example.com",
        institution="Complete Hospital",
        first_patient_date=date(2026, 2, 1),
        estimated_completion_date=date(2027, 12, 31),
        study_type="RCT",
        primary_objective="Test the intervention vs control",
        secondary_objectives=[
            "Assess safety",
            "Measure quality of life",
            "Evaluate cost-effectiveness"
        ],
        target_sample_size=200,
        inclusion_criteria_summary="Adults 18-65, diagnosis confirmed",
        exclusion_criteria_summary="Pregnant, severe comorbidities",
        background="This is background text for the study.",
        hypothesis="Intervention will be superior to control."
    )


@pytest.fixture
def temp_repo(tmp_path):
    """Create temporary repository for testing."""
    repo_path = tmp_path / "test_projects"
    repo = ProjectRepository(base_path=repo_path)
    yield repo
    # Cleanup
    if repo_path.exists():
        shutil.rmtree(repo_path)


# ============================================================================
# TEST PROJECTMETADATA - CREATION & VALIDATION
# ============================================================================

class TestProjectMetadataCreation:
    """Test ProjectMetadata creation and basic validation."""
    
    def test_valid_metadata_creation(self, valid_metadata):
        """Test creating metadata with valid required fields."""
        assert valid_metadata.name == "Test Clinical Study"
        assert valid_metadata.short_name == "TCS"
        assert valid_metadata.protocol_number == "TCS-2026-001"
        assert valid_metadata.target_sample_size == 50
    
    def test_missing_name_raises_error(self):
        """Test that missing name raises ValidationError."""
        with pytest.raises(ValidationError):
            ProjectMetadata(
                name="",
                short_name="TEST",
                protocol_number="TEST-001",
                principal_investigator="Dr. Test",
                contact_email="test@example.com",
                institution="Test Hospital",
                target_sample_size=50
            )
    
    def test_missing_short_name_raises_error(self):
        """Test that missing short_name raises ValidationError."""
        with pytest.raises(ValidationError):
            ProjectMetadata(
                name="Test Study",
                short_name="",
                protocol_number="TEST-001",
                principal_investigator="Dr. Test",
                contact_email="test@example.com",
                institution="Test Hospital",
                target_sample_size=50
            )
    
    def test_missing_protocol_number_raises_error(self):
        """Test that missing protocol_number raises ValidationError."""
        with pytest.raises(ValidationError):
            ProjectMetadata(
                name="Test Study",
                short_name="TEST",
                protocol_number="",
                principal_investigator="Dr. Test",
                contact_email="test@example.com",
                institution="Test Hospital",
                target_sample_size=50
            )
    
    def test_invalid_sample_size_raises_error(self):
        """Test that zero/negative sample size raises ValidationError."""
        with pytest.raises(ValidationError):
            ProjectMetadata(
                name="Test Study",
                short_name="TEST",
                protocol_number="TEST-001",
                principal_investigator="Dr. Test",
                contact_email="test@example.com",
                institution="Test Hospital",
                target_sample_size=0
            )
    
    def test_default_timestamps(self, valid_metadata):
        """Test that created_at and last_modified are set automatically."""
        assert isinstance(valid_metadata.created_at, datetime)
        assert isinstance(valid_metadata.last_modified, datetime)
        assert valid_metadata.created_at <= datetime.now()
        assert valid_metadata.last_modified <= datetime.now()


class TestProjectMetadataValidation:
    """Test various validation methods."""
    
    def test_validate_required_fields_all_present(self, valid_metadata):
        """Test validation passes with all required fields."""
        errors = valid_metadata.validate_required_fields()
        assert errors == []
    
    def test_validate_required_fields_missing_name(self):
        """Test validation catches missing name."""
        metadata = ProjectMetadata(
            name="Valid Name",
            short_name="VN",
            protocol_number="VN-001",
            principal_investigator="Dr. Test",
            contact_email="test@example.com",
            institution="Test Hospital",
            target_sample_size=50
        )
        metadata.name = ""
        errors = metadata.validate_required_fields()
        assert any("name is required" in e.lower() for e in errors)
    
    def test_validate_email_valid_format(self, valid_metadata):
        """Test valid email passes validation."""
        errors = valid_metadata.validate_email()
        assert errors == []
    
    def test_validate_email_invalid_format(self, valid_metadata):
        """Test invalid email format is caught."""
        valid_metadata.contact_email = "not-an-email"
        errors = valid_metadata.validate_email()
        assert len(errors) > 0
        assert "Invalid email" in errors[0]
    
    def test_validate_dates_valid_chronology(self, complete_metadata):
        """Test dates in correct chronological order pass validation."""
        errors = complete_metadata.validate_dates()
        assert errors == []
    
    def test_validate_dates_approval_after_first_patient(self, complete_metadata):
        """Test that approval after first patient is caught."""
        complete_metadata.approval_date = date(2026, 3, 1)
        complete_metadata.first_patient_date = date(2026, 2, 1)
        errors = complete_metadata.validate_dates()
        assert len(errors) > 0
        assert "Approval date" in errors[0]
    
    def test_validate_dates_first_patient_after_completion(self, complete_metadata):
        """Test that first patient after completion is caught."""
        complete_metadata.first_patient_date = date(2028, 1, 1)
        complete_metadata.estimated_completion_date = date(2027, 12, 31)
        errors = complete_metadata.validate_dates()
        assert len(errors) > 0
        assert "First patient date" in errors[0]
    
    def test_validate_sample_size_positive(self, valid_metadata):
        """Test positive sample size is valid."""
        errors = valid_metadata.validate_sample_size()
        assert errors == []
    
    def test_validate_sample_size_negative(self, valid_metadata):
        """Test negative sample size is caught."""
        valid_metadata.target_sample_size = -10
        errors = valid_metadata.validate_sample_size()
        assert len(errors) > 0
        assert "negative" in errors[0].lower()
    
    def test_validate_sample_size_unreasonably_large(self, valid_metadata):
        """Test unreasonably large sample size triggers warning."""
        valid_metadata.target_sample_size = 2000000
        errors = valid_metadata.validate_sample_size()
        assert len(errors) > 0
        assert "unreasonably large" in errors[0].lower()
    
    def test_validate_all_combines_all_checks(self, valid_metadata):
        """Test validate_all runs all validation methods."""
        # Should pass with valid data
        errors = valid_metadata.validate_all()
        assert errors == []
        
        # Make multiple invalid changes
        valid_metadata.contact_email = "invalid"
        valid_metadata.target_sample_size = -5
        
        errors = valid_metadata.validate_all()
        assert len(errors) >= 2  # Should catch both errors


class TestProjectMetadataSerialization:
    """Test JSON serialization and deserialization."""
    
    def test_to_dict_includes_all_fields(self, complete_metadata):
        """Test to_dict includes all metadata fields."""
        data = complete_metadata.to_dict()
        
        assert data['name'] == "Complete Test Study"
        assert data['short_name'] == "CTS"
        assert data['target_sample_size'] == 200
        assert 'created_at' in data
        assert 'last_modified' in data
    
    def test_to_dict_converts_dates_to_iso(self, complete_metadata):
        """Test dates are converted to ISO format strings."""
        data = complete_metadata.to_dict()
        
        assert data['approval_date'] == "2026-01-01"
        assert data['first_patient_date'] == "2026-02-01"
        assert isinstance(data['approval_date'], str)
    
    def test_from_dict_roundtrip(self, complete_metadata):
        """Test to_dict → from_dict preserves all data."""
        data = complete_metadata.to_dict()
        restored = ProjectMetadata.from_dict(data)
        
        assert restored.name == complete_metadata.name
        assert restored.short_name == complete_metadata.short_name
        assert restored.approval_date == complete_metadata.approval_date
        assert restored.first_patient_date == complete_metadata.first_patient_date
        assert restored.target_sample_size == complete_metadata.target_sample_size
        assert restored.primary_objective == complete_metadata.primary_objective
    
    def test_from_dict_handles_none_dates(self, valid_metadata):
        """Test from_dict handles None dates correctly."""
        data = valid_metadata.to_dict()
        restored = ProjectMetadata.from_dict(data)
        
        assert restored.approval_date is None
        assert restored.first_patient_date is None


class TestProjectMetadataUtilityMethods:
    """Test utility methods like summary, update_timestamp."""
    
    def test_summary_generates_readable_text(self, complete_metadata):
        """Test summary method produces human-readable output."""
        summary = complete_metadata.summary()
        
        assert "Complete Test Study" in summary
        assert "CTS" in summary
        assert "Dr. Lead Investigator" in summary
        assert "200 patients" in summary
    
    def test_update_timestamp_changes_last_modified(self, valid_metadata):
        """Test update_timestamp updates last_modified field."""
        original_time = valid_metadata.last_modified
        
        # Wait a tiny bit to ensure time difference
        import time
        time.sleep(0.01)
        
        valid_metadata.update_timestamp()
        
        assert valid_metadata.last_modified > original_time


# ============================================================================
# TEST PROJECTREPOSITORY - PERSISTENCE & MANAGEMENT
# ============================================================================

class TestProjectRepositoryInitialization:
    """Test ProjectRepository initialization."""
    
    def test_repository_creates_base_directory(self, tmp_path):
        """Test repository creates Projects directory."""
        repo_path = tmp_path / "new_projects"
        repo = ProjectRepository(base_path=repo_path)
        
        assert repo_path.exists()
        assert repo_path.is_dir()
    
    def test_repository_uses_existing_directory(self, tmp_path):
        """Test repository works with existing directory."""
        repo_path = tmp_path / "existing_projects"
        repo_path.mkdir()
        
        repo = ProjectRepository(base_path=repo_path)
        assert repo.base_path == repo_path


class TestProjectRepositoryCreateProject:
    """Test project creation functionality."""
    
    def test_create_project_creates_directory_structure(self, temp_repo, valid_metadata):
        """Test create_project creates all subdirectories."""
        project_path = temp_repo.create_project(valid_metadata)
        
        assert project_path.exists()
        assert (project_path / "data").exists()
        assert (project_path / "results").exists()
        assert (project_path / "results" / "table1").exists()
        assert (project_path / "results" / "models").exists()
        assert (project_path / "results" / "reports").exists()
    
    def test_create_project_saves_metadata_json(self, temp_repo, valid_metadata):
        """Test create_project saves metadata.json file."""
        project_path = temp_repo.create_project(valid_metadata)
        metadata_file = project_path / "metadata.json"
        
        assert metadata_file.exists()
        
        with open(metadata_file, 'r') as f:
            data = json.load(f)
        
        assert data['name'] == "Test Clinical Study"
        assert data['short_name'] == "TCS"
    
    def test_create_project_rejects_duplicate(self, temp_repo, valid_metadata):
        """Test cannot create project with duplicate short_name."""
        temp_repo.create_project(valid_metadata)
        
        with pytest.raises(DataSaveError):
            temp_repo.create_project(valid_metadata)
    
    def test_create_project_validates_metadata(self, temp_repo):
        """Test create_project rejects invalid metadata."""
        invalid_metadata = ProjectMetadata(
            name="Test",
            short_name="T",
            protocol_number="T-001",
            principal_investigator="Dr. Test",
            contact_email="invalid-email",  # Invalid
            institution="Test",
            target_sample_size=50
        )
        
        with pytest.raises(ValidationError):
            temp_repo.create_project(invalid_metadata)


class TestProjectRepositorySaveLoad:
    """Test save and load functionality."""
    
    def test_save_creates_metadata_file(self, temp_repo, valid_metadata):
        """Test save creates metadata.json."""
        temp_repo.create_project(valid_metadata)
        
        # Modify and save again
        valid_metadata.primary_objective = "New objective"
        temp_repo.save(valid_metadata)
        
        metadata_file = temp_repo.get_project_path("TCS") / "metadata.json"
        assert metadata_file.exists()
    
    def test_save_updates_timestamp(self, temp_repo, valid_metadata):
        """Test save updates last_modified timestamp."""
        temp_repo.create_project(valid_metadata)
        original_time = valid_metadata.last_modified
        
        import time
        time.sleep(0.01)
        
        temp_repo.save(valid_metadata)
        assert valid_metadata.last_modified > original_time
    
    def test_load_retrieves_saved_metadata(self, temp_repo, complete_metadata):
        """Test load retrieves exactly what was saved."""
        temp_repo.create_project(complete_metadata)
        
        loaded = temp_repo.load("CTS")
        
        assert loaded.name == complete_metadata.name
        assert loaded.short_name == complete_metadata.short_name
        assert loaded.target_sample_size == complete_metadata.target_sample_size
        assert loaded.primary_objective == complete_metadata.primary_objective
    
    def test_load_nonexistent_project_raises_error(self, temp_repo):
        """Test loading nonexistent project raises DataLoadError."""
        with pytest.raises(DataLoadError):
            temp_repo.load("NONEXISTENT")
    
    def test_save_load_roundtrip_preserves_data(self, temp_repo, complete_metadata):
        """Test complete save/load cycle preserves all data."""
        temp_repo.create_project(complete_metadata)
        loaded = temp_repo.load("CTS")
        
        # Check all important fields
        assert loaded.name == complete_metadata.name
        assert loaded.approval_date == complete_metadata.approval_date
        assert loaded.first_patient_date == complete_metadata.first_patient_date
        assert loaded.secondary_objectives == complete_metadata.secondary_objectives
        assert loaded.co_investigators == complete_metadata.co_investigators


class TestProjectRepositoryManagement:
    """Test project listing and management."""
    
    def test_list_projects_returns_all_projects(self, temp_repo, valid_metadata, complete_metadata):
        """Test list_projects finds all created projects."""
        temp_repo.create_project(valid_metadata)
        temp_repo.create_project(complete_metadata)
        
        projects = temp_repo.list_projects()
        
        assert len(projects) == 2
        assert "TCS" in projects
        assert "CTS" in projects
    
    def test_list_projects_returns_empty_for_new_repo(self, temp_repo):
        """Test list_projects returns empty list for new repository."""
        projects = temp_repo.list_projects()
        assert projects == []
    
    def test_exists_returns_true_for_existing_project(self, temp_repo, valid_metadata):
        """Test exists returns True for created project."""
        temp_repo.create_project(valid_metadata)
        
        assert temp_repo.exists("TCS") is True
    
    def test_exists_returns_false_for_nonexistent_project(self, temp_repo):
        """Test exists returns False for nonexistent project."""
        assert temp_repo.exists("NONEXISTENT") is False
    
    def test_get_project_path_returns_correct_path(self, temp_repo):
        """Test get_project_path returns expected path."""
        path = temp_repo.get_project_path("TEST")
        
        assert "TEST" in str(path)
        assert path.parent == temp_repo.base_path
    
    def test_delete_project_removes_directory(self, temp_repo, valid_metadata):
        """Test delete_project removes project directory."""
        temp_repo.create_project(valid_metadata)
        assert temp_repo.exists("TCS")
        
        temp_repo.delete_project("TCS", confirm=True)
        
        assert not temp_repo.exists("TCS")
    
    def test_delete_project_requires_confirmation(self, temp_repo, valid_metadata):
        """Test delete_project requires confirm=True."""
        temp_repo.create_project(valid_metadata)
        
        with pytest.raises(ValueError):
            temp_repo.delete_project("TCS", confirm=False)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestProjectMetadataIntegration:
    """Integration tests with complete workflows."""
    
    def test_complete_project_lifecycle(self, temp_repo):
        """Test complete project lifecycle: create, modify, save, load, delete."""
        # Create project
        metadata = ProjectMetadata(
            name="Lifecycle Test Study",
            short_name="LTS",
            protocol_number="LTS-2026-001",
            principal_investigator="Dr. Lifecycle",
            contact_email="lifecycle@test.com",
            institution="Test Hospital",
            target_sample_size=75,
            study_type="Cohort"
        )
        
        # Create
        project_path = temp_repo.create_project(metadata)
        assert project_path.exists()
        
        # Modify
        metadata.primary_objective = "Updated objective"
        metadata.first_patient_date = date(2026, 3, 1)
        temp_repo.save(metadata)
        
        # Load and verify
        loaded = temp_repo.load("LTS")
        assert loaded.primary_objective == "Updated objective"
        assert loaded.first_patient_date == date(2026, 3, 1)
        
        # Delete
        temp_repo.delete_project("LTS", confirm=True)
        assert not temp_repo.exists("LTS")
    
    def test_multiple_projects_coexist(self, temp_repo):
        """Test multiple projects can coexist in same repository."""
        # Create 3 different projects
        for i in range(1, 4):
            metadata = ProjectMetadata(
                name=f"Study {i}",
                short_name=f"S{i}",
                protocol_number=f"S{i}-2026-001",
                principal_investigator=f"Dr. {i}",
                contact_email=f"dr{i}@test.com",
                institution="Test Hospital",
                target_sample_size=i * 25
            )
            temp_repo.create_project(metadata)
        
        # Verify all exist
        projects = temp_repo.list_projects()
        assert len(projects) == 3
        assert all(f"S{i}" in projects for i in range(1, 4))
        
        # Load and verify each
        for i in range(1, 4):
            loaded = temp_repo.load(f"S{i}")
            assert loaded.name == f"Study {i}"
            assert loaded.target_sample_size == i * 25


class TestSampleProjectCreation:
    """Test the create_sample_project convenience function."""
    
    def test_create_sample_project_returns_valid_metadata(self):
        """Test create_sample_project returns valid metadata."""
        sample = create_sample_project()
        
        assert sample.name == "Ultra-Processed Foods Study"
        assert sample.short_name == "UPS"
        assert sample.target_sample_size == 100
        
        # Should be valid
        errors = sample.validate_all()
        assert errors == []
    
    def test_sample_project_can_be_saved(self, temp_repo):
        """Test sample project can be saved to repository."""
        sample = create_sample_project()
        
        # Shouldn't raise any exceptions
        project_path = temp_repo.create_project(sample)
        assert project_path.exists()
        
        # Should be loadable
        loaded = temp_repo.load("UPS")
        assert loaded.name == sample.name
