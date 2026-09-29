"""
Tests for TrainingPage.prefill_from_config and the staged "_pending_config"
lifecycle - the "duplicate a model" hand-off from the embedded dashboard.

Covers:
- the config + target/predictors get staged, not written anywhere
- the staged selection survives a dataset loaded *after* the hand-off
- the persistent banner shows and the model-config card is greyed out
- clearing (cancel button / navigating away) returns to normal AutoML mode
- "Start training" with a staged config trains that config, not AutoML
"""
import os
import pytest

pytest.importorskip("PySide6.QtWidgets")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pandas as pd
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QHideEvent

from hamelin.view.pages.training_page import TrainingPage


DUP_PAYLOAD = {
    "based_on": "Source_Model",
    "new_run_name": "Source_Model_copy",
    "config": {
        "input_features": [{"name": "age"}, {"name": "sex"}],
        "output_features": [{"name": "outcome"}],
        "trainer": {"epochs": 42},
    },
}


class _DataModel:
    def __init__(self, df):
        self.df = df

    def get_active_df(self):
        return self.df


def _df(*cols):
    return pd.DataFrame({c: [0, 1] for c in cols})


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def page(qapp):
    return TrainingPage()


def test_prefill_stages_config_target_and_name(page):
    page.prefill_from_config(DUP_PAYLOAD)

    assert page._pending_config == DUP_PAYLOAD["config"]
    assert page._pending_target == "outcome"
    assert page._pending_features == ["age", "sex"]
    assert page.model_name_edit.text() == "Source_Model_copy"


def test_prefill_shows_banner_and_greys_the_model_card(page):
    assert page._pending_banner.isVisible() is False
    assert page.model_card.isEnabled() is True

    page.prefill_from_config(DUP_PAYLOAD)

    assert page._pending_banner.isVisibleTo(page) is True
    assert page.model_card.isEnabled() is False


def test_selection_survives_a_dataset_loaded_after_the_handoff(page):
    # The natural order: duplicate first, then load the dataset.
    page.prefill_from_config(DUP_PAYLOAD)
    assert page.primary_combo.count() == 0

    page.set_data_model(_DataModel(_df("age", "sex", "outcome", "noise")))

    assert page.primary_combo.currentText() == "outcome"
    assert sorted(i.text() for i in page.features_list.selectedItems()) == ["age", "sex"]
    assert page._pending_banner.isVisibleTo(page) is True


def test_clear_pending_config_returns_to_normal_mode(page):
    page.prefill_from_config(DUP_PAYLOAD)

    page._clear_pending_config()

    assert page._pending_config is None
    assert page._pending_target == ""
    assert page._pending_features == []
    assert page._pending_banner.isVisibleTo(page) is False
    assert page.model_card.isEnabled() is True


def test_navigating_away_clears_a_staged_config(page):
    page.prefill_from_config(DUP_PAYLOAD)

    page.hideEvent(QHideEvent())  # an in-app page switch is non-spontaneous

    assert page._pending_config is None
    assert page.model_card.isEnabled() is True


class _FakeSignal:
    def connect(self, *_a, **_k):
        pass


class _FakeWorker:
    last_kwargs = None

    def __init__(self, **kwargs):
        _FakeWorker.last_kwargs = kwargs
        self.progress = _FakeSignal()
        self.finished = _FakeSignal()
        self.error = _FakeSignal()
        self.started = False

    def start(self):
        self.started = True


def test_start_training_trains_the_staged_config_not_automl(page, monkeypatch):
    monkeypatch.setattr(
        "hamelin.view.pages.training_page.LudwigTrainerWorker", _FakeWorker
    )
    page.prefill_from_config(DUP_PAYLOAD)
    page.set_data_model(_DataModel(_df("age", "sex", "outcome")))
    page.model_name_edit.setText("Source_Model_copy")

    page._start_training()

    kw = _FakeWorker.last_kwargs
    assert kw is not None
    assert kw["backend_kwargs"] == {"config": DUP_PAYLOAD["config"]}
    assert kw["time_limit_s"] == 0
    assert kw["target"] == "outcome"
    assert sorted(kw["features"]) == ["age", "sex"]
