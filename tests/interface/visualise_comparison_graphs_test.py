from PySide6.QtCore import QPointF

from hamelin.interface.widgets.visualise_comparison_graphs import VisualiseComparisonGraphsWidget
from hamelin.interface.utils.app_state import app_state


def _select_first_metric(widget):
    widget.metric_selector.selected = widget.metric_labels[0]
    widget.metric_selector._update_label()
    widget.update_graph()


class _FakeClickEvent:
    def __init__(self, pos):
        self._pos = pos

    def scenePos(self):
        return self._pos


def test_axis_labels_get_star_prefix_for_favorited_models(qtbot, monkeypatch):
    import hamelin.interface.utils.get_model_paths as gmp
    import hamelin.interface.widgets.visualise_comparison_graphs as graphs_mod

    models = gmp.get_model_names()
    if not models:
        return

    monkeypatch.setattr(graphs_mod, "is_favorite", lambda m: m == models[0])

    widget = VisualiseComparisonGraphsWidget()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)
    _select_first_metric(widget)

    assert widget._plotted_models[0] == models[0]

    axis = widget.graph.getAxis("bottom")
    ticks = axis._tickLevels[0] if hasattr(axis, "_tickLevels") else None
    assert ticks is not None
    labels = [text for _, text in ticks]
    assert labels[0].startswith("★")
    for label in labels[1:]:
        assert label.startswith("☆")


def test_clicking_below_plot_on_a_model_column_toggles_favorite(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp
    import hamelin.interface.utils.favorites as favorites

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonGraphsWidget()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)
    _select_first_metric(widget)

    vb = widget.graph.getViewBox()
    plot_rect = vb.mapRectToScene(vb.boundingRect())
    scene_x = vb.mapViewToScene(QPointF(0, 0)).x()
    below_plot = QPointF(scene_x, plot_rect.bottom() + 10)

    was_favorite = favorites.is_favorite(widget._plotted_models[0])
    widget._on_graph_clicked(_FakeClickEvent(below_plot))
    assert favorites.is_favorite(widget._plotted_models[0]) is (not was_favorite)

    widget._on_graph_clicked(_FakeClickEvent(below_plot))
    assert favorites.is_favorite(widget._plotted_models[0]) is was_favorite


def test_clicking_on_a_bar_does_not_toggle_favorite(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp
    import hamelin.interface.utils.favorites as favorites

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonGraphsWidget()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)
    _select_first_metric(widget)

    vb = widget.graph.getViewBox()
    plot_rect = vb.mapRectToScene(vb.boundingRect())
    scene_x = vb.mapViewToScene(QPointF(0, 0)).x()
    on_bar = QPointF(scene_x, plot_rect.center().y())

    before = favorites.load_favorites()
    widget._on_graph_clicked(_FakeClickEvent(on_bar))
    assert favorites.load_favorites() == before


def test_clicking_with_no_data_plotted_does_not_crash(qtbot):
    widget = VisualiseComparisonGraphsWidget()
    qtbot.addWidget(widget)
    widget._on_graph_clicked(_FakeClickEvent(QPointF(0, 0)))


def test_resize_positions_info_button_bottom_right(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonGraphsWidget()
    qtbot.addWidget(widget)
    widget.show()
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)
    widget.resize(900, 700)

    pos = widget.info_btn.pos()
    assert pos.x() == widget.graph_card.width() - widget.info_btn.width() - 15
    assert pos.y() == 60


# favorites_only toggle

def test_favorites_only_limits_plotted_models(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp
    import hamelin.interface.utils.favorites as favorites

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonGraphsWidget()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)

    was_favorite = favorites.is_favorite(models[0])
    if not was_favorite:
        favorites.toggle_favorite(models[0])

    widget.favorites_only_btn.setChecked(True)
    _select_first_metric(widget)

    assert widget._plotted_models == [models[0]]

    if not was_favorite:
        favorites.toggle_favorite(models[0])  # restore


def test_favorites_only_with_no_favorites_plots_nothing(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp
    import hamelin.interface.utils.favorites as favorites

    models = gmp.get_model_names()
    if not models:
        return

    for m in models:
        if favorites.is_favorite(m):
            favorites.toggle_favorite(m)

    widget = VisualiseComparisonGraphsWidget()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)

    widget.favorites_only_btn.setChecked(True)

    assert widget._plotted_models == []


# split toggle (test / train)

def test_split_toggle_defaults_to_test(qtbot):
    widget = VisualiseComparisonGraphsWidget()
    qtbot.addWidget(widget)

    assert widget.split == "test"
    assert widget.split_toggle_btn.isChecked() is False


def test_toggling_split_switches_to_training_metrics(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_graphs as vcg

    monkeypatch.setattr(vcg, "build_comparison_data", lambda models, split="test": (
        [{"model": m, f"{split}/accuracy/best": 0.5} for m in models],
        ["accuracy"],
        [f"{split}/accuracy/best"],
    ))

    widget = VisualiseComparisonGraphsWidget()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(["model_a"], None)

    widget.split_toggle_btn.setChecked(True)

    assert widget.split == "training"
    assert widget.metrics_keys == ["training/accuracy/best"]
    assert "Train" in widget.split_toggle_btn.text()


def test_toggling_split_keeps_a_metric_selected_and_plotted(qtbot):
    # Regression test: metric_selector.clear() wipes the dropdown's
    # selection on every update_ui() call. Switching split used to have
    # nothing to re-select on (the old code only matched the exact launch
    # criterion key, whose split prefix no longer matches after toggling),
    # leaving the graph silently empty.
    import hamelin.interface.utils.get_model_paths as gmp

    models = gmp.get_model_names()
    if not models:
        return

    widget = VisualiseComparisonGraphsWidget()
    qtbot.addWidget(widget)
    app_state.set_advanced_mode(True)
    widget.set_data(models, None)

    assert widget.metric_selector.currentText() != ""
    assert widget._plotted_models != []

    widget.split_toggle_btn.setChecked(True)

    assert widget.metric_selector.currentText() != ""
    assert widget._plotted_models != []

    widget.split_toggle_btn.setChecked(False)

    assert widget.metric_selector.currentText() != ""
    assert widget._plotted_models != []


# simple-mode priority gate

def _fake_build_comparison_data(models, split="test"):
    return (
        [{"model": "model_a", "test/accuracy/best": 0.9,
          "test/precision/best": 0.8, "test/roc_auc/best": 0.85}],
        ["accuracy", "precision", "roc_auc"],
        ["test/accuracy/best", "test/precision/best", "test/roc_auc/best"],
    )


def test_simple_mode_shows_priority_gate_instead_of_the_graph(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_graphs as vcg

    monkeypatch.setattr(vcg, "build_comparison_data", _fake_build_comparison_data)

    widget = VisualiseComparisonGraphsWidget()
    qtbot.addWidget(widget)

    app_state.set_advanced_mode(False)
    widget.set_data(["model_a"], None)

    assert widget.priority_selector.isVisibleTo(widget) is True
    assert widget.graph_card.isVisibleTo(widget) is False
    assert widget.metric_selector.isVisibleTo(widget) is False
    assert widget._plotted_models == []


def test_choosing_a_priority_reveals_the_graph_and_preselects_the_metric(qtbot, monkeypatch):
    import hamelin.interface.widgets.visualise_comparison_graphs as vcg

    monkeypatch.setattr(vcg, "build_comparison_data", _fake_build_comparison_data)

    widget = VisualiseComparisonGraphsWidget()
    qtbot.addWidget(widget)

    app_state.set_advanced_mode(False)
    widget.set_data(["model_a"], None)
    widget.priority_selector._cards["precision"].mousePressEvent(None)

    assert widget.priority_selector.isVisibleTo(widget) is False
    assert widget.graph_card.isVisibleTo(widget) is True
    assert widget._selected_metric_name == "precision"
    assert widget.metric_selector.currentText() == "Reliability of Positive Results"

    # a later set_data() doesn't re-ask - remembered for the page's life.
    widget.set_data(["model_a"], None)
    assert widget.priority_selector.isVisibleTo(widget) is False
