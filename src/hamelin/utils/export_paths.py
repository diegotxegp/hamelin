"""
Export paths
~~~~~~~~~~~~

Where the pages' "Export ..." dialogs open by default: a subfolder of the
active project's ``results/`` folder, so what a project generates stays with
the project. The user can still pick any other location in the dialog.

    results/tables/        Table 1, cleaned dataset
    results/reports/       quality report, dataset summary, model report
    results/forecasts/     recruitment chart and timeline
    results/predictions/   Prediction page output

Without an open project the bare file name is returned, i.e. the dialog
behaves as it always did.
"""

from __future__ import annotations

from pathlib import Path

from hamelin.utils.logger import log

EXPORT_KINDS = ("tables", "reports", "forecasts", "predictions")


def default_export_path(project_dir, kind: str, filename: str) -> str:
    """Suggested save path for *filename* under the project's results/<kind>/
    folder (created on demand), or just *filename* if there is no usable
    project."""
    if kind not in EXPORT_KINDS:
        raise ValueError(f"Unknown export kind {kind!r}; expected one of {EXPORT_KINDS}")
    if not project_dir:
        return filename
    root = Path(project_dir)
    if not root.is_dir():
        return filename
    folder = root / "results" / kind
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        log.warning(f"Cannot create export folder {folder}: {exc}")
        return filename
    return str(folder / filename)
