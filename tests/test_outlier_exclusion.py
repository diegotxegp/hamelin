"""
Tests for DataModel outlier exclusion feature
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Block B — IS3 Outlier Action UI (Sprint 4, Day 38)

Tests cover:
- exclude_outliers() detection accuracy and return value
- get_active_df() filtering
- restore_excluded_rows()
- Edge cases: no data, no numeric cols, custom threshold
- Idempotency / copy guarantees
"""

import pytest
import pandas as pd
import numpy as np

from hamelin.model.data_model import DataModel


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def model_with_outlier():
    """DataModel with one clear outlier: index 19 has age=1000 (far beyond 3 SD).

    With 19 values at 10 and one at 1000:
      mean ≈ 59.5,  SD ≈ 221  →  3×SD ≈ 664  ≤  |1000 - 59.5| = 940.5  ✔
      Normal rows have |10 - 59.5| = 49.5 ≤ 664  ✔ (not flagged)
    """
    dm = DataModel()
    ages = [10] * 19 + [1000]        # index 19 is the outlier
    df = pd.DataFrame({
        "age": ages,
        "sex": (["M", "F"] * 10)[:20],
    })
    dm.df = df.copy()
    dm.column_metadata = {
        "age": {"is_numeric": True},
        "sex": {"is_numeric": False},
    }
    return dm


@pytest.fixture
def model_no_numeric():
    """DataModel with only categorical columns."""
    dm = DataModel()
    dm.df = pd.DataFrame({
        "group": ["A", "B", "A", "C"],
        "label": ["yes", "no", "yes", "no"],
    })
    dm.column_metadata = {
        "group": {"is_numeric": False},
        "label": {"is_numeric": False},
    }
    return dm


@pytest.fixture
def model_clean():
    """DataModel with no outliers — all values within 2 SD."""
    dm = DataModel()
    rng = np.random.default_rng(42)
    values = rng.normal(loc=50, scale=5, size=100)
    dm.df = pd.DataFrame({"score": values})
    dm.column_metadata = {"score": {"is_numeric": True}}
    return dm


# ── exclude_outliers() ────────────────────────────────────────────────────────

def test_exclude_outliers_returns_count(model_with_outlier):
    """exclude_outliers() returns the number of newly excluded rows."""
    n = model_with_outlier.exclude_outliers(std_threshold=3.0)
    assert n >= 1


def test_exclude_outliers_detects_correct_row(model_with_outlier):
    """The known extreme row (index 19, age=1000) should be in excluded_rows."""
    model_with_outlier.exclude_outliers(std_threshold=3.0)
    assert 19 in model_with_outlier.excluded_rows


def test_exclude_outliers_normal_rows_not_excluded(model_with_outlier):
    """Normal rows (indices 0-18) should NOT end up in excluded_rows."""
    model_with_outlier.exclude_outliers(std_threshold=3.0)
    normal_indices = set(range(19))
    assert normal_indices.isdisjoint(model_with_outlier.excluded_rows)


def test_exclude_outliers_no_data():
    """exclude_outliers() on empty model returns 0."""
    dm = DataModel()
    assert dm.exclude_outliers() == 0


def test_exclude_outliers_no_numeric(model_no_numeric):
    """exclude_outliers() with no numeric columns returns 0."""
    n = model_no_numeric.exclude_outliers()
    assert n == 0
    assert len(model_no_numeric.excluded_rows) == 0


def test_exclude_outliers_custom_threshold(model_with_outlier):
    """
    With a very high threshold (10 SD), even the extreme row is within bounds
    and nothing is excluded.
    """
    n = model_with_outlier.exclude_outliers(std_threshold=10.0)
    assert n == 0
    assert len(model_with_outlier.excluded_rows) == 0


def test_exclude_outliers_idempotent(model_with_outlier):
    """Calling exclude_outliers() twice does not double-count rows."""
    n1 = model_with_outlier.exclude_outliers()
    n2 = model_with_outlier.exclude_outliers()
    # Second call finds no *new* rows
    assert n2 == 0
    # Total set size must be same as after first call
    assert len(model_with_outlier.excluded_rows) == n1


def test_exclude_outliers_clean_data(model_clean):
    """No rows excluded when all data is well within 3 SD."""
    n = model_clean.exclude_outliers(std_threshold=3.0)
    # Allow 0 or very few chance outliers in random normal data
    assert n == 0 or n <= 3   # generous bound for 100-row normal sample


# ── restore_excluded_rows() ───────────────────────────────────────────────────

def test_restore_clears_excluded(model_with_outlier):
    """restore_excluded_rows() empties excluded_rows."""
    model_with_outlier.exclude_outliers()
    assert len(model_with_outlier.excluded_rows) > 0
    model_with_outlier.restore_excluded_rows()
    assert len(model_with_outlier.excluded_rows) == 0


def test_restore_on_empty_model():
    """restore_excluded_rows() on a model with no data does not raise."""
    dm = DataModel()
    dm.restore_excluded_rows()  # should not raise
    assert len(dm.excluded_rows) == 0


# ── get_active_df() ───────────────────────────────────────────────────────────

def test_get_active_df_excludes_rows(model_with_outlier):
    """get_active_df() must not contain excluded rows."""
    model_with_outlier.exclude_outliers()
    active = model_with_outlier.get_active_df()
    for idx in model_with_outlier.excluded_rows:
        assert idx not in active.index


def test_get_active_df_no_exclusions(model_with_outlier):
    """When nothing is excluded, get_active_df() returns all rows."""
    active = model_with_outlier.get_active_df()
    assert len(active) == len(model_with_outlier.df)


def test_get_active_df_is_copy(model_with_outlier):
    """get_active_df() must return a copy, not a view of the original."""
    active = model_with_outlier.get_active_df()
    original_len = len(model_with_outlier.df)
    active["age"] = 0   # mutate the copy
    # Original DataFrame must be unchanged
    assert len(model_with_outlier.df) == original_len
    assert model_with_outlier.df["age"].iloc[0] != 0


def test_get_active_df_no_data():
    """get_active_df() on a DataModel with no df loaded returns empty DataFrame."""
    dm = DataModel()
    result = dm.get_active_df()
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_active_df_restored_after_restore(model_with_outlier):
    """After restore_excluded_rows(), get_active_df() returns full dataset again."""
    model_with_outlier.exclude_outliers()
    model_with_outlier.restore_excluded_rows()
    active = model_with_outlier.get_active_df()
    assert len(active) == len(model_with_outlier.df)
