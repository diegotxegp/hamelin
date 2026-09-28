"""
Tests for TrainingPage's model-name sanitization/collision-avoidance
helpers (see "Model name" field, section 3 of the Training page).

Both helpers are @staticmethod, so they're testable directly through the
class without constructing a QApplication/widget tree - consistent with
this suite's focus on backend logic rather than UI construction.
"""
from pathlib import Path

from hamelin.view.pages.training_page import TrainingPage


# _sanitize_model_name

def test_sanitize_keeps_a_clean_name_as_is():
    assert TrainingPage._sanitize_model_name("LPP_risk_v1", "fallback") == "LPP_risk_v1"


def test_sanitize_collapses_whitespace_to_underscores():
    assert TrainingPage._sanitize_model_name("My Cool Model", "fallback") == "My_Cool_Model"


def test_sanitize_strips_unsafe_characters():
    assert TrainingPage._sanitize_model_name("My/Model:v1!!", "fallback") == "MyModelv1"


def test_sanitize_strips_leading_trailing_whitespace_and_separators():
    assert TrainingPage._sanitize_model_name("  _-hello-_  ", "fallback") == "hello"


def test_sanitize_falls_back_when_blank():
    assert TrainingPage._sanitize_model_name("", "fallback-id") == "fallback-id"


def test_sanitize_falls_back_when_nothing_usable_survives():
    # Emoji / punctuation-only input strips down to nothing.
    assert TrainingPage._sanitize_model_name("🎉!!!", "fallback-id") == "fallback-id"


# _unique_checkpoint_name

def test_unique_name_unchanged_when_available(tmp_path):
    assert TrainingPage._unique_checkpoint_name("model_a", tmp_path) == "model_a"


def test_unique_name_appends_suffix_on_collision(tmp_path):
    (tmp_path / "model_a").mkdir()
    assert TrainingPage._unique_checkpoint_name("model_a", tmp_path) == "model_a_2"


def test_unique_name_keeps_incrementing_past_multiple_collisions(tmp_path):
    (tmp_path / "model_a").mkdir()
    (tmp_path / "model_a_2").mkdir()
    (tmp_path / "model_a_3").mkdir()
    assert TrainingPage._unique_checkpoint_name("model_a", tmp_path) == "model_a_4"


# _features_from_config - the "train from imported config" fallback used
# when nothing is (re-)checked in the features list, instead of silently
# training on every column in the dataset (see _start_training_from_config).

def test_features_from_config_reads_input_feature_names():
    config = {"input_features": [{"name": "age"}, {"name": "sex"}]}
    assert TrainingPage._features_from_config(config, target="outcome") == ["age", "sex"]


def test_features_from_config_prefers_column_over_name():
    # Ludwig configs can carry both - "column" is the actual source
    # dataframe column, "name" the feature's (possibly renamed) identity.
    config = {"input_features": [{"name": "renamed_age", "column": "age"}]}
    assert TrainingPage._features_from_config(config, target="outcome") == ["age"]

def test_features_from_config_excludes_the_target():
    # The target can end up looking like an input feature in a hand-edited
    # or malformed config - never train "predicting X from X".
    config = {"input_features": [{"name": "age"}, {"name": "outcome"}]}
    assert TrainingPage._features_from_config(config, target="outcome") == ["age"]


def test_features_from_config_empty_when_no_input_features():
    assert TrainingPage._features_from_config({}, target="outcome") == []
