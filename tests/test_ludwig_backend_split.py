"""
Tests for LudwigBackend._held_out_test_set - splits off a genuinely
untouched test set before training, so evaluate() (see run() and
_run_with_config()) measures the model on rows it never saw instead of
silently including training rows, which inflates every reported metric.
"""
import pandas as pd
import pytest

from hamelin.analytics.automl.ludwig_backend import _held_out_test_set


def _sample_df(n=100, positives=30):
    return pd.DataFrame({
        "age": range(n),
        "outcome": ["yes"] * positives + ["no"] * (n - positives),
    })


def test_split_sizes_match_test_split_fraction():
    df = _sample_df(n=100)
    train_df, test_df = _held_out_test_set(df, "outcome", test_split=0.2, random_seed=42)

    assert len(train_df) == 80
    assert len(test_df) == 20


def test_train_and_test_rows_are_disjoint():
    df = _sample_df(n=100)
    train_df, test_df = _held_out_test_set(df, "outcome", test_split=0.3, random_seed=1)

    assert set(train_df["age"]).isdisjoint(set(test_df["age"]))
    assert len(train_df) + len(test_df) == len(df)


def test_same_seed_gives_the_same_split():
    df = _sample_df(n=60)
    train_a, test_a = _held_out_test_set(df, "outcome", test_split=0.2, random_seed=7)
    train_b, test_b = _held_out_test_set(df, "outcome", test_split=0.2, random_seed=7)

    assert list(train_a["age"]) == list(train_b["age"])
    assert list(test_a["age"]) == list(test_b["age"])


def test_stratifies_by_target_when_possible():
    # 40% positive overall - a stratified split keeps that ratio in both
    # halves instead of leaving the test set with too few (or zero)
    # positive cases purely by chance, which small clinical datasets are
    # especially prone to with a plain random split.
    df = _sample_df(n=100, positives=40)
    train_df, test_df = _held_out_test_set(df, "outcome", test_split=0.2, random_seed=42)

    assert (test_df["outcome"] == "yes").sum() == pytest.approx(8, abs=1)
    assert (train_df["outcome"] == "yes").sum() == pytest.approx(32, abs=1)


def test_falls_back_to_plain_split_for_continuous_target():
    df = pd.DataFrame({"age": range(50), "los_days": [i * 0.37 for i in range(50)]})
    # Would raise if stratify=df[target] were used unconditionally - every
    # value is unique, so no class has the >=2 members stratify needs.
    train_df, test_df = _held_out_test_set(df, "los_days", test_split=0.2, random_seed=42)

    assert len(test_df) == 10
    assert len(train_df) == 40


def test_falls_back_when_a_class_is_too_small_to_stratify():
    df = pd.DataFrame({
        "age": range(21),
        "outcome": ["no"] * 20 + ["yes"] * 1,  # a single positive - can't stratify
    })
    train_df, test_df = _held_out_test_set(df, "outcome", test_split=0.2, random_seed=42)

    assert len(train_df) + len(test_df) == 21


def test_test_split_is_clamped_to_a_sane_range():
    df = _sample_df(n=100)
    train_df, test_df = _held_out_test_set(df, "outcome", test_split=0.9, random_seed=42)
    assert len(test_df) == 50  # clamped to the 0.5 max, not 90 rows held out

    train_df, test_df = _held_out_test_set(df, "outcome", test_split=0.0, random_seed=42)
    assert len(test_df) == 5  # clamped to the 0.05 min, not zero
