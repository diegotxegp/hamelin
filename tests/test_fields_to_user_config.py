"""
Tests for LudwigBackend._fields_to_user_config - the translation from
TrainingPage's flat model-config fields to a partial Ludwig config passed
as auto_train(user_config=...).

Pure dict-in / dict-out, no Ludwig or PySide6 needed.
"""
from hamelin.analytics.automl.ludwig_backend import (
    _DEFAULT_MAX_CONCURRENT_TRIALS,
    _fields_to_user_config,
)

# Left unset ("Search Strategy" at its default), every case below still
# gets this same baseline concurrency cap - see _fields_to_user_config's
# "else" branch for why (Ludwig's own default is unbounded, which OOMs on
# a modest machine).
_DEFAULT_HYPEROPT = {"executor": {"max_concurrent_trials": _DEFAULT_MAX_CONCURRENT_TRIALS}}


def test_empty_fields_still_cap_concurrency():
    assert _fields_to_user_config({}, "outcome") == {"hyperopt": _DEFAULT_HYPEROPT}


def test_metric_maps_to_trainer_validation():
    # A metric alone (no Search Strategy picked) still forces the hyperopt
    # objective - see _fields_to_user_config's "if metric:" block docstring
    # comment for why Ludwig's own default objective can't be trusted here.
    cfg = _fields_to_user_config({"metric": "accuracy"}, "outcome")
    assert cfg == {
        "trainer": {"validation_metric": "accuracy", "validation_field": "outcome"},
        "hyperopt": {
            "executor": {"max_concurrent_trials": _DEFAULT_MAX_CONCURRENT_TRIALS},
            "output_feature": "outcome",
            "metric": "accuracy",
            "goal": "maximize",
        },
    }


def test_class_imbalance_maps_to_preprocessing_for_binary():
    # Ludwig only supports dataset balancing for binary output features
    # (configuration/preprocessing.md, "Data Balancing").
    cfg = _fields_to_user_config(
        {"class_imbalance": True, "problem_type": "binary"}, "outcome"
    )
    assert cfg["preprocessing"] == {"oversample_minority": 0.5}


def test_class_imbalance_ignored_for_non_binary():
    # Not a documented Ludwig option outside binary - must not be forced.
    cfg = _fields_to_user_config(
        {"class_imbalance": True, "problem_type": "category"}, "outcome"
    )
    assert "preprocessing" not in cfg


def test_class_imbalance_false_is_ignored():
    cfg = _fields_to_user_config(
        {"class_imbalance": False, "problem_type": "binary"}, "outcome"
    )
    assert cfg == {"hyperopt": _DEFAULT_HYPEROPT}


def test_search_none_still_caps_concurrency():
    cfg = _fields_to_user_config({"search": "none"}, "outcome")
    assert cfg == {"hyperopt": _DEFAULT_HYPEROPT}


def test_search_random_builds_hyperopt_block():
    cfg = _fields_to_user_config(
        {"search": "random", "max_iter": 30, "parallel_trials": 3}, "outcome"
    )
    hopt = cfg["hyperopt"]
    assert hopt["search_alg"] == {"type": "variant_generator"}
    assert hopt["executor"] == {"num_samples": 30, "max_concurrent_trials": 3}
    # no metric given -> no objective forced
    assert "metric" not in hopt and "goal" not in hopt


def test_search_with_regression_metric_minimizes():
    cfg = _fields_to_user_config(
        {"search": "bayesian", "metric": "mean_absolute_error"}, "y"
    )
    hopt = cfg["hyperopt"]
    assert hopt["search_alg"] == {"type": "hyperopt"}
    assert hopt["metric"] == "mean_absolute_error"
    assert hopt["goal"] == "minimize"
    assert hopt["output_feature"] == "y"
    # executor still has sane fallbacks when counts are absent
    assert hopt["executor"]["num_samples"] == 10
    assert hopt["executor"]["max_concurrent_trials"] == 1


def test_search_with_classification_metric_maximizes():
    cfg = _fields_to_user_config({"search": "random", "metric": "roc_auc"}, "y")
    assert cfg["hyperopt"]["goal"] == "maximize"
    assert cfg["hyperopt"]["output_feature"] == "y"
    assert cfg["hyperopt"]["search_alg"] == {"type": "variant_generator"}


def test_unknown_search_strategy_falls_back_to_variant_generator():
    # "hyperband" used to be offered as a Search Strategy, but it's a
    # documented Ludwig `executor.scheduler` type, not a `search_alg` one
    # (configuration/hyperparameter_optimization.md) - no longer mapped.
    cfg = _fields_to_user_config({"search": "hyperband"}, "y")
    assert cfg["hyperopt"]["search_alg"] == {"type": "variant_generator"}


def test_all_fields_together():
    cfg = _fields_to_user_config(
        {
            "metric": "roc_auc",
            "class_imbalance": True,
            "problem_type": "binary",
            "search": "random",
            "max_iter": 25,
            "parallel_trials": 4,
        },
        "outcome",
    )
    assert cfg["trainer"]["validation_metric"] == "roc_auc"
    assert cfg["preprocessing"]["oversample_minority"] == 0.5
    assert cfg["hyperopt"]["metric"] == "roc_auc"
    assert cfg["hyperopt"]["executor"]["num_samples"] == 25


def test_parallel_trials_is_honoured_even_without_a_search_strategy():
    """The UI's "Parallel trials" used to be dropped unless a search strategy
    was chosen, so the hidden default cap (3) applied instead of the value
    the user saw (4)."""
    cfg = _fields_to_user_config({"parallel_trials": 4}, "outcome")
    assert cfg["hyperopt"]["executor"]["max_concurrent_trials"] == 4
    # nothing set at all -> the memory-safe default still applies
    cfg = _fields_to_user_config({}, "outcome")
    assert cfg["hyperopt"]["executor"]["max_concurrent_trials"] == _DEFAULT_MAX_CONCURRENT_TRIALS
