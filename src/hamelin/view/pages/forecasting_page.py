"""
Forecasting Page
~~~~~~~~~~~~~~~~

Connects ForecastingPage UI to RecruitmentTracker backend.
The user selects the enrollment-date column from the loaded dataset,
sets a target sample size, and presses t("forecasting.btn.generate").
The page then:
  1. Runs RecruitmentTracker.process_dataset() to extract events.
  2. Shows current recruitment status (enrolled, remaining, velocity).
  3. Calls forecast_completion() and displays results.
  4. Fills the projected timeline table with monthly milestones.
  5. Allows CSV export of the timeline.
"""

from __future__ import annotations

import csv
import os
from datetime import date

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal
from qfluentwidgets import (
    TitleLabel, StrongBodyLabel, BodyLabel, CardWidget,
    PushButton, PrimaryPushButton, ComboBox, SpinBox, DoubleSpinBox,
    FluentIcon, InfoBar, InfoBarPosition,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from hamelin.analytics.forecasting_chart import RecruitmentChart
from hamelin.analytics.recruitment_tracker import RecruitmentTracker
from hamelin.core.project import ProjectMetadata
from hamelin.model.data_model import DataModel
from hamelin.utils.exceptions import ValidationError
from hamelin.utils.logger import log
from hamelin.utils.export_paths import default_export_path
from hamelin.utils.usage_logger import usage_log
from hamelin.view.widgets import HelpButton, PageHelpButton, style_table_widget
from hamelin.view.widgets.theme_colors import apply_scroll_area_theme, bind_style, colors, on_theme_changed, style_figure, apply_transparent_container
from hamelin.i18n import t



class ForecastingPage(QWidget):
    """
    Recruitment forecasting page connected to RecruitmentTracker.

    Receives a DataModel from MainWindow (via set_data_model) and
    optionally a ProjectMetadata (via set_project_metadata).

    Signals
    -------
    tracker_ready(object):
        Emitted after a successful forecast run, carrying the live
        RecruitmentTracker so other pages (e.g. DashboardPage) can
        consume it without re-processing the dataset.
    """

    tracker_ready = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ForecastingPage")
        self._data_model: DataModel | None = None
        self._project_metadata: ProjectMetadata | None = None
        self._project_dir = None
        self._tracker: RecruitmentTracker | None = None
        self._timeline_rows: list = []   # for CSV export
        self._chart_canvas: FigureCanvasQTAgg | None = None
        self._chart_obj: RecruitmentChart | None = None
        self._chart_container: QVBoxLayout | None = None
        log.debug("Initializing Forecasting Page")
        self._init_ui()
        on_theme_changed(self._apply_chart_theme)

    # ── Public setters (called by MainWindow) ──────────────────────────
    def set_data_model(self, dm: DataModel) -> None:
        """Receive a DataModel from MainWindow when data is loaded."""
        self._data_model = dm
        self._populate_date_columns()
        log.info("ForecastingPage received DataModel")

    def set_project_dir(self, project_dir) -> None:
        """Where the exports open by default (results/forecasts/ of the project)."""
        self._project_dir = project_dir

    def set_project_metadata(self, metadata: ProjectMetadata) -> None:
        """Receive project metadata so target sample size is pre-filled."""
        self._project_metadata = metadata
        if metadata.target_sample_size:
            self._target_spin.setValue(metadata.target_sample_size)
        start_date = getattr(metadata, "start_date", None) or getattr(metadata, "first_patient_date", None)
        if start_date:
            self._start_lbl.setText(str(start_date))
        log.info(f"ForecastingPage received project metadata: {metadata.short_name}")

    # ── UI construction ────────────────────────────────────────────────
    def _init_ui(self):
        """Build the user interface."""
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        scroll.setWidget(container)
        # Make the scroll area transparent so the app's real (theme-aware)
        # background shows through instead of QScrollArea's own opaque,
        # theme-blind palette background.
        apply_scroll_area_theme(scroll)
        apply_transparent_container(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # ── Title ──────────────────────────────────────────────────────
        title_row = QHBoxLayout()
        title = TitleLabel(t("forecasting.title"))
        title.setAlignment(Qt.AlignLeft)
        title_row.addWidget(title)
        title_row.addWidget(PageHelpButton(t("forecasting.help"), self))
        title_row.addStretch()
        layout.addLayout(title_row)

        subtitle = StrongBodyLabel(t("forecasting.subtitle"))
        bind_style(subtitle, lambda c: f"color: {c.text_secondary};")
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # ── Current Status Card ────────────────────────────────────────
        status_card = CardWidget()
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(20, 20, 20, 20)
        status_layout.setSpacing(12)

        title_row = QHBoxLayout()
        title_row.addWidget(StrongBodyLabel(t("forecasting.section.status")))
        title_row.addWidget(HelpButton(
            t("forecasting.txt.this_section_updates_automatically_after")
        ))
        title_row.addStretch()
        status_layout.addLayout(title_row)

        status_grid = QFormLayout()
        status_grid.setSpacing(10)
        self._recruited_lbl = BodyLabel("—")
        status_grid.addRow("Currently Recruited:", self._recruited_lbl)
        self._target_status_lbl = BodyLabel("—")
        status_grid.addRow("Target Sample Size:", self._target_status_lbl)
        self._remaining_lbl = BodyLabel("—")
        status_grid.addRow("Remaining:", self._remaining_lbl)
        self._rate_lbl = BodyLabel("—")
        status_grid.addRow("Avg. Recruitment Rate:", self._rate_lbl)
        self._start_lbl = BodyLabel("—")
        status_grid.addRow("Study Start Date:", self._start_lbl)
        status_layout.addLayout(status_grid)
        layout.addWidget(status_card)

        # ── Forecast Parameters Card ───────────────────────────────────
        params_card = CardWidget()
        params_layout = QVBoxLayout(params_card)
        params_layout.setContentsMargins(20, 20, 20, 20)
        params_layout.setSpacing(15)

        title_row2 = QHBoxLayout()
        title_row2.addWidget(StrongBodyLabel(t("forecasting.section.parameters")))
        title_row2.addWidget(HelpButton(
            t("forecasting.txt.configure_the_inputs_needed_to_generate")
        ))
        title_row2.addStretch()
        params_layout.addLayout(title_row2)

        params_form = QFormLayout()
        params_form.setSpacing(12)

        self._date_col_combo = ComboBox()
        self._date_col_combo.setPlaceholderText(t("forecasting.placeholder.date.col"))
        self._date_col_combo.setMinimumWidth(220)
        params_form.addRow("Enrollment Date Column:", self._date_col_combo)

        self._target_spin = SpinBox()
        self._target_spin.setRange(1, 100_000)
        self._target_spin.setValue(100)
        params_form.addRow("Target Sample Size:", self._target_spin)

        self._history_spin = SpinBox()
        self._history_spin.setRange(1, 3650)
        self._history_spin.setValue(90)
        self._history_spin.setSuffix(" days")
        params_form.addRow("Historical Period:", self._history_spin)

        self._conf_spin = DoubleSpinBox()
        self._conf_spin.setRange(0.50, 0.99)
        self._conf_spin.setValue(0.95)
        self._conf_spin.setSingleStep(0.05)
        self._conf_spin.setDecimals(2)
        params_form.addRow("Confidence Level:", self._conf_spin)

        params_layout.addLayout(params_form)

        self._generate_btn = PrimaryPushButton(t("forecasting.btn.generate"), self)
        self._generate_btn.setIcon(FluentIcon.DOCUMENT)
        self._generate_btn.clicked.connect(self._generate_forecast)
        params_layout.addWidget(self._generate_btn)

        layout.addWidget(params_card)

        # ── Forecast Results Card ──────────────────────────────────────
        results_card = CardWidget()
        results_layout = QVBoxLayout(results_card)
        results_layout.setContentsMargins(20, 20, 20, 20)
        results_layout.setSpacing(15)
        results_layout.addWidget(StrongBodyLabel(t("forecasting.section.results")))

        results_form = QFormLayout()
        results_form.setSpacing(10)
        self._completion_lbl = BodyLabel(t("forecasting.status.not.calculated"))
        results_form.addRow("Predicted Completion:", self._completion_lbl)
        self._days_remaining_lbl = BodyLabel(t("forecasting.status.not.calculated"))
        results_form.addRow("Days to Target:", self._days_remaining_lbl)
        self._ci_lbl = BodyLabel(t("forecasting.status.not.calculated"))
        results_form.addRow("95% CI (±days):", self._ci_lbl)
        self._r2_lbl = BodyLabel(t("forecasting.status.not.calculated"))
        results_form.addRow("R² (model fit):", self._r2_lbl)
        self._on_track_lbl = BodyLabel(t("forecasting.status.not.calculated"))
        results_form.addRow("On Track:", self._on_track_lbl)
        results_layout.addLayout(results_form)
        layout.addWidget(results_card)

        # ── Chart Card ────────────────────────────────────────────────
        chart_card = CardWidget()
        chart_card_layout = QVBoxLayout(chart_card)
        chart_card_layout.setContentsMargins(20, 20, 20, 20)
        chart_card_layout.setSpacing(10)
        chart_card_layout.addWidget(StrongBodyLabel(t("forecasting.section.chart")))

        self._chart_canvas = FigureCanvasQTAgg(self._build_empty_chart_fig())
        self._chart_canvas.setMinimumHeight(380)
        self._chart_container = QVBoxLayout()
        self._chart_container.addWidget(self._chart_canvas)
        chart_card_layout.addLayout(self._chart_container)

        chart_export_row = QHBoxLayout()
        self._export_chart_btn = PushButton(t("forecasting.btn.export.chart"), self)
        self._export_chart_btn.setIcon(FluentIcon.PHOTO)
        self._export_chart_btn.setEnabled(False)
        self._export_chart_btn.clicked.connect(self._export_chart)
        chart_export_row.addWidget(self._export_chart_btn)
        chart_export_row.addStretch()
        chart_card_layout.addLayout(chart_export_row)
        layout.addWidget(chart_card)

        # ── Timeline Table Card ────────────────────────────────────────
        timeline_card = CardWidget()
        timeline_layout = QVBoxLayout(timeline_card)
        timeline_layout.setContentsMargins(20, 20, 20, 20)
        timeline_layout.setSpacing(15)
        timeline_layout.addWidget(StrongBodyLabel(t("forecasting.section.timeline")))

        self._timeline_table = QTableWidget()
        self._timeline_table.setColumnCount(4)
        self._timeline_table.setHorizontalHeaderLabels([
            "Month", "Projected Enrolled", "Lower CI", "Upper CI"
        ])
        self._timeline_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._timeline_table.setAlternatingRowColors(True)
        style_table_widget(self._timeline_table)
        self._timeline_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self._timeline_table.setMinimumHeight(220)
        timeline_layout.addWidget(self._timeline_table)
        layout.addWidget(timeline_card)

        # ── Export ─────────────────────────────────────────────────────
        export_row = QHBoxLayout()
        self._export_csv_btn = PushButton(t("forecasting.btn.export.csv"), self)
        self._export_csv_btn.setIcon(FluentIcon.SAVE)
        self._export_csv_btn.setEnabled(False)
        self._export_csv_btn.clicked.connect(self._export_csv)
        export_row.addWidget(self._export_csv_btn)
        export_row.addStretch()
        layout.addLayout(export_row)

        layout.addStretch()
        log.debug("Forecasting Page initialized successfully")

    # ── Internal helpers ───────────────────────────────────────────────
    def _populate_date_columns(self):
        """Fill the date column combo with dataset column names."""
        if self._data_model is None or self._data_model.df is None:
            return
        self._date_col_combo.clear()
        for col in self._data_model.df.columns:
            self._date_col_combo.addItem(col)
        date_hints = ["date", "fecha", "enroll", "inclusion", "ingreso", "alta"]
        for i, col in enumerate(self._data_model.df.columns):
            if any(h in col.lower() for h in date_hints):
                self._date_col_combo.setCurrentIndex(i)
                break

    def _log_filled_fields(self) -> None:
        """One usage-log row per non-empty forecast parameter, mirroring
        MetadataPage._log_filled_fields(), so a usability study can see
        which forecast settings people actually configure."""
        fields = {
            "Enrollment Date Column": self._date_col_combo.currentText(),
            "Target Sample Size": self._target_spin.value(),
            "Historical Period (days)": self._history_spin.value(),
            "Confidence Level": self._conf_spin.value(),
        }
        for element, value in fields.items():
            if value:
                usage_log.event("Forecasting", "field_filled", element, str(value))

    # ── Main forecast logic ────────────────────────────────────────────
    def _generate_forecast(self):
        """Run the full recruitment forecast pipeline."""
        usage_log.event("Forecasting", "click", "Generate Forecast button")
        self._log_filled_fields()
        if self._data_model is None or self._data_model.df is None:
            InfoBar.warning(
                title=t("forecasting.txt.no_data_loaded"),
                content=t("forecasting.txt.go_to_the_data_page_and"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        date_col = self._date_col_combo.currentText()
        if not date_col:
            InfoBar.warning(
                title=t("forecasting.txt.no_date_column"),
                content=t("forecasting.txt.select_the_enrollment_date_column_from"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        target = self._target_spin.value()

        # Build ProjectMetadata (reuse saved one if available)
        if self._project_metadata is not None:
            meta = self._project_metadata
            meta.target_sample_size = target
        else:
            meta = ProjectMetadata(
                name="Unnamed Project",
                short_name="unnamed",
                principal_investigator="—",
                target_sample_size=target,
            )

        # Run tracker
        try:
            tracker = RecruitmentTracker(meta)
            n_events = tracker.process_dataset(
                df=self._data_model.df,
                date_column=date_col,
            )
        except ValidationError as exc:
            InfoBar.error(
                title=t("forecasting.txt.data_error"), content=str(exc),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=6000, parent=self,
            )
            return

        if n_events == 0:
            InfoBar.warning(
                title=t("forecasting.txt.no_events_found"),
                content=(
                    t("forecasting.txt.column_0_contained_no_valid_dates").format(date_col)
                ),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=5000, parent=self,
            )
            return

        self._tracker = tracker

        # Update status
        summary = tracker.get_summary()
        self._recruited_lbl.setText(str(summary["total_enrolled"]))
        self._target_status_lbl.setText(str(target))
        self._remaining_lbl.setText(str(max(0, target - summary["total_enrolled"])))
        rate = summary.get("avg_patients_per_month", 0)
        self._rate_lbl.setText(t("forecasting.txt.0_1f_patients_month").format(rate))
        self._start_lbl.setText(str(summary.get("first_enrollment", "—")))

        # Forecast
        try:
            forecast = tracker.forecast_completion()
        except ValidationError as exc:
            InfoBar.warning(
                title=t("forecasting.txt.forecast_unavailable"), content=str(exc),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=5000, parent=self,
            )
            return

        # Update results
        self._completion_lbl.setText(forecast["predicted_completion_date"])
        self._days_remaining_lbl.setText(t("forecasting.txt.0_days_2").format(forecast['days_remaining']))
        self._ci_lbl.setText(t("forecasting.txt.0_days").format(forecast['confidence_interval_days']))
        self._r2_lbl.setText(str(forecast.get("r_squared", "—")))
        on_track = forecast.get("on_track", True)
        self._on_track_lbl.setText("✅ Yes" if on_track else "⚠️ No")

        self._build_timeline_table(forecast)
        self._export_csv_btn.setEnabled(True)

        InfoBar.success(
            title=t("forecasting.txt.forecast_generated"),
            content=(
                t("forecasting.txt.0_enrollment_events_processed_predicted_").format(n_events, forecast['predicted_completion_date'])
            ),
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=4000, parent=self,
        )
        self._render_chart()
        self.tracker_ready.emit(self._tracker)
        log.info(f"Forecast generated: {forecast}")
        usage_log.event("Forecasting", "created", "Forecast", forecast['predicted_completion_date'])

    def _build_timeline_table(self, forecast: dict):
        """Populate the projected monthly timeline table."""
        self._timeline_rows.clear()
        self._timeline_table.setRowCount(0)

        try:
            completion = date.fromisoformat(forecast["predicted_completion_date"])
        except (ValueError, KeyError):
            return

        today = date.today()
        if completion <= today:
            return

        ci_days = forecast["confidence_interval_days"]
        total_enrolled = len(self._tracker.events)
        target = self._target_spin.value()
        days_remaining = forecast["days_remaining"]
        if days_remaining <= 0:
            return

        daily_rate = max(0, target - total_enrolled) / days_remaining

        # Monthly milestones
        milestones = []
        cur = today.replace(day=1)
        while cur <= completion:
            milestones.append(cur)
            cur = cur.replace(month=cur.month % 12 + 1,
                              year=cur.year + (1 if cur.month == 12 else 0))
        if not milestones or milestones[-1] != completion:
            milestones.append(completion)

        self._timeline_table.setRowCount(len(milestones))
        for row_idx, milestone in enumerate(milestones):
            days_ahead = (milestone - today).days
            projected = min(target, round(total_enrolled + daily_rate * days_ahead))
            lower = max(0, round(projected - daily_rate * ci_days))
            upper = min(target, round(projected + daily_rate * ci_days))

            self._timeline_table.setItem(
                row_idx, 0, QTableWidgetItem(milestone.strftime("%b %Y"))
            )
            self._timeline_table.setItem(row_idx, 1, QTableWidgetItem(str(projected)))
            self._timeline_table.setItem(row_idx, 2, QTableWidgetItem(str(lower)))
            self._timeline_table.setItem(row_idx, 3, QTableWidgetItem(str(upper)))

            self._timeline_rows.append({
                "month": milestone.strftime("%b %Y"),
                "projected_enrolled": projected,
                "lower_ci": lower,
                "upper_ci": upper,
            })
    # ── Chart rendering & export ───────────────────────────────────
    def _build_empty_chart_fig(self) -> Figure:
        c = colors()
        fig = Figure(figsize=(10, 4.5))
        fig.patch.set_facecolor(c.chart_face)
        ax = fig.add_subplot(111)
        ax.axis("off")
        ax.text(
            0.5, 0.5, "Run forecast to see chart",
            ha="center", va="center", transform=ax.transAxes,
            fontsize=11, color=c.text_secondary,
        )
        return fig

    def _apply_chart_theme(self) -> None:
        """Re-render whatever the chart slot is currently showing (a real
        forecast, or the placeholder) so a theme switch updates it live."""
        if self._chart_obj is not None:
            self._render_chart()
            return
        if self._chart_container is None or self._chart_canvas is None:
            return
        new_canvas = FigureCanvasQTAgg(self._build_empty_chart_fig())
        new_canvas.setMinimumHeight(380)
        old_canvas = self._chart_canvas
        self._chart_container.replaceWidget(old_canvas, new_canvas)
        old_canvas.setParent(None)  # type: ignore[arg-type]
        old_canvas.deleteLater()
        self._chart_canvas = new_canvas

    def _render_chart(self) -> None:
        """Build a new RecruitmentChart and swap it into the canvas slot."""
        if self._tracker is None:
            return
        target = self._target_spin.value()
        chart = RecruitmentChart(self._tracker, target)
        fig = chart.build()
        self._chart_obj = chart

        # Swap old canvas for new one — cleanest way to update a figure in Qt
        new_canvas = FigureCanvasQTAgg(fig)
        new_canvas.setMinimumHeight(380)
        old_canvas = self._chart_canvas
        self._chart_container.replaceWidget(old_canvas, new_canvas)
        old_canvas.setParent(None)  # type: ignore[arg-type]
        old_canvas.deleteLater()
        self._chart_canvas = new_canvas

        self._export_chart_btn.setEnabled(True)
        log.debug("Recruitment chart rendered")

    def _export_chart(self) -> None:
        """Save the current chart as PNG or SVG."""
        usage_log.event("Forecasting", "click", "Export Chart button")
        if self._chart_obj is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self.window(), t("forecasting.txt.export_chart"),
            default_export_path(self._project_dir, "forecasts", "recruitment_forecast.png"),
            t("forecasting.txt.png_files_png_svg_files_svg"),
        )
        if not path:
            return
        try:
            self._chart_obj.save(path, dpi=300)
            InfoBar.success(
                title=t("forecasting.txt.chart_exported"),
                content=t("forecasting.txt.chart_saved_to_0").format(os.path.basename(path)),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=3000, parent=self,
            )
            log.info(f"Recruitment chart exported: {path}")
            usage_log.event("Forecasting", "exported", "Chart", os.path.basename(path))
        except Exception as exc:
            InfoBar.error(
                title=t("forecasting.txt.export_error"), content=str(exc),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=5000, parent=self,
            )
            log.error(f"Chart export failed: {exc}")
    # ── Export ─────────────────────────────────────────────────────────
    def _export_csv(self):
        """Export the projected timeline to a CSV file."""
        usage_log.event("Forecasting", "click", "Export Timeline CSV button")
        if not self._timeline_rows:
            return
        path, _ = QFileDialog.getSaveFileName(
            self.window(), t("forecasting.txt.export_timeline"),
            default_export_path(self._project_dir, "forecasts", "recruitment_forecast.csv"),
            t("forecasting.txt.csv_files_csv_all_files"),
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["month", "projected_enrolled", "lower_ci", "upper_ci"],
                )
                writer.writeheader()
                writer.writerows(self._timeline_rows)
            InfoBar.success(
                title=t("data.txt.exported"),
                content=t("forecasting.txt.timeline_saved_to_0").format(os.path.basename(path)),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=3000, parent=self,
            )
            log.info(f"Forecast timeline exported to {path}")
            usage_log.event("Forecasting", "exported", "Timeline CSV", os.path.basename(path))
        except Exception as exc:
            InfoBar.error(
                title=t("forecasting.txt.export_error"), content=str(exc),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=5000, parent=self,
            )
            log.error(f"Export failed: {exc}")
