"""
Dataset change record
~~~~~~~~~~~~~~~~~~~~~

Everything the user does to a dataset on the Data page (rows or columns
removed, duplicates or outliers excluded, variable types overridden, ...)
is recorded next to the dataset, the same way the Ludwig configuration is
recorded with each trained model:

    <project>/data/<dataset>.changes.json

The original data file is never modified: the record describes which rows
and columns are left out and which types were overridden, plus a dated
history of every change.  A copy is stored with each trained model
(``data_changes.json``) so a model can always be traced back to the exact
data it was trained on.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from hamelin.utils.logger import log

CHANGES_SUFFIX = ".changes.json"
MODEL_COPY_NAME = "data_changes.json"
_MAX_LISTED = 500          # row ids listed in one history entry (the total is always given)


def changes_path(project_dir, dataset) -> Path:
    """Where the change record of *dataset* (a file name or path) lives."""
    return Path(project_dir) / "data" / f"{Path(str(dataset)).stem}{CHANGES_SUFFIX}"


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _entry(action: str, detail: str, items: list | None = None) -> dict[str, Any]:
    e: dict[str, Any] = {"time": _now(), "action": action, "detail": detail}
    if items:
        e["items"] = items[:_MAX_LISTED]
        if len(items) > _MAX_LISTED:
            e["items_truncated"] = len(items)
    return e


def _sorted(values) -> list:
    try:
        return sorted(values)
    except TypeError:
        return sorted(values, key=str)


def _row_numbers(ids) -> list:
    """1-based row numbers for integer index labels, the label itself otherwise."""
    return _sorted(int(i) + 1 if str(i).lstrip("-").isdigit() else i for i in ids)


def _snapshot(dm) -> dict[str, Any]:
    return {"rows": set(dm.excluded_rows), "cols": set(dm.excluded_columns),
            "types": dict(dm.column_types)}


def load_record(project_dir, dataset) -> dict[str, Any] | None:
    path = changes_path(project_dir, dataset)
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
    except (OSError, ValueError):
        return None


def mark_baseline(dm, project_dir=None) -> None:
    """Adopt the model's current state as "nothing new to log" (called after a
    saved state has been applied) and pick up the previous history."""
    dm._logged_state = _snapshot(dm)
    if project_dir is not None and dm.filepath and not dm.change_log:
        rec = load_record(project_dir, dm.filepath)
        if rec:
            dm.change_log = list(rec.get("history", []))


def _diff_into_log(dm, reason: str) -> None:
    prev = dm._logged_state or {"rows": set(), "cols": set(), "types": {}}
    cur = _snapshot(dm)
    def _rownums(ids):
        return _row_numbers(ids)

    added_rows, restored_rows = cur["rows"] - prev["rows"], prev["rows"] - cur["rows"]
    if added_rows:
        dm.change_log.append(_entry(
            "rows_removed", f"{len(added_rows)} row(s) removed — {reason}", _rownums(added_rows)))
    if restored_rows:
        dm.change_log.append(_entry(
            "rows_restored", f"{len(restored_rows)} row(s) restored", _rownums(restored_rows)))
    added_cols, restored_cols = cur["cols"] - prev["cols"], prev["cols"] - cur["cols"]
    if added_cols:
        dm.change_log.append(_entry(
            "columns_removed", f"{len(added_cols)} column(s) removed", _sorted(added_cols)))
    if restored_cols:
        dm.change_log.append(_entry(
            "columns_restored", f"{len(restored_cols)} column(s) restored", _sorted(restored_cols)))
    for col in _sorted(set(cur["types"]) | set(prev["types"])):
        old, new = prev["types"].get(col), cur["types"].get(col)
        if old != new:
            dm.change_log.append(_entry(
                "type_changed", f"'{col}': {old or 'inferred'} → {new or 'inferred'}"))
    dm._logged_state = cur
    dm._change_reason = None


def build_record(dm) -> dict[str, Any]:
    """The JSON document describing the dataset's current state and history."""
    df = dm.df
    n_rows, n_cols = (len(df), len(df.columns)) if df is not None else (0, 0)
    kept_rows = n_rows - len([r for r in dm.excluded_rows if df is not None and r in df.index])
    kept_cols = n_cols - len([c for c in dm.excluded_columns if df is not None and c in df.columns])
    rows_removed = _row_numbers(dm.excluded_rows)
    return {
        "dataset": Path(str(dm.filepath)).name if dm.filepath else None,
        "source_file": str(dm.filepath) if dm.filepath else None,
        "updated": _now(),
        "note": ("The original file is never modified. Rows and columns listed here are left out of "
                 "Table 1, training and exports; row numbers start at 1 (first data row)."),
        "original": {"rows": n_rows, "columns": n_cols},
        "in_use": {"rows": kept_rows, "columns": kept_cols},
        "rows_removed": {"count": len(rows_removed), "row_numbers": rows_removed},
        "columns_removed": _sorted(dm.excluded_columns),
        "variable_types_overridden": dict(sorted(dm.column_types.items())),
        "history": list(dm.change_log),
    }


def save_record(dm, project_dir) -> Path | None:
    """Update the change history from the model's current state and write the file."""
    if dm.df is None or not dm.filepath:
        return None
    try:
        if dm._logged_state is None:
            rec = load_record(project_dir, dm.filepath)
            if rec and not dm.change_log:
                dm.change_log = list(rec.get("history", []))
            dm._logged_state = {"rows": set(), "cols": set(), "types": {}}
        _diff_into_log(dm, dm._change_reason or "selected on the Data page")
        path = changes_path(project_dir, dm.filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        record = build_record(dm)
        old = load_record(project_dir, dm.filepath)
        if old is not None and {**old, "updated": None} == {**record, "updated": None}:
            return path        # nothing changed: keep the file (and its timestamp) as is
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False, default=str),
                        encoding="utf-8")
        return path
    except Exception as exc:  # noqa: BLE001
        log.warning(f"Could not write the dataset change record: {exc}")
        return None


def copy_to_model(project_dir, dataset, model_dir) -> None:
    """Store the dataset's change record inside a trained model's folder."""
    try:
        rec = load_record(project_dir, dataset)
        if rec is None:
            return
        Path(model_dir).mkdir(parents=True, exist_ok=True)
        (Path(model_dir) / MODEL_COPY_NAME).write_text(
            json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        log.warning(f"Could not copy the dataset change record to the model: {exc}")
