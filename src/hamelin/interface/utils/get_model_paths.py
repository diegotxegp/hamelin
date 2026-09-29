import os
import pathlib

# Root folder to scan for trained-model runs. Overridable via env var so the
# app can be pointed at a project's model folder (e.g. when launched as a
# satellite tool from another app) instead of the local "results/" default.
RESULTS_DIR = os.environ.get("INTERFACE_RESULTS_DIR", "results")


def get_model_paths(results_dir=None):
    # None (rather than defaulting straight to RESULTS_DIR) so this reads
    # the module's current RESULTS_DIR on every call instead of freezing
    # whatever it was when this function was first defined - callers can
    # still override it explicitly by passing their own results_dir.
    root = pathlib.Path(results_dir if results_dir is not None else RESULTS_DIR)

    if not root.exists():
        return []

    models = []

    for p in root.iterdir():
        if not p.is_dir():
            continue

        # Recognized purely by structure (a model_hyperparameters.json,
        # flat or nested under "model/") rather than by folder-name prefix.
        # Used to only accept names starting with "experiment_run" - Ludwig's
        # own default naming - which meant a folder saved under a different
        # scheme (e.g. Hamelin's results/models/<model_id>/) was invisible
        # here even though its contents were in the exact shape this function
        # already knows how to read.
        model_file = p / "model" / "model_hyperparameters.json"
        alt_model_file = p / "model_hyperparameters.json"

        if model_file.exists():
            model_path = p / "model"
        elif alt_model_file.exists():
            model_path = p
        else:
            continue

        models.append({
            "run": p.name,
            "model_path": str(model_path)
        })

    return models

def get_model_names(results_dir=None):
    models = get_model_paths(results_dir)
    return [model["run"] for model in models]

def model_path_from_name(model_name, results_dir=None):
    models = get_model_paths(results_dir)
    for model in models:
        if model["run"] == model_name:
            return model["model_path"]
    return None

import json
from pathlib import Path


def _run_dir_from_model_path(model_path):
    """model_path points at .../experiment_run[/model]; the report/description
    files live one level up when a nested "model" dir is used."""
    p = Path(model_path)
    if p.name == "model":
        return p.parent
    return p


def load_training_report(model_path):
    run_dir = _run_dir_from_model_path(model_path)
    report_file = run_dir / "training_report.json"

    if not report_file.exists():
        return {}

    try:
        with open(report_file, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def load_run_description(model_path):
    run_dir = _run_dir_from_model_path(model_path)
    desc_file = run_dir / "description.json"

    if not desc_file.exists():
        return {}

    try:
        with open(desc_file, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def get_model_dataset(model_path):
    """Resolve the dataset file a given run was actually trained/evaluated
    on, instead of assuming a fixed filename. Falls back to None if the
    run's description doesn't record it, so callers can surface that
    instead of silently comparing against the wrong data.

    Ludwig writes the "dataset" field into description.json (the command
    that was run), not training_report.json.
    """
    desc = load_run_description(model_path)
    dataset = desc.get("dataset")

    if not dataset:
        return None

    dataset_path = Path(dataset)
    if not dataset_path.is_absolute():
        dataset_path = Path.cwd() / dataset_path

    return str(dataset_path) if dataset_path.exists() else None


def get_dataset_size(model_path):
    """Total row count of the dataset a run was trained/evaluated on, or
    None if it can't be resolved. This is the WHOLE dataset, not the size
    of the test split specifically - see get_evaluated_size() for the
    exact test-set count when it's available."""
    dataset_path = get_model_dataset(model_path)
    if not dataset_path:
        return None
    try:
        import pandas as pd
        return len(pd.read_csv(dataset_path))
    except Exception:
        return None


def load_test_predictions(model_path):
    """Load a run's saved test_predictions.csv - one row per held-out
    patient, with y_true/y_pred/y_score columns alongside the original
    features (see LudwigBackend._build_predictions_frame in hamelin-v2).
    Returns None if it doesn't exist (a run saved before this existed, or
    from a non-Ludwig backend) or can't be read, so callers can degrade
    gracefully (e.g. hide a confidence interval) instead of crashing."""
    predictions_csv = Path(model_path) / "test_predictions.csv"
    if not predictions_csv.exists():
        return None
    try:
        import pandas as pd
        return pd.read_csv(predictions_csv)
    except Exception:
        return None


def get_subgroup_columns(model_path, max_unique=8):
    """Column names in a run's saved test_predictions.csv that look like
    categorical patient attributes usable to break its metrics down by
    subgroup (e.g. sex, a comorbidity flag) - anything with few enough
    distinct values to be a meaningful group, excluding the columns this
    file itself adds (y_true/y_pred/y_score/y_prob_<class>). A continuous
    column (e.g. raw age) is excluded rather than treated as one group per
    value - binning it would need a real choice about bin edges, left for
    later rather than guessed here.

    Returns [] if there's no saved predictions file at all (nothing to
    break down), so callers can hide the feature entirely for a model
    saved before test_predictions.csv existed."""
    df = load_test_predictions(model_path)
    if df is None:
        return []

    # Excluding the target column itself - "accuracy broken down by the
    # thing being predicted" isn't a subgroup analysis, it's circular.
    target_name = get_output_feature_info(model_path).get("name")
    reserved = {"y_true", "y_pred", "y_score", target_name}
    candidates = []
    for col in df.columns:
        if col in reserved or col.startswith("y_prob_"):
            continue
        try:
            n_unique = df[col].nunique(dropna=True)
        except TypeError:
            continue
        if 1 < n_unique <= max_unique:
            candidates.append(col)
    return candidates


def get_evaluated_size(model_path):
    """Number of patients a run was actually evaluated on, and whether
    that's an exact count.

    Prefers test_predictions.csv (one row per held-out patient - see
    load_test_predictions): its row count IS the test set, no guessing
    needed. Falls back to get_dataset_size() - the WHOLE dataset's row
    count - for older runs saved before that file existed, which is only
    an upper bound (the real test split is some fraction of it, never
    recorded anywhere else for those runs) - callers should treat the two
    differently rather than presenting both as the same kind of number.

    Returns (size, is_exact) - size is None if neither is resolvable.
    """
    predictions = load_test_predictions(model_path)
    if predictions is not None:
        return len(predictions), True

    return get_dataset_size(model_path), False


def dataset_size_lines(models, results_dir=None):
    """Structured version of the comparison popups' dataset-size note: one
    line per model, plus a closing caveat, kept as separate strings so a UI
    can render them as its own distinct section instead of one plain-text
    blob. A model "tested" on a handful of patients can look far better or
    worse than it really is - this makes that visible instead of letting a
    clean-looking percentage speak for itself.

    Returns (per_model_lines, caveat).
    """
    lines = []
    for m in models:
        path = model_path_from_name(m, results_dir)
        size, is_exact = get_evaluated_size(path) if path else (None, False)
        if size is None:
            lines.append(f"{m}: dataset size unknown")
        elif is_exact:
            lines.append(f"{m}: {size} patients evaluated (exact test set)")
        else:
            lines.append(f"{m}: ~{size} patients (whole dataset - exact test size not recorded for this run)")

    caveat = (
        "Smaller datasets make these numbers less reliable: a model "
        "evaluated on a handful of patients can look far better or worse "
        "than it really is."
    )
    return lines, caveat


def get_output_feature_info(model_path):
    """Best-effort real answer for what a model predicts, read straight from
    the Ludwig run report / config rather than guessed from metric names.
    Returns a dict like {"type": "category", "name": "sentiment",
    "classes": ["positive", "negative"]} or {} if unavailable."""
    report = load_training_report(model_path)

    schema_outputs = report.get("data_schema", {}).get("output_features", [])
    if schema_outputs:
        f = schema_outputs[0]
        return {
            "type": f.get("type"),
            "name": f.get("name"),
            "classes": f.get("classes"),
        }

    config_outputs = report.get("config", {}).get("output_features", [])
    if config_outputs:
        f = config_outputs[0]
        return {"type": f.get("type"), "name": f.get("name"), "classes": None}

    run_dir = _run_dir_from_model_path(model_path)
    for fname in ("description.json",):
        desc_path = run_dir / fname
        if desc_path.exists():
            try:
                with open(desc_path, "r") as fh:
                    desc = json.load(fh)
                outs = desc.get("config", {}).get("output_features", [])
                if outs:
                    return {"type": outs[0].get("type"), "name": outs[0].get("name"), "classes": None}
            except Exception:
                pass

    return {}


OUTPUT_TYPE_LABELS = {
    "category": "Classification",
    "binary": "Classification",
    "set": "Multi-label Classification",
    "number": "Regression",
    "vector": "Regression",
    "sequence": "Sequence Generation",
    "text": "Text Generation",
    "timeseries": "Forecasting",
}


def get_run_metadata(model_path):
    """Human-facing provenance info for a run: dataset, Ludwig version,
    seed, epochs trained, and when it was generated. Used anywhere a model's
    numbers are shown, so results can't be read without knowing where they
    came from."""
    report = load_training_report(model_path)
    desc = load_run_description(model_path)
    dataset = get_model_dataset(model_path)

    return {
        "dataset_name": Path(desc["dataset"]).name if desc.get("dataset") else None,
        "dataset_path": dataset,
        "ludwig_version": report.get("environment", {}).get("ludwig_version") or report.get("ludwig_version"),
        "random_seed": report.get("random_seed"),
        "epochs_trained": report.get("epochs_trained"),
        "generated_at": report.get("generated_at"),
    }


def get_input_feature_names(model_path):
    """Names of the predictive variables (Ludwig input features) a model
    was trained on, read the same way get_output_feature_info() reads the
    target: training_report.json's data_schema first, falling back to its
    config, then to model_hyperparameters.json for a model whose report
    happens to be missing that section. Returns [] if none of those are
    available."""
    report = load_training_report(model_path)

    schema_inputs = report.get("data_schema", {}).get("input_features", [])
    if schema_inputs:
        return [f.get("name") for f in schema_inputs if f.get("name")]

    config_inputs = report.get("config", {}).get("input_features", [])
    if config_inputs:
        return [f.get("name") for f in config_inputs if f.get("name")]

    hp_path = Path(model_path) / "model_hyperparameters.json"
    if hp_path.exists():
        try:
            with open(hp_path, "r") as f:
                hp = json.load(f)
            return [f.get("name") for f in hp.get("input_features", []) if f.get("name")]
        except Exception:
            pass

    return []


def get_project_info(results_dir=None):
    """Metadata for the clinical project/study a model belongs to, read
    straight from Hamelin's own metadata.json - one level above
    RESULTS_DIR, since Hamelin always points RESULTS_DIR at
    "<project_dir>/results/models" (see MainWindow._open_interface_page).
    Returns {} when there's no such file - e.g. the standalone interface
    app (no INTERFACE_RESULTS_DIR override), which has no notion of a
    "project" at all - so callers can just skip showing this rather than
    show something wrong."""
    root = Path(results_dir if results_dir is not None else RESULTS_DIR)
    # <project>/results/models -> metadata.json lives at the project root.
    metadata_file = next(
        (p / "metadata.json" for p in (root.parent.parent, root.parent) if (p / "metadata.json").exists()),
        root.parent / "metadata.json",
    )

    if not metadata_file.exists():
        return {}

    try:
        with open(metadata_file, "r") as f:
            data = json.load(f)
    except Exception:
        return {}

    return {
        "name": data.get("name"),
        "protocol_number": data.get("protocol_number"),
        "institution": data.get("institution"),
        "principal_investigator": data.get("principal_investigator"),
        "study_type": data.get("study_type"),
        "primary_objective": data.get("primary_objective"),
        "secondary_objectives": data.get("secondary_objectives") or [],
    }


def get_model_config(model_path, include_defaults=False):
    """Full Ludwig config for a run, as recorded in training_report.json.

    By default this strips the "defaults" block: Ludwig always writes out
    per-feature-type defaults for every feature type it supports, not just
    the ones a given run actually uses, and that block dwarfs everything
    else in the config. Left in, it drowns out the settings that actually
    vary between two runs when diffing. Pass include_defaults=True to get
    the raw config back unfiltered.
    """
    report = load_training_report(model_path)
    config = report.get("config", {})

    if not include_defaults:
        config = {k: v for k, v in config.items() if k != "defaults"}

    return config


def _flatten_config(prefix, obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            _flatten_config(f"{prefix}.{k}" if prefix else str(k), v, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _flatten_config(f"{prefix}.{i}" if prefix else str(i), v, out)
    else:
        out[prefix] = obj


def flatten_config(config):
    """Public wrapper around _flatten_config for callers that just want a
    flat {"dotted.key": value} view of a full config, not a diff."""
    flat = {}
    _flatten_config("", config, flat)
    return flat


_MISSING = object()


def diff_configs(model_path_a, model_path_b, include_defaults=False):
    """Compare two runs' Ludwig configs and return only what differs.

    Returns a list of dicts, sorted by key:
        {"key": "trainer.learning_rate", "value_a": ..., "value_b": ...,
         "only_in": None | "a" | "b"}

    "only_in" is set when a key exists on only one side (e.g. one run has
    an extra input feature) so a UI can tell that apart from "same key,
    different value". Values are compared post-flattening, so a nested
    dict/list only shows up as a diff at the leaf keys that actually
    changed - not as one big opaque "config differs" blob.
    """
    config_a = get_model_config(model_path_a, include_defaults=include_defaults)
    config_b = get_model_config(model_path_b, include_defaults=include_defaults)

    flat_a, flat_b = {}, {}
    _flatten_config("", config_a, flat_a)
    _flatten_config("", config_b, flat_b)

    diffs = []
    for key in sorted(set(flat_a) | set(flat_b)):
        va = flat_a.get(key, _MISSING)
        vb = flat_b.get(key, _MISSING)

        if va is not _MISSING and vb is not _MISSING and va == vb:
            continue

        diffs.append({
            "key": key,
            "value_a": None if va is _MISSING else va,
            "value_b": None if vb is _MISSING else vb,
            "only_in": "b" if va is _MISSING else ("a" if vb is _MISSING else None),
        })

    return diffs


def detect_model_type_from_ludwig(model_path):
    """Best-effort label for the "Model Type" badge (visualise_gif.py).

    description.json is written by Ludwig's own train()/auto_train() run
    output (ludwig_runs/) - it's not written by LudwigModel.save(), so it's
    absent for anything saved to results/models/ (every model trained
    since the switch away from ludwig_runs/ as the canonical model
    location). model_hyperparameters.json (written by LudwigModel.save())
    carries the same "type" per input feature though, so the same
    text/image/number -> NLP/CNN/MLP classification below is applied to
    whichever of the two files is actually present, instead of only ever
    running for description.json and silently falling back to "Unknown"
    for every checkpoint-saved tabular model.
    """
    desc_path = _run_dir_from_model_path(model_path) / "description.json"
    hp_path = Path(model_path) / "model_hyperparameters.json"

    input_features = []
    if desc_path.exists():
        with open(desc_path, "r") as f:
            desc = json.load(f)

        if "model_type" in desc:
            return desc["model_type"]

        input_features = desc.get("input_features", [])

    # Hamelin writes its own description.json into every checkpoint with
    # only {"dataset": ...} in it, so an existing file doesn't mean it
    # describes the model.
    if not input_features and hp_path.exists():
        with open(hp_path, "r") as f:
            input_features = json.load(f).get("input_features", [])

    if input_features:
        types = [f.get("type") for f in input_features]

        if "text" in types:
            return "NLP"
        if "image" in types:
            return "CNN"

        encoders = [f.get("encoder") for f in input_features if "encoder" in f]
        if any("bert" in str(e) for e in encoders):
            return "Transformer"
        if any("cnn" in str(e) for e in encoders):
            return "CNN"
        if any("lstm" in str(e) for e in encoders):
            return "RNN"

        # No text/image feature and no sequence-style encoder - plain
        # tabular input (number/category/binary/date), the common case for
        # clinical data. Ludwig's default combiner for this is a fully
        # connected concat combiner, i.e. an MLP.
        if any(t in ("number", "category", "binary", "date") for t in types):
            return "MLP"

    return "Unknown"