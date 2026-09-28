"""
Training Timeline Widget — HAMELIN
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Matplotlib-based widget that plots the accuracy (or any metric) of
training runs over time as a line chart with markers.

Author: GitHub Copilot AI
Date: February 23, 2026
Sprint: 3, Day 25
"""

from __future__ import annotations

from typing import Optional

import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy

from hamelin.analytics.history_visualizer import HistoryVisualizer
from hamelin.core.model_history import ModelHistory
from hamelin.utils.logger import log
from hamelin.view.widgets.theme_colors import colors, on_theme_changed, style_figure


class TrainingTimelineWidget(QWidget):
    """
    Line chart of a single metric across all training runs, ordered by time.

    Usage::

        widget = TrainingTimelineWidget(metric="accuracy", parent=self)
        widget.load(project_dir)
    """

    def __init__(
        self,
        metric: str = "accuracy",
        split: str = "test",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._metric = metric
        self._split = split
        self._viz: Optional[HistoryVisualizer] = None
        self._init_ui()
        on_theme_changed(self._apply_theme)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, project_dir) -> None:
        """Load training history from *project_dir* and redraw."""
        try:
            history = ModelHistory(project_dir)
            self._viz = HistoryVisualizer(history)
            self._draw()
            log.debug(f"TrainingTimelineWidget: loaded {len(history)} records")
        except Exception as exc:
            log.warning(f"TrainingTimelineWidget.load error: {exc}")
            self._draw_empty(error=str(exc))

    def set_metric(self, metric: str, split: str = "test") -> None:
        """Switch the displayed metric and redraw."""
        self._metric = metric
        self._split = split
        self._draw()

    def clear(self) -> None:
        self._viz = None
        self._draw_empty()

    def _apply_theme(self) -> None:
        """Re-render whatever's currently shown so a theme switch updates
        it live, without a restart."""
        self._draw() if self._viz is not None else self._draw_empty()

    # ------------------------------------------------------------------
    # UI setup
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._figure = Figure(figsize=(6, 3), tight_layout=True)
        self._canvas = FigureCanvas(self._figure)
        self._canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # TrainingPage builds this widget - and draws the empty placeholder
        # below - at app startup, before the page is ever shown/laid out,
        # so the canvas would otherwise still be at Qt's default tiny size.
        # tight_layout can't fit axes decorations into that ("Tight layout
        # not applied" UserWarning) - give it real room up front instead.
        self._canvas.setMinimumSize(400, 200)
        layout.addWidget(self._canvas)

        self._draw_empty()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _draw(self) -> None:
        if self._viz is None:
            self._draw_empty()
            return

        df = self._viz.metric_trend(self._metric, self._split)
        col = f"{self._split}_{self._metric}"

        if df.empty or col not in df.columns:
            self._draw_empty(message=f"No '{self._metric}' data available.")
            return

        self._figure.clear()
        ax = self._figure.add_subplot(111)

        x = df["timestamp"]
        y = df[col]

        ax.plot(x, y, marker="o", linewidth=2, color="#0078d4", markersize=6)
        ax.fill_between(x, y, alpha=0.08, color="#0078d4")

        # Annotate last point
        if len(y) > 0:
            ax.annotate(
                f"{y.iloc[-1]:.3f}",
                (x.iloc[-1], y.iloc[-1]),
                textcoords="offset points",
                xytext=(6, 4),
                fontsize=8,
                color="#0078d4",
            )

        ax.set_xlabel("Date", fontsize=9)
        ax.set_ylabel(f"{self._split.capitalize()} {self._metric}", fontsize=9)
        ax.set_title(f"{self._metric.capitalize()} over training runs", fontsize=10)
        ax.tick_params(axis="x", labelrotation=30, labelsize=8)
        ax.tick_params(axis="y", labelsize=8)
        ax.grid(True, alpha=0.3)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        style_figure(self._figure, ax)
        self._canvas.draw()

    def _draw_empty(self, message: str = "No training data yet.", error: str = "") -> None:
        self._figure.clear()
        ax = self._figure.add_subplot(111)
        text = error if error else message
        c = colors()
        ax.text(
            0.5, 0.5, text,
            ha="center", va="center",
            fontsize=10, color=c.text_secondary,
            transform=ax.transAxes,
        )
        ax.set_axis_off()
        self._figure.patch.set_facecolor(c.chart_face)
        self._canvas.draw()
