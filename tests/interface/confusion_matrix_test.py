from hamelin.interface.widgets.confusion_matrix import ConfusionMatrixWidget


def _render(widget, labels, matrix):
    widget.last_labels = labels
    widget.last_matrix = matrix
    widget._render_table(labels, matrix)


def test_render_table_shows_raw_counts_by_default(qtbot):
    widget = ConfusionMatrixWidget()
    qtbot.addWidget(widget)

    _render(widget, ["a", "b"], [[8, 2], [1, 9]])

    assert widget.table.item(0, 0).text() == "8"
    assert widget.table.item(1, 1).text() == "9"


def test_toggle_display_switches_to_percentages(qtbot):
    widget = ConfusionMatrixWidget()
    qtbot.addWidget(widget)
    _render(widget, ["a", "b"], [[8, 2], [1, 9]])

    widget.on_toggle_display()

    assert widget.show_percentage is True
    assert widget.table.item(0, 0).text() == "80.0%"
    assert widget.toggle_btn.text() == "Show Counts"


def test_on_cell_clicked_filters_matching_patients(qtbot):
    widget = ConfusionMatrixWidget()
    qtbot.addWidget(widget)
    widget.last_labels = ["sick", "healthy"]
    widget.last_rows = [
        {"_true_label": "sick", "_predicted_label": "healthy", "_confidence": 0.4, "age": 50},
        {"_true_label": "sick", "_predicted_label": "sick", "_confidence": 0.9, "age": 60},
        {"_true_label": "healthy", "_predicted_label": "healthy", "_confidence": 0.8, "age": 40},
    ]

    widget.on_cell_clicked(0, 1)  # true=sick, predicted=healthy

    assert widget.error_popup is not None
    matches = [
        r for r in widget.last_rows
        if r["_true_label"] == "sick" and r["_predicted_label"] == "healthy"
    ]
    assert len(matches) == 1
    assert matches[0]["age"] == 50


def test_on_cell_clicked_out_of_range_does_nothing(qtbot):
    widget = ConfusionMatrixWidget()
    qtbot.addWidget(widget)
    widget.last_labels = ["a", "b"]
    widget.last_rows = []

    widget.on_cell_clicked(5, 5)

    assert widget.error_popup is None


def test_clear_matrix_empties_the_table(qtbot):
    widget = ConfusionMatrixWidget()
    qtbot.addWidget(widget)
    _render(widget, ["a", "b"], [[1, 0], [0, 1]])

    widget.clear_matrix()

    assert widget.table.rowCount() == 0
    assert widget.table.columnCount() == 0


# update_confusion_matrix - a missing dataset_path (get_model_dataset()
# reads description.json, which only exists for Ludwig's own run output,
# not model_checkpoints/) used to short-circuit the whole page even when
# compute_confusion_matrix() could still succeed from test_predictions.csv
# alone - it doesn't actually need dataset_path in that case.

def test_missing_dataset_path_does_not_block_a_saved_predictions_result(qtbot, monkeypatch):
    import hamelin.interface.widgets.confusion_matrix as cm_mod

    monkeypatch.setattr(cm_mod.gmp, "model_path_from_name", lambda m: "fake/path")
    monkeypatch.setattr(cm_mod.gmp, "get_model_dataset", lambda p: None)
    monkeypatch.setattr(cm_mod.gmp, "get_run_metadata", lambda p: {})
    monkeypatch.setattr(
        cm_mod.pcm, "compute_confusion_matrix",
        lambda model_path, dataset_path, **kwargs: {"labels": ["a", "b"], "matrix": [[1, 0], [0, 1]], "rows": []},
    )

    widget = ConfusionMatrixWidget()
    qtbot.addWidget(widget)
    widget.models_dropdown.selected = "fake_model"
    widget.update_confusion_matrix()

    assert widget.no_data_hint.isHidden() is True
    assert widget.table.isHidden() is False
    assert widget.table.rowCount() == 2


def test_genuine_failure_shows_no_data_hint_instead_of_a_blank_table(qtbot, monkeypatch):
    import hamelin.interface.widgets.confusion_matrix as cm_mod

    monkeypatch.setattr(cm_mod.gmp, "model_path_from_name", lambda m: "fake/path")
    monkeypatch.setattr(cm_mod.gmp, "get_model_dataset", lambda p: None)

    def _raise(model_path, dataset_path, **kwargs):
        raise ValueError("no predictions, no dataset")
    monkeypatch.setattr(cm_mod.pcm, "compute_confusion_matrix", _raise)

    widget = ConfusionMatrixWidget()
    qtbot.addWidget(widget)
    widget.models_dropdown.selected = "fake_model"
    widget.update_confusion_matrix()

    assert widget.no_data_hint.isHidden() is False
    assert widget.table.isHidden() is True


# Decision threshold input

def test_threshold_input_hidden_when_not_supported(qtbot, monkeypatch):
    import hamelin.interface.widgets.confusion_matrix as cm_mod

    monkeypatch.setattr(cm_mod.gmp, "model_path_from_name", lambda m: "fake/path")
    monkeypatch.setattr(cm_mod.gmp, "get_model_dataset", lambda p: None)
    monkeypatch.setattr(cm_mod.gmp, "get_run_metadata", lambda p: {})
    monkeypatch.setattr(cm_mod.pcm, "supports_threshold_adjustment", lambda p: False)
    monkeypatch.setattr(
        cm_mod.pcm, "compute_confusion_matrix",
        lambda model_path, dataset_path, **kwargs: {"labels": ["a", "b"], "matrix": [[1, 0], [0, 1]], "rows": []},
    )

    widget = ConfusionMatrixWidget()
    qtbot.addWidget(widget)
    widget.models_dropdown.selected = "fake_model"
    widget.update_confusion_matrix()

    assert widget.threshold_group.isHidden() is True


def test_threshold_input_shown_and_passed_through_when_supported(qtbot, monkeypatch):
    import hamelin.interface.widgets.confusion_matrix as cm_mod

    monkeypatch.setattr(cm_mod.gmp, "model_path_from_name", lambda m: "fake/path")
    monkeypatch.setattr(cm_mod.gmp, "get_model_dataset", lambda p: None)
    monkeypatch.setattr(cm_mod.gmp, "get_run_metadata", lambda p: {})
    monkeypatch.setattr(cm_mod.pcm, "supports_threshold_adjustment", lambda p: True)

    captured = {}
    def _fake_compute(model_path, dataset_path, threshold=None):
        captured["threshold"] = threshold
        return {"labels": ["a", "b"], "matrix": [[1, 0], [0, 1]], "rows": []}
    monkeypatch.setattr(cm_mod.pcm, "compute_confusion_matrix", _fake_compute)

    widget = ConfusionMatrixWidget()
    qtbot.addWidget(widget)
    widget.models_dropdown.selected = "fake_model"
    widget.update_confusion_matrix()

    assert widget.threshold_group.isHidden() is False
    assert captured["threshold"] == 0.5

    widget.threshold_input.setValue(30)

    assert widget.threshold_input.value() == 30
    assert captured["threshold"] == 0.30


def test_threshold_resets_to_default_on_new_model_selection(qtbot, monkeypatch):
    import hamelin.interface.widgets.confusion_matrix as cm_mod

    monkeypatch.setattr(cm_mod.gmp, "get_model_dataset", lambda p: None)
    monkeypatch.setattr(cm_mod.gmp, "get_run_metadata", lambda p: {})
    monkeypatch.setattr(cm_mod.pcm, "supports_threshold_adjustment", lambda p: True)
    monkeypatch.setattr(
        cm_mod.pcm, "compute_confusion_matrix",
        lambda model_path, dataset_path, threshold=None: {"labels": ["a", "b"], "matrix": [[1, 0], [0, 1]], "rows": []},
    )
    monkeypatch.setattr(cm_mod.gmp, "model_path_from_name", lambda m: f"fake/{m}")

    widget = ConfusionMatrixWidget()
    qtbot.addWidget(widget)
    widget.models_dropdown.selected = "model_a"
    widget.update_confusion_matrix()
    widget.threshold_input.setValue(20)
    assert widget.threshold_value == 0.20

    widget.models_dropdown.selected = "model_b"
    widget.update_confusion_matrix()

    assert widget.threshold_value == 0.5
    assert widget.threshold_input.value() == 50
