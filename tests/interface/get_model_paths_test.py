import json

import hamelin.interface.utils.get_model_paths as gmp


def _make_run(results_dir, run_name, nested_model_dir=True, hyperparams=None, description=None, report=None):
    run_dir = results_dir / run_name
    if nested_model_dir:
        model_dir = run_dir / "model"
    else:
        model_dir = run_dir
    model_dir.mkdir(parents=True)

    (model_dir / "model_hyperparameters.json").write_text(json.dumps(hyperparams or {}))

    if description is not None:
        (run_dir / "description.json").write_text(json.dumps(description))
    if report is not None:
        (run_dir / "training_report.json").write_text(json.dumps(report))

    return run_dir, model_dir


# get_model_paths / get_model_names / model_path_from_name

def test_get_model_paths_missing_dir_returns_empty(tmp_path):
    assert gmp.get_model_paths(tmp_path / "nope") == []


def test_get_model_paths_ignores_empty_directories(tmp_path):
    _make_run(tmp_path, "experiment_run_1")
    (tmp_path / "some_other_dir").mkdir()
    models = gmp.get_model_paths(tmp_path)
    assert [m["run"] for m in models] == ["experiment_run_1"]


def test_get_model_paths_is_not_limited_to_the_experiment_run_prefix(tmp_path):
    # Folders are recognized by structure (a model_hyperparameters.json,
    # flat or nested), not by name - e.g. Hamelin saves its checkpoints
    # under model_checkpoints/<model_id>/, not experiment_run*.
    _make_run(tmp_path, "some_hamelin_model_id")
    models = gmp.get_model_paths(tmp_path)
    assert [m["run"] for m in models] == ["some_hamelin_model_id"]


def test_get_model_paths_supports_nested_and_flat_model_dir(tmp_path):
    _make_run(tmp_path, "experiment_run_nested", nested_model_dir=True)
    _make_run(tmp_path, "experiment_run_flat", nested_model_dir=False)
    models = {m["run"]: m["model_path"] for m in gmp.get_model_paths(tmp_path)}
    assert models["experiment_run_nested"].endswith("experiment_run_nested/model")
    assert models["experiment_run_flat"].endswith("experiment_run_flat")


def test_get_model_paths_skips_runs_without_hyperparameters(tmp_path):
    run_dir = tmp_path / "experiment_run_empty"
    run_dir.mkdir()
    assert gmp.get_model_paths(tmp_path) == []


def test_get_model_names(tmp_path):
    _make_run(tmp_path, "experiment_run_a")
    _make_run(tmp_path, "experiment_run_b")
    assert sorted(gmp.get_model_names(tmp_path)) == ["experiment_run_a", "experiment_run_b"]


def test_model_path_from_name_found_and_not_found(tmp_path):
    _make_run(tmp_path, "experiment_run_a")
    assert gmp.model_path_from_name("experiment_run_a", tmp_path) is not None
    assert gmp.model_path_from_name("does_not_exist", tmp_path) is None


# load_training_report / load_run_description

def test_load_training_report_missing_returns_empty(tmp_path):
    assert gmp.load_training_report(tmp_path / "missing") == {}


def test_load_training_report_reads_from_run_dir_when_model_path_is_nested(tmp_path):
    run_dir, model_dir = _make_run(tmp_path, "experiment_run_a", report={"epochs_trained": 5})
    assert gmp.load_training_report(model_dir)["epochs_trained"] == 5
    assert gmp.load_training_report(run_dir)["epochs_trained"] == 5


def test_load_run_description_missing_returns_empty(tmp_path):
    assert gmp.load_run_description(tmp_path / "missing") == {}


# get_model_dataset

def test_get_model_dataset_no_dataset_field(tmp_path):
    _, model_dir = _make_run(tmp_path, "experiment_run_a", description={})
    assert gmp.get_model_dataset(model_dir) is None


def test_get_model_dataset_resolves_absolute_existing_path(tmp_path):
    dataset_file = tmp_path / "data.csv"
    dataset_file.write_text("a,b\n1,2\n")
    _, model_dir = _make_run(tmp_path, "experiment_run_a", description={"dataset": str(dataset_file)})
    assert gmp.get_model_dataset(model_dir) == str(dataset_file)


def test_get_model_dataset_missing_file_returns_none(tmp_path):
    _, model_dir = _make_run(tmp_path, "experiment_run_a", description={"dataset": "nope.csv"})
    assert gmp.get_model_dataset(model_dir) is None


# get_dataset_size / dataset_size_lines

def test_get_dataset_size_counts_csv_rows(tmp_path):
    dataset_file = tmp_path / "data.csv"
    dataset_file.write_text("a,b\n1,2\n3,4\n5,6\n")
    _, model_dir = _make_run(tmp_path, "experiment_run_a", description={"dataset": str(dataset_file)})
    assert gmp.get_dataset_size(model_dir) == 3


def test_get_dataset_size_none_when_dataset_unresolvable(tmp_path):
    _, model_dir = _make_run(tmp_path, "experiment_run_a", description={})
    assert gmp.get_dataset_size(model_dir) is None


def test_dataset_size_lines_lists_each_model_and_a_caveat(tmp_path):
    # No test_predictions.csv here - whole-dataset approximation path.
    dataset_file = tmp_path / "data.csv"
    dataset_file.write_text("a\n1\n2\n")
    _make_run(tmp_path, "experiment_run_a", description={"dataset": str(dataset_file)})

    lines, caveat = gmp.dataset_size_lines(["experiment_run_a"], results_dir=tmp_path)

    assert lines == ["experiment_run_a: ~2 patients (whole dataset - exact test size not recorded for this run)"]
    assert "less reliable" in caveat


def test_dataset_size_lines_unknown_model(tmp_path):
    lines, caveat = gmp.dataset_size_lines(["does_not_exist"], results_dir=tmp_path)
    assert lines == ["does_not_exist: dataset size unknown"]


# get_evaluated_size - prefers the exact test_predictions.csv row count

def test_get_evaluated_size_exact_from_saved_predictions(tmp_path):
    _, model_dir = _make_run(tmp_path, "experiment_run_a")
    (model_dir / "test_predictions.csv").write_text("y_true,y_pred\nyes,yes\nno,yes\nno,no\n")

    size, is_exact = gmp.get_evaluated_size(model_dir)

    assert size == 3
    assert is_exact is True


def test_get_evaluated_size_falls_back_to_whole_dataset(tmp_path):
    dataset_file = tmp_path / "data.csv"
    dataset_file.write_text("a\n1\n2\n3\n4\n")
    _, model_dir = _make_run(tmp_path, "experiment_run_a", description={"dataset": str(dataset_file)})

    size, is_exact = gmp.get_evaluated_size(model_dir)

    assert size == 4
    assert is_exact is False


def test_get_evaluated_size_none_when_neither_available(tmp_path):
    _, model_dir = _make_run(tmp_path, "experiment_run_a", description={})
    assert gmp.get_evaluated_size(model_dir) == (None, False)


def test_dataset_size_lines_marks_exact_test_set_when_available(tmp_path):
    _, model_dir = _make_run(tmp_path, "experiment_run_a")
    (model_dir / "test_predictions.csv").write_text("y_true,y_pred\nyes,yes\nno,no\n")

    lines, _ = gmp.dataset_size_lines(["experiment_run_a"], results_dir=tmp_path)

    assert lines == ["experiment_run_a: 2 patients evaluated (exact test set)"]


# get_output_feature_info

def test_get_output_feature_info_from_data_schema(tmp_path):
    report = {"data_schema": {"output_features": [{"type": "category", "name": "outcome", "classes": ["a", "b"]}]}}
    _, model_dir = _make_run(tmp_path, "experiment_run_a", report=report)
    info = gmp.get_output_feature_info(model_dir)
    assert info == {"type": "category", "name": "outcome", "classes": ["a", "b"]}


def test_get_output_feature_info_falls_back_to_config(tmp_path):
    report = {"config": {"output_features": [{"type": "number", "name": "score"}]}}
    _, model_dir = _make_run(tmp_path, "experiment_run_a", report=report)
    info = gmp.get_output_feature_info(model_dir)
    assert info == {"type": "number", "name": "score", "classes": None}


def test_get_output_feature_info_empty_when_nothing_available(tmp_path):
    _, model_dir = _make_run(tmp_path, "experiment_run_a", report={})
    assert gmp.get_output_feature_info(model_dir) == {}


# get_model_config

def test_get_model_config_strips_defaults_by_default(tmp_path):
    report = {"config": {"trainer": {"epochs": 5}, "defaults": {"huge": "block"}}}
    _, model_dir = _make_run(tmp_path, "experiment_run_a", report=report)
    assert "defaults" not in gmp.get_model_config(model_dir)
    assert "defaults" in gmp.get_model_config(model_dir, include_defaults=True)


# diff_configs

def test_diff_configs_reports_changed_added_and_removed_keys(tmp_path):
    report_a = {"config": {"trainer": {"epochs": 5, "batch_size": 32}}}
    report_b = {"config": {"trainer": {"epochs": 10}, "combiner": {"type": "concat"}}}
    _, model_a = _make_run(tmp_path, "experiment_run_a", report=report_a)
    _, model_b = _make_run(tmp_path, "experiment_run_b", report=report_b)

    diffs = {d["key"]: d for d in gmp.diff_configs(model_a, model_b)}

    assert diffs["trainer.epochs"]["value_a"] == 5
    assert diffs["trainer.epochs"]["value_b"] == 10
    assert diffs["trainer.epochs"]["only_in"] is None

    assert diffs["trainer.batch_size"]["only_in"] == "a"
    assert diffs["combiner.type"]["only_in"] == "b"


def test_diff_configs_identical_configs_have_no_diffs(tmp_path):
    report = {"config": {"trainer": {"epochs": 5}}}
    _, model_a = _make_run(tmp_path, "experiment_run_a", report=report)
    _, model_b = _make_run(tmp_path, "experiment_run_b", report=report)
    assert gmp.diff_configs(model_a, model_b) == []


# detect_model_type_from_ludwig

def test_detect_model_type_from_description_explicit_field(tmp_path):
    _, model_dir = _make_run(tmp_path, "experiment_run_a", description={"model_type": "CNN"})
    assert gmp.detect_model_type_from_ludwig(model_dir) == "CNN"


def test_detect_model_type_from_description_input_features(tmp_path):
    _, model_dir = _make_run(tmp_path, "experiment_run_a", description={"input_features": [{"type": "image"}]})
    assert gmp.detect_model_type_from_ludwig(model_dir) == "CNN"


def test_detect_model_type_from_hyperparameters_encoder(tmp_path):
    _, model_dir = _make_run(
        tmp_path, "experiment_run_a",
        hyperparams={"input_features": [{"encoder": "lstm"}]},
    )
    assert gmp.detect_model_type_from_ludwig(model_dir) == "RNN"


def test_detect_model_type_unknown_when_nothing_matches(tmp_path):
    run_dir = tmp_path / "experiment_run_a"
    run_dir.mkdir()
    assert gmp.detect_model_type_from_ludwig(run_dir) == "Unknown"


def test_detect_model_type_tabular_from_hyperparameters_is_mlp(tmp_path):
    # No description.json (the case for every model saved to
    # model_checkpoints/ via LudwigModel.save(), which never writes one) -
    # only model_hyperparameters.json, with plain tabular feature types and
    # no sequence/image encoder. Used to fall through to "Unknown".
    _, model_dir = _make_run(
        tmp_path, "experiment_run_a",
        hyperparams={"input_features": [{"type": "number"}, {"type": "category"}]},
    )
    assert gmp.detect_model_type_from_ludwig(model_dir) == "MLP"


# get_subgroup_columns

def test_get_subgroup_columns_picks_low_cardinality_columns(tmp_path):
    _, model_dir = _make_run(tmp_path, "experiment_run_a")
    # 9 distinct ages (one per row) - above max_unique=8, so treated as
    # continuous rather than a usable group axis; sex/outcome (2 values
    # each) are the real candidates.
    rows = "\n".join(
        f"{'F' if i % 2 else 'M'},{30 + i},{'no' if i % 2 else 'yes'},no,no,0.8" for i in range(9)
    )
    (model_dir / "test_predictions.csv").write_text("sex,age,outcome,y_true,y_pred,y_score\n" + rows + "\n")
    assert sorted(gmp.get_subgroup_columns(model_dir)) == ["outcome", "sex"]


def test_get_subgroup_columns_excludes_reserved_and_probability_columns(tmp_path):
    _, model_dir = _make_run(tmp_path, "experiment_run_a")
    (model_dir / "test_predictions.csv").write_text(
        "sex,y_true,y_pred,y_score,y_prob_no,y_prob_yes\n"
        "F,no,no,0.8,0.8,0.2\n"
        "M,yes,yes,0.7,0.3,0.7\n"
    )
    assert gmp.get_subgroup_columns(model_dir) == ["sex"]


def test_get_subgroup_columns_excludes_the_target_column(tmp_path):
    _, model_dir = _make_run(
        tmp_path, "experiment_run_a",
        report={"data_schema": {"output_features": [{"type": "binary", "name": "outcome"}]}},
    )
    (model_dir / "test_predictions.csv").write_text(
        "sex,outcome,y_true,y_pred,y_score\n"
        "F,no,no,no,0.8\n"
        "M,yes,yes,yes,0.7\n"
    )
    assert gmp.get_subgroup_columns(model_dir) == ["sex"]


def test_get_subgroup_columns_excludes_high_cardinality_columns(tmp_path):
    _, model_dir = _make_run(tmp_path, "experiment_run_a")
    header = "sex,patient_id,y_true,y_pred,y_score\n"
    rows = "".join(f"{'F' if i % 2 else 'M'},{i},no,no,0.8\n" for i in range(10))
    (model_dir / "test_predictions.csv").write_text(header + rows)
    assert gmp.get_subgroup_columns(model_dir) == ["sex"]


def test_get_subgroup_columns_excludes_constant_columns(tmp_path):
    _, model_dir = _make_run(tmp_path, "experiment_run_a")
    (model_dir / "test_predictions.csv").write_text(
        "sex,site,y_true,y_pred,y_score\n"
        "F,A,no,no,0.8\n"
        "M,A,yes,yes,0.7\n"
    )
    # "site" is the same value on every row - not a usable split.
    assert gmp.get_subgroup_columns(model_dir) == ["sex"]


def test_get_subgroup_columns_empty_when_no_saved_predictions(tmp_path):
    _, model_dir = _make_run(tmp_path, "experiment_run_a")
    assert gmp.get_subgroup_columns(model_dir) == []
