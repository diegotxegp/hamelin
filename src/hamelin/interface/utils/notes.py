"""Free-text notes for a model, stored as a plain ``notes.txt`` inside that
model's run folder (next to its training_report.json) rather than app-local
state, so the note travels with the model and any tool pointed at the same
results directory can read it.

Deliberately folder-scoped, not a shared index like favorites.json:
deleting a model's folder is meant to take its note with it.
"""

from pathlib import Path

import hamelin.interface.utils.get_model_paths as gmp


def _note_file(model_name):
    model_path = gmp.model_path_from_name(model_name)
    if not model_path:
        return None
    # model_path may be ".../<run>/model" - keep the note at the run root,
    # alongside training_report.json, not inside the saved-model dir.
    run_dir = Path(model_path)
    if run_dir.name == "model":
        run_dir = run_dir.parent
    return run_dir / "notes.txt"


def load_note(model_name):
    """The saved note for *model_name*, or "" if there's none / it can't be
    read."""
    path = _note_file(model_name)
    if path is None or not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def save_note(model_name, text):
    """Write *text* as the note for *model_name*. An empty/whitespace-only
    note removes the file so the folder stays clean. Returns True on
    success (including the delete), False if the model or path is
    unavailable or the write fails."""
    path = _note_file(model_name)
    if path is None:
        return False

    text = (text or "").strip()
    try:
        if not text:
            if path.exists():
                path.unlink()
            return True
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
        return True
    except OSError:
        return False
