"""
DatasetRegistry
~~~~~~~~~~~~~~~

Manages the list of datasets associated with a project.
Each project folder contains a ``data/dataset_index.json`` file with one
entry per dataset that has been loaded into that project.

File format::

    [
      {
        "filename": "UPS-BaseCompleta.csv",
        "original_name": "UPS-BaseCompleta_DATA_LABELS_2025-04-23_0912.csv",
        "added": "2026-02-26T10:30:00",
        "last_used": "2026-02-26T10:30:00",
        "rows": 1245,
        "columns": 87
      }
    ]

Usage::

    reg = DatasetRegistry(project_dir)
    reg.register("mydata.csv", original_name="raw.csv", rows=100, columns=20)
    entries = reg.list_datasets()   # [{"filename": ..., ...}, ...]
    last    = reg.get_last_used()   # "mydata.csv" or None
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from hamelin.utils.logger import log
from hamelin.utils.exceptions import DataSaveError


class DatasetRegistry:
    """Reads and writes ``data/dataset_index.json`` inside a project folder."""

    INDEX_FILENAME = "dataset_index.json"

    def __init__(self, project_dir: Path) -> None:
        self._data_dir = Path(project_dir) / "data"
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self._data_dir / self.INDEX_FILENAME
        # Last action performed by copy_and_register: 'copied' | 'existing' | None
        self.last_action: str | None = None

    # ── public API ────────────────────────────────────────────────────

    def copy_and_register(
        self,
        source_path: Path | str,
        rows: int,
        columns: int,
    ) -> Path:
        """
        Copy *source_path* into the project ``data/`` folder and register it.

        If a file with the same name already exists in the project folder, a
        numeric suffix is added (e.g. ``mydata_1.csv``).

        Returns the destination path inside the project folder.
        """
        source = Path(source_path)

        # If a dataset with the same original filename is already registered,
        # treat it as the same dataset and do NOT copy a duplicate. Return the
        # existing path so callers can reuse it.
        entries = self._read()
        for e in entries:
            if e.get("original_name") == source.name or e.get("filename") == source.name:
                existing = self._data_dir / e["filename"]
                if existing.exists():
                    log.info(
                        f"DatasetRegistry: dataset with original name '{source.name}' already exists as '{existing.name}' — returning existing file"
                    )
                    self.last_action = 'existing'
                    return existing
                # If registry points to missing file, fall back to normal copy

        dest = self._unique_dest(source.name)
        try:
            shutil.copy2(source, dest)
        except Exception as exc:
            raise DataSaveError(f"Failed to copy dataset into project: {exc}") from exc
        log.info(f"DatasetRegistry: copied '{source.name}' → '{dest}'")
        self.last_action = 'copied'

        self._upsert(
            filename=dest.name,
            original_name=source.name,
            rows=rows,
            columns=columns,
        )
        return dest

    def register_existing(self, filename: str, rows: int, columns: int) -> None:
        """
        Register a file that is *already* inside the project ``data/`` folder.
        Used when re-importing a dataset that was placed there manually.
        """
        self._upsert(filename=filename, original_name=filename, rows=rows, columns=columns)

    def list_datasets(self) -> list[dict]:
        """Return all registered datasets sorted newest-first."""
        entries = self._read()
        # Filter out registry entries whose files no longer exist on disk.
        filtered = []
        removed = False
        for e in entries:
            path = self._data_dir / e.get("filename", "")
            if path.exists():
                filtered.append(e)
            else:
                removed = True
                log.warning(f"DatasetRegistry: registry entry for missing file removed: {e.get('filename')}")

        if removed:
            # Persist cleaned index to avoid repeatedly showing missing entries
            try:
                self._write(filtered)
            except Exception:
                log.warning("DatasetRegistry: failed to persist cleaned index")

        return sorted(filtered, key=lambda e: e.get("added", ""), reverse=True)

    def get_last_used(self) -> str | None:
        """Return the filename of the most-recently used dataset, or None."""
        entries = self._read()
        if not entries:
            return None
        return max(entries, key=lambda e: e.get("last_used", ""))["filename"]

    def set_last_used(self, filename: str) -> None:
        """Update the ``last_used`` timestamp for *filename*."""
        entries = self._read()
        now = datetime.now().isoformat(timespec="seconds")
        for e in entries:
            if e["filename"] == filename:
                e["last_used"] = now
                break
        self._write(entries)

    def dataset_path(self, filename: str) -> Path:
        """Return the full path for *filename* inside the project data folder."""
        return self._data_dir / filename

    def has_datasets(self) -> bool:
        return bool(self._read())

    # ── private helpers ───────────────────────────────────────────────

    def _read(self) -> list[dict]:
        if not self._index_path.exists():
            return []
        try:
            with open(self._index_path, encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception as exc:
            log.warning(f"DatasetRegistry: could not read index — {exc}")
            return []

    def _write(self, entries: list[dict]) -> None:
        try:
            with open(self._index_path, "w", encoding="utf-8") as f:
                json.dump(entries, f, indent=2, ensure_ascii=False)
        except Exception as exc:
            log.error(f"DatasetRegistry: could not write index — {exc}")

    def _upsert(
        self,
        filename: str,
        original_name: str,
        rows: int,
        columns: int,
    ) -> None:
        entries = self._read()
        now = datetime.now().isoformat(timespec="seconds")
        for e in entries:
            if e["filename"] == filename:
                e["last_used"] = now
                e["rows"] = rows
                e["columns"] = columns
                break
        else:
            entries.append(
                {
                    "filename": filename,
                    "original_name": original_name,
                    "added": now,
                    "last_used": now,
                    "rows": rows,
                    "columns": columns,
                }
            )
        self._write(entries)

    def _unique_dest(self, filename: str) -> Path:
        """Return a Path that does not collide with any existing file."""
        dest = self._data_dir / filename
        if not dest.exists():
            return dest
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        counter = 1
        while True:
            candidate = self._data_dir / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1
