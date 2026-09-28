import json
from pathlib import Path

from hamelin.core.project import ProjectRepository, create_sample_project
from hamelin.core.dataset_registry import DatasetRegistry


def test_removed_file_is_cleaned(tmp_path):
    # Setup a temporary Projects base and create a sample project
    base = tmp_path / "ProjectsBase"
    repo = ProjectRepository(base_path=base)

    meta = create_sample_project()
    # Ensure unique short_name for the temporary test
    meta.short_name = "TMPTEST"
    meta.name = "TMPTEST Project"
    meta.protocol_number = "TMP-001"
    meta.principal_investigator = "Dr Test"
    meta.contact_email = "test@example.org"
    meta.institution = "Test Institute"
    meta.target_sample_size = 10

    project_path = repo.create_project(meta)

    # Create a small CSV source file
    src = tmp_path / "source.csv"
    src.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")

    reg = DatasetRegistry(project_path)

    # Register (copy) the dataset into the project
    dest = reg.copy_and_register(str(src), rows=2, columns=2)
    assert dest.exists()

    entries = reg.list_datasets()
    assert any(e["filename"] == dest.name for e in entries)

    # Remove the actual file from disk (simulate manual deletion)
    dest.unlink()
    # Now list_datasets should clean the registry and return empty list
    entries_after = reg.list_datasets()
    assert entries_after == []

    # Ensure the index file on disk no longer references the removed filename
    index_path = project_path / "data" / "dataset_index.json"
    assert index_path.exists()
    data = json.loads(index_path.read_text(encoding="utf-8"))
    assert all(e["filename"] != dest.name for e in data)
