"""Tests for utils/notes.py - per-model free-text notes kept in the run folder."""
import json

import pytest

import hamelin.interface.utils.get_model_paths as gmp
from hamelin.interface.utils.notes import load_note, save_note, _note_file


def _make_run(results_dir, run_name, nested_model_dir=True):
    run_dir = results_dir / run_name
    model_dir = run_dir / "model" if nested_model_dir else run_dir
    model_dir.mkdir(parents=True)
    (model_dir / "model_hyperparameters.json").write_text(json.dumps({}))
    return run_dir


@pytest.fixture
def results_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(gmp, "RESULTS_DIR", str(tmp_path))
    return tmp_path


def test_load_note_empty_when_none_saved(results_dir):
    _make_run(results_dir, "run_a")
    assert load_note("run_a") == ""


def test_save_then_load_roundtrip(results_dir):
    _make_run(results_dir, "run_a")
    assert save_note("run_a", "  looks overfit, retrain with more dropout  ")
    assert load_note("run_a") == "looks overfit, retrain with more dropout"


def test_note_lands_at_run_root_not_inside_model_dir(results_dir):
    run_dir = _make_run(results_dir, "run_a", nested_model_dir=True)
    save_note("run_a", "hello")
    assert (run_dir / "notes.txt").read_text() == "hello"
    assert not (run_dir / "model" / "notes.txt").exists()


def test_empty_note_deletes_the_file(results_dir):
    run_dir = _make_run(results_dir, "run_a")
    save_note("run_a", "temp")
    assert (run_dir / "notes.txt").exists()
    assert save_note("run_a", "   ")
    assert not (run_dir / "notes.txt").exists()
    assert load_note("run_a") == ""


def test_unknown_model_is_a_noop(results_dir):
    assert load_note("nope") == ""
    assert save_note("nope", "x") is False
    assert _note_file("nope") is None


def test_flat_run_dir_also_supported(results_dir):
    run_dir = _make_run(results_dir, "flat_run", nested_model_dir=False)
    save_note("flat_run", "note on a flat run")
    assert (run_dir / "notes.txt").read_text() == "note on a flat run"
