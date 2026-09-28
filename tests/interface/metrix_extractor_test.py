import json

from hamelin.interface.utils import metrix_extractor as mx


def _write_report(root, model_dir, metrics):
    run_dir = root / model_dir
    run_dir.mkdir(parents=True)
    (run_dir / "training_report.json").write_text(json.dumps({"metrics": metrics}))


def test_load_run_metrics_missing_file(tmp_path):
    assert mx.load_run_metrics("does_not_exist", results_dir=tmp_path) == {}


def test_load_run_metrics_malformed_json(tmp_path):
    run_dir = tmp_path / "bad_run"
    run_dir.mkdir()
    (run_dir / "training_report.json").write_text("{not json")
    assert mx.load_run_metrics("bad_run", results_dir=tmp_path) == {}


def test_load_run_metrics_flattens_nested_metrics(tmp_path):
    _write_report(tmp_path, "run1", {
        "test": {"accuracy": {"best": 0.9, "last": 0.85}},
        "train": {"loss": {"last": 0.1}},
    })
    flat = mx.load_run_metrics("run1", results_dir=tmp_path)
    assert flat == {
        "test/accuracy/best": 0.9,
        "test/accuracy/last": 0.85,
        "train/loss/last": 0.1,
    }


def test_load_run_metrics_follows_a_changed_results_dir(tmp_path, monkeypatch):
    # Regression test for the frozen-at-import bug: load_run_metrics used to
    # bake gmp.RESULTS_DIR's value into a module-level constant at import
    # time, so it never saw later changes to the results directory.
    import hamelin.interface.utils.get_model_paths as gmp
    monkeypatch.setattr(gmp, "RESULTS_DIR", str(tmp_path))
    _write_report(tmp_path, "run1", {"test": {"accuracy": {"best": 0.9}}})

    assert mx.load_run_metrics("run1") == {"test/accuracy/best": 0.9}


def test_extract_test_metrics_prefers_best_over_last():
    metrics = {
        "test/accuracy/last": 0.7,
        "test/accuracy/best": 0.9,
        "test/loss/last": 0.2,
        "train/accuracy/best": 0.99,
    }
    names, keys = mx.extract_test_metrics(metrics)
    assert set(names) == {"accuracy", "loss"}
    assert "test/accuracy/best" in keys
    assert "test/accuracy/last" not in keys
    assert "train/accuracy/best" not in keys


def test_extract_test_metrics_ignores_non_numeric():
    metrics = {"test/label/best": "positive", "test/accuracy/best": 0.9}
    names, keys = mx.extract_test_metrics(metrics)
    assert names == ["accuracy"]
    assert keys == ["test/accuracy/best"]


def test_extract_test_metrics_empty():
    assert mx.extract_test_metrics({}) == ([], [])


def test_extract_split_metrics_reads_the_training_split():
    metrics = {
        "training/accuracy/best": 0.99,
        "test/accuracy/best": 0.7,
    }
    names, keys = mx.extract_split_metrics(metrics, "training")
    assert names == ["accuracy"]
    assert keys == ["training/accuracy/best"]


def test_build_comparison_data_can_read_the_training_split(monkeypatch):
    monkeypatch.setattr(mx, "load_run_metrics", lambda m: {
        "training/accuracy/best": 0.99,
        "test/accuracy/best": 0.7,
    })

    data, metric_names, metrics_keys = mx.build_comparison_data(["run_a"], split="training")

    assert metric_names == ["accuracy"]
    assert metrics_keys == ["training/accuracy/best"]


def test_is_lower_better():
    assert mx.is_lower_better("loss") is True
    assert mx.is_lower_better("test/mean_squared_error") is True
    assert mx.is_lower_better("accuracy") is False
    assert mx.is_lower_better("f1") is False


def test_checkpoint_disclosure_all_best():
    text = mx.checkpoint_disclosure(["test/accuracy/best", "test/loss/best"])
    assert "best checkpoint" in text


def test_checkpoint_disclosure_all_last():
    text = mx.checkpoint_disclosure(["test/accuracy/last"])
    assert "final-epoch" in text


def test_checkpoint_disclosure_mixed():
    text = mx.checkpoint_disclosure(["test/accuracy/best", "test/loss/last"])
    assert "mix" in text


def test_checkpoint_disclosure_empty():
    assert mx.checkpoint_disclosure([]) == ""


# build_comparison_data - shared by the table/graph/heatmap comparison views

def test_build_comparison_data_builds_one_row_per_model(monkeypatch):
    monkeypatch.setattr(mx, "load_run_metrics", lambda m: {
        "test/accuracy/best": 0.9 if m == "run_a" else 0.8,
    })

    data, metric_names, metrics_keys = mx.build_comparison_data(["run_a", "run_b"])

    assert [row["model"] for row in data] == ["run_a", "run_b"]
    assert data[0]["test/accuracy/best"] == 0.9
    assert metric_names == ["accuracy"]
    assert metrics_keys == ["test/accuracy/best"]


def test_build_comparison_data_unions_metrics_across_models(monkeypatch):
    def fake_metrics(m):
        if m == "run_a":
            return {"test/accuracy/best": 0.9}
        return {"test/f1/best": 0.7}

    monkeypatch.setattr(mx, "load_run_metrics", fake_metrics)

    data, metric_names, metrics_keys = mx.build_comparison_data(["run_a", "run_b"])

    assert metric_names == ["accuracy", "f1"]
    assert set(metrics_keys) == {"test/accuracy/best", "test/f1/best"}


def test_build_comparison_data_with_no_models():
    assert mx.build_comparison_data([]) == ([], [], [])


def test_build_comparison_data_missing_metrics_file(monkeypatch):
    monkeypatch.setattr(mx, "load_run_metrics", lambda m: {})

    data, metric_names, metrics_keys = mx.build_comparison_data(["run_a"])

    assert data == [{"model": "run_a"}]
    assert metric_names == []
    assert metrics_keys == []


# get_target_column - lets callers show what a model actually predicts
# next to its name, e.g. in the comparison model picker.

def _write_report_with_config(root, model_dir, output_features):
    run_dir = root / model_dir
    run_dir.mkdir(parents=True)
    (run_dir / "training_report.json").write_text(json.dumps({
        "config": {"output_features": output_features},
    }))


def test_get_target_column_reads_the_output_feature(tmp_path):
    _write_report_with_config(tmp_path, "run1", [{"column": "sentiment"}])
    assert mx.get_target_column("run1", results_dir=tmp_path) == "sentiment"


def test_get_target_column_missing_file(tmp_path):
    assert mx.get_target_column("does_not_exist", results_dir=tmp_path) is None


def test_get_target_column_malformed_json(tmp_path):
    run_dir = tmp_path / "bad_run"
    run_dir.mkdir()
    (run_dir / "training_report.json").write_text("{not json")
    assert mx.get_target_column("bad_run", results_dir=tmp_path) is None


def test_get_target_column_missing_output_features(tmp_path):
    run_dir = tmp_path / "run1"
    run_dir.mkdir()
    (run_dir / "training_report.json").write_text(json.dumps({"config": {}}))
    assert mx.get_target_column("run1", results_dir=tmp_path) is None
