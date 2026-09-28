"""
Project Metadata Page
~~~~~~~~~~~~~~~~~~~~~

Two-screen layout inside a QStackedWidget:

  Screen 0 — Project Selector
      Lists all saved projects as clickable cards.
      t("metadata.btn.new") opens a blank form.

  Screen 1 — Project Form
      Standard edit form for project metadata.
      "← Back" returns to the Selector without saving.
      t("metadata.btn.save") persists to disk and returns to the Selector.

Author: GitHub Copilot AI
Sprint: 2, Day 15-16
"""

from __future__ import annotations

from datetime import date as PyDate
from functools import partial
from time import strftime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QScrollArea, QStackedWidget, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QDate
from qfluentwidgets import (
    TitleLabel, StrongBodyLabel, BodyLabel, CaptionLabel, CardWidget,
    PushButton, PrimaryPushButton, TransparentPushButton,
    LineEdit, TextEdit, DateEdit, ComboBox, SpinBox,
    FluentIcon, InfoBar, InfoBarPosition, MessageBox,
)

from hamelin.utils.logger import log
from hamelin.utils.usage_logger import usage_log
from hamelin.utils.exceptions import ValidationError, DataSaveError
from hamelin.core.project import ProjectMetadata, ProjectRepository
from hamelin.core.dataset_registry import DatasetRegistry
from hamelin.core.model_history import ModelHistory
from hamelin.view.widgets.help_button import HelpButton
from hamelin.view.widgets.page_help import PageHelpButton
from hamelin.view.widgets.theme_colors import apply_scroll_area_theme, bind_style
from hamelin.i18n import t


class MetadataPage(QWidget):
    """
    Project management page with selector + form screens.

    Signals:
        metadata_saved:          Emitted after a successful save.  Caller
                                 should call get_current_metadata() to read it.
        project_loaded:          Emitted when an existing project is opened
                                 from the selector (payload = ProjectMetadata).
        recruitment_configured:  Emitted when target_sample_size > 0.
    """

    metadata_saved = Signal()
    project_loaded = Signal(ProjectMetadata)
    recruitment_configured = Signal()
    all_projects_deleted = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MetadataPage")
        self._repository = ProjectRepository()
        self._current_metadata: ProjectMetadata | None = None
        self._selected_short_name: str | None = None
        # short_name -> metadata loaded by the last _refresh_selector() pass,
        # so callers like MainWindow._auto_load_project() can reuse it
        # instead of re-reading the same metadata.json from disk.
        self._selector_meta_cache: dict[str, ProjectMetadata] = {}
        log.debug("Initializing Metadata Page")
        self._init_ui()
        self._refresh_selector()

    # ──────────────────────────────────────────────────────────────────
    # UI construction
    # ──────────────────────────────────────────────────────────────────

    def _init_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self._stack = QStackedWidget(self)
        outer.addWidget(self._stack)
        self._stack.addWidget(self._build_selector_widget())  # index 0
        self._stack.addWidget(self._build_form_widget())       # index 1
        log.debug("Metadata Page initialized successfully")

    # ── Screen 0: project selector ────────────────────────────────────

    def _build_selector_widget(self) -> QWidget:
        """Build the project list / landing screen."""
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = TitleLabel(t("metadata.title"))
        layout.addWidget(title)

        subtitle = StrongBodyLabel(t("metadata.subtitle"))
        bind_style(subtitle, lambda c: f"color: {c.text_secondary};")
        layout.addWidget(subtitle)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        new_btn = PrimaryPushButton(t("metadata.btn.new.project"), root)
        new_btn.setIcon(FluentIcon.ADD)
        new_btn.setFixedWidth(180)
        new_btn.clicked.connect(self._on_new_project)
        btn_row.addWidget(new_btn)

        # Skips the form entirely - creates a project with auto-generated
        # placeholder metadata so the user can start loading data right
        # away and fill in the real study details later, from the form.
        generic_btn = PushButton(t("metadata.btn.new.generic"), root)
        generic_btn.setIcon(FluentIcon.SPEED_HIGH)
        generic_btn.clicked.connect(self._on_new_generic_project)
        btn_row.addWidget(generic_btn)

        btn_row.addStretch()

        delete_all_btn = PushButton(t("metadata.btn.delete.all"), root)
        delete_all_btn.setIcon(FluentIcon.DELETE)
        delete_all_btn.clicked.connect(self._on_delete_all_projects)
        btn_row.addWidget(delete_all_btn)

        layout.addLayout(btn_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self._cards_container = QWidget()
        self._cards_layout = QVBoxLayout(self._cards_container)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(10)
        self._cards_layout.addStretch()

        scroll.setWidget(self._cards_container)
        # Make the scroll area transparent so the app's real (theme-aware)
        # background shows through instead of QScrollArea's own opaque,
        # theme-blind palette background.
        apply_scroll_area_theme(scroll)
        self._cards_container.setStyleSheet("background: transparent;")
        layout.addWidget(scroll)

        self._no_projects_lbl = BodyLabel(
            "No projects yet — click \"New Project\" to get started."
        )
        bind_style(self._no_projects_lbl, lambda c: f"color: {c.text_secondary};")
        self._no_projects_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._no_projects_lbl)
        self._no_projects_lbl.hide()

        return root

    def _refresh_selector(self):
        """Re-read Projects/ directory and rebuild the card list."""
        while self._cards_layout.count() > 1:
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        projects = self._repository.list_projects()
        self._no_projects_lbl.setVisible(len(projects) == 0)

        self._selector_meta_cache = {}
        for short_name in sorted(projects):
            try:
                meta = self._repository.load(short_name)
            except Exception as exc:
                log.warning(f"Could not load project card \'{short_name}\': {exc}")
                continue
            self._selector_meta_cache[short_name] = meta
            card = self._build_project_card(meta)
            self._cards_layout.insertWidget(self._cards_layout.count() - 1, card)

    def _count_project_contents(self, short_name: str) -> tuple[int, int]:
        """Return (n_datasets, n_models) for a saved project, or (0, 0) if
        either registry can't be read (e.g. corrupted or not yet created)."""
        try:
            ppath = self._repository.get_project_path(short_name)
            n_datasets = len(DatasetRegistry(ppath).list_datasets())
            n_models = len(ModelHistory(ppath))
            return n_datasets, n_models
        except Exception as exc:
            log.warning(f"Could not count contents of project '{short_name}': {exc}")
            return 0, 0

    def _build_project_card(self, meta: ProjectMetadata) -> CardWidget:
        """Return a summary card for one saved project."""
        card = CardWidget()
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        row = QHBoxLayout(card)
        row.setContentsMargins(20, 15, 20, 15)
        row.setSpacing(15)

        info_col = QVBoxLayout()
        info_col.setSpacing(4)
        info_col.addWidget(StrongBodyLabel(f"{meta.name}  [{meta.short_name}]"))

        details: list[str] = []
        if meta.study_type:
            details.append(meta.study_type)
        if meta.target_sample_size:
            details.append(f"Target: {meta.target_sample_size} patients")
        n_datasets, n_models = self._count_project_contents(meta.short_name)
        details.append(
            f"{n_datasets} dataset{'s' if n_datasets != 1 else ''} · "
            f"{n_models} model{'s' if n_models != 1 else ''}"
        )
        if meta.last_modified:
            mod_str = meta.last_modified.strftime("%Y-%m-%d")
            details.append(f"Last modified: {mod_str}")
        if details:
            caption = CaptionLabel("  ·  ".join(details))
            bind_style(caption, lambda c: f"color: {c.text_secondary};")
            info_col.addWidget(caption)

        row.addLayout(info_col, stretch=1)

        # Select button: choose project as active without opening metadata.
        # For whichever project is currently active, use the accent-colored
        # PrimaryPushButton instead of the plain one so it's clearly marked
        # in the list — same visual language the form's own "Save" button
        # already uses for "the button that matters here".
        is_selected = meta.short_name == self._selected_short_name
        button_cls = PrimaryPushButton if is_selected else PushButton
        select_btn = button_cls(
            t("metadata.btn.selected") if is_selected else t("metadata.btn.select"),
            card,
        )
        select_btn.setIcon(FluentIcon.ACCEPT)
        # Wide enough for "✓ Selected" (the longer of the two button texts)
        # plus its icon, so it never gets clipped.
        select_btn.setFixedWidth(130)
        select_btn.clicked.connect(partial(self._on_select_project, meta.short_name))
        row.addWidget(select_btn, alignment=Qt.AlignVCenter)

        open_btn = PushButton(t("metadata.btn.open"), card)
        open_btn.setIcon(FluentIcon.FOLDER)
        open_btn.setFixedWidth(110)
        open_btn.clicked.connect(partial(self._on_open_project, meta.short_name))
        row.addWidget(open_btn, alignment=Qt.AlignVCenter)

        return card

    # ── Screen 1: metadata form ───────────────────────────────────────

    def _build_form_widget(self) -> QWidget:
        """Build the metadata edit form screen."""
        root = QWidget()

        scroll = QScrollArea(root)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        scroll.setWidget(container)
        # Make the scroll area transparent so the app's real (theme-aware)
        # background shows through instead of QScrollArea's own opaque,
        # theme-blind palette background.
        apply_scroll_area_theme(scroll)
        container.setStyleSheet("background: transparent;")

        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        self._back_btn = TransparentPushButton(t("metadata.btn.back"), root)
        self._back_btn.clicked.connect(self._on_back)
        layout.addWidget(self._back_btn, alignment=Qt.AlignLeft)

        title_row = QHBoxLayout()
        title = TitleLabel(t("metadata.detail.title"))
        title_row.addWidget(title)
        title_row.addWidget(PageHelpButton(t("metadata.help"), root))
        title_row.addStretch()
        layout.addLayout(title_row)

        subtitle = StrongBodyLabel(t("metadata.detail.subtitle"))
        bind_style(subtitle, lambda c: f"color: {c.text_secondary};")
        layout.addWidget(subtitle)
        layout.addSpacing(10)

        # ── Basic Information Card ─────────────────────────────────────
        basic_card = CardWidget()
        basic_layout = QVBoxLayout(basic_card)
        basic_layout.setContentsMargins(20, 20, 20, 20)
        basic_layout.setSpacing(15)

        bh_row = QHBoxLayout()
        bh_row.addWidget(StrongBodyLabel(t("metadata.section.basic")))
        bh_row.addWidget(HelpButton(
            "Enter the study name, short acronym, protocol number, principal "
            "investigator, contact e-mail, institution, and study type. "
            "Fields marked * are required to save."
        ))
        bh_row.addStretch()
        basic_layout.addLayout(bh_row)

        form = QFormLayout()
        form.setSpacing(10)

        self._name_input = LineEdit()
        self._name_input.setPlaceholderText(t("metadata.placeholder.name"))
        form.addRow("Project Name *:", self._name_input)

        self._short_name_input = LineEdit()
        self._short_name_input.setPlaceholderText(t("metadata.placeholder.shortname"))
        self._short_name_input.setMaximumWidth(200)
        form.addRow("Acronym *:", self._short_name_input)

        self._protocol_input = LineEdit()
        self._protocol_input.setPlaceholderText(t("metadata.placeholder.protocol"))
        form.addRow("Protocol Number *:", self._protocol_input)

        self._pi_input = LineEdit()
        self._pi_input.setPlaceholderText(t("metadata.placeholder.pi"))
        form.addRow("Principal Investigator *:", self._pi_input)

        self._email_input = LineEdit()
        self._email_input.setPlaceholderText(t("metadata.placeholder.email"))
        form.addRow("Contact Email *:", self._email_input)

        self._institution_input = LineEdit()
        self._institution_input.setPlaceholderText(t("metadata.placeholder.institution"))
        form.addRow("Institution *:", self._institution_input)

        self._study_type_combo = ComboBox()
        self._study_type_combo.addItems([
            t("metadata.studytype.registry"),
            t("metadata.studytype.observational"),
            t("metadata.studytype.clinical"),
        ])
        form.addRow("Study Type:", self._study_type_combo)

        basic_layout.addLayout(form)
        layout.addWidget(basic_card)

        # ── Ethics Approval Card ───────────────────────────────────────
        # Every protocol document (registry, observational, or RCT) opens
        # with an ethics-committee approval section - ProjectMetadata
        # already had ethics_approval_number/ethics_committee/approval_date
        # fields (src/core/project.py), just never exposed here.
        ethics_card = CardWidget()
        ethics_layout = QVBoxLayout(ethics_card)
        ethics_layout.setContentsMargins(20, 20, 20, 20)
        ethics_layout.setSpacing(15)

        eh_row = QHBoxLayout()
        eh_row.addWidget(StrongBodyLabel(t("metadata.section.ethics")))
        eh_row.addWidget(HelpButton(
            "Which ethics/IRB committee approved this study, its approval "
            "number, and the approval date. Optional, but every study "
            "protocol reserves a section for this - fill it in once "
            "approval comes through if it isn't available yet."
        ))
        eh_row.addStretch()
        ethics_layout.addLayout(eh_row)

        ethics_form = QFormLayout()
        ethics_form.setSpacing(10)

        self._ethics_committee_input = LineEdit()
        self._ethics_committee_input.setPlaceholderText(t("metadata.placeholder.ethicscommittee"))
        ethics_form.addRow(t("metadata.label.ethicscommittee"), self._ethics_committee_input)

        self._ethics_approval_number_input = LineEdit()
        self._ethics_approval_number_input.setPlaceholderText(t("metadata.placeholder.ethicsapprovalnumber"))
        ethics_form.addRow(t("metadata.label.ethicsapprovalnumber"), self._ethics_approval_number_input)

        self._approval_date = DateEdit()
        ethics_form.addRow(t("metadata.label.approvaldate"), self._approval_date)

        ethics_layout.addLayout(ethics_form)
        layout.addWidget(ethics_card)

        # ── Recruitment Information Card ───────────────────────────────
        recruit_card = CardWidget()
        recruit_layout = QVBoxLayout(recruit_card)
        recruit_layout.setContentsMargins(20, 20, 20, 20)
        recruit_layout.setSpacing(15)

        rh_row = QHBoxLayout()
        rh_row.addWidget(StrongBodyLabel(t("metadata.section.recruitment")))
        rh_row.addWidget(HelpButton(
            "Set the target sample size and study timeline. This enables the "
            "Forecasting tab to predict when you will reach your enrollment goal."
        ))
        rh_row.addStretch()
        recruit_layout.addLayout(rh_row)

        recruit_form = QFormLayout()
        recruit_form.setSpacing(10)

        self._target_input = SpinBox()
        self._target_input.setRange(1, 100000)
        self._target_input.setValue(100)
        recruit_form.addRow("Target Sample Size *:", self._target_input)

        self._start_date = DateEdit()
        recruit_form.addRow("Start Date:", self._start_date)

        self._end_date = DateEdit()
        recruit_form.addRow("Expected End Date:", self._end_date)

        recruit_layout.addLayout(recruit_form)
        layout.addWidget(recruit_card)

        # ── Study Objectives Card ───────────────────────────────────────
        # Was a single "Description" field bound to primary_objective under
        # a mismatched label - every protocol document keeps the primary
        # objective and secondary objectives in their own clearly separate
        # sections (never lumped into one free-text "description"), so this
        # now matches that split instead of burying both in one text box.
        desc_card = CardWidget()
        desc_layout = QVBoxLayout(desc_card)
        desc_layout.setContentsMargins(20, 20, 20, 20)
        desc_layout.setSpacing(15)

        dh_row = QHBoxLayout()
        dh_row.addWidget(StrongBodyLabel(t("metadata.section.objectives")))
        dh_row.addWidget(HelpButton(
            "The primary objective is the single main clinical question this "
            "study answers - what generated reports lead with. Secondary "
            "objectives are any additional questions the study also looks "
            "at; one per line, and optional."
        ))
        dh_row.addStretch()
        desc_layout.addLayout(dh_row)

        desc_layout.addWidget(BodyLabel(t("metadata.label.primaryobjective")))
        self._desc_input = TextEdit()
        self._desc_input.setPlaceholderText(
            t("metadata.placeholder.description")
        )
        self._desc_input.setMaximumHeight(100)
        desc_layout.addWidget(self._desc_input)

        desc_layout.addWidget(BodyLabel(t("metadata.label.secondaryobjectives")))
        self._secondary_objectives_input = TextEdit()
        self._secondary_objectives_input.setPlaceholderText(
            t("metadata.placeholder.secondaryobjectives")
        )
        self._secondary_objectives_input.setMaximumHeight(100)
        desc_layout.addWidget(self._secondary_objectives_input)

        layout.addWidget(desc_card)

        # ── Action Buttons ─────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        save_btn = PrimaryPushButton(t("metadata.btn.save"), root)
        save_btn.setIcon(FluentIcon.SAVE)
        save_btn.clicked.connect(self._save_metadata)

        reset_btn = PushButton(t("metadata.btn.reset"), root)
        reset_btn.setIcon(FluentIcon.CANCEL)
        reset_btn.clicked.connect(self._on_reset_clicked)

        # Same discard-and-return-to-the-selector action as the "← Back to
        # Projects" link at the top of the form, just also reachable down
        # here next to Save/Reset — where the user's eye actually is after
        # scrolling through the form to decide what to do with their edits.
        # No setIcon() here - the label text already carries its own
        # arrow ("←"), same as the original top-of-form back link, so an
        # icon would just duplicate it.
        back_btn = PushButton(t("metadata.btn.back"), root)
        back_btn.clicked.connect(self._on_back)

        btn_row.addWidget(back_btn)
        btn_row.addWidget(reset_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

        layout.addStretch()
        return root

    # ──────────────────────────────────────────────────────────────────
    # Screen navigation
    # ──────────────────────────────────────────────────────────────────

    def _show_selector(self):
        self._refresh_selector()
        self._stack.setCurrentIndex(0)

    def _show_form(self):
        self._stack.setCurrentIndex(1)

    # ──────────────────────────────────────────────────────────────────
    # Button handlers
    # ──────────────────────────────────────────────────────────────────

    def _on_new_project(self):
        usage_log.event("Projects", "click", "New Project button")
        self._reset_form()
        self._show_form()
        log.debug("New project form opened")

    def _on_new_generic_project(self):
        """Create a project with auto-generated placeholder metadata,
        skipping the form so the user can start working immediately."""
        usage_log.event("Projects", "click", "Quick Project button")
        log.info("Quick generic project clicked")
        stamp = strftime("%Y%m%d%H%M%S")
        short_name = f"PROJ{stamp}"
        metadata = ProjectMetadata(
            name=f"Untitled Project {stamp}",
            short_name=short_name,
            protocol_number=f"AUTO-{stamp}",
            principal_investigator="Unspecified",
            contact_email="generic@hamelin.local",
            institution="Unspecified",
            target_sample_size=100,
        )
        try:
            self._repository.create_project(metadata)
        except (ValidationError, DataSaveError) as exc:
            InfoBar.error(
                title="Error", content=str(exc),
                orient=Qt.Horizontal, isClosable=True, duration=6000,
                position=InfoBarPosition.TOP, parent=self,
            )
            return

        InfoBar.success(
            title=t("metadata.title"),
            content=t("metadata.msg.generic.success").format(short_name=short_name),
            orient=Qt.Horizontal, isClosable=True, duration=5000,
            position=InfoBarPosition.TOP, parent=self,
        )
        log.info(f"Quick generic project '{short_name}' created")
        usage_log.event("Projects", "created", "Quick Project", short_name)
        self._refresh_selector()

    def _on_delete_all_projects(self):
        """Delete every saved project after a confirmation prompt."""
        usage_log.event("Projects", "click", "Delete All Projects button")
        projects = self._repository.list_projects()
        if not projects:
            return

        dlg = MessageBox(
            t("metadata.msg.deleteall.title"),
            t("metadata.msg.deleteall.confirm").format(n=len(projects)),
            self,
        )
        if not dlg.exec():
            usage_log.event("Projects", "click", "Delete All Projects — cancelled")
            return
        usage_log.event("Projects", "click", "Delete All Projects — confirmed", f"{len(projects)} project(s)")

        failed: list[str] = []
        for short_name in projects:
            try:
                self._repository.delete_project(short_name, confirm=True)
            except Exception as exc:
                log.error(f"Failed to delete project '{short_name}': {exc}")
                failed.append(short_name)

        self._selected_short_name = None
        self._current_metadata = None
        self._refresh_selector()

        if failed:
            InfoBar.error(
                title="Some Projects Not Deleted",
                content=f"Failed: {', '.join(failed)}",
                orient=Qt.Horizontal, isClosable=True, duration=6000,
                position=InfoBarPosition.TOP, parent=self,
            )
        else:
            InfoBar.success(
                title=t("metadata.title"),
                content=t("metadata.msg.deleteall.success").format(n=len(projects)),
                orient=Qt.Horizontal, isClosable=True, duration=4000,
                position=InfoBarPosition.TOP, parent=self,
            )
        log.warning(f"Deleted {len(projects) - len(failed)} project(s) via 'Delete All'")
        self.all_projects_deleted.emit()

    def _on_open_project(self, short_name: str):
        usage_log.event("Projects", "click", "Open button", short_name)
        try:
            meta = self._repository.load(short_name)
        except Exception as exc:
            log.error(f"Failed to open project \'{short_name}\': {exc}")
            return
        self._selected_short_name = short_name
        self._load_into_form(meta)
        self._show_form()
        # Opening the project in the form also signals that a project was loaded
        self.project_loaded.emit(meta)
        log.info(f"Project \'{short_name}\' opened")

    def _on_select_project(self, short_name: str):
        """Select a project from the selector without opening its metadata."""
        usage_log.event("Projects", "click", "Select button", short_name)
        self._selected_short_name = short_name
        # Rebuilds the cards (which re-reads metadata.json for each project
        # anyway) and marks the new selection - read the just-loaded
        # metadata back from there instead of also loading it ourselves
        # first, which would read the same file twice.
        self._refresh_selector()
        meta = self._selector_meta_cache.get(short_name)
        if meta is None:
            log.error(f"Failed to select project '{short_name}': not found")
            return
        # Emit project_loaded so MainWindow forwards the selection to pages
        self.project_loaded.emit(meta)
        log.info(f"Project '{short_name}' selected")

    def _on_back(self):
        usage_log.event("Projects", "click", "Back to Projects button")
        self._show_selector()

    def _on_reset_clicked(self):
        usage_log.event("Projects", "click", "Reset button")
        self._reset_form()

    # ──────────────────────────────────────────────────────────────────
    # Public API  (called by MainWindow)
    # ──────────────────────────────────────────────────────────────────

    def load_project(self, metadata: ProjectMetadata) -> None:
        """Programmatically open a project in the form (e.g. from the home page)."""
        self._load_into_form(metadata)
        self._show_form()

    def set_active_project(self, metadata: ProjectMetadata) -> None:
        """Mark a project as the active/selected one without navigating
        away from whichever screen is currently visible. Used for the
        silent startup auto-load, so it doesn't yank the user into the
        edit form the first time they open the Projects page."""
        self._current_metadata = metadata
        self._selected_short_name = metadata.short_name
        self._refresh_selector()

    def get_current_metadata(self) -> ProjectMetadata | None:
        """Return current form state as ProjectMetadata, or None if required fields empty."""
        name = self._name_input.text().strip()
        short_name = self._short_name_input.text().strip()
        protocol = self._protocol_input.text().strip()
        if not name or not short_name or not protocol:
            return None
        try:
            return self._build_metadata()
        except Exception:
            return None

    # ──────────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────────

    def _load_into_form(self, metadata: ProjectMetadata) -> None:
        """Populate all form widgets from a ProjectMetadata instance."""
        self._current_metadata = metadata
        self._name_input.setText(metadata.name)
        self._short_name_input.setText(metadata.short_name)
        self._protocol_input.setText(metadata.protocol_number)
        self._pi_input.setText(metadata.principal_investigator)
        self._email_input.setText(metadata.contact_email)
        self._institution_input.setText(metadata.institution)

        index = self._study_type_combo.findText(metadata.study_type)
        if index >= 0:
            self._study_type_combo.setCurrentIndex(index)

        self._ethics_committee_input.setText(metadata.ethics_committee)
        self._ethics_approval_number_input.setText(metadata.ethics_approval_number)
        if metadata.approval_date:
            self._approval_date.setDate(
                QDate(metadata.approval_date.year,
                      metadata.approval_date.month,
                      metadata.approval_date.day)
            )

        self._target_input.setValue(metadata.target_sample_size)

        if metadata.first_patient_date:
            self._start_date.setDate(
                QDate(metadata.first_patient_date.year,
                      metadata.first_patient_date.month,
                      metadata.first_patient_date.day)
            )
        if metadata.estimated_completion_date:
            self._end_date.setDate(
                QDate(metadata.estimated_completion_date.year,
                      metadata.estimated_completion_date.month,
                      metadata.estimated_completion_date.day)
            )

        self._desc_input.setPlainText(metadata.primary_objective)
        self._secondary_objectives_input.setPlainText("\n".join(metadata.secondary_objectives))
        log.info(f"Loaded project \'{metadata.short_name}\' into form")

    def _build_metadata(self) -> ProjectMetadata:
        """Read all form fields and return a ProjectMetadata instance."""
        def to_py_date(q_date) -> PyDate | None:
            py = q_date.toPython()
            return py if py.year > 1752 else None

        kwargs = dict(
            name=self._name_input.text().strip(),
            short_name=self._short_name_input.text().strip().upper(),
            protocol_number=self._protocol_input.text().strip(),
            principal_investigator=self._pi_input.text().strip(),
            contact_email=self._email_input.text().strip(),
            institution=self._institution_input.text().strip(),
            study_type=self._study_type_combo.currentText(),
            target_sample_size=self._target_input.value(),
            first_patient_date=to_py_date(self._start_date.date()),
            estimated_completion_date=to_py_date(self._end_date.date()),
            primary_objective=self._desc_input.toPlainText().strip(),
            secondary_objectives=[
                line.strip() for line in self._secondary_objectives_input.toPlainText().splitlines()
                if line.strip()
            ],
            ethics_committee=self._ethics_committee_input.text().strip(),
            ethics_approval_number=self._ethics_approval_number_input.text().strip(),
            approval_date=to_py_date(self._approval_date.date()),
        )
        if self._current_metadata is not None:
            kwargs["created_at"] = self._current_metadata.created_at
        return ProjectMetadata(**kwargs)

    def _log_filled_fields(self, metadata: ProjectMetadata) -> None:
        """One usage-log row per non-empty form field, so a usability study
        can see exactly which fields people actually fill in vs. skip."""
        fields = {
            "Project Name": metadata.name,
            "Acronym": metadata.short_name,
            "Protocol Number": metadata.protocol_number,
            "Principal Investigator": metadata.principal_investigator,
            "Contact Email": metadata.contact_email,
            "Institution": metadata.institution,
            "Study Type": metadata.study_type,
            "Target Sample Size": metadata.target_sample_size,
            "Ethics Committee": metadata.ethics_committee,
            "Ethics Approval Number": metadata.ethics_approval_number,
            "Approval Date": metadata.approval_date,
            "Start Date": metadata.first_patient_date,
            "Expected End Date": metadata.estimated_completion_date,
            "Primary Objective": metadata.primary_objective,
            "Secondary Objectives": (
                f"{len(metadata.secondary_objectives)} line(s)"
                if metadata.secondary_objectives else ""
            ),
        }
        for element, value in fields.items():
            if value:
                usage_log.event("Projects", "field_filled", element, str(value))

    def _save_metadata(self):
        usage_log.event("Projects", "click", "Save Project button")
        log.info("Save project clicked")
        try:
            metadata = self._build_metadata()
        except ValidationError as exc:
            InfoBar.error(
                title="Validation Error", content=str(exc),
                orient=Qt.Horizontal, isClosable=True, duration=6000,
                position=InfoBarPosition.TOP, parent=self,
            )
            return

        try:
            self._repository.save(metadata)
            self._current_metadata = metadata
        except (ValidationError, DataSaveError) as exc:
            InfoBar.error(
                title="Save Error", content=str(exc),
                orient=Qt.Horizontal, isClosable=True, duration=6000,
                position=InfoBarPosition.TOP, parent=self,
            )
            return

        InfoBar.success(
            title="Project Saved",
            content=f"\'{metadata.short_name}\' saved to Projects/{metadata.short_name}/",
            orient=Qt.Horizontal, isClosable=True, duration=4000,
            position=InfoBarPosition.TOP, parent=self,
        )
        log.info(f"Project \'{metadata.short_name}\' saved")
        self._log_filled_fields(metadata)

        self.metadata_saved.emit()
        if metadata.target_sample_size > 0:
            self.recruitment_configured.emit()

        self._show_selector()

    def _reset_form(self):
        self._current_metadata = None
        self._name_input.clear()
        self._short_name_input.clear()
        self._protocol_input.clear()
        self._pi_input.clear()
        self._email_input.clear()
        self._institution_input.clear()
        self._study_type_combo.setCurrentIndex(0)
        self._target_input.setValue(100)
        self._desc_input.clear()
        self._secondary_objectives_input.clear()
        self._ethics_committee_input.clear()
        self._ethics_approval_number_input.clear()
        log.debug("Metadata form reset")
