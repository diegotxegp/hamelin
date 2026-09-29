"""Housekeeping keeps everything a project generates inside its folder, tidy."""
from hamelin.core.project_layout import move_legacy_summaries, remove_trial_dumps, tidy_project


def _project(tmp_path):
    p = tmp_path / "PROJ"
    (p / "data").mkdir(parents=True)
    (p / "data" / "d.csv").write_text("a\n1\n")
    (p / "data" / "d_summary.txt").write_text("summary")
    (p / "ludwig_runs" / "hyperopt" / "trial_0").mkdir(parents=True)
    (p / "ludwig_runs" / "hyperopt" / "trial_0" / "weights.bin").write_bytes(b"x" * 1000)
    (p / "model_checkpoints" / "run1").mkdir(parents=True)
    (p / "model_checkpoints" / "run1" / "model_hyperparameters.json").write_text("{}")
    return p


def test_tidy_moves_summaries_checkpoints_and_drops_trial_dumps(tmp_path):
    p = _project(tmp_path)
    tidy_project(p)
    assert (p / "data" / "d.csv").exists()                              # datasets stay
    assert not (p / "data" / "d_summary.txt").exists()
    assert (p / "results" / "reports" / "d_summary.txt").read_text() == "summary"
    assert (p / "results" / "models" / "run1" / "model_hyperparameters.json").exists()
    assert not (p / "model_checkpoints").exists()
    assert not (p / "ludwig_runs").exists()
    tidy_project(p)                                                     # idempotent


def test_tidy_keeps_trial_dumps_while_a_training_runs(tmp_path):
    p = _project(tmp_path)
    tidy_project(p, trial_dumps=False)
    assert (p / "ludwig_runs").exists()
    assert remove_trial_dumps(p) >= 1000 and not (p / "ludwig_runs").exists()


def test_existing_report_is_not_overwritten(tmp_path):
    p = _project(tmp_path)
    (p / "results" / "reports").mkdir(parents=True)
    (p / "results" / "reports" / "d_summary.txt").write_text("newer")
    assert move_legacy_summaries(p) == 1
    assert (p / "results" / "reports" / "d_summary.txt").read_text() == "newer"
    assert not (p / "data" / "d_summary.txt").exists()


def test_old_daily_logs_are_pruned_but_usage_log_is_kept(tmp_path):
    import os
    import time

    from hamelin.utils.logger import _prune_old_logs

    old, new, usage = (tmp_path / "hamelin_2026-01-01.log", tmp_path / "hamelin_2026-09-28.log",
                       tmp_path / "usage_log.csv")
    for f in (old, new, usage):
        f.write_text("x")
    ancient = time.time() - 90 * 86400
    os.utime(old, (ancient, ancient))
    os.utime(usage, (ancient, ancient))
    _prune_old_logs(tmp_path)
    assert not old.exists() and new.exists() and usage.exists()
