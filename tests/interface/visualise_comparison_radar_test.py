import numpy as np

from hamelin.interface.widgets.visualise_comparison_radar import VisualiseComparisonRadarWidget
from hamelin.interface.utils.radar import RadarItem
from hamelin.interface.utils.app_state import app_state


def _radar_items(widget):
    return [it for it in widget.graph.getPlotItem().items if isinstance(it, RadarItem)]


def _fake_load_run_metrics(models_metrics):
    def _load(model):
        return dict(models_metrics.get(model, {}))
    return _load


def test_set_data_seeds_model_selector_and_compare_dropdown(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_radar as vcr

    monkeypatch.setattr(vcr.gmp, "get_model_names", lambda: ["model_a", "model_b", "model_c"])
    monkeypatch.setattr(vcr, "load_run_metrics", _fake_load_run_metrics({
        "model_a": {"test/accuracy/best": 0.5},
        "model_b": {"test/accuracy/best": 0.6},
        "model_c": {"test/accuracy/best": 0.7},
    }))

    widget = VisualiseComparisonRadarWidget()
    qtbot.addWidget(widget)
    widget.set_data(["model_b", "model_c"])

    assert widget.model_selector.currentText() == "model_b"
    assert sorted(widget.compare_dropdown.get_selected()) == ["model_b", "model_c"]


def test_direct_entry_with_no_models_defaults_to_first_model_and_all_included(qtbot, monkeypatch):
    # The landing page's "Radar Chart Comparison" button calls set_data([]).
    import hamelin.interface.widgets.visualise_comparison_radar as vcr

    monkeypatch.setattr(vcr.gmp, "get_model_names", lambda: ["model_a", "model_b"])
    monkeypatch.setattr(vcr, "load_run_metrics", _fake_load_run_metrics({
        "model_a": {"test/accuracy/best": 0.5},
        "model_b": {"test/accuracy/best": 0.6},
    }))

    widget = VisualiseComparisonRadarWidget()
    qtbot.addWidget(widget)
    widget.set_data([])

    assert widget.model_selector.currentText() == "model_a"
    assert sorted(widget.compare_dropdown.get_selected()) == ["model_a", "model_b"]


def test_draws_exactly_two_polygons_model_and_average(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_radar as vcr

    monkeypatch.setattr(vcr.gmp, "get_model_names", lambda: ["model_a", "model_b", "model_c"])
    monkeypatch.setattr(vcr, "load_run_metrics", _fake_load_run_metrics({
        "model_a": {"test/accuracy/best": 0.9},
        "model_b": {"test/accuracy/best": 0.5},
        "model_c": {"test/accuracy/best": 0.7},
    }))

    widget = VisualiseComparisonRadarWidget()
    qtbot.addWidget(widget)
    widget.set_data(["model_a", "model_b", "model_c"])

    # Exactly 2 polygons regardless of how many models feed the average:
    # the selected model and the average line - not one per model.
    assert len(_radar_items(widget)) == 2


def test_average_reflects_only_included_models(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_radar as vcr

    monkeypatch.setattr(vcr.gmp, "get_model_names", lambda: ["model_a", "model_b", "model_c"])
    monkeypatch.setattr(vcr, "load_run_metrics", _fake_load_run_metrics({
        "model_a": {"test/accuracy/best": 0.9},
        "model_b": {"test/accuracy/best": 0.5},
        "model_c": {"test/accuracy/best": 0.1},
    }))

    widget = VisualiseComparisonRadarWidget()
    qtbot.addWidget(widget)
    widget.set_data(["model_a", "model_b", "model_c"])

    # Uncheck model_c - average should now be computed from model_a/b only.
    for w in widget.compare_dropdown.item_widgets:
        if w.property("raw_value") == "model_c":
            w.setChecked(False)

    assert widget.last_mean_raw["accuracy"] == (0.9 + 0.5) / 2


def test_only_selected_model_included_average_matches_model(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_radar as vcr

    monkeypatch.setattr(vcr.gmp, "get_model_names", lambda: ["model_a", "model_b"])
    monkeypatch.setattr(vcr, "load_run_metrics", _fake_load_run_metrics({
        "model_a": {"test/accuracy/best": 0.42},
        "model_b": {"test/accuracy/best": 0.9},
    }))

    widget = VisualiseComparisonRadarWidget()
    qtbot.addWidget(widget)
    widget.set_data(["model_a", "model_b"])

    for w in widget.compare_dropdown.item_widgets:
        w.setChecked(False)

    assert widget.last_mean_raw["accuracy"] == 0.42
    assert widget.last_model_raw["accuracy"] == 0.42


def test_no_model_available_shows_empty_hint(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_radar as vcr

    monkeypatch.setattr(vcr.gmp, "get_model_names", lambda: [])

    widget = VisualiseComparisonRadarWidget()
    qtbot.addWidget(widget)
    widget.set_data([])

    assert widget.empty_hint.isHidden() is False
    assert widget.graph_card.isHidden() is True


def test_favorites_only_narrows_the_average(qtbot, monkeypatch):
    # No UI toggle for this right now (temporarily removed along with
    # split/export - see visualise_comparison_radar.py), but the
    # underlying filter is still there and still correct.
    import hamelin.interface.widgets.visualise_comparison_radar as vcr
    import hamelin.interface.utils.favorites as favorites

    monkeypatch.setattr(vcr.gmp, "get_model_names", lambda: ["model_a", "model_b"])
    monkeypatch.setattr(vcr, "load_run_metrics", _fake_load_run_metrics({
        "model_a": {"test/accuracy/best": 0.9},
        "model_b": {"test/accuracy/best": 0.1},
    }))
    monkeypatch.setattr(favorites, "is_favorite", lambda m: m == "model_a")
    monkeypatch.setattr(vcr, "is_favorite", lambda m: m == "model_a")

    widget = VisualiseComparisonRadarWidget()
    qtbot.addWidget(widget)
    widget.set_data(["model_a", "model_b"])

    widget.favorites_only = True
    widget.update_graph()

    # Only model_a (the favorite) feeds the average now - since it's also
    # the selected model, model line == average line.
    assert widget.last_mean_raw["accuracy"] == 0.9


def test_on_axis_hovered_accepts_empty_numpy_array(qtbot):
    widget = VisualiseComparisonRadarWidget()
    qtbot.addWidget(widget)
    widget._on_axis_hovered(None, np.array([]))


def test_on_axis_hovered_accepts_multi_element_numpy_array_without_crashing(qtbot):
    widget = VisualiseComparisonRadarWidget()
    qtbot.addWidget(widget)

    class FakeSpot:
        def data(self):
            return None

    points = np.array([FakeSpot(), FakeSpot()], dtype=object)
    widget._on_axis_hovered(None, points)


def test_favorites_only_and_split_toggles_are_not_on_this_page(qtbot):
    # Temporarily removed from the UI - see visualise_comparison_radar.py.
    # (Export was added back - it belongs on every visual comparison view.)
    widget = VisualiseComparisonRadarWidget()
    qtbot.addWidget(widget)

    assert not hasattr(widget, "favorites_only_btn")
    assert not hasattr(widget, "split_toggle_btn")
    assert hasattr(widget, "export_btn")


def test_no_separate_label_next_to_compare_dropdown(qtbot):
    # The dropdown's own placeholder text ("Include in comparison") is
    # what's shown until something's picked, same as every other dropdown
    # in the app - no separate QLabel duplicating it.
    widget = VisualiseComparisonRadarWidget()
    qtbot.addWidget(widget)

    labels = [c.text() for c in widget.findChildren(type(widget.title)) if c.text() == "Include in comparison:"]
    assert labels == []


def test_legend_labels_have_no_inherited_border(qtbot):
    # graph_card's own stylesheet (QWidget { border: 2px solid black; ... })
    # cascades to any descendant QWidget that doesn't override
    # border/background itself - the legend text labels used to inherit it
    # and show up as boxed frames.
    widget = VisualiseComparisonRadarWidget()
    qtbot.addWidget(widget)

    for text in ("Selected model", "Average of included models"):
        label = next(c for c in widget.findChildren(type(widget.title)) if c.text() == text)
        style = label.styleSheet()
        assert "border: none" in style
        assert "background: transparent" in style
