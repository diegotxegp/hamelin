"""
Home Page - Dashboard
~~~~~~~~~~~~~~~~~~~~~

Main dashboard page showing project overview and quick stats.
"""

from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from qfluentwidgets import (
    TitleLabel, StrongBodyLabel, BodyLabel, CardWidget,
    InfoBarIcon, FluentIcon
)

from hamelin.core.project import ProjectRepository
from hamelin.core.dataset_registry import DatasetRegistry
from hamelin.core.model_history import ModelHistory
from hamelin.utils.logger import log
from hamelin.utils.paths import resources_dir
from hamelin.view.widgets import PageHelpButton
from hamelin.view.widgets.theme_colors import bind_style
from hamelin.i18n import t


class StatCard(CardWidget):
    """Card widget for displaying statistics"""
    
    def __init__(self, title: str, value: str, icon: FluentIcon, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 120)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        title_label = BodyLabel(title)
        bind_style(title_label, lambda c: f"color: {c.text_secondary};")
        
        self._value_label = TitleLabel(value)
        
        layout.addWidget(title_label)
        layout.addWidget(self._value_label)
        layout.addStretch()

    def set_value(self, value: str) -> None:
        self._value_label.setText(value)


class HomePage(QWidget):
    """
    Home page showing project dashboard.
    
    Displays:
    - Project statistics
    - Recent activity
    - Quick actions
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HomePage")
        log.debug("Initializing Home Page")
        self._init_ui()
    
    def _init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # ── Header: logo + title ───────────────────────────────────────
        header_row = QHBoxLayout()
        header_row.setSpacing(18)
        header_row.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        logo_lbl = QLabel()
        _logo_path = resources_dir() / "assets" / "logo.png"
        if _logo_path.exists():
            pix = QPixmap(str(_logo_path)).scaled(
                80, 80,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_lbl.setPixmap(pix)
        logo_lbl.setFixedSize(80, 80)
        header_row.addWidget(logo_lbl)

        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        title = TitleLabel(t("home.title"))
        title.setAlignment(Qt.AlignLeft)
        subtitle = StrongBodyLabel(t("home.subtitle"))
        bind_style(subtitle, lambda c: f"color: {c.text_secondary};")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header_row.addLayout(title_col)
        header_row.addWidget(PageHelpButton(t("home.help"), self))
        header_row.addStretch()

        layout.addLayout(header_row)
        
        # Spacing
        layout.addSpacing(20)
        
        # Statistics Cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        self._projects_card = StatCard(t("metadata.title"), "0", FluentIcon.FOLDER)
        stats_layout.addWidget(self._projects_card)

        self._datasets_card = StatCard(t("home.stat.datasets"), "0", FluentIcon.DOCUMENT)
        stats_layout.addWidget(self._datasets_card)

        self._models_card = StatCard(t("home.stat.models"), "0", FluentIcon.ROBOT)
        stats_layout.addWidget(self._models_card)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Welcome message
        layout.addSpacing(20)
        welcome_card = CardWidget()
        welcome_layout = QVBoxLayout(welcome_card)
        welcome_layout.setContentsMargins(20, 20, 20, 20)
        welcome_layout.setSpacing(10)
        
        welcome_title = StrongBodyLabel(t("home.welcome.title"))
        welcome_text = BodyLabel(t("home.welcome.description"))
        welcome_text.setWordWrap(True)
        
        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_text)
        
        layout.addWidget(welcome_card)
        
        # Stretch to push everything to top
        layout.addStretch()

        log.debug("Home Page initialized successfully")
        self.update_stats()

    # ── Public API ───────────────────────────────────────────────────

    def update_stats(self) -> None:
        """Refresh the stat cards from disk (called on init and on project save)."""
        try:
            repo = ProjectRepository()
            n_projects = len(repo.list_projects())
            self._projects_card.set_value(str(n_projects))
            # Count datasets and models across all projects
            total_datasets = 0
            total_models = 0
            for pname in repo.list_projects():
                try:
                    ppath = repo.get_project_path(pname)
                    ds_reg = DatasetRegistry(ppath)
                    total_datasets += len(ds_reg.list_datasets())
                    history = ModelHistory(ppath)
                    total_models += len(history)
                except Exception:
                    # If a single project has corrupted registry/history, skip it
                    continue

            self._datasets_card.set_value(str(total_datasets))
            self._models_card.set_value(str(total_models))
            log.debug(f"HomePage stats refreshed: {n_projects} project(s), {total_datasets} dataset(s), {total_models} model(s)")
        except Exception as exc:
            log.warning(f"HomePage.update_stats failed: {exc}")
