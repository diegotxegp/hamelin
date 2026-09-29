"""
Recruitment Forecasting Chart for HAMELIN

Generates a publication-quality matplotlib figure showing:
  - Historical cumulative enrollment (scatter + line)
  - Linear regression trend line (extended to forecast horizon)
  - 95% confidence interval band (shaded)
  - Target sample size horizontal line
  - Predicted completion marker
  - Key annotations (R², predicted date, CI)

Usage:
    chart = RecruitmentChart(tracker, target=200)
    fig = chart.build()           # → matplotlib Figure
    chart.save("forecast.png")    # → PNG at 300 DPI

Author: GitHub Copilot AI
Date: February 20, 2026
Version: 2.0
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend — rendering is handled by Qt canvas

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from hamelin.utils.lazy import LazyModule

stats = LazyModule("scipy.stats")

from hamelin.analytics.recruitment_tracker import RecruitmentTracker
from hamelin.utils.logger import log
# hamelin.utils.theme_colors, not hamelin.view.widgets.theme_colors - this module
# must stay free of any hamelin.view import (see that module's docstring) or
# it circularly imports the widgets that import it.
from hamelin.utils.theme_colors import colors, style_figure


class RecruitmentChart:
    """
    Generate a recruitment forecast chart from a RecruitmentTracker.

    The chart is composed of:
      - Historical data: cumulative enrolled patients per day (dots + line)
      - Trend line: linear regression extended from last historical date to
        the predicted completion date
      - CI band: shaded area representing the 95% confidence interval around
        the trend (derived from confidence_interval_days in the forecast)
      - Target line: horizontal dashed line at the target sample size
      - Completion marker: star at (predicted_completion_date, target)
      - Annotation box: R², predicted date, ±CI

    Handles edge cases gracefully:
      - Fewer than 3 events → returns an informative empty figure
      - Forecast unavailable (ValidationError) → returns an error figure
      - CI = 0 → skips the shaded band

    Args:
        tracker: A RecruitmentTracker instance with processed events.
        target: Target sample size for the study.

    Example:
        >>> chart = RecruitmentChart(tracker, target=200)
        >>> fig = chart.build()
        >>> chart.save("output/forecast.png", dpi=300)
    """

    # ── Colour scheme ──────────────────────────────────────────────────
    # Data-series colours are fixed accents (distinct, accessible on both
    # a light and dark figure background). Background/grid come from
    # theme_colors.colors() instead - see build()/save()/_build_empty_figure().
    _HIST_COLOR = "#2563EB"       # Blue — historical enrollment
    _TREND_COLOR = "#DC2626"      # Red — trend line
    _CI_COLOR = "#FCA5A5"         # Light red — CI band
    _TARGET_COLOR = "#16A34A"     # Green — target line
    _COMPLETION_COLOR = "#7C3AED" # Purple — completion star

    def __init__(self, tracker: RecruitmentTracker, target: int) -> None:
        """
        Initialise the chart.

        Args:
            tracker: RecruitmentTracker with processed enrollment events.
            target: Target patient count for the study.
        """
        self._tracker = tracker
        self._target = target
        self._fig: Optional[Figure] = None

    # ── Public API ─────────────────────────────────────────────────────

    def build(self) -> Figure:
        """
        Build and return the matplotlib Figure.

        Returns:
            A matplotlib Figure ready to embed in a Qt canvas or save to file.

        Raises:
            Nothing — all errors are handled internally and produce an
            informative empty figure instead.
        """
        timeline = self._tracker.get_timeline()

        if timeline.empty or len(self._tracker.events) < 3:
            return self._build_empty_figure(
                "Not enough data to generate chart\n"
                "(need at least 3 enrollment events)"
            )

        try:
            forecast = self._tracker.forecast_completion()
        except Exception as exc:
            return self._build_empty_figure(f"Forecast unavailable:\n{exc}")

        fig, ax = plt.subplots(figsize=(10, 4.5))

        # ── Historical data ────────────────────────────────────────────
        hist_dates = pd.to_datetime(timeline["date"])
        hist_cumulative = timeline["cumulative_enrolled"].values.astype(float)

        ax.plot(
            hist_dates, hist_cumulative,
            color=self._HIST_COLOR, linewidth=1.8, label="Historical enrollment",
            zorder=3,
        )
        ax.scatter(
            hist_dates, hist_cumulative,
            color=self._HIST_COLOR, s=18, alpha=0.55, zorder=4,
        )

        # ── Linear regression ──────────────────────────────────────────
        first_date = timeline["date"].min()
        x_days = np.array([(d - first_date).days for d in timeline["date"]])
        slope, intercept, r_value, _, _ = stats.linregress(x_days, hist_cumulative)

        # ── Trend & CI band ────────────────────────────────────────────
        completion_iso = forecast["predicted_completion_date"]
        completion_date = date.fromisoformat(completion_iso)
        ci_days = max(0, forecast.get("confidence_interval_days", 0))

        last_hist_date = timeline["date"].max()
        # Extend curve to completion + CI upper bound
        pad = timedelta(days=ci_days + 10)
        end_plot = completion_date + pad

        trend_dates = pd.date_range(
            start=pd.Timestamp(last_hist_date),
            end=pd.Timestamp(end_plot),
            periods=120,
        )
        trend_x = np.array(
            [(pd.Timestamp(d).date() - first_date).days for d in trend_dates]
        )
        trend_y = np.clip(slope * trend_x + intercept, 0, self._target)

        ax.plot(
            trend_dates, trend_y,
            color=self._TREND_COLOR, linewidth=2, linestyle="--",
            label="Trend (linear regression)", zorder=3,
        )

        if ci_days > 0:
            # Shift trend line ±(slope × ci_days) in recruitment space
            delta = slope * ci_days
            upper = np.clip(trend_y + delta, 0, self._target)
            lower = np.clip(trend_y - delta, 0, self._target)
            ax.fill_between(
                trend_dates, lower, upper,
                color=self._CI_COLOR, alpha=0.35,
                label="95% confidence interval", zorder=2,
            )

        # ── Target line ────────────────────────────────────────────────
        ax.axhline(
            y=self._target,
            color=self._TARGET_COLOR, linewidth=1.5, linestyle=":",
            label=f"Target ({self._target} patients)", zorder=3,
        )

        # ── Completion marker ──────────────────────────────────────────
        ax.scatter(
            [pd.Timestamp(completion_date)], [self._target],
            color=self._COMPLETION_COLOR, s=140, marker="*", zorder=5,
            label=f"Predicted completion ({completion_iso})",
        )

        # ── Annotation box ─────────────────────────────────────────────
        r2 = forecast.get("r_squared", round(r_value ** 2, 3))
        annotation_text = (
            f"R² = {r2:.3f}\n"
            f"Predicted: {completion_iso}\n"
            f"CI: ±{ci_days} days"
        )
        c = colors()
        ax.annotate(
            annotation_text,
            xy=(0.02, 0.97), xycoords="axes fraction",
            fontsize=8, verticalalignment="top", color=c.text_primary,
            bbox=dict(
                boxstyle="round,pad=0.4", facecolor=c.card_background,
                edgecolor=c.table_gridline, alpha=0.90,
            ),
        )

        # ── Axes formatting ────────────────────────────────────────────
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")

        ax.set_xlabel("Date", fontsize=10)
        ax.set_ylabel("Cumulative Patients", fontsize=10)
        ax.set_title("Recruitment Forecast", fontsize=12, fontweight="bold", pad=12)

        ax.set_ylim(bottom=0, top=self._target * 1.10)
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

        ax.grid(axis="y", color=c.table_gridline, linewidth=0.8, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.legend(loc="lower right", fontsize=8, framealpha=0.9)

        style_figure(fig, ax)
        fig.tight_layout()
        self._fig = fig
        log.debug("RecruitmentChart built successfully")
        return fig

    def save(self, path: str, dpi: int = 300) -> None:
        """
        Save the chart to a file.

        Args:
            path: Output file path. Extension determines format (.png, .svg, .pdf).
            dpi: Resolution in dots per inch (default 300 for publication quality).

        Example:
            >>> chart.save("output/forecast.png", dpi=300)
        """
        if self._fig is None:
            self._fig = self.build()
        self._fig.savefig(path, dpi=dpi, bbox_inches="tight",
                          facecolor=colors().chart_face)
        log.info(f"Recruitment chart saved: {path} (dpi={dpi})")

    # ── Internal helpers ───────────────────────────────────────────────

    @staticmethod
    def _build_empty_figure(message: str) -> Figure:
        """
        Return a figure with a centred message, used for error/empty states.

        Args:
            message: Text to display on the figure.

        Returns:
            A matplotlib Figure showing the message.
        """
        c = colors()
        fig, ax = plt.subplots(figsize=(10, 4.5))
        fig.patch.set_facecolor(c.chart_face)
        ax.set_facecolor(c.chart_face)
        ax.text(
            0.5, 0.5, message,
            ha="center", va="center",
            transform=ax.transAxes,
            fontsize=12, color=c.text_secondary,
        )
        ax.axis("off")
        return fig
