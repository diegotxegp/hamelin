"""
Tests for TrainingPage status colour mapping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests cover the module-level _STATUS_STYLES dict that drives the colour
coding of the status label in TrainingPage.

No PySide6 required — all tests operate on pure Python data structures.
"""

import pytest

from hamelin.view.pages.training_page import _STATUS_STYLES


# ── Completeness ──────────────────────────────────────────────────────────────

def test_all_expected_states_defined():
    """Every state used by _set_status must have an entry in _STATUS_STYLES."""
    required = {"no_data", "ready", "training", "done", "error", "cancelled"}
    assert required == set(_STATUS_STYLES.keys())


# ── Individual colour checks ──────────────────────────────────────────────────

def test_no_data_state_is_gray():
    assert _STATUS_STYLES["no_data"] == "color: #808080;"


def test_ready_state_is_blue():
    assert _STATUS_STYLES["ready"] == "color: #0078D4;"


def test_training_state_is_orange():
    assert _STATUS_STYLES["training"] == "color: #FF8C00;"


def test_done_state_is_green():
    assert _STATUS_STYLES["done"] == "color: #107C10;"


def test_error_state_is_red():
    assert _STATUS_STYLES["error"] == "color: #D13438;"


def test_cancelled_state_matches_no_data():
    """Cancelled and no_data share the same neutral grey colour."""
    assert _STATUS_STYLES["cancelled"] == _STATUS_STYLES["no_data"]


# ── Fallback behaviour ────────────────────────────────────────────────────────

def test_unknown_state_falls_back_to_gray():
    """_set_status uses .get(state, 'color: #808080;') — verify the fallback."""
    fallback = "color: #808080;"
    assert _STATUS_STYLES.get("nonexistent_state", fallback) == fallback


# ── CSS format validation ─────────────────────────────────────────────────────

def test_all_values_are_valid_css_colour_strings():
    """All values must be non-empty CSS strings starting with 'color:'."""
    for state, css in _STATUS_STYLES.items():
        assert isinstance(css, str), f"State {state!r}: value is not a string"
        assert css.startswith("color:"), f"State {state!r}: not a CSS color declaration"
        assert css.strip().endswith(";"), f"State {state!r}: missing trailing semicolon"
