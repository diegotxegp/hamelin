"""
ModelResultsWidget
~~~~~~~~~~~~~~~~~~

Displays the results of a completed AutoML training run.

Layout
------
  ┌───────────────────────────────────────────────────────────────────┐
  │  [KPICard: AUC] [KPICard: Accuracy] [KPICard: Sensib.] [Especif.]│
  ├───────────────────────────────────────────────────────────────────┤
  │  Interpretación clínica auto-generada (BodyLabel)                 │
  └───────────────────────────────────────────────────────────────────┘

Usage::

    widget = ModelResultsWidget(parent)
    widget.load(automl_result)   # populate with AutoMLResult
    widget.clear()               # back to empty placeholder

Notes
-----
- No Confusion Matrix section - it never had real data to show (the
  ``vis`` dict never carries a "confusion_matrix" key yet) and was pure
  clutter that always read "(data not available for this model)".
- No ROC curve either: its data was never extracted, so it only ever
  read "(data not available for this model)".
- The widget starts hidden; ``TrainingPage`` calls ``setVisible(True)``
  after ``load()``.

Author: GitHub Copilot AI
Date: February 24, 2026
Sprint: 3, Day 28 (stretch goal skeleton)
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
)
from PySide6.QtCore import Qt
from qfluentwidgets import (
    CardWidget, StrongBodyLabel, BodyLabel, FluentIcon,
)

from hamelin.analytics.automl.base import AutoMLResult
from hamelin.utils.logger import log
from hamelin.i18n import t
from hamelin.view.widgets.kpi_card_widget import KPICardWidget
from hamelin.view.widgets.theme_colors import bind_style, isDarkTheme, on_theme_changed


# ── Metric helpers ────────────────────────────────────────────────────────────

def _fmt(value: float | None, pct: bool = False) -> str:
    """Format a float metric for display (e.g. 0.8731 → '87.3%' or '0.873')."""
    if value is None:
        return "—"
    if pct:
        return f"{value * 100:.1f}%"
    return f"{value:.3f}"


def _get(metrics: dict, *keys: str) -> float | None:
    """Return the first key found in *metrics*, or None."""
    for k in keys:
        v = metrics.get(k)
        if isinstance(v, (int, float)):
            return float(v)
    return None


def _kpi_status(value: float | None, good: float = 0.75) -> str:
    if value is None:
        return "default"
    return "good" if value >= good else "warning"


class ModelResultsWidget(QWidget):
    """
    Shows training metrics, visualisation placeholders, and a plain-language
    interpretation of the last AutoML result.

    The widget is empty by default.  Call :meth:`load` with an
    :class:`~hamelin.analytics.automl.base.AutoMLResult` to populate it.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._result: AutoMLResult | None = None
        self._hide_sens_card: bool = False
        self._hide_spec_card: bool = False
        self._init_ui()
        self._show_empty()

    # ── Public API ────────────────────────────────────────────────────

    def load(self, result: AutoMLResult) -> None:
        """
        Populate the widget with *result*.

        Parameters
        ----------
        result:
            An :class:`AutoMLResult` returned by any registered backend.
        """
        self._result = result
        metrics = result.test_metrics or {}

        # ── KPI cards — adapt to the task type ─────────────────────────
        # Ludwig's classification and regression metric key sets don't
        # overlap, so presence of any classification key is a reliable
        # signal of which one this run actually was. The 4 cards used to
        # always show AUC/Accuracy/Sensitivity/Specificity regardless,
        # which left them all blank ("—") for a regression run - the real
        # metrics were there, just relegated to the small text line below.
        auc = _get(metrics, "roc_auc", "auc", "roc_auc_score")
        acc = _get(metrics, "accuracy", "accuracy_score")
        sens = _get(metrics, "recall", "sensitivity", "true_positive_rate")
        spec = _get(metrics, "specificity", "true_negative_rate", "tnr")
        is_classification = any(v is not None for v in (auc, acc, sens, spec))

        # Sensitivity/specificity only mean something for a binary outcome
        # (positive vs. negative). A multi-class category output (3+
        # possible values) has no single "positive" class, so Ludwig never
        # reports recall/specificity for it at all - those two cards would
        # otherwise sit permanently blank ("—") even though the run trained
        # fine. accuracy_micro was tried as a 3rd-card replacement, but it's
        # just accuracy again under another name, which read as confusing
        # duplication rather than a useful extra number - so that card is
        # hidden outright for multi-class instead (see is_multiclass below).
        # hits_at_k is a genuinely different metric, so it still fills the
        # 4th card when Ludwig reports it.
        accuracy_micro = _get(metrics, "accuracy_micro")
        hits_at_k = _get(metrics, "hits_at_k")
        is_multiclass = is_classification and sens is None and spec is None and (
            accuracy_micro is not None or hits_at_k is not None
        )

        if is_classification:
            self._card_auc.set_label("AUC-ROC")
            self._card_auc.update_value(_fmt(auc, pct=False), subtitle="AUC-ROC (0–1)")
            self._card_auc.set_status(_kpi_status(auc))

            self._card_acc.set_label("Accuracy")
            self._card_acc.update_value(_fmt(acc, pct=True), subtitle="correct predictions")
            self._card_acc.set_status(_kpi_status(acc))

            if is_multiclass:
                # No good 3rd card: accuracy_micro is just accuracy again
                # under another name and confused more than it explained,
                # so that card is hidden outright rather than filled with
                # a near-duplicate of the "Accuracy" card next to it.
                self._hide_sens_card = True

                if hits_at_k is not None:
                    self._hide_spec_card = False
                    self._card_spec.set_label("Hits @ K")
                    self._card_spec.update_value(_fmt(hits_at_k, pct=True), subtitle="true class within the top predictions")
                    self._card_spec.set_status("default")
                else:
                    self._hide_spec_card = True

                shown_keys = {"roc_auc", "auc", "roc_auc_score", "accuracy",
                              "accuracy_score", "accuracy_micro", "hits_at_k"}
            else:
                self._hide_sens_card = False
                self._hide_spec_card = False
                self._card_sens.set_label("Sensitivity")
                self._card_sens.update_value(_fmt(sens, pct=True), subtitle="positive cases detected")
                self._card_sens.set_status(_kpi_status(sens))

                self._card_spec.set_label("Specificity")
                self._card_spec.update_value(_fmt(spec, pct=True), subtitle="negative cases correct")
                self._card_spec.set_status(_kpi_status(spec))

                shown_keys = {"roc_auc", "auc", "roc_auc_score", "accuracy",
                              "accuracy_score", "recall", "sensitivity", "specificity",
                              "true_negative_rate", "tnr", "true_positive_rate"}
        else:
            self._hide_sens_card = False
            self._hide_spec_card = False
            r2 = _get(metrics, "r2")
            rmse = _get(metrics, "root_mean_squared_error", "rmse")
            mae = _get(metrics, "mean_absolute_error", "mae")
            loss = _get(metrics, "loss")

            self._card_auc.set_label("R²")
            self._card_auc.update_value(_fmt(r2, pct=False), subtitle="goodness of fit (1 = perfect)")
            self._card_auc.set_status(_kpi_status(r2, good=0.7))

            self._card_acc.set_label("RMSE")
            self._card_acc.update_value(_fmt(rmse, pct=False), subtitle="avg. error, same units as target")
            self._card_acc.set_status("default")

            self._card_sens.set_label("MAE")
            self._card_sens.update_value(_fmt(mae, pct=False), subtitle="avg. absolute error")
            self._card_sens.set_status("default")

            self._card_spec.set_label("Loss")
            self._card_spec.update_value(_fmt(loss, pct=False), subtitle="training loss")
            self._card_spec.set_status("default")

            shown_keys = {"r2", "root_mean_squared_error", "rmse",
                          "mean_absolute_error", "mae", "loss"}

        # Show "extra" metrics row only if we have values not shown in cards
        extra_metrics = {k: v for k, v in metrics.items()
                 if k not in shown_keys and isinstance(v, (int, float))}
        if extra_metrics:
            extra_lines = "  |  ".join(
                f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}"
                for k, v in sorted(extra_metrics.items())
            )
            self._extra_metrics_lbl.setText(extra_lines)
            self._extra_metrics_lbl.setVisible(True)
        else:
            self._extra_metrics_lbl.setVisible(False)

        # ── Auto-generated clinical text ─────────────────────────────
        if is_classification:
            interpretation = self._build_interpretation(result, auc, acc, sens, spec)
        else:
            interpretation = self._build_regression_interpretation(r2, rmse, mae)
        self._interpretation_lbl.setText(interpretation)

        # ── Model info label ─────────────────────────────────────────
        self._model_info_lbl.setText(
            t("common.txt.model_0_trials_1_duration_2").format(result.model_type, result.num_trials, result.training_time_seconds)
        )

        self._update_advice(result)
        self._show_results()
        log.debug(f"ModelResultsWidget: loaded result for {result.model_type}")

    def clear(self) -> None:
        """Reset to empty placeholder state."""
        self._result = None
        self._show_empty()
        log.debug("ModelResultsWidget: cleared")

    # ── Private helpers ───────────────────────────────────────────────

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)

        # ── Outer card ────────────────────────────────────────────────
        self._card = CardWidget()
        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(16)

        # Title row
        title_lbl = StrongBodyLabel(t("common.txt.model_results"))
        card_layout.addWidget(title_lbl)

        # Model info (type · trials · time)
        self._model_info_lbl = BodyLabel("")
        bind_style(self._model_info_lbl, lambda c: f"color: {c.text_secondary}; font-size: 12px;")
        card_layout.addWidget(self._model_info_lbl)

        # ── KPI cards row ─────────────────────────────────────────────
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(10)

        self._card_auc = KPICardWidget(
            label="AUC-ROC",
            value="—",
            subtitle="AUC-ROC (0–1)",
            icon=FluentIcon.SPEED_HIGH,
        )
        self._card_acc = KPICardWidget(
            label="Accuracy",
            value="—",
            subtitle="correct predictions",
            icon=FluentIcon.ACCEPT,
        )
        self._card_sens = KPICardWidget(
            label="Sensitivity",
            value="—",
            subtitle="positive cases detected",
            icon=FluentIcon.UP,
        )
        self._card_spec = KPICardWidget(
            label="Specificity",
            value="—",
            subtitle="negative cases correct",
            icon=FluentIcon.DOWN,
        )

        for card in (self._card_auc, self._card_acc, self._card_sens, self._card_spec):
            kpi_row.addWidget(card)
        kpi_row.addStretch()
        card_layout.addLayout(kpi_row)

        # Extra metrics (hidden by default)
        self._extra_metrics_lbl = BodyLabel("")
        bind_style(self._extra_metrics_lbl, lambda c: f"color: {c.text_secondary}; font-size: 11px;")
        self._extra_metrics_lbl.setVisible(False)
        card_layout.addWidget(self._extra_metrics_lbl)

        # ── Clinical interpretation text ──────────────────────────────
        self._interpretation_lbl = BodyLabel("")
        self._interpretation_lbl.setWordWrap(True)

        def _apply_interpretation_theme() -> None:
            bg, fg = ("#12301F", "#8FE3B4") if isDarkTheme() else ("#F0FBF5", "#1a6640")
            self._interpretation_lbl.setStyleSheet(
                f"background: {bg}; border-radius: 6px; padding: 10px;"
                f"color: {fg}; font-size: 13px;"
            )
        on_theme_changed(_apply_interpretation_theme)
        card_layout.addWidget(self._interpretation_lbl)

        # ── How to read this result (rule-based advice) ───────────────
        self._advice_title = StrongBodyLabel(t("advice.title"))
        card_layout.addWidget(self._advice_title)
        self._advice_lbl = BodyLabel("")
        self._advice_lbl.setWordWrap(True)
        self._advice_lbl.setTextFormat(Qt.RichText)
        card_layout.addWidget(self._advice_lbl)

        # ── Empty placeholder ─────────────────────────────────────────
        self._empty_lbl = BodyLabel(
            t("common.txt.results_will_appear_here_after_training")
        )
        self._empty_lbl.setAlignment(Qt.AlignCenter)
        bind_style(self._empty_lbl, lambda c: f"color: {c.text_secondary}; padding: 20px;")
        card_layout.addWidget(self._empty_lbl)

        main_layout.addWidget(self._card)

    def _show_empty(self) -> None:
        """Hide results, show placeholder."""
        self._model_info_lbl.setText("")
        for card in (self._card_auc, self._card_acc, self._card_sens, self._card_spec):
            card.setVisible(False)
        self._extra_metrics_lbl.setVisible(False)
        self._interpretation_lbl.setVisible(False)
        self._advice_title.setVisible(False)
        self._advice_lbl.setVisible(False)
        self._empty_lbl.setVisible(True)

    def _show_results(self) -> None:
        """Show results, hide placeholder."""
        self._empty_lbl.setVisible(False)
        self._card_auc.setVisible(True)
        self._card_acc.setVisible(True)
        # A multi-class run hides one or both of these - see load()'s
        # is_multiclass branch for why there's no good metric to put in
        # them for that case.
        self._card_sens.setVisible(not self._hide_sens_card)
        self._card_spec.setVisible(not self._hide_spec_card)
        self._interpretation_lbl.setVisible(True)
        has_advice = bool(self._advice_lbl.text())
        self._advice_title.setVisible(has_advice)
        self._advice_lbl.setVisible(has_advice)

    def _update_advice(self, result: AutoMLResult) -> None:
        """Fill the "How to read this result" block; never lets a problem
        in the advice rules break the results view."""
        text = ""
        try:
            from hamelin.analytics.result_advice import advice_html, build_advice

            preds = (result.extra or {}).get("test_predictions")
            adv = build_advice(result.test_metrics, result.train_metrics, preds)
            text = advice_html(adv)
        except Exception as exc:  # noqa: BLE001
            log.warning(f"ModelResultsWidget: advice unavailable — {exc}")
        self._advice_lbl.setText(text)

    @staticmethod
    def _build_interpretation(
        result: AutoMLResult,
        auc: float | None,
        acc: float | None,
        sens: float | None,
        spec: float | None,
    ) -> str:
        """Generate a short plain-language summary for clinicians."""
        parts: list[str] = []

        if acc is not None:
            parts.append(
                f"The model correctly classifies {acc * 100:.1f}% of cases."
            )
        if auc is not None:
            if auc >= 0.90:
                quality = "excellent discriminative ability"
            elif auc >= 0.80:
                quality = "good discriminative ability"
            elif auc >= 0.70:
                quality = "moderate discriminative ability"
            else:
                quality = "limited discriminative ability"
            parts.append(f"AUC-ROC = {auc:.3f} — {quality}.")
        if sens is not None:
            parts.append(
                f"Detects {sens * 100:.1f}% of positive cases (sensitivity)."
            )
        if spec is not None:
            parts.append(
                f"Correctly identifies {spec * 100:.1f}% of negative cases (specificity)."
            )

        if not parts:
            parts.append(
                "No standard classification metrics found. "
                "Check the detailed values in the results area."
            )

        return "  ".join(parts)

    @staticmethod
    def _build_regression_interpretation(
        r2: float | None,
        rmse: float | None,
        mae: float | None,
    ) -> str:
        """Generate a short plain-language summary for a regression run."""
        parts: list[str] = []

        if r2 is not None:
            if r2 >= 0.90:
                quality = "excellent fit"
            elif r2 >= 0.70:
                quality = "good fit"
            elif r2 >= 0.50:
                quality = "moderate fit"
            elif r2 >= 0:
                quality = "weak fit — the model barely captures the pattern"
            else:
                quality = (
                    "worse than simply predicting the average every time — "
                    "the model isn't finding a real relationship here"
                )
            parts.append(f"R² = {r2:.3f} — {quality}.")
        if mae is not None:
            parts.append(
                f"On average, predictions are off by {mae:.3f} (mean absolute error)."
            )
        if rmse is not None:
            parts.append(f"Root mean squared error: {rmse:.3f}.")

        if not parts:
            parts.append(
                "No standard regression metrics found. "
                "Check the detailed values in the results area."
            )

        return "  ".join(parts)
