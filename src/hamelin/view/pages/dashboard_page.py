"""
Dashboard Page
~~~~~~~~~~~~~~

Project status overview: header, KPI cards, model history.

Public API (called by MainWindow)
----------------------------------
    set_project_metadata(meta)   → KPI cards + header
    set_data_model(dm)           → Variables / Data Quality cards
    set_tracker(tracker)         → enables rate + forecast KPIs
    refresh()                    → manual refresh

Navigation signals
------------------
    navigate_to_data
    navigate_to_training
    navigate_to_interface
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
)
from PySide6.QtCore import Qt, Signal, QFileSystemWatcher
from qfluentwidgets import (
    TitleLabel, StrongBodyLabel, BodyLabel,
    CardWidget, PushButton, ProgressBar, FluentIcon,
    ScrollArea,
)

from hamelin.analytics.kpi_calculator import KPICalculator, KPIResult
from hamelin.utils.logger import log
from hamelin.utils.usage_logger import usage_log
from hamelin.view.widgets.help_button import HelpButton
from hamelin.view.widgets.page_help import PageHelpButton
from hamelin.view.widgets.kpi_card_widget import KPICardWidget
from hamelin.view.widgets.model_history_widget import ModelHistoryWidget
from hamelin.view.widgets.recruitment_chart_widget import RecruitmentChartWidget
from hamelin.view.widgets.theme_colors import bind_style
from hamelin.i18n import t




class DashboardPage(QWidget):
    """
    Project status dashboard.

    Displays KPI cards computed by :class:`KPICalculator` plus a project
    header and model training history.

    Minimal required flow
    ---------------------
    1. ``set_project_metadata(meta)`` — enables header + basic KPIs
    2. ``set_tracker(tracker)``       — enables rate / end-date / on-track KPIs
    3. ``set_data_model(dm)``         — enables data quality + variables cards
    """

    navigate_to_data      = Signal()
    navigate_to_training  = Signal()
    navigate_to_interface = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("DashboardPage")

        self._metadata = None
        self._tracker  = None
        self._dm       = None
        self._project_dir: str | None = None

        self._watcher = QFileSystemWatcher(self)
        self._watcher.fileChanged.connect(self._on_watched_change)
        self._watcher.directoryChanged.connect(self._on_watched_change)

        self._init_ui()
        log.debug("DashboardPage initialised")

    # ── UI construction ────────────────────────────────────────────────

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = ScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        self._layout = QVBoxLayout(container)
        self._layout.setContentsMargins(30, 30, 30, 30)
        self._layout.setSpacing(20)

        self._build_title_row()
        self._build_project_header()
        self._build_kpi_section()
        self._build_progress_bar()
        self._build_recruitment_chart()
        self._build_data_cards()
        self._build_model_history()
        self._build_quick_actions()
        self._layout.addStretch()

        scroll.setWidget(container)
        root.addWidget(scroll)

    def _build_title_row(self) -> None:
        row = QHBoxLayout()
        title = TitleLabel(t("dashboard.title"))
        title.setAlignment(Qt.AlignLeft)
        row.addWidget(title)
        row.addWidget(PageHelpButton(t("dashboard.help"), self))
        row.addStretch()
        refresh_btn = PushButton(t("dashboard.btn.refresh"), self)
        refresh_btn.setIcon(FluentIcon.SYNC)
        refresh_btn.clicked.connect(self._on_refresh_clicked)
        row.addWidget(refresh_btn)
        self._layout.addLayout(row)

        subtitle = StrongBodyLabel(t("dashboard.subtitle"))
        bind_style(subtitle, lambda c: f"color: {c.text_secondary};")
        self._layout.addWidget(subtitle)

    def _build_project_header(self) -> None:
        card = CardWidget()
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(40)

        def _kv(label: str) -> StrongBodyLabel:
            col = QVBoxLayout()
            col.setSpacing(2)
            lbl = BodyLabel(label)
            bind_style(lbl, lambda c: f"color: {c.text_secondary}; font-size: 11px;")
            val = StrongBodyLabel("—")
            col.addWidget(lbl)
            col.addWidget(val)
            box = QWidget()
            box.setLayout(col)
            card_layout.addWidget(box)
            return val

        self._hdr_name   = _kv("Study Name")
        self._hdr_pi     = _kv("Principal Investigator")
        self._hdr_start  = _kv("First Patient Date")
        self._hdr_target = _kv("Target Sample Size")
        card_layout.addStretch()
        self._layout.addWidget(card)

    def _build_kpi_section(self) -> None:
        header_row = QHBoxLayout()
        kpi_title = StrongBodyLabel(t("dashboard.section.kpi"))
        kpi_help = HelpButton(
            "KPIs are computed from your project metadata and recruitment events. "
            "Rate and estimated end-date require enrollment data to be processed "
            "on the Recruitment Forecasting page first."
        )
        header_row.addWidget(kpi_title)
        header_row.addWidget(kpi_help)
        header_row.addStretch()
        self._layout.addLayout(header_row)

        grid = QGridLayout()
        grid.setSpacing(12)

        self._card_recruited  = KPICardWidget("Recruited",    "0",  icon=FluentIcon.PEOPLE)
        self._card_remaining  = KPICardWidget(t("forecasting.label.remaining"),    "—",  icon=FluentIcon.REMOVE)
        self._card_completion = KPICardWidget("Completion",   "0%", icon=FluentIcon.PIE_SINGLE)
        self._card_rate       = KPICardWidget("Rate / month", "—",  icon=FluentIcon.SPEED_HIGH)
        self._card_end_date   = KPICardWidget("Est. End Date","—",  icon=FluentIcon.CALENDAR)
        self._card_on_track   = KPICardWidget(t("forecasting.label.on.track"),     "—",  icon=FluentIcon.ACCEPT)
        self._card_days       = KPICardWidget("Days Elapsed", "0",  icon=FluentIcon.HISTORY)

        cards = [
            self._card_recruited, self._card_remaining, self._card_completion,
            self._card_rate,      self._card_end_date,  self._card_on_track,
            self._card_days,
        ]
        cols = 4
        for i, card in enumerate(cards):
            grid.addWidget(card, i // cols, i % cols)

        self._layout.addLayout(grid)

    def _build_progress_bar(self) -> None:
        card = CardWidget()
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(8)

        top = QHBoxLayout()
        top.addWidget(StrongBodyLabel(t("dashboard.section.progress")))
        top.addWidget(HelpButton(
            "Percentage of target sample size enrolled so far. "
            "Computed from recruited / target_sample_size."
        ))
        top.addStretch()
        cl.addLayout(top)

        self._progress_bar = ProgressBar()
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(True)
        cl.addWidget(self._progress_bar)

        self._progress_detail = BodyLabel(t("dashboard.msg.no.data"))
        bind_style(self._progress_detail, lambda c: f"color: {c.text_secondary};")
        cl.addWidget(self._progress_detail)

        self._layout.addWidget(card)

    def _build_recruitment_chart(self) -> None:
        """Recruitment chart card — populated when tracker_ready signal fires."""
        card = CardWidget()
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(8)

        row = QHBoxLayout()
        row.addWidget(StrongBodyLabel(t("dashboard.section.chart")))
        row.addWidget(HelpButton(
            "Evolución del reclutamiento a lo largo del tiempo con\n"
            "la proyección hasta alcanzar el tamaño muestral objetivo.\n\n"
            "Se actualiza automáticamente al ejecutar el pronóstico\n"
            "en la pestaña Reclutamiento."
        ))
        row.addStretch()
        cl.addLayout(row)

        self._recruitment_chart = RecruitmentChartWidget(self)
        cl.addWidget(self._recruitment_chart)
        self._layout.addWidget(card)

    def _build_data_cards(self) -> None:
        """Variables + Data Quality summary row."""
        card = CardWidget()
        cl = QHBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(40)

        def _item(label: str, default: str) -> StrongBodyLabel:
            col = QVBoxLayout()
            col.addWidget(BodyLabel(label))
            val = StrongBodyLabel(default)
            col.addWidget(val)
            box = QWidget()
            box.setLayout(col)
            cl.addWidget(box)
            return val

        self._lbl_quality = _item(t("dashboard.label.quality"),  "N/A")
        self._lbl_vars    = _item(t("dashboard.label.variables"),      "0")
        self._lbl_rows    = _item("Rows loaded",    "0")
        cl.addStretch()
        self._layout.addWidget(card)

    def _build_model_history(self) -> None:
        card = CardWidget()
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)

        row = QHBoxLayout()
        row.addWidget(StrongBodyLabel(t("dashboard.section.history")))
        row.addWidget(HelpButton("Training runs logged for the current project."))
        row.addStretch()
        cl.addLayout(row)

        self._history_widget = ModelHistoryWidget(self)
        cl.addWidget(self._history_widget)
        self._layout.addWidget(card)

    def _build_quick_actions(self) -> None:
        card = CardWidget()
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 16, 20, 16)
        cl.setSpacing(12)

        cl.addWidget(StrongBodyLabel(t("dashboard.section.actions")))

        row = QHBoxLayout()
        row.setSpacing(10)
        for label, icon, sig in [
            ("Load Data",        FluentIcon.FOLDER,   self.navigate_to_data),
            # Table 1 now lives inside the Data page as a section.
            ("Generate Table 1", FluentIcon.DOCUMENT, self.navigate_to_data),
            ("Train Model",      FluentIcon.PLAY,     self.navigate_to_training),
            ("Advanced Dashboard", FluentIcon.VIEW,   self.navigate_to_interface),
        ]:
            btn = PushButton(label, self)
            btn.setIcon(icon)
            btn.clicked.connect(sig)
            btn.clicked.connect(lambda _=False, lbl=label: usage_log.event("Dashboard", "click", f"{lbl} button"))
            row.addWidget(btn)
        row.addStretch()
        cl.addLayout(row)
        self._layout.addWidget(card)

    # ── Public API (called by MainWindow) ──────────────────────────────

    def set_project_metadata(self, meta) -> None:
        """Update header and KPI cards from project metadata."""
        self._metadata = meta
        try:
            self._update_header(meta)
            self._recompute_kpis()
        except Exception as exc:
            log.warning(f"DashboardPage.set_project_metadata: {exc}")

    def set_tracker(self, tracker) -> None:
        """Attach a RecruitmentTracker to enable rate/forecast KPIs and chart."""
        self._tracker = tracker
        self._recompute_kpis()
        # Update recruitment chart
        try:
            target = int(getattr(self._metadata, "target_sample_size", 0) or 0)
            self._recruitment_chart.load(tracker, target)
        except Exception as exc:
            log.warning(f"DashboardPage.set_tracker chart: {exc}")

    def set_data_model(self, dm) -> None:
        """Update Variables and Data Quality cards from a DataModel."""
        self._dm = dm
        try:
            df = dm.df
            if df is None:
                return
            n_cols = len(df.columns)
            n_rows = len(df)
            if n_rows > 0:
                complete = int(df.dropna().shape[0] / n_rows * 100)
                self._lbl_quality.setText(f"{complete}%")
            self._lbl_vars.setText(str(n_cols))
            self._lbl_rows.setText(str(n_rows))
            log.debug(f"Dashboard: data model updated — {n_cols} cols, {n_rows} rows")
        except Exception as exc:
            log.warning(f"DashboardPage.set_data_model: {exc}")

    def load_project(self, project_dir: str) -> None:
        """Reload model history from *project_dir* and register file watcher."""
        self._project_dir = project_dir
        try:
            self._history_widget.load(project_dir)
        except Exception as exc:
            log.warning(f"DashboardPage.load_project: {exc}")
        self.watch_project(project_dir)

    def watch_project(self, project_dir: str) -> None:
        """Register *project_dir* and key files for auto-refresh."""
        try:
            # Remove previously watched paths to avoid stale paths
            existing = self._watcher.directories() + self._watcher.files()
            if existing:
                self._watcher.removePaths(existing)
            self._watcher.addPath(str(project_dir))
            for fname in ("recruitment_log.json", "model_history.json"):
                p = Path(project_dir) / fname
                if p.exists():
                    self._watcher.addPath(str(p))
            log.debug(f"DashboardPage: watching {project_dir}")
        except Exception as exc:
            log.warning(f"DashboardPage.watch_project: {exc}")

    def _on_watched_change(self, path: str = "") -> None:
        """Called by QFileSystemWatcher on any change inside the project dir."""
        log.debug(f"DashboardPage: file change detected — {path}")
        self.refresh()

    def refresh(self) -> None:
        """Manual refresh — recomputes KPIs."""
        self._recompute_kpis()
        log.debug("DashboardPage: manual refresh")

    def _on_refresh_clicked(self) -> None:
        usage_log.event("Dashboard", "click", "Refresh button")
        self.refresh()

    # ── Private helpers ────────────────────────────────────────────────

    def _update_header(self, meta) -> None:
        self._hdr_name.setText(
            getattr(meta, "name", None) or getattr(meta, "study_name", "—") or "—"
        )
        self._hdr_pi.setText(getattr(meta, "principal_investigator", "—") or "—")
        fpd: Optional[date] = getattr(meta, "first_patient_date", None)
        self._hdr_start.setText(fpd.isoformat() if fpd else "—")
        target = getattr(meta, "target_sample_size", 0) or 0
        self._hdr_target.setText(str(target) if target else "—")

    def _recompute_kpis(self) -> None:
        meta    = self._metadata
        tracker = self._tracker
        if meta is None:
            return
        if tracker is None:
            self._apply_basic_kpis(meta)
            return
        try:
            result = KPICalculator(meta, tracker).calculate()
            self._apply_full_kpis(result)
        except Exception as exc:
            log.warning(f"DashboardPage._recompute_kpis: {exc}")
            self._apply_basic_kpis(meta)

    def _apply_basic_kpis(self, meta) -> None:
        target = int(getattr(meta, "target_sample_size", 0) or 0)
        recruited = int(
            getattr(meta, "recruited_patients", None) or
            getattr(meta, "total_enrolled", None) or 0
        )
        remaining = max(0, target - recruited)
        pct = round(recruited / target * 100, 1) if target > 0 else 0.0
        fpd   = getattr(meta, "first_patient_date", None)
        days  = max(0, (date.today() - fpd).days) if fpd else 0

        self._card_recruited.update_value(str(recruited),  f"of {target} target")
        self._card_remaining.update_value(str(remaining))
        self._card_completion.update_value(f"{pct}%")
        self._card_days.update_value(str(days),            "days since first patient")
        self._card_rate.update_value("—",     "Load recruitment data")
        self._card_end_date.update_value("—", "Load recruitment data")
        self._card_on_track.update_value("—", "Load recruitment data")
        self._card_on_track.set_status("default")

        self._progress_bar.setValue(int(pct))
        self._progress_detail.setText(
            f"{recruited} enrolled / {target} target ({pct}%)"
            if target > 0 else "No target set"
        )
        self._set_completion_colour(pct)

    def _apply_full_kpis(self, r: KPIResult) -> None:
        self._card_recruited.update_value(
            str(r.total_recruited), f"of {r.target_sample_size} target"
        )
        self._card_remaining.update_value(str(r.remaining))
        self._card_completion.update_value(f"{r.completion_pct:.1f}%")
        self._card_rate.update_value(f"{r.rate_per_month:.1f}", "patients / month")

        if r.estimated_end_date:
            self._card_end_date.update_value(
                r.estimated_end_date.strftime("%b %Y"),
                r.estimated_end_date.isoformat(),
            )
        else:
            self._card_end_date.update_value("—", "rate is zero")

        self._card_days.update_value(str(r.days_elapsed), "days elapsed")

        if r.on_track:
            self._card_on_track.update_value("✓ On Track")
            self._card_on_track.set_status("good")
        else:
            self._card_on_track.update_value("✗ At Risk")
            self._card_on_track.set_status("warning")

        pct = int(r.completion_pct)
        self._progress_bar.setValue(pct)
        self._progress_detail.setText(
            f"{r.total_recruited} enrolled / {r.target_sample_size} target "
            f"({r.completion_pct:.1f}%)  —  "
            f"{r.rate_per_month:.1f} patients/month"
        )
        self._set_completion_colour(r.completion_pct)

    def _set_completion_colour(self, pct: float) -> None:
        if pct >= 100:
            status = "good"
        elif pct >= 75:
            status = "info"
        elif pct >= 50:
            status = "default"
        else:
            status = "warning"
        self._card_completion.set_status(status)
        self._card_recruited.set_status(status)

