"""
Project layout housekeeping
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Everything Hamelin generates for a project lives inside that project's
folder, in a fixed place:

    <project>/metadata.json, project_state.json     project description / UI state
    <project>/data/                                  the project's datasets (+ dataset_index.json)
    <project>/results/models/<name>/                 trained models (weights, config, predictions, settings)
    <project>/results/tables|reports|forecasts|predictions/   exports (see hamelin.utils.export_paths)

plus one disposable folder, ``ludwig_runs/``, where Ludwig dumps every
hyperparameter trial (checkpoints and weights included, easily hundreds of
MB). Nothing reads it after training - the winning model is saved under
results/models/ - so it is removed when a run ends and again when a project
is opened. ``tidy_project`` also moves files that older versions left in the
wrong place.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from hamelin.core.model_history import migrate_legacy_checkpoints
from hamelin.utils.logger import log

TRIAL_DUMPS_DIR = "ludwig_runs"


def _size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def remove_trial_dumps(project_dir) -> int:
    """Delete <project>/ludwig_runs/; returns the bytes freed."""
    folder = Path(project_dir) / TRIAL_DUMPS_DIR
    if not folder.is_dir():
        return 0
    freed = 0
    try:
        freed = _size(folder)
    except OSError:
        pass
    shutil.rmtree(folder, ignore_errors=True)
    if freed:
        log.info(f"Removed Ludwig trial dumps of {Path(project_dir).name} ({freed / 2**20:.0f} MB)")
    return freed


def move_legacy_summaries(project_dir) -> int:
    """Dataset summaries used to be written into data/ (next to the
    datasets); they are reports, so they belong in results/reports/."""
    project_dir = Path(project_dir)
    data = project_dir / "data"
    if not data.is_dir():
        return 0
    moved = 0
    for f in data.glob("*_summary.txt"):
        dest_dir = project_dir / "results" / "reports"
        dest_dir.mkdir(parents=True, exist_ok=True)
        target = dest_dir / f.name
        if target.exists():
            f.unlink()          # already regenerated in the right place
        else:
            shutil.move(str(f), str(target))
        moved += 1
    return moved


def tidy_project(project_dir, trial_dumps: bool = True) -> None:
    """Bring *project_dir* to the current layout (idempotent, best effort)."""
    if not project_dir or not Path(project_dir).is_dir():
        return
    try:
        migrate_legacy_checkpoints(Path(project_dir))
        move_legacy_summaries(project_dir)
        if trial_dumps:
            remove_trial_dumps(project_dir)
    except Exception as exc:  # noqa: BLE001
        log.warning(f"tidy_project({project_dir}) failed: {exc}")
