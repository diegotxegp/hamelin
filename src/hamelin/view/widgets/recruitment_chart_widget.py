"""
RecruitmentChartWidget
~~~~~~~~~~~~~~~~~~~~~~

PySide6 FigureCanvas wrapper that renders a RecruitmentChart inside a
dashboard or any other page.

Usage::

    widget = RecruitmentChartWidget(parent)
    widget.load(tracker, target=200)   # render chart
    widget.clear()                     # back to placeholder
"""

from __future__ import annotations

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QWidget, QVBoxLayout

from hamelin.analytics.forecasting_chart import RecruitmentChart
from hamelin.utils.logger import log
from hamelin.view.widgets.theme_colors import colors, on_theme_changed


class RecruitmentChartWidget(QWidget):
    """
    Embeds a :class:`RecruitmentChart` (matplotlib) inside a PySide6 widget.

    The widget starts in an empty/placeholder state.  Call :meth:`load`
    after the ``RecruitmentTracker`` has processed a dataset to render the
    full chart.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._canvas: FigureCanvasQTAgg | None = None
        self._chart_layout = QVBoxLayout(self)
        self._chart_layout.setContentsMargins(0, 0, 0, 0)
        # Last-shown state, so a theme change can redraw whatever's
        # currently on screen (real chart or placeholder) live.
        self._last_tracker = None
        self._last_target: int | None = None
        self._show_placeholder()
        on_theme_changed(self._apply_theme)

    # ── Public API ─────────────────────────────────────────────────────

    def load(self, tracker, target: int) -> None:
        """
        Render the recruitment chart for *tracker* towards *target*.

        Parameters
        ----------
        tracker:
            A :class:`~hamelin.analytics.recruitment_tracker.RecruitmentTracker`
            that has already processed a dataset.
        target:
            Target sample size (integer).
        """
        self._last_tracker = tracker
        self._last_target = target
        try:
            chart = RecruitmentChart(tracker, target)
            fig = chart.build()
            self._replace_canvas(fig)
            log.debug("RecruitmentChartWidget: chart rendered successfully")
        except Exception as exc:
            log.warning(f"RecruitmentChartWidget.load error: {exc}")
            self._show_placeholder(f"Error al renderizar el gráfico: {exc}")

    def clear(self) -> None:
        """Reset the widget to the placeholder state."""
        self._last_tracker = None
        self._last_target = None
        self._show_placeholder()
        log.debug("RecruitmentChartWidget: cleared")

    # ── Private helpers ────────────────────────────────────────────────

    def _apply_theme(self) -> None:
        """Re-render whatever's currently shown (real chart or placeholder)
        so a theme switch updates it live, without a restart."""
        if self._last_tracker is not None and self._last_target is not None:
            self.load(self._last_tracker, self._last_target)
        else:
            self._show_placeholder()

    def _show_placeholder(
        self,
        message: str = (
            "Sin datos de reclutamiento\n"
            "Ejecuta el pronóstico en la pestaña Reclutamiento para ver la gráfica"
        ),
    ) -> None:
        """Display a grey placeholder figure with *message*."""
        c = colors()
        fig = Figure(figsize=(10, 3.5))
        fig.patch.set_facecolor(c.chart_face)
        ax = fig.add_subplot(111)
        ax.axis("off")
        ax.text(
            0.5, 0.5, message,
            ha="center", va="center", transform=ax.transAxes,
            fontsize=11, color=c.text_secondary,
        )
        self._replace_canvas(fig)

    def _replace_canvas(self, fig: Figure) -> None:
        """Swap the current FigureCanvas for one built from *fig*."""
        if self._canvas is not None:
            self._chart_layout.removeWidget(self._canvas)
            self._canvas.setParent(None)
            self._canvas.deleteLater()
            self._canvas = None

        canvas = FigureCanvasQTAgg(fig)
        canvas.setMinimumHeight(320)
        self._canvas = canvas
        self._chart_layout.addWidget(canvas)
