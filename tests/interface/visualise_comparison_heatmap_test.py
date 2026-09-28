import numpy as np
from matplotlib.backend_bases import MouseEvent

from hamelin.interface.widgets.visualise_comparison_heatmap import VisualiseComparisonHeatmap
from hamelin.interface.utils.app_state import app_state


def _click_label(widget, index):
    renderer = widget.canvas.get_renderer()
    label = widget.ax.get_yticklabels()[index]
    bbox = label.get_window_extent(renderer=renderer)
    cx, cy = bbox.x0 + bbox.width / 2, bbox.y0 + bbox.height / 2
    widget._on_heatmap_clicked(MouseEvent("button_press_event", widget.canvas, cx, cy))


def test_heatmap_shows_star_prefix_for_favorited_models(qtbot, monkeypatch):
    import hamelin.interface.utils.get_model_paths as gmp
    import hamelin.interface.widgets.visualise_comparison_heatmap as heatmap_mod

    models = gmp.get_model_names()
    if not models:
        return

    monkeypatch.setattr(heatmap_mod, "is_favorite", lambda m: m == models[0])

    widget = VisualiseComparisonHeatmap()
    qtbot.addWidget(widget)
    widget.show()
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)

    labels = [l.get_text() for l in widget.ax.get_yticklabels()]
    assert labels[0].startswith("★")
    for label in labels[1:]:
        assert label.startswith("☆")


def test_clicking_a_row_label_toggles_favorite(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp
    import hamelin.interface.utils.favorites as favorites

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonHeatmap()
    qtbot.addWidget(widget)
    widget.show()
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)

    was_favorite = favorites.is_favorite(models[0])
    _click_label(widget, 0)
    assert favorites.is_favorite(models[0]) is (not was_favorite)

    # restore state so this test doesn't leak into others via favorites.json
    _click_label(widget, 0)
    assert favorites.is_favorite(models[0]) is was_favorite


def test_clicking_outside_any_label_does_nothing(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp
    import hamelin.interface.utils.favorites as favorites

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonHeatmap()
    qtbot.addWidget(widget)
    widget.show()
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)

    before = favorites.load_favorites()
    event = MouseEvent("button_press_event", widget.canvas, 1, 1)
    widget._on_heatmap_clicked(event)
    assert favorites.load_favorites() == before


def test_cells_are_annotated_with_raw_values(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonHeatmap()
    qtbot.addWidget(widget)
    widget.show()
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)

    texts = [t.get_text() for t in widget.ax.texts]
    assert len(texts) > 0
    for text in texts:
        float(text)  # every annotation should parse as a number


def test_resize_positions_info_button_bottom_right(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonHeatmap()
    qtbot.addWidget(widget)
    widget.show()
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)
    widget.resize(900, 700)

    pos = widget.info_btn.pos()
    assert pos.x() == widget.heatmap_card.width() - widget.info_btn.width() - 15
    assert pos.y() == 60


# favorites_only toggle

def test_favorites_only_limits_shown_models(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp
    import hamelin.interface.utils.favorites as favorites

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonHeatmap()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)

    was_favorite = favorites.is_favorite(models[0])
    if not was_favorite:
        favorites.toggle_favorite(models[0])

    widget.favorites_only_btn.setChecked(True)

    assert widget.models == [models[0]]

    if not was_favorite:
        favorites.toggle_favorite(models[0])  # restore


def test_favorites_only_with_no_favorites_shows_nothing(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp
    import hamelin.interface.utils.favorites as favorites

    models = gmp.get_model_names()
    if not models:
        return

    for m in models:
        if favorites.is_favorite(m):
            favorites.toggle_favorite(m)

    widget = VisualiseComparisonHeatmap()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)

    widget.favorites_only_btn.setChecked(True)

    assert widget.models == []


def test_unchecking_favorites_only_restores_all_models(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonHeatmap()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)

    widget.favorites_only_btn.setChecked(True)
    widget.favorites_only_btn.setChecked(False)

    assert widget.models == models


# split toggle (test / train)

def test_split_toggle_defaults_to_test(qtbot):
    widget = VisualiseComparisonHeatmap()
    qtbot.addWidget(widget)

    assert widget.split == "test"
    assert widget.split_toggle_btn.isChecked() is False


def test_toggling_split_switches_to_training_metrics(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_heatmap as vch

    monkeypatch.setattr(vch, "build_comparison_data", lambda models, split="test": (
        [{"model": m, f"{split}/accuracy/best": 0.5} for m in models],
        ["accuracy"],
        [f"{split}/accuracy/best"],
    ))

    widget = VisualiseComparisonHeatmap()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(["model_a"], None)

    widget.split_toggle_btn.setChecked(True)

    assert widget.split == "training"
    assert widget.metrics_keys == ["training/accuracy/best"]
    assert "Train" in widget.split_toggle_btn.text()


# simple-mode priority gate

def _fake_build_comparison_data(models, split="test"):
    return (
        [{"model": "model_a", "test/accuracy/best": 0.9,
          "test/precision/best": 0.8, "test/roc_auc/best": 0.85}],
        ["accuracy", "precision", "roc_auc"],
        ["test/accuracy/best", "test/precision/best", "test/roc_auc/best"],
    )


def test_simple_mode_shows_priority_gate_instead_of_the_heatmap(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_heatmap as vch

    monkeypatch.setattr(vch, "build_comparison_data", _fake_build_comparison_data)

    widget = VisualiseComparisonHeatmap()
    qtbot.addWidget(widget)

    app_state.set_advanced_mode(False)
    widget.set_data(["model_a"], None)

    assert widget.priority_selector.isVisibleTo(widget) is True
    assert widget.heatmap_card.isVisibleTo(widget) is False


def test_choosing_a_priority_reveals_the_heatmap_and_filters_columns(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_heatmap as vch

    monkeypatch.setattr(vch, "build_comparison_data", _fake_build_comparison_data)

    widget = VisualiseComparisonHeatmap()
    qtbot.addWidget(widget)

    app_state.set_advanced_mode(False)
    widget.set_data(["model_a"], None)
    widget.priority_selector._cards["precision"].mousePressEvent(None)

    assert widget.priority_selector.isVisibleTo(widget) is False
    assert widget.heatmap_card.isVisibleTo(widget) is True
    # precision (priority) + roc_auc (has a quality scale) survive, with
    # precision first; accuracy (neither) is dropped.
    assert widget.display_metric_names == ["precision", "roc_auc"]
    # export/glossary still see the full, unfiltered set.
    assert widget.metric_names == ["accuracy", "precision", "roc_auc"]

    # a later set_data() doesn't re-ask - remembered for the page's life.
    widget.set_data(["model_a"], None)
    assert widget.priority_selector.isVisibleTo(widget) is False


def test_advanced_mode_skips_the_gate_and_shows_every_metric(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_heatmap as vch

    monkeypatch.setattr(vch, "build_comparison_data", _fake_build_comparison_data)

    widget = VisualiseComparisonHeatmap()
    qtbot.addWidget(widget)

    app_state.set_advanced_mode(True)
    widget.set_data(["model_a"], None)

    assert widget.priority_selector.isVisibleTo(widget) is False
    assert widget.heatmap_card.isVisibleTo(widget) is True
    assert widget.display_metric_names == ["accuracy", "precision", "roc_auc"]
