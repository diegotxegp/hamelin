"""
Predictor
~~~~~~~~~

Run a saved Ludwig model against new, unlabeled data (the Prediction page).

Unlike ``evaluate()``, ``LudwigModel.predict()`` needs no ground-truth
column, so the uploaded dataset only has to carry the model's input
features. The result is shaped like the rest of the app's prediction
exports: the original columns first, then per output feature
``predicted_<feature>``, ``confidence_<feature>`` (classification) and one
``prob_<feature>_<class>`` per class.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pandas as pd
from PySide6.QtCore import QThread, Signal

from hamelin.utils.logger import log

CONFIG_FILENAME = "model_hyperparameters.json"


def resolve_model_dir(path: str | Path) -> Path | None:
    """The folder that directly holds model_hyperparameters.json - *path*
    itself, or its ``model/`` subfolder (Ludwig's own experiment layout) -
    or None if *path* isn't a saved Ludwig model."""
    p = Path(path)
    for candidate in (p, p / "model"):
        if (candidate / CONFIG_FILENAME).is_file():
            return candidate
    return None


def required_input_columns(model_dir: str | Path) -> list[str]:
    """Names of the input features the model needs in a dataset."""
    from hamelin.interface.utils.get_model_paths import get_input_feature_names
    return get_input_feature_names(str(model_dir))


def _output_features(model_dir: Path) -> list[str]:
    try:
        cfg = json.loads((model_dir / CONFIG_FILENAME).read_text(encoding="utf-8"))
        return [f["name"] for f in cfg.get("output_features", []) if f.get("name")]
    except Exception:  # noqa: BLE001
        return []


def _binary_labels(model_dir: Path, feature: str):
    """{False: raw, True: raw} for a numeric-coded binary output, read from
    the dataset the model was trained on (Ludwig only decodes string-coded
    binaries back to their raw labels on its own), or None."""
    try:
        from hamelin.analytics.automl.ludwig_backend import _binary_output_mapping
        from hamelin.interface.utils.get_model_paths import get_model_dataset

        dataset = get_model_dataset(str(model_dir))
        if not dataset:
            return None
        train_df = pd.read_csv(dataset, usecols=[feature])
        return _binary_output_mapping(train_df, feature, pd.Series([True]))
    except Exception:  # noqa: BLE001
        return None


def build_predictions_frame(df: pd.DataFrame, predictions: pd.DataFrame, model_dir: Path | None = None) -> pd.DataFrame:
    """Original *df* columns + a readable block of prediction columns."""
    out = df.reset_index(drop=True).copy()
    preds = predictions.reset_index(drop=True)
    features = [c[: -len("_predictions")] for c in preds.columns if c.endswith("_predictions")]
    for feat in features:
        values = preds[f"{feat}_predictions"]
        if values.dtype == bool and model_dir is not None:
            mapping = _binary_labels(model_dir, feat)
            if mapping is not None:
                values = values.map(mapping)
        out[f"predicted_{feat}"] = values.values
        if f"{feat}_probability" in preds.columns:
            out[f"confidence_{feat}"] = preds[f"{feat}_probability"].values
        prefix = f"{feat}_probabilities_"
        for col in preds.columns:
            if col.startswith(prefix):
                out[f"prob_{feat}_{col[len(prefix):]}"] = preds[col].values
    return out


def predict_unlabeled(model_dir: str | Path, df: pd.DataFrame) -> pd.DataFrame:
    """Load the model at *model_dir* and predict every row of *df*."""
    from ludwig.api import LudwigModel

    resolved = resolve_model_dir(model_dir)
    if resolved is None:
        raise ValueError(f"No saved Ludwig model found in {model_dir}")
    # backend="local": Ludwig auto-picks Ray when it's importable, and its
    # Ray backend can't reload a model (see LudwigBackend._load_best_model_local).
    # No from_checkpoint: that's for hyperopt trial dirs; a LudwigModel.save()
    # folder (what TrainingPage writes) holds model_weights, not training_checkpoints.
    model = LudwigModel.load(str(resolved), backend="local")
    # predict() creates its output_directory (default "results", relative to
    # the current directory) even with skip_save_predictions, so point it at
    # a throwaway folder instead of littering wherever the app was launched.
    with tempfile.TemporaryDirectory(prefix="hamelin_predict_") as scratch:
        predictions, _ = model.predict(
            dataset=df.reset_index(drop=True), skip_save_predictions=True,
            skip_save_unprocessed_output=True, output_directory=scratch,
        )
    if len(predictions) != len(df):
        log.warning(f"Predictor: {len(df)} rows in, {len(predictions)} predictions out")
        raise ValueError(
            f"Ludwig returned {len(predictions)} predictions for {len(df)} rows - "
            "some rows were dropped during preprocessing (missing values?)."
        )
    return build_predictions_frame(df, predictions, resolved)


class PredictWorker(QThread):
    """Runs predict_unlabeled() off the UI thread."""

    prediction_ready = Signal(object)  # pandas.DataFrame
    error = Signal(str)

    def __init__(self, model_dir: str | Path, df: pd.DataFrame, parent=None) -> None:
        super().__init__(parent)
        self._model_dir = model_dir
        self._df = df.copy()

    def run(self) -> None:  # noqa: D102
        try:
            self.prediction_ready.emit(predict_unlabeled(self._model_dir, self._df))
        except Exception as exc:  # noqa: BLE001
            log.error(f"PredictWorker failed: {exc}", exc_info=True)
            self.error.emit(str(exc))
