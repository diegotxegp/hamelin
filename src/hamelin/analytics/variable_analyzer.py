"""
VariableAnalyzerWorker
~~~~~~~~~~~~~~~~~~~~~~

Background QThread that runs Ludwig's ``get_dataset_info`` + ``infer_type``
on a DataFrame and emits a per-column analysis dict.

Emitted signal payload (``analysis_ready``) is a dict of the form::

    {
        "age": {
            "ludwig_type": "number",
            "missing_pct":  0.03,
            "num_distinct": 48,
        },
        "sex": {
            "ludwig_type": "binary",
            "missing_pct":  0.00,
            "num_distinct": 2,
        },
        ...
    }

Usage::

    worker = VariableAnalyzerWorker(df)
    worker.analysis_ready.connect(my_slot)
    worker.error.connect(lambda msg: log.warning(msg))
    worker.start()
"""

from __future__ import annotations

import pandas as pd
from PySide6.QtCore import QThread, Signal

from hamelin.utils.logger import log


def prewarm_ludwig_type_inference() -> None:
    """Import ``ludwig.automl.base_config`` once, ahead of time.

    That module does a hard, unconditional ``import dask.dataframe`` at its
    top - ~2-3s the first time it happens in a process (dask.dataframe's own
    import chain), even though get_dataset_info()/infer_type() themselves
    run in well under a second. Left alone, that cost lands on the first
    dataset a user ever loads on the Data page. Call this once from a
    background thread at app startup instead, so it's already cached in
    sys.modules (process-wide, not thread-local) by the time
    VariableAnalyzerWorker.run() needs it for real.

    Best-effort only: any import failure here is silently swallowed -
    VariableAnalyzerWorker.run() already handles and reports that case
    itself when actually used.
    """
    try:
        import ludwig.automl.base_config  # noqa: F401
    except Exception:
        pass


class VariableAnalyzerWorker(QThread):
    """Runs Ludwig type inference in a background thread."""

    # dict[column_name, dict] — emitted on success
    analysis_ready = Signal(dict)
    # str — emitted if Ludwig raises unexpectedly
    error = Signal(str)

    def __init__(self, df: pd.DataFrame, parent=None) -> None:
        super().__init__(parent)
        self._df = df.copy()

    # ------------------------------------------------------------------
    def run(self) -> None:  # noqa: D102
        try:
            from ludwig.automl.base_config import get_dataset_info, infer_type  # lazy

            log.debug("VariableAnalyzerWorker: starting Ludwig type inference")
            info = get_dataset_info(self._df)

            result: dict[str, dict] = {}
            for field in info.fields:
                col = field.name
                # Compute stats from the DataFrame directly — more reliable than
                # Ludwig's FieldInfo attributes which can be 0/unpopulated.
                series = self._df[col] if col in self._df.columns else None
                if series is not None and len(series) > 0:
                    missing_pct = float(series.isna().mean())
                    num_distinct = int(series.nunique(dropna=True))
                else:
                    missing_pct = 0.0
                    num_distinct = 0

                try:
                    ltype = infer_type(field, missing_pct, info.row_count)
                except Exception:  # noqa: BLE001
                    ltype = "unknown"

                result[col] = {
                    "ludwig_type": ltype,
                    "missing_pct": missing_pct,
                    "num_distinct": num_distinct,
                }

            log.debug(
                f"VariableAnalyzerWorker: analysis complete — {len(result)} fields"
            )
            self.analysis_ready.emit(result)

        except Exception as exc:  # noqa: BLE001
            log.warning(f"VariableAnalyzerWorker: inference failed — {exc}")
            self.error.emit(str(exc))
