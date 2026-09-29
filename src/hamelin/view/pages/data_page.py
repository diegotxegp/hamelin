"""
Data Management Page
~~~~~~~~~~~~~~~~~~~~

Data loading, inspection, and quality assessment.
"""

from pathlib import Path
from hamelin.utils.paths import workspace_dir

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QListWidget, QFileDialog,
    QScrollArea, QAbstractItemView, QPlainTextEdit, QTreeWidget, QTreeWidgetItem, QLabel,
    QSizePolicy, QDialog, QDialogButtonBox, QComboBox
)
from PySide6.QtCore import Qt, Signal
from qfluentwidgets import (
    TitleLabel, StrongBodyLabel, BodyLabel, CardWidget,
    PushButton, LineEdit, FluentIcon, IconWidget, InfoBar, InfoBarPosition,
    IndeterminateProgressBar, ComboBox
)

import pandas as pd

from hamelin.utils.logger import log
from hamelin.utils.usage_logger import usage_log
from hamelin.utils.export_paths import default_export_path
from hamelin.utils.exceptions import DataLoadError
from hamelin.model.data_model import DataModel
from hamelin.view.widgets import HelpButton, PageHelpButton, attach_help_popup, style_table_widget
from hamelin.view.widgets.theme_colors import apply_scroll_area_theme, bind_style, colors, isDarkTheme, on_theme_changed, apply_transparent_container
from hamelin.analytics.variable_analyzer import VariableAnalyzerWorker
from hamelin.core.dataset_registry import DatasetRegistry
from hamelin.view.pages.table1_page import Table1Page
from hamelin.view.widgets.config_dialog import show_config_dialog
from hamelin.i18n import t

# Where "Browse" opens by default - a single, top-level place to keep
# source datasets before they're loaded into a project (which copies its
# own working copy into that project's own data/ folder - see
# set_project_dir()'s docstring). Already existed as an empty folder
# (with just a .gitkeep) before this was ever pointed at it; not created
# here, just used - mkdir(exist_ok=True) is only a safety net in case
# that .gitkeep placeholder is ever removed.
_DATASETS_DIR = workspace_dir() / "data"


class DataPage(QWidget):
    """
    Data management and inspection page.
    
    Features:
    - Load data from files (CSV, Excel, SPSS)
    - Preview data
    - View data quality metrics
    - Inspect variables
    - Export/reload operations
    
    Signals:
    - data_loaded: Emitted when data is successfully loaded
    """
    
    data_loaded = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DataPage")
        self._data_model: DataModel | None = None
        self._removed_columns: list[str] = []        # columns hidden by the user
        self._removed_row_indices: set[int] = set()  # df.index values of hidden rows
        self._preview_row_map: list = []             # visual row idx → df.index value
        self._selection_mode: str = "columns"        # "columns" or "rows"
        self._analyzer_worker: VariableAnalyzerWorker | None = None
        self._analyzer_generation: int = 0  # bumped each launch; discards stale results
        self._last_variable_analysis: dict | None = None  # cached for "reset types"
        self._project_dir: Path | None = None          # set by MainWindow
        self._dataset_registry: DatasetRegistry | None = None
        # Value labels for the metric cards — populated in _init_ui
        self._rows_lbl = None
        self._cols_lbl = None
        self._missing_lbl = None
        self._memory_lbl = None
        # Outlier exclusion UI refs — set in _init_ui
        self._exclude_outliers_btn = None
        self._restore_outliers_btn = None
        self._outliers_lbl = None
        # Maps column name -> QComboBox widget in the variables table
        self._col_type_combos: dict[str, QComboBox] = {}
        on_theme_changed(self._restyle_type_combos)
        # Table 1 is embedded as a section of this page (it's just another
        # view over the same loaded dataset) rather than its own nav page.
        self.table1_section = Table1Page(self)
        self.data_loaded.connect(self._update_table1_section)
        log.debug("Initializing Data Page")
        self._init_ui()
    
    def _show_preview_placeholder(self) -> None:
        """Dark, disabled single-cell placeholder for the data preview
        table, matching the "load a dataset" hint used elsewhere (e.g.
        Table1's variable list) instead of a blank empty box."""
        table = self.data_table
        table.setRowCount(1)
        table.setColumnCount(1)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        item = QTableWidgetItem("— load a dataset to see the preview —")
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        table.setItem(0, 0, item)
        table.setEnabled(False)

    def _clear_preview_placeholder(self) -> None:
        """Restore the preview table to its normal, populated appearance."""
        table = self.data_table
        table.setEnabled(True)
        table.horizontalHeader().setVisible(True)
        table.verticalHeader().setVisible(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        table.horizontalHeader().setDefaultSectionSize(120)
        table.horizontalHeader().resizeSection(0, 120)

    def _show_variables_placeholder(self) -> None:
        """Dark, disabled single-cell placeholder for the variable types
        table, shown instead of hiding it and leaving blank space."""
        table = self.variables_table
        table.setColumnCount(1)
        table.setRowCount(1)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        item = QTableWidgetItem("— load a dataset to see variable types —")
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        table.setItem(0, 0, item)
        table.setEnabled(False)
        table.setVisible(True)

    def _clear_variables_placeholder(self) -> None:
        """Restore the variable types table to its normal 3-column layout."""
        table = self.variables_table
        table.setEnabled(True)
        table.horizontalHeader().setVisible(True)
        table.verticalHeader().setVisible(True)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Variable", "Set type", "Info"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

    def _restyle_type_combos(self) -> None:
        for cb in list(self._col_type_combos.values()):
            try:
                cb.setStyleSheet(self._type_combo_qss(cb))
            except RuntimeError:
                pass  # combo already deleted with a rebuilt table

    @staticmethod
    def _type_combo_qss(combo) -> str:
        c = colors()
        overridden = bool(combo.property("overridden"))
        color = "#0078d4" if overridden else c.text_primary
        weight = "font-weight: bold;" if overridden else ""
        return f"ComboBox {{ color: {color}; {weight} }}"

    def _init_ui(self):
        """Initialize user interface"""
        # Outer scroll so the page works at any window height
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        scroll.setWidget(container)
        # A raw QScrollArea paints an opaque QPalette::Base background that
        # doesn't follow Hamelin's light/dark theme - make it transparent so
        # the correctly themed background behind it shows through instead.
        apply_scroll_area_theme(scroll)
        apply_transparent_container(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Title
        title_row = QHBoxLayout()
        title = TitleLabel(t("data.title"))
        title.setAlignment(Qt.AlignLeft)
        title_row.addWidget(title)
        title_row.addWidget(PageHelpButton(t("data.help"), self))
        title_row.addStretch()
        main_layout.addLayout(title_row)

        # Subtitle
        subtitle = StrongBodyLabel(t("data.subtitle"))
        bind_style(subtitle, lambda c: f"color: {c.text_secondary};")
        main_layout.addWidget(subtitle)
        
        main_layout.addSpacing(20)
        
        # File Selection Card
        file_card = CardWidget()
        file_layout = QVBoxLayout(file_card)
        file_layout.setContentsMargins(20, 20, 20, 20)
        file_layout.setSpacing(15)
        # Section header with help
        title_row = QHBoxLayout()
        file_title = StrongBodyLabel(t("data.section.source"))
        title_row.addWidget(file_title)
        help_btn = HelpButton(t("help.data.formats"))
        title_row.addWidget(help_btn)
        title_row.addStretch()
        file_layout.addLayout(title_row)
        
        # File path row
        file_row = QHBoxLayout()
        file_row.setSpacing(10)
        
        self.file_path_edit = LineEdit()
        self.file_path_edit.setPlaceholderText(t("data.placeholder.filepath"))
        self.file_path_edit.setReadOnly(True)
        file_row.addWidget(self.file_path_edit, stretch=1)
        
        browse_btn = PushButton(t("data.btn.browse"), self)
        browse_btn.setIcon(FluentIcon.FOLDER)
        browse_btn.clicked.connect(self._browse_file)
        file_row.addWidget(browse_btn)
        
        self.load_btn = PushButton(t("data.btn.load"), self)
        self.load_btn.setIcon(FluentIcon.ACCEPT)
        self.load_btn.clicked.connect(self._on_load_clicked)
        file_row.addWidget(self.load_btn)
        
        # (formats_label will be placed below the file selection row so it
        # doesn't compete visually with the project datasets control)

        # ── Project dataset selector (hidden until a project is active) ──
        self._project_datasets_section = QWidget()
        proj_ds_layout = QHBoxLayout(self._project_datasets_section)
        proj_ds_layout.setContentsMargins(0, 8, 0, 0)
        proj_ds_layout.setSpacing(10)
        proj_ds_lbl = BodyLabel(t("data.txt.project_datasets"))
        bind_style(proj_ds_lbl, lambda c: f"color: {c.text_secondary}; font-size: 12px;")
        proj_ds_layout.addWidget(proj_ds_lbl)
        self._dataset_combo = ComboBox(self)
        self._dataset_combo.setMinimumWidth(300)
        self._dataset_combo.setPlaceholderText(t("data.placeholder.datasets"))
        proj_ds_layout.addWidget(self._dataset_combo, stretch=1)
        self.load_saved_btn = PushButton(t("data.btn.load.selected"), self)
        self.load_saved_btn.setIcon(FluentIcon.ACCEPT)
        self.load_saved_btn.clicked.connect(self._on_dataset_combo_load)
        proj_ds_layout.addWidget(self.load_saved_btn)
        self._project_datasets_section.setVisible(False)
        file_layout.addWidget(self._project_datasets_section)

        # File path row (moved below project dataset selector to keep added
        # datasets visually above the "add new" controls)
        file_layout.addLayout(file_row)

        # Supported formats info (placed after the add/load row)
        formats_label = BodyLabel(t("data.label.formats"))
        bind_style(formats_label, lambda c: f"color: {c.text_secondary}; font-size: 11px;")
        file_layout.addWidget(formats_label)

        main_layout.addWidget(file_card)
        
        # Data Quality Metrics Cards (Grid)
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(15)
        
        # Rows count card
        rows_card, self._rows_lbl = self._create_metric_card(
            FluentIcon.ALIGNMENT, t("data.label.rows"), "0", "Observations"
        )
        metrics_row.addWidget(rows_card)

        # Columns count card
        cols_card, self._cols_lbl = self._create_metric_card(
            FluentIcon.MENU, t("data.label.cols"), "0", t("dashboard.label.variables")
        )
        metrics_row.addWidget(cols_card)

        # Missing values card
        missing_card, self._missing_lbl = self._create_metric_card(
            FluentIcon.CLOSE, t("data.label.missing"), "0%", "Data completeness"
        )
        metrics_row.addWidget(missing_card)

        # Memory usage card
        memory_card, self._memory_lbl = self._create_metric_card(
            FluentIcon.SAVE, t("data.label.memory"), "0 KB", "Dataset size"
        )
        metrics_row.addWidget(memory_card)
        
        main_layout.addLayout(metrics_row)
        
        # Data Preview Card
        preview_card = CardWidget()
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(20, 20, 20, 20)
        preview_layout.setSpacing(15)
        
        preview_header = QHBoxLayout()
        preview_title = StrongBodyLabel(t("data.section.inspection"))
        preview_header.addWidget(preview_title)
        
        help_btn = HelpButton(t("help.data.preview"))
        preview_header.addWidget(help_btn)
        preview_header.addStretch()
        
        preview_info = BodyLabel(t("data.txt.all_rows_use_scroll"))
        bind_style(preview_info, lambda c: f"color: {c.text_secondary}; font-size: 11px;")
        preview_header.addWidget(preview_info)
        
        preview_layout.addLayout(preview_header)
        
        # Data table
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        style_table_widget(self.data_table)
        # Inspection only - editing a cell here would silently change the
        # in-memory dataset without going through any of the app's actual
        # data-editing flows (rule builder, type overrides, row/column
        # exclusion), so cells must not be directly editable.
        self.data_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.data_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectColumns)
        self.data_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        # Fixed-width columns with horizontal scroll bar
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.data_table.horizontalHeader().setDefaultSectionSize(120)
        self.data_table.horizontalHeader().setStretchLastSection(False)
        self.data_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.data_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.data_table.setMinimumHeight(300)
        # Auto-detect mode: clicking a column header → SelectColumns,
        # clicking a row number → SelectRows
        self.data_table.horizontalHeader().sectionPressed.connect(
            lambda _: self._set_selection_mode("columns")
        )
        self.data_table.verticalHeader().sectionPressed.connect(
            lambda _: self._set_selection_mode("rows")
        )
        # Double-click header to edit/override Ludwig type for the column
        header = self.data_table.horizontalHeader()
        # try double-click signal (if available)
        try:
            header.sectionDoubleClicked.connect(self._on_header_edit_type)
        except Exception:
            # Some bindings may not expose sectionDoubleClicked — ignore
            pass
        # Always provide a right-click context menu on the header as fallback
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(lambda pos: self._on_header_context_menu(pos))
        self._show_preview_placeholder()
        preview_layout.addWidget(self.data_table)

        # ── Remove / Restore actions ───────────────────────────────────
        col_actions = QHBoxLayout()
        self._remove_btn = PushButton(t("data.btn.remove.selected"), self)
        self._remove_btn.setIcon(FluentIcon.REMOVE_FROM)
        self._remove_btn.clicked.connect(self._remove_selected)
        self._remove_btn.setEnabled(False)
        self._restore_col_btn = PushButton(t("data.btn.restore.all"), self)
        self._restore_col_btn.setIcon(FluentIcon.SYNC)
        self._restore_col_btn.clicked.connect(self._restore_all)
        self._restore_col_btn.setEnabled(False)
        self._removed_info_lbl = BodyLabel("")
        bind_style(self._removed_info_lbl, lambda c: f"color: {c.text_secondary}; font-size: 11px;")
        col_actions.addWidget(self._remove_btn)
        col_actions.addWidget(self._restore_col_btn)
        col_actions.addWidget(self._removed_info_lbl)
        col_actions.addStretch()
        preview_layout.addLayout(col_actions)

        # ── Outlier actions — moved here (rather than down near the
        # variable-types table) since outliers are about rows in THIS
        # table, same as the remove/restore actions right above. ──────
        outlier_actions = QHBoxLayout()
        outlier_actions.setSpacing(10)

        self._exclude_outliers_btn = PushButton(t("data.btn.exclude"), self)
        self._exclude_outliers_btn.setIcon(FluentIcon.FILTER)
        attach_help_popup(
            self._exclude_outliers_btn,
            t("data.txt.automatically_mark_rows_where_any_numeri")
        )
        self._exclude_outliers_btn.clicked.connect(self._exclude_outliers)
        self._exclude_outliers_btn.setEnabled(False)
        outlier_actions.addWidget(self._exclude_outliers_btn)

        self._restore_outliers_btn = PushButton(t("data.btn.restore"), self)
        self._restore_outliers_btn.setIcon(FluentIcon.SYNC)
        attach_help_popup(self._restore_outliers_btn, t("data.txt.clear_all_outlier_exclusions_and_include"))
        self._restore_outliers_btn.clicked.connect(self._restore_excluded_rows)
        self._restore_outliers_btn.setEnabled(False)
        outlier_actions.addWidget(self._restore_outliers_btn)

        self._outliers_lbl = BodyLabel("")
        # Saturated red needs a lighter variant on dark backgrounds to keep
        # enough contrast - the light value (#D13438) is also used for
        # _STATUS_STYLES["error"] elsewhere, unchanged.
        bind_style(
            self._outliers_lbl,
            lambda c: f"color: {'#FF6B6B' if isDarkTheme() else '#D13438'}; font-size: 11px;",
        )
        outlier_actions.addWidget(self._outliers_lbl)

        outlier_actions.addStretch()
        preview_layout.addLayout(outlier_actions)

        main_layout.addWidget(preview_card)
        
        # Variable List Card
        variables_card = CardWidget()
        variables_layout = QVBoxLayout(variables_card)
        variables_layout.setContentsMargins(20, 20, 20, 20)
        variables_layout.setSpacing(15)
        
        # Section header with help
        title_row = QHBoxLayout()
        variables_title = StrongBodyLabel(t("data.section.variables"))
        title_row.addWidget(variables_title)
        help_btn = HelpButton(t("help.data.variables"))
        title_row.addWidget(help_btn)
        title_row.addStretch()
        variables_layout.addLayout(title_row)
        
        # Progress bar shown while Ludwig infers types
        self._var_progress = IndeterminateProgressBar(self)
        self._var_progress.setVisible(False)
        self._var_progress.stop()
        variables_layout.addWidget(self._var_progress)

        self._var_status_lbl = BodyLabel(t("data.txt.analysing_variable_types"))
        bind_style(
            self._var_status_lbl,
            lambda c: f"color: {c.text_secondary}; font-style: italic; font-size: 11px;",
        )
        self._var_status_lbl.setVisible(False)
        variables_layout.addWidget(self._var_status_lbl)

        # Variables table — hidden until Ludwig analysis completes.
        # Columns: Variable name | Set type (ComboBox, shows the inferred
        # type as "<type> (original)") | Info
        self.variables_table = QTableWidget()
        self.variables_table.setColumnCount(3)
        self.variables_table.setHorizontalHeaderLabels(
            ["Variable", "Set type", "Info"]
        )
        self.variables_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.variables_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.variables_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.variables_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.variables_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.variables_table.setAlternatingRowColors(True)
        style_table_widget(self.variables_table)
        self.variables_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.variables_table.setMinimumHeight(400)
        self.variables_table.setMaximumHeight(800)
        self._show_variables_placeholder()
        variables_layout.addWidget(self.variables_table)

        # Give the card a larger minimum height so the panel appears bigger by default
        variables_card.setMinimumHeight(420)

        main_layout.addWidget(variables_card)

        # ── Row 1: data operations ─────────────────────────────────────
        actions_row1 = QHBoxLayout()
        actions_row1.setSpacing(10)

        # Format picker + Export button grouped tightly together (no gap
        # between them, wider gap to the unrelated buttons that follow) so
        # it visually reads as one "export as ___" control instead of two
        # unrelated widgets that happen to sit next to each other.
        export_group = QHBoxLayout()
        export_group.setSpacing(0)

        self._export_format_combo = ComboBox()
        self._export_format_combo.addItems(["CSV", "Excel (.xlsx)", "Word (.docx)"])
        attach_help_popup(self._export_format_combo, t("data.txt.file_format_used_by_the_export"))
        export_group.addWidget(self._export_format_combo)

        export_btn = PushButton(t("data.btn.export"), self)
        export_btn.setIcon(FluentIcon.SAVE)
        attach_help_popup(export_btn, t("data.txt.export_the_dataset_in_the_format"))
        export_btn.clicked.connect(self._export_data)
        export_group.addWidget(export_btn)

        actions_row1.addLayout(export_group)
        actions_row1.addSpacing(20)

        reload_btn = PushButton(t("data.btn.reset.types"), self)
        reload_btn.setIcon(FluentIcon.SYNC)
        attach_help_popup(
            reload_btn,
            t("data.txt.revert_every_variable_back_to_its")
        )
        reload_btn.clicked.connect(self._reset_variable_types)
        actions_row1.addWidget(reload_btn)

        quality_report_btn = PushButton(t("data.btn.quality"), self)
        quality_report_btn.setIcon(FluentIcon.DOCUMENT)
        attach_help_popup(quality_report_btn, t("data.txt.save_a_csv_with_per_variable"))
        quality_report_btn.clicked.connect(self._generate_quality_report)
        actions_row1.addWidget(quality_report_btn)

        remove_duplicates_btn = PushButton(t("data.btn.remove_duplicates"), self)
        remove_duplicates_btn.setIcon(FluentIcon.BROOM)
        attach_help_popup(
            remove_duplicates_btn,
            t("data.txt.hide_every_duplicate_row_keeping_the")
        )
        remove_duplicates_btn.clicked.connect(self._remove_duplicates)
        actions_row1.addWidget(remove_duplicates_btn)

        self._view_changes_btn = PushButton(t("data.btn.view_changes"), self)
        self._view_changes_btn.setIcon(FluentIcon.VIEW)
        attach_help_popup(self._view_changes_btn, t("data.help.view_changes"))
        self._view_changes_btn.clicked.connect(self._on_view_changes)
        actions_row1.addWidget(self._view_changes_btn)

        actions_row1.addStretch()
        main_layout.addLayout(actions_row1)

        # Stretch
        # Missingness figure label (top variables)
        self._missing_fig_label = QLabel()
        self._missing_fig_label.setVisible(False)
        self._missing_fig_label.setStyleSheet("background: transparent;")
        main_layout.addWidget(self._missing_fig_label)

        # Dataset summary card (hidden until a dataset is loaded)
        self._summary_card = CardWidget()
        summary_layout = QVBoxLayout(self._summary_card)
        summary_layout.setContentsMargins(20, 20, 20, 20)
        summary_layout.setSpacing(8)
        summary_title = StrongBodyLabel(t("data.txt.data_summary"))
        summary_layout.addWidget(summary_title)
        self._summary_label = QLabel()
        self._summary_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._summary_label.setWordWrap(False)   # preserve monospace column alignment
        self._summary_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        bind_style(
            self._summary_label,
            lambda c: (
                f"color: {c.text_primary}; font-size: 12px; "
                "font-family: monospace; background: transparent;"
            ),
        )
        self._summary_label.setContentsMargins(4, 4, 4, 4)
        self._summary_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        summary_scroll = QScrollArea()
        summary_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        apply_scroll_area_theme(summary_scroll)
        summary_scroll.setWidget(self._summary_label)
        summary_scroll.setWidgetResizable(True)
        summary_scroll.setFixedHeight(380)
        summary_layout.addWidget(summary_scroll)

        export_summary_btn = PushButton(t("data.txt.export_data_summary"), self)
        export_summary_btn.setIcon(FluentIcon.DOCUMENT)
        attach_help_popup(export_summary_btn, t("data.txt.save_the_data_summary_text_to"))
        export_summary_btn.clicked.connect(self._export_summary)
        summary_layout.addWidget(export_summary_btn, alignment=Qt.AlignLeft)

        self._summary_card.setVisible(False)
        main_layout.addWidget(self._summary_card)

        # Table 1 — same "baseline characteristics" generator that used to
        # be its own nav page, now a section here since it's just another
        # view over this same loaded dataset. Just a small subtitle, no
        # big card wrapper, so it reads as "we've moved into this part of
        # the page" rather than a whole separate module.
        table1_title_row = QHBoxLayout()
        table1_subtitle = StrongBodyLabel(t("data.section.table1"))
        bind_style(table1_subtitle, lambda c: f"color: {c.text_secondary};")
        table1_title_row.addWidget(table1_subtitle)
        table1_help_btn = HelpButton(t("help.data.table1"))
        table1_title_row.addWidget(table1_help_btn)
        table1_title_row.addStretch()
        main_layout.addLayout(table1_title_row)

        main_layout.addWidget(self.table1_section)

        main_layout.addStretch()

        log.debug("Data Page initialized successfully")
    
    def _create_metric_card(self, icon: FluentIcon, title: str,
                            value: str, subtitle: str):
        """Create a metric card widget. Returns (card, value_label)."""
        card = CardWidget()
        # icon(24) + title(~17) + big value TitleLabel(~39) + subtitle(~14)
        # + 3x8 spacing + 2x16 margins needs ~150px - the old fixed 120px
        # was shorter than its own content, so the large value number got
        # visually clipped/squeezed at the bottom of the card.
        card.setFixedHeight(155)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        icon_widget = IconWidget(icon, card)
        icon_widget.setFixedSize(24, 24)
        layout.addWidget(icon_widget)

        title_label = BodyLabel(title)
        bind_style(title_label, lambda c: f"color: {c.text_secondary}; font-size: 12px;")
        layout.addWidget(title_label)

        value_label = TitleLabel(value)
        layout.addWidget(value_label)

        subtitle_label = BodyLabel(subtitle)
        bind_style(subtitle_label, lambda c: f"color: {c.text_secondary}; font-size: 10px;")
        layout.addWidget(subtitle_label)

        layout.addStretch()
        return card, value_label
    
    def _browse_file(self):
        """Open file browser dialog"""
        usage_log.event("Data", "click", "Browse button")
        log.info("Opening file browser")
        _DATASETS_DIR.mkdir(parents=True, exist_ok=True)
        file_path, _ = QFileDialog.getOpenFileName(
            self.window(),
            t("data.dialog.select"),
            str(_DATASETS_DIR),
            t("data.dialog.filters")
        )
        
        if file_path:
            self.file_path_edit.setText(file_path)
            log.info(f"Selected file: {file_path}")
            usage_log.event("Data", "select", "File path", file_path)

    def _on_load_clicked(self) -> None:
        usage_log.event("Data", "click", "Load button")
        self._load_data()

    def get_data_model(self) -> DataModel | None:
        """Return the currently loaded DataModel (used by other pages)."""
        return self._data_model

    # ── Project dataset persistence ────────────────────────────────────

    def set_project_dir(self, project_dir, auto_load_last: bool = True) -> None:
        """Called by MainWindow when a project is opened or created.

        Args:
            project_dir: path or short name of project
            auto_load_last: if True, attempt to auto-load the last-used dataset
                            into the DataPage. Set to False to only populate
                            the project dataset selector without loading data.
        """
        if project_dir is None:
            self._project_dir = None
            self.table1_section.set_project_dir(None)
            self._dataset_registry = None
            self._project_datasets_section.setVisible(False)
            return

        # project_dir may be just a short_name string ("DGHFGD") or a full Path.
        # Always resolve to the absolute project folder via ProjectRepository.
        from hamelin.core.project import ProjectRepository
        candidate = Path(project_dir)
        if candidate.is_absolute() and candidate.exists():
            self._project_dir = candidate
        else:
            # Treat as short_name and ask the repo for the real path
            self._project_dir = ProjectRepository().get_project_path(str(project_dir))

        self.table1_section.set_project_dir(self._project_dir)
        self._dataset_registry = DatasetRegistry(self._project_dir)
        self._refresh_dataset_combo()
        # Auto-load the last-used dataset if requested and no data is currently loaded
        if auto_load_last and self._data_model is None:
            last = self._dataset_registry.get_last_used()
            if last:
                path = self._dataset_registry.dataset_path(last)
                if path.exists():
                    self.file_path_edit.setText(str(path))
                    self._load_data()
        log.debug(f"DataPage: project_dir resolved to {self._project_dir}")

    def _refresh_dataset_combo(self, selected: str | None = None) -> None:
        """Repopulate the dataset combobox from the registry."""
        if self._dataset_registry is None:
            self._project_datasets_section.setVisible(False)
            return
        entries = self._dataset_registry.list_datasets()
        self._dataset_combo.blockSignals(True)
        self._dataset_combo.clear()
        for e in entries:
            label = f"{e['filename']}  ({e['rows']} rows × {e['columns']} cols)"
            self._dataset_combo.addItem(label, userData=e["filename"])
        self._dataset_combo.blockSignals(False)
        if entries:
            # Select the requested item, or the first one
            target = selected or self._dataset_registry.get_last_used()
            for i in range(self._dataset_combo.count()):
                if self._dataset_combo.itemData(i) == target:
                    self._dataset_combo.setCurrentIndex(i)
                    break
            self._project_datasets_section.setVisible(True)
        else:
            self._project_datasets_section.setVisible(False)

    def _on_dataset_combo_load(self) -> None:
        """Load the dataset selected in the combobox."""
        usage_log.event("Data", "click", "Load Selected Dataset button", self._dataset_combo.currentText())
        if self._dataset_registry is None:
            return
        idx = self._dataset_combo.currentIndex()
        if idx < 0:
            return
        filename = self._dataset_combo.itemData(idx)
        if not filename:
            return
        path = self._dataset_registry.dataset_path(filename)
        if not path.exists():
            InfoBar.error(
                title=t("data.txt.file_not_found"),
                content=t("data.txt.0_no_longer_exists_in_the").format(filename),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self,
            )
            return
        self.file_path_edit.setText(str(path))
        self._load_data()
        self._dataset_registry.set_last_used(filename)

    def _update_table1_section(self) -> None:
        """Keep the embedded Table 1 section in sync whenever data_loaded
        fires (initial load, or after removing columns/rows)."""
        if self._data_model is None:
            return
        self.table1_section.set_data_model(self._data_model)

    @staticmethod
    def _size_columns_to_headers(table: QTableWidget, minimum: int = 120) -> None:
        """Widen any column whose header text doesn't fit in *minimum*
        pixels, so long column names (e.g. "Enfermedad respiratoria")
        aren't visually clipped. Short headers stay at the minimum -
        this only ever grows a column, never shrinks it below that."""
        from PySide6.QtGui import QFontMetrics

        header = table.horizontalHeader()
        metrics = QFontMetrics(header.font())
        padding = 24  # header padding + sort indicator space
        for col in range(table.columnCount()):
            item = table.horizontalHeaderItem(col)
            text = item.text() if item is not None else ""
            needed = metrics.horizontalAdvance(text) + padding
            if needed > minimum:
                table.setColumnWidth(col, needed)

        # A dataset with few columns otherwise leaves a bare empty strip to
        # their right - Interactive resize mode has nothing to scroll to
        # there, it's just dead space. Distribute it evenly across the
        # existing columns instead, same as a spreadsheet would, but only
        # when there's actually leftover room (a wide dataset that already
        # needs its horizontal scrollbar is untouched).
        n_cols = table.columnCount()
        if n_cols:
            viewport_width = table.viewport().width()
            total_width = sum(table.columnWidth(c) for c in range(n_cols))
            extra = (viewport_width - total_width) // n_cols
            if extra > 0:
                for col in range(n_cols):
                    table.setColumnWidth(col, table.columnWidth(col) + extra)

    def _load_data(self):
        """Load data from the selected file and update all UI sections."""
        file_path = self.file_path_edit.text()
        log.debug(
            f"_load_data called — file='{file_path}' "
            f"registry={'SET → ' + str(self._project_dir) if self._dataset_registry else 'NOT SET'}"
        )

        if not file_path:
            InfoBar.warning(
                title=t("data.txt.no_file_selected"),
                content=t("data.txt.please_select_a_data_file_first"),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )
            return

        log.info(f"Loading data from: {file_path}")

        try:
            dm = DataModel()
            dm.load_from_file(file_path)
            self._data_model = dm
            # If this project has a saved state, load and apply it
            try:
                if self._project_dir is not None:
                    dm.load_state(self._project_dir)
                    # Re-generate metadata so any persisted column type overrides
                    # are reflected in `column_metadata` (assigned_type)
                    try:
                        dm._generate_column_metadata()
                    except Exception:
                        pass
            except Exception:
                log.debug("No project state loaded or failed to apply it")
        except DataLoadError as exc:
            InfoBar.error(
                title=t("data.txt.load_error"),
                content=str(exc),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=6000,
                parent=self,
            )
            log.error(f"Failed to load data: {exc}")
            return

        # ── Update metric cards ────────────────────────────────────────
        self._rows_lbl.setText(str(dm.n_rows))
        self._cols_lbl.setText(str(dm.n_columns))

        total_cells = dm.n_rows * dm.n_columns
        total_missing = sum(dm.missing_values.values())
        missing_pct = (total_missing / total_cells * 100) if total_cells > 0 else 0
        self._missing_lbl.setText(f"{missing_pct:.1f}%")

        mem_bytes = dm.df.memory_usage(deep=True).sum()
        if mem_bytes < 1024:
            mem_str = f"{mem_bytes} B"
        elif mem_bytes < 1024 * 1024:
            mem_str = f"{mem_bytes / 1024:.1f} KB"
        else:
            mem_str = f"{mem_bytes / 1024 / 1024:.1f} MB"
        self._memory_lbl.setText(mem_str)

        # ── Update preview table ───────────────────────────────────────
        preview = dm.df
        self._preview_row_map = list(preview.index)  # visual idx → df.index
        self._clear_preview_placeholder()
        self.data_table.setRowCount(len(preview))
        self.data_table.setColumnCount(len(preview.columns))
        self.data_table.setHorizontalHeaderLabels(list(preview.columns))

        # Pre-build a display DataFrame: datetime cols → "YYYY-MM-DD", NaN/NaT → ""
        display_df = preview.copy()
        for col in display_df.columns:
            if pd.api.types.is_datetime64_any_dtype(display_df[col]):
                display_df[col] = display_df[col].dt.strftime("%Y-%m-%d").fillna("")
            else:
                display_df[col] = display_df[col].fillna("").astype(str).replace("nan", "")

        self._fill_preview_table(display_df)
        self._size_columns_to_headers(self.data_table)

        # ── Variable table: show progress bar, launch Ludwig in background ──
        self.variables_table.setVisible(False)
        self.variables_table.setRowCount(0)
        self._col_type_combos.clear()
        self._var_progress.setVisible(True)
        self._var_progress.start()
        self._var_status_lbl.setVisible(True)

        self._start_analyzer_worker(dm.df)

        # Reset removal state for the new dataset
        self._removed_columns.clear()
        self._removed_row_indices.clear()
        self._remove_btn.setEnabled(True)
        self._restore_col_btn.setEnabled(False)
        self._removed_info_lbl.setText("")
        self._set_selection_mode("columns")

        InfoBar.success(
            title=t("data.txt.data_loaded"),
            content=t("data.txt.0_rows_1_columns_loaded_successfully").format(dm.n_rows, dm.n_columns),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self,
        )
        log.info(f"Data loaded: {dm.n_rows}r × {dm.n_columns}c")
        usage_log.event("Data", "loaded", Path(file_path).name, f"{dm.n_rows} rows × {dm.n_columns} cols")

        # ── Persist dataset to project folder if a project is active ──
        if self._dataset_registry is not None:
            import traceback as _tb
            try:
                source = Path(file_path)
                project_data_dir = (self._project_dir / "data").resolve()
                already_inside = source.parent.resolve() == project_data_dir
                if already_inside:
                    self._dataset_registry.set_last_used(source.name)
                    self._refresh_dataset_combo(selected=source.name)
                    log.debug(f"Dataset already in project folder: {source.name}")
                else:
                    dest = self._dataset_registry.copy_and_register(
                        source_path=file_path,
                        rows=dm.n_rows,
                        columns=dm.n_columns,
                    )
                    self._dataset_registry.set_last_used(dest.name)
                    self.file_path_edit.setText(str(dest))
                    self._refresh_dataset_combo(selected=dest.name)
                    # Show different message when the registry returned an
                    # existing file (duplicate original name) vs when a new
                    # copy was created.
                    if getattr(self._dataset_registry, 'last_action', None) == 'existing':
                        log.info(f"Dataset already exists in project: {dest}")
                        InfoBar.info(
                            title=t("data.txt.dataset_exists"),
                            content=t("data.txt.a_dataset_with_the_same_name").format(self._project_dir.name),
                            orient=Qt.Horizontal,
                            isClosable=True,
                            position=InfoBarPosition.TOP,
                            duration=5000,
                            parent=self,
                        )
                    else:
                        log.info(f"Dataset saved to project: {dest}")
                        InfoBar.success(
                            title=t("data.txt.saved_to_project"),
                            content=t("data.txt.dataset_copied_to_projects_0_data").format(self._project_dir.name),
                            orient=Qt.Horizontal,
                            isClosable=True,
                            position=InfoBarPosition.TOP,
                            duration=4000,
                            parent=self,
                        )
                    # Persist project state after adding/loading a dataset
                    try:
                        if self._data_model is not None and self._project_dir is not None:
                            self._data_model.save_state(self._project_dir)
                    except Exception:
                        log.debug("Failed to persist project state after saving dataset")
            except Exception as exc:
                log.error(f"Could not save dataset to project: {exc}\n{_tb.format_exc()}")
                InfoBar.warning(
                    title=t("data.txt.could_not_save_to_project"),
                    content=str(exc),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=6000,
                    parent=self,
                )
        else:
            log.warning("_dataset_registry is None — no project active, dataset not saved to project folder")

        self.data_loaded.emit()
        self._remove_btn.setEnabled(True)
        if self._exclude_outliers_btn is not None:
            self._exclude_outliers_btn.setEnabled(True)

        # Update dataset summary panel
        try:
            self._update_dataset_summary()
        except Exception as exc:
            log.exception(f"Failed to update dataset summary: {exc}")

    # ── Ludwig variable analysis ────────────────────────────────────────
    # Icons for Ludwig native types (shown directly — no remapping)
    _LUDWIG_TYPE_ICONS: dict[str, str] = {
        "number":     "\U0001f522",  # 🔢
        "binary":     "\U00002b55",  # ⭕
        "category":   "\U0001f4dd",  # 📝
        "date":       "\U0001f4c5",  # 📅
        "text":       "\U0001f4c4",  # 📄
        "sequence":   "\U0001f524",  # 🔤
        "timeseries": "\U0001f4c8",  # 📈
        "vector":     "\U0001f9ee",  # 🧮
        "set":        "\U0001f522",  # 🔢
        "bag":        "\U0001f4e6",  # 📦
        "image":      "\U0001f5bc",  # 🖼️
        "audio":      "\U0001f50a",  # 🔊
        "h3":         "\U0001f5fa",  # 🗺️
    }

# Ordered list of all Ludwig-supported types shown in the ComboBox
    _LUDWIG_TYPES: list[str] = [
        'number', 'binary', 'category', 'text', 'date',
        'timeseries', 'sequence', 'vector', 'set', 'bag',
        'image', 'audio', 'h3',
    ]

    def _fill_preview_table(self, display_df: pd.DataFrame) -> None:
        """Put *display_df* (already strings) into the preview table.

        Reads the frame once as plain Python lists instead of one
        ``df.iloc[row, col]`` per cell (each of which costs ~0.2 ms: a
        30-column, 3 800-row dataset took ~25 s just to show) and repaints
        once at the end instead of after every item.
        """
        table = self.data_table
        table.setUpdatesEnabled(False)
        try:
            for row_idx, row in enumerate(display_df.to_numpy(dtype=object).tolist()):
                for col_idx, val in enumerate(row):
                    table.setItem(row_idx, col_idx, QTableWidgetItem(val))
        finally:
            table.setUpdatesEnabled(True)

    def _start_analyzer_worker(self, df: pd.DataFrame) -> None:
        """Launch a background type-inference worker for *df*.

        Never interrupts a worker that's already running: QThread.terminate()
        hard-kills the OS thread wherever it happens to be, and this worker
        spends its whole life inside native Ludwig/pandas calls - killing it
        mid-call can corrupt interpreter state and crash the process with no
        traceback. Instead every worker is tagged with a generation number;
        when one finishes, its result is only applied if it's still current -
        an older worker that finishes late is just discarded.

        The two "Load" buttons are disabled for the duration instead: this
        analysis can take tens of seconds (Ludwig's own import cost - see
        prewarm_ludwig_type_inference()'s docstring), and clicking Load
        again mid-analysis used to silently start a second, fully
        concurrent Ludwig analysis - harmless to correctness thanks to the
        generation guard above, but wasteful (two full analyses running at
        once) and confusing (their progress bars/log lines interleave).
        """
        self.load_btn.setEnabled(False)
        self.load_saved_btn.setEnabled(False)

        self._analyzer_generation += 1
        generation = self._analyzer_generation
        worker = VariableAnalyzerWorker(df, parent=self)
        worker.analysis_ready.connect(
            lambda analysis, gen=generation: self._on_analyzer_worker_done(gen, analysis)
        )
        worker.error.connect(
            lambda message, gen=generation: self._on_analyzer_worker_error(gen, message)
        )
        worker.finished.connect(worker.deleteLater)
        self._analyzer_worker = worker
        worker.start()

    def _on_analyzer_worker_done(self, generation: int, analysis: dict) -> None:
        if generation != self._analyzer_generation:
            return  # superseded by a later load/refresh - stale, discard
        self.load_btn.setEnabled(True)
        self.load_saved_btn.setEnabled(True)
        self._on_variable_analysis_ready(analysis)

    def _on_analyzer_worker_error(self, generation: int, message: str) -> None:
        """Handle VariableAnalyzerWorker.error - previously unconnected,
        so a failed analysis left the progress bar spinning forever with
        no feedback at all."""
        if generation != self._analyzer_generation:
            return  # superseded - a newer worker's outcome is what counts
        self.load_btn.setEnabled(True)
        self.load_saved_btn.setEnabled(True)
        self._var_progress.stop()
        self._var_progress.setVisible(False)
        self._var_status_lbl.setVisible(False)
        InfoBar.warning(
            title=t("data.txt.variable_analysis_failed"),
            content=t("data.txt.could_not_infer_variable_types_0").format(message),
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=6000, parent=self,
        )

    def _on_variable_analysis_ready(self, analysis: dict) -> None:
        """Populate variables table with Ludwig types and an editable ComboBox per row."""
        self._last_variable_analysis = analysis
        self._var_progress.stop()
        self._var_progress.setVisible(False)
        self._var_status_lbl.setVisible(False)
        self.variables_table.setRowCount(0)
        self._col_type_combos.clear()
        self._clear_variables_placeholder()
        self.variables_table.setVisible(True)

        df = self._data_model.df if self._data_model is not None else None

        self.variables_table.setRowCount(len(analysis))
        self.variables_table.setSortingEnabled(False)

        for row, (col, info) in enumerate(analysis.items()):
            raw = str(info["ludwig_type"]).split(".")[-1].lower()
            icon = self._LUDWIG_TYPE_ICONS.get(raw, "\U0001f4c4")

            # ── Col 0: variable name (read-only, with stats tooltip) ──
            name_item = QTableWidgetItem(col)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if df is not None and col in df.columns:
                series = df[col]
                n_total = len(series)
                n_missing = int(series.isna().sum())
                n_unique = int(series.nunique(dropna=True))
                tooltip = (
                    f"Non-null: {n_total - n_missing}\n"
                    f"Missing: {n_missing} ({n_missing / n_total * 100:.1f}%)\n"
                    f"Unique: {n_unique}"
                )
                if pd.api.types.is_numeric_dtype(series):
                    s = series.dropna()
                    if not s.empty:
                        tooltip += (
                            f"\nMin: {s.min():.4f}  "
                            f"Max: {s.max():.4f}  "
                            f"Mean: {s.mean():.4f}"
                        )
                name_item.setToolTip(tooltip)
            self.variables_table.setItem(row, 0, name_item)

            # ── Col 1: ComboBox — inferred type shown inline as
            # "<type> (original)", user can override to any other type ──
            combo = ComboBox()
            combo.setFixedHeight(26)
            inferred_type = raw if raw in self._LUDWIG_TYPES else self._LUDWIG_TYPES[0]
            for ludwig_type in self._LUDWIG_TYPES:
                label = f"{ludwig_type} (original)" if ludwig_type == inferred_type else ludwig_type
                # userData= as a keyword, not positional - ComboBox.addItem's
                # 2nd positional param is icon, not userData; passing it
                # positionally silently left every item's userData as None,
                # so the findData() lookup below always returned -1 and the
                # combo showed no text at all until the user manually
                # picked something from the dropdown.
                combo.addItem(label, userData=ludwig_type)
            # Current selection: user override > Ludwig inference
            assigned = (
                self._data_model.column_types.get(col)
                if self._data_model is not None else None
            )
            selection = (
                assigned if (assigned and assigned in self._LUDWIG_TYPES)
                else inferred_type
            )
            combo.setCurrentIndex(combo.findData(selection))
            # Highlight columns where user has set a manual override. A bare
            # QComboBox falls back to the system palette (white text on this
            # table's light rows), so it always gets an explicit, themed
            # style - the override state just changes colour/weight.
            combo.setProperty("overridden", bool(assigned))
            combo.setStyleSheet(self._type_combo_qss(combo))
            # Connect change signal
            def _make_handler(c=col, cb=combo):
                def _on_type_changed(index: int) -> None:
                    try:
                        chosen = cb.itemData(index)
                        usage_log.event("Data", "select", f"Set type: {c}", str(chosen))
                        self._apply_column_type(c, chosen)
                        cb.setProperty("overridden", True)
                        cb.setStyleSheet(self._type_combo_qss(cb))
                    except Exception as exc:
                        log.warning(f"Could not set type for '{c}': {exc}")
                return _on_type_changed
            combo.currentIndexChanged.connect(_make_handler())
            self.variables_table.setCellWidget(row, 1, combo)
            self._col_type_combos[col] = combo

            # ── Col 2: concise stats (read-only, greyed) ──
            if df is not None and col in df.columns:
                series = df[col]
                n_total = len(series)
                n_missing = int(series.isna().sum())
                n_unique = int(series.nunique(dropna=True))
                n_nonnull = n_total - n_missing
                stats_text = (
                    f"non-null: {n_nonnull}  |"
                    f"  missing: {n_missing / n_total * 100:.1f}%  |"
                    f"  unique: {n_unique}"
                )
            else:
                stats_text = ""
            stats_item = QTableWidgetItem(stats_text)
            stats_item.setFlags(stats_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            stats_item.setForeground(Qt.GlobalColor.gray)
            self.variables_table.setItem(row, 2, stats_item)

        self.variables_table.resizeColumnsToContents()
        self.variables_table.setSortingEnabled(True)
        log.debug(f"Variables table populated — {len(analysis)} fields")

    def _on_header_edit_type(self, section_index: int) -> None:
        """Show a small dialog allowing the user to choose a Ludwig type for the column."""
        if self._data_model is None or self._data_model.df is None:
            return
        if section_index < 0 or section_index >= self.data_table.columnCount():
            return
        col_name = self.data_table.horizontalHeaderItem(section_index).text()

        # Build dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(t("data.txt.set_variable_type_0").format(col_name))
        dlg_layout = QVBoxLayout(dialog)

        # Combo with Ludwig types (use keys from mapping plus common fallbacks)
        types = list(self._LUDWIG_TYPE_ICONS.keys())
        # Ensure common ones first
        preferred = ['number', 'binary', 'category', 'text', 'date', 'timeseries', 'image', 'audio']
        ordered = [t for t in preferred if t in types] + [t for t in types if t not in preferred]
        type_combo = ComboBox(dialog)
        for t in ordered:
            type_combo.addItem(t)

        # Preselect assigned type or inferred type
        assigned = None
        if self._data_model and col_name in self._data_model.column_types:
            assigned = self._data_model.column_types.get(col_name)
        inferred = None
        meta = self._data_model.get_column_info(col_name)
        if meta:
            inferred = meta.get('inferred_type')

        if assigned and assigned in ordered:
            type_combo.setCurrentText(assigned)
        elif inferred and inferred in ordered:
            type_combo.setCurrentText(inferred)

        dlg_layout.addWidget(StrongBodyLabel(t("data.txt.column_0").format(col_name)))
        dlg_layout.addWidget(type_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dlg_layout.addWidget(buttons)

        def on_accept():
            chosen = type_combo.currentText()
            usage_log.event("Data", "select", f"Set type: {col_name}", chosen)
            try:
                self._apply_column_type(col_name, chosen)
                InfoBar.success(
                    title=t("data.txt.type_set"),
                    content=t("data.txt.0_set_to_1").format(col_name, chosen),
                    orient=Qt.Horizontal, isClosable=True,
                    position=InfoBarPosition.TOP, duration=3000, parent=self,
                )
            except Exception as exc:
                log.exception(f"Failed to set column type: {exc}")
                InfoBar.error(
                    title=t("data.txt.error"),
                    content=str(exc), orient=Qt.Horizontal, isClosable=True,
                    position=InfoBarPosition.TOP, duration=4000, parent=self,
                )
            dialog.accept()

        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)

        dialog.exec()

    def _on_header_context_menu(self, pos) -> None:
        """Context-menu handler for header right-click. Opens the type editor for the clicked section."""
        header = self.data_table.horizontalHeader()
        idx = header.logicalIndexAt(pos.x())
        if idx is None or idx < 0:
            return
        self._on_header_edit_type(idx)

    def _apply_column_type(self, column: str, chosen_type: str) -> None:
        """Apply the chosen Ludwig type to the DataModel, refresh UI and persist state."""
        if self._data_model is None:
            return
        # Apply override to model
        self._data_model.set_column_type(column, chosen_type)
        # Recompute metadata and refresh UI
        try:
            self._data_model._calculate_metrics()
            self._data_model._generate_column_metadata()
        except Exception:
            pass
        self._refresh_ui_from_model()
        # Persist to project state if available
        try:
            if self._project_dir is not None:
                self._data_model.save_state(self._project_dir)
        except Exception:
            log.debug("Failed to save project state after setting column type")

    def _reset_variable_types(self) -> None:
        """Clear every manual type override, reverting all columns back to
        their originally inferred type. Does not touch the dataset itself
        (values, rows, columns) - only the type overrides, so unlike
        _apply_column_type() this deliberately does NOT call
        _refresh_ui_from_model() - that would re-trigger a full Ludwig
        re-analysis in the background for no reason, since nothing about
        the active dataframe changed."""
        usage_log.event("Data", "click", "Reset Types to Inferred button")
        if self._data_model is None:
            return
        self._data_model.reset_column_types()
        try:
            self._data_model._calculate_metrics()
            self._data_model._generate_column_metadata()
        except Exception:
            pass
        if self._last_variable_analysis is not None:
            self._on_variable_analysis_ready(self._last_variable_analysis)
        try:
            if self._project_dir is not None:
                self._data_model.save_state(self._project_dir)
        except Exception:
            log.debug("Failed to save project state after resetting column types")

    # ── Selection mode (auto-switched by header clicks) ────────────────
    def _set_selection_mode(self, mode: str):
        """Switch selectionBehavior based on which header the user pressed."""
        if self._selection_mode == mode:
            return
        self._selection_mode = mode
        if mode == "columns":
            self.data_table.setSelectionBehavior(
                QAbstractItemView.SelectionBehavior.SelectColumns
            )
        else:
            self.data_table.setSelectionBehavior(
                QAbstractItemView.SelectionBehavior.SelectRows
            )

    # ── Single remove action ───────────────────────────────────────────
    def _remove_selected(self):
        """Remove selected columns or rows depending on current selection mode."""
        usage_log.event("Data", "click", "Remove Selected button", self._selection_mode)
        if self._selection_mode == "columns":
            selected = self.data_table.selectionModel().selectedColumns()
            if not selected:
                InfoBar.warning(
                    title=t("data.txt.nothing_selected"),
                    content=t("data.txt.click_a_column_header_to_select"),
                    orient=Qt.Horizontal, isClosable=True,
                    position=InfoBarPosition.TOP, duration=3000, parent=self,
                )
                return
            cols_added = []
            for index in selected:
                col_idx = index.column()
                col_name = self.data_table.horizontalHeaderItem(col_idx).text()
                if col_name not in self._removed_columns:
                    self._removed_columns.append(col_name)
                # Persist exclusion to DataModel so other pages see the change
                if self._data_model is not None:
                    if col_name not in self._data_model.excluded_columns:
                        self._data_model.excluded_columns.add(col_name)
                        cols_added.append(col_name)
                self.data_table.setColumnHidden(col_idx, True)
            if cols_added:
                # Recompute metadata and refresh UI from model
                try:
                    self._data_model._calculate_metrics()
                    self._data_model._generate_column_metadata()
                except Exception:
                    pass
                self._refresh_ui_from_model()
            log.info(f"Hidden columns: {self._removed_columns}")
        else:
            selected = self.data_table.selectionModel().selectedRows()
            if not selected:
                InfoBar.warning(
                    title=t("data.txt.nothing_selected"),
                    content=t("data.txt.click_a_row_number_to_select"),
                    orient=Qt.Horizontal, isClosable=True,
                    position=InfoBarPosition.TOP, duration=3000, parent=self,
                )
                return
            rows_added = []
            for index in selected:
                visual_row = index.row()
                self.data_table.setRowHidden(visual_row, True)
                if visual_row < len(self._preview_row_map):
                    df_idx = self._preview_row_map[visual_row]
                    if df_idx not in self._removed_row_indices:
                        self._removed_row_indices.add(df_idx)
                    if self._data_model is not None and df_idx not in self._data_model.excluded_rows:
                        self._data_model.excluded_rows.add(df_idx)
                        rows_added.append(df_idx)
            if rows_added:
                try:
                    self._data_model._calculate_metrics()
                    self._data_model._generate_column_metadata()
                except Exception:
                    pass
                self._refresh_ui_from_model()
            log.info(f"Hidden row indices: {self._removed_row_indices}")

        self._update_removed_label()
        self._restore_col_btn.setEnabled(True)
        # Broadcast the updated data model so other pages update
        try:
            self.data_loaded.emit()
        except Exception:
            pass
        # Persist project state after user removed columns/rows
        try:
            if self._data_model is not None and self._project_dir is not None:
                self._data_model.save_state(self._project_dir)
        except Exception:
            log.debug("Failed to save project state after remove_selected")

    # ── Restore all ────────────────────────────────────────────────────
    def _restore_all(self):
        """Show all previously hidden columns and rows."""
        usage_log.event("Data", "click", "Restore All button")
        # Clear visual hiding
        for col_idx in range(self.data_table.columnCount()):
            self.data_table.setColumnHidden(col_idx, False)
        for row_idx in range(self.data_table.rowCount()):
            self.data_table.setRowHidden(row_idx, False)

        # Clear removal state
        self._removed_columns.clear()
        self._removed_row_indices.clear()
        self._removed_info_lbl.setText("")
        self._restore_col_btn.setEnabled(False)

        # Clear exclusions in the DataModel and refresh UI
        if self._data_model is not None:
            try:
                self._data_model.excluded_columns.clear()
                self._data_model.excluded_rows.clear()
                self._data_model._calculate_metrics()
                self._data_model._generate_column_metadata()
            except Exception:
                pass
            self._refresh_ui_from_model()

        log.info("All columns and rows restored")
        # persist state after restore
        try:
            if self._data_model is not None and self._project_dir is not None:
                self._data_model.save_state(self._project_dir)
        except Exception:
            log.debug("Failed to save project state after restore_all")

    def _on_view_changes(self) -> None:
        """Show the record of every change made to the dataset (also saved
        next to it as <dataset>.changes.json)."""
        usage_log.event("Data", "click", "View Data Changes button")
        dm = self._data_model
        if dm is None or dm.df is None:
            InfoBar.warning(
                title=t("data.txt.no_dataset"), content=t("data.txt.load_a_dataset_first_to_see_its_changes"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=3000, parent=self,
            )
            return
        from hamelin.core.dataset_changes import build_record, changes_path, save_record
        if self._project_dir is not None:
            save_record(dm, self._project_dir)
        where = (changes_path(self._project_dir, dm.filepath) if self._project_dir and dm.filepath else None)
        note = t("data.txt.changes_note").format(where if where else "—")
        show_config_dialog(self.window(), t("data.txt.changes_title"), build_record(dm), note)

    def _remove_duplicates(self) -> None:
        """Hide every duplicate row (keeping the first occurrence of each),
        same rows the Data Summary's "duplicate rows detected" warning
        counts. Reuses the same hide-don't-delete mechanism as Remove
        Selected/Restore All, so it stays reversible and consistent with
        the rest of the row-exclusion state (Table 1, Training, exports)."""
        usage_log.event("Data", "click", "Remove Duplicates button")
        if self._data_model is None or self._data_model.df is None:
            return

        df = self._data_model.df
        dup_indices = [
            idx for idx in df.index[df.duplicated(keep="first")]
            if idx not in self._removed_row_indices
        ]
        if not dup_indices:
            InfoBar.success(
                title=t("data.txt.no_duplicates"),
                content=t("data.txt.no_duplicate_rows_found"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=3000, parent=self,
            )
            return

        self._data_model._change_reason = "duplicate rows (first occurrence kept)"
        row_of_index = {df_idx: i for i, df_idx in enumerate(self._preview_row_map)}
        for df_idx in dup_indices:
            self._removed_row_indices.add(df_idx)
            self._data_model.excluded_rows.add(df_idx)
            visual_row = row_of_index.get(df_idx)
            if visual_row is not None:
                self.data_table.setRowHidden(visual_row, True)

        try:
            self._data_model._calculate_metrics()
            self._data_model._generate_column_metadata()
        except Exception:
            pass
        self._refresh_ui_from_model()
        self._update_removed_label()
        self._restore_col_btn.setEnabled(True)

        InfoBar.success(
            title=t("data.txt.duplicates_removed"),
            content=t("data.txt.0_duplicate_row_s_hidden").format(len(dup_indices)),
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=4000, parent=self,
        )
        log.info(f"Removed {len(dup_indices)} duplicate rows: {dup_indices}")
        usage_log.event("Data", "deleted", "Duplicate rows", f"{len(dup_indices)} row(s)")

        try:
            self.data_loaded.emit()
        except Exception:
            pass
        try:
            if self._data_model is not None and self._project_dir is not None:
                self._data_model.save_state(self._project_dir)
        except Exception:
            log.debug("Failed to save project state after remove_duplicates")

    def _update_removed_label(self):
        """Refresh the info label showing hidden counts."""
        parts = []
        if self._removed_columns:
            parts.append(f"{len(self._removed_columns)} col(s) hidden")
        if self._removed_row_indices:
            parts.append(f"{len(self._removed_row_indices)} row(s) hidden")
        self._removed_info_lbl.setText(",  ".join(parts))

    def _refresh_ui_from_model(self) -> None:
        """Refresh the preview table and metric cards using DataModel.get_active_df()."""
        if self._data_model is None or self._data_model.df is None:
            return

        import pandas as pd

        df = self._data_model.get_active_df()

        # Update metric cards
        self._rows_lbl.setText(str(len(df)))
        self._cols_lbl.setText(str(len(df.columns)))

        total_cells = len(df) * (len(df.columns) if df.columns is not None else 0)
        total_missing = int(df.isnull().sum().sum()) if not df.empty else 0
        missing_pct = (total_missing / total_cells * 100) if total_cells > 0 else 0
        self._missing_lbl.setText(f"{missing_pct:.1f}%")

        mem_bytes = df.memory_usage(deep=True).sum()
        if mem_bytes < 1024:
            mem_str = f"{mem_bytes} B"
        elif mem_bytes < 1024 * 1024:
            mem_str = f"{mem_bytes / 1024:.1f} KB"
        else:
            mem_str = f"{mem_bytes / 1024 / 1024:.1f} MB"
        self._memory_lbl.setText(mem_str)

        # Repopulate preview table
        preview = df.copy()
        self._preview_row_map = list(preview.index)
        self._clear_preview_placeholder()
        self.data_table.setRowCount(len(preview))
        self.data_table.setColumnCount(len(preview.columns))
        self.data_table.setHorizontalHeaderLabels(list(preview.columns))

        # Pre-build display DataFrame
        display_df = preview.copy()
        for col in display_df.columns:
            if pd.api.types.is_datetime64_any_dtype(display_df[col]):
                display_df[col] = display_df[col].dt.strftime("%Y-%m-%d").fillna("")
            else:
                display_df[col] = display_df[col].fillna("").astype(str).replace("nan", "")

        self._fill_preview_table(display_df)
        self._size_columns_to_headers(self.data_table)

        # Relaunch variable analyzer for the active df
        self.variables_table.setVisible(False)
        self.variables_table.setRowCount(0)
        self._col_type_combos.clear()
        self._var_progress.setVisible(True)
        self._var_progress.start()
        self._var_status_lbl.setVisible(True)
        self._start_analyzer_worker(df)

    # File format choices for _export_data(), keyed by the export format
    # combo's text: (default filename, file dialog filter).
    _EXPORT_FORMATS = {
        "CSV": ("cleaned_data.csv", "CSV files (*.csv);;All files (*.*)"),
        "Excel (.xlsx)": ("cleaned_data.xlsx", "Excel files (*.xlsx);;All files (*.*)"),
        "Word (.docx)": ("cleaned_data.doc", "Word files (*.doc);;All files (*.*)"),
    }

    def _export_data(self):
        """Export the dataset, excluding any columns the user has hidden,
        in whichever format is selected in the export format dropdown."""
        usage_log.event("Data", "click", "Export button", self._export_format_combo.currentText())
        if self._data_model is None or self._data_model.df is None:
            InfoBar.warning(
                title=t("data.txt.no_data"),
                content=t("data.txt.load_a_dataset_first"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=3000, parent=self,
            )
            return

        fmt = self._export_format_combo.currentText()
        default_name, file_filter = self._EXPORT_FORMATS.get(fmt, self._EXPORT_FORMATS["CSV"])
        path, _ = QFileDialog.getSaveFileName(
            self.window(), t("data.btn.export"),
            default_export_path(self._project_dir, "tables", default_name), file_filter,
        )
        if not path:
            return

        df = self._data_model.df
        df_export = df.drop(
            columns=[c for c in self._removed_columns if c in df.columns],
            errors="ignore",
        )
        rows_to_drop = [i for i in self._removed_row_indices if i in df_export.index]
        if rows_to_drop:
            df_export = df_export.drop(index=rows_to_drop, errors="ignore")

        try:
            if fmt == "Excel (.xlsx)":
                df_export.to_excel(path, index=False)
            elif fmt == "Word (.docx)":
                # No python-docx dependency in this venv - write an HTML
                # table instead. Word opens .doc files containing HTML
                # just fine (the classic "Web Page, Filtered" trick), so
                # this needs no new dependency. Not a true OOXML .docx -
                # ask before adding python-docx if that's ever needed.
                html = df_export.to_html(index=False, border=1)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(html)
            else:
                df_export.to_csv(path, index=False)
        except Exception as exc:
            InfoBar.error(
                title=t("data.txt.export_failed"),
                content=str(exc),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=6000, parent=self,
            )
            log.error(f"Dataset export failed ({fmt}): {exc}")
            return

        removed_note = (
            f" ({len(self._removed_columns)} column(s) excluded)"
            if self._removed_columns else ""
        )
        InfoBar.success(
            title=t("data.txt.exported"),
            content=t("data.txt.saved_0_columns_to_1_2").format(len(df_export.columns), path, removed_note),
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=4000, parent=self,
        )
        log.info(f"Exported {len(df_export.columns)} columns to {path}")
        usage_log.event("Data", "exported", Path(path).name, fmt)

    def _generate_quality_report(self):
        """Generate data quality report as a CSV (Excel-compatible)."""
        import pandas as pd

        usage_log.event("Data", "click", "Generate Quality Report button")
        log.info("Generating quality report")

        if self._data_model is None or self._data_model.df is None:
            InfoBar.warning(
                title=t("data.txt.no_dataset_loaded"),
                content=t("data.txt.please_load_a_dataset_before_generating"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self.window(),
            t("data.txt.save_quality_report"),
            default_export_path(self._project_dir, "reports", "quality_report.csv"),
            t("data.txt.csv_files_csv_all_files"),
        )
        if not path:
            return

        df = self._data_model.df
        rows = []
        for col in df.columns:
            series = df[col]
            n_total = len(series)
            n_missing = int(series.isna().sum())
            pct_missing = round(n_missing / n_total * 100, 2) if n_total else 0.0
            n_unique = int(series.nunique(dropna=True))
            col_type = str(series.dtype)
            if pd.api.types.is_numeric_dtype(series):
                col_min = round(float(series.min()), 4) if not series.dropna().empty else ""
                col_max = round(float(series.max()), 4) if not series.dropna().empty else ""
                col_mean = round(float(series.mean()), 4) if not series.dropna().empty else ""
            else:
                col_min = col_max = col_mean = ""
            rows.append({
                "Column": col,
                "Type": col_type,
                "Non-Null Count": n_total - n_missing,
                "Missing Count": n_missing,
                "Missing %": pct_missing,
                "Unique Values": n_unique,
                "Min": col_min,
                "Max": col_max,
                "Mean": col_mean,
            })

        report_df = pd.DataFrame(rows)
        report_df.to_csv(path, index=False, encoding="utf-8-sig")  # utf-8-sig for Excel compat

        InfoBar.success(
            title=t("data.txt.report_saved"),
            content=t("data.txt.quality_report_with_0_variables_saved").format(len(rows), path),
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=5000, parent=self,
        )
        log.info(f"Quality report exported: {len(rows)} columns to {path}")
        usage_log.event("Data", "saved", "Quality Report", Path(path).name)

    def _export_summary(self):
        """Export the rendered dataset summary to a file (.txt or .md)."""
        usage_log.event("Data", "click", "Export Data Summary button")
        if self._summary_label is None or not self._summary_card.isVisible():
            InfoBar.warning(
                title=t("data.txt.no_summary"),
                content=t("data.txt.load_a_dataset_to_generate_the"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=3000, parent=self,
            )
            return
        path, _ = QFileDialog.getSaveFileName(
            self.window(), t("data.txt.export_summary"),
            default_export_path(self._project_dir, "reports", "dataset_summary.txt"), t("data.txt.text_files_txt_markdown_md_all")
        )
        if not path:
            return
        try:
            text = self._summary_label.text()
            Path(path).write_text(text, encoding='utf-8')
            InfoBar.success(
                title=t("data.txt.summary_exported"),
                content=t("data.txt.summary_saved_to_0").format(Path(path).name),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=3000, parent=self,
            )
            log.info(f"Summary exported: {path}")
            usage_log.event("Data", "saved", "Data Summary", Path(path).name)
        except Exception as exc:
            log.exception(f"Failed to export summary: {exc}")
            InfoBar.error(
                title=t("data.txt.export_failed"),
                content=str(exc), orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=6000, parent=self,
            )

    # ── Outlier exclusion ─────────────────────────────────────────────

    def _exclude_outliers(self):
        """Mark rows with any numeric value >3 SD as excluded in the DataModel."""
        usage_log.event("Data", "click", "Exclude Outliers button")
        if self._data_model is None:
            return
        n = self._data_model.exclude_outliers(std_threshold=3.0)
        total = len(self._data_model.excluded_rows)
        if n == 0 and total == 0:
            InfoBar.warning(
                title=t("data.txt.no_outliers_found"),
                content=t("data.txt.no_rows_exceed_3_sd_threshold"),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
            return
        if n == 0:
            InfoBar.info(
                title=t("data.txt.no_new_outliers"),
                content=t("data.txt.0_row_s_already_excluded_use").format(total),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=4000, parent=self,
            )
        else:
            InfoBar.success(
                title=t("data.txt.outliers_excluded"),
                content=t("data.txt.0_row_s_newly_excluded_1").format(n, total),
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=5000, parent=self,
            )
        self._update_outliers_label()
        if self._restore_outliers_btn is not None:
            self._restore_outliers_btn.setEnabled(total > 0)
        # persist state after excluding outliers
        try:
            if self._data_model is not None and self._project_dir is not None:
                self._data_model.save_state(self._project_dir)
        except Exception:
            log.debug("Failed to save project state after exclude_outliers")

    def _restore_excluded_rows(self):
        """Clear all outlier exclusions in the DataModel."""
        usage_log.event("Data", "click", "Restore Excluded button")
        if self._data_model is None:
            return
        self._data_model.restore_excluded_rows()
        self._update_outliers_label()
        if self._restore_outliers_btn is not None:
            self._restore_outliers_btn.setEnabled(False)
        InfoBar.success(
            title=t("data.txt.exclusions_cleared"),
            content=t("data.txt.all_rows_restored_for_analysis"),
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=3000, parent=self,
        )
        # persist state after restoring excluded rows
        try:
            if self._data_model is not None and self._project_dir is not None:
                self._data_model.save_state(self._project_dir)
        except Exception:
            log.debug("Failed to save project state after restore_excluded_rows")

    def _update_outliers_label(self):
        """Refresh the outliers count label."""
        if self._outliers_lbl is None:
            return
        if self._data_model is None or not self._data_model.excluded_rows:
            self._outliers_lbl.setText("")
        else:
            n = len(self._data_model.excluded_rows)
            self._outliers_lbl.setText(t("data.txt.0_row_s_excluded_as_outliers").format(n))

    # ── Dataset summary generation ───────────────────────────────────
    def _format_bytes(self, nbytes: int) -> str:
        if nbytes < 1024:
            return f"{nbytes} B"
        if nbytes < 1024 * 1024:
            return f"{nbytes / 1024:.2f} KB"
        return f"{nbytes / 1024 / 1024:.2f} MB"

    def _render_missingness_plot(self, missing_series, top_n: int = 10):
        """Render a horizontal bar plot of top-N variables by missingness and set it to the QLabel."""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import io
            from PySide6.QtGui import QPixmap

            if missing_series is None or missing_series.empty:
                self._missing_fig_label.setVisible(False)
                return

            df_missing = missing_series[missing_series > 0]
            if df_missing.empty:
                self._missing_fig_label.setVisible(False)
                return

            df_plot = (df_missing / (self._data_model.n_rows if self._data_model else 1) * 100).sort_values(ascending=True).tail(top_n)
            if df_plot.empty:
                self._missing_fig_label.setVisible(False)
                return

            from hamelin.view.widgets.theme_colors import style_figure

            fig, ax = plt.subplots(figsize=(6, max(2, 0.25 * len(df_plot))))
            ax.barh(df_plot.index.astype(str), df_plot.values, color='#D13438')
            ax.set_xlabel('Missing (%)')
            ax.set_title('Top variables by missingness')
            ax.grid(axis='x', linestyle='--', alpha=0.4)
            # Saved as a transparent PNG (see savefig below), so the figure
            # face colour doesn't matter here - only tick/label/title text
            # needs a colour that stays legible against whatever page
            # background (light or dark) ends up behind the transparent PNG.
            style_figure(fig, ax)
            plt.tight_layout()

            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=100, transparent=True)
            plt.close(fig)
            buf.seek(0)
            pix = QPixmap()
            pix.loadFromData(buf.getvalue())
            self._missing_fig_label.setPixmap(pix)
            self._missing_fig_label.setVisible(True)
        except Exception:
            self._missing_fig_label.setVisible(False)
            raise

    def _update_dataset_summary(self) -> None:
        """Compute and display a clinical-friendly dataset summary."""
        if self._data_model is None or self._data_model.df is None:
            self._summary_card.setVisible(False)
            return

        df = self._data_model.df
        n_rows = df.shape[0]
        n_cols = df.shape[1]

        file_name = Path(self.file_path_edit.text()).name if self.file_path_edit.text() else ""
        mem_bytes = df.memory_usage(deep=True).sum()

        # ── Variable types ──────────────────────────────────────────────────────
        numeric_cols  = df.select_dtypes(include=['number']).columns.tolist()
        cat_cols      = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
        date_cols     = df.select_dtypes(include=['datetime']).columns.tolist()
        other_cols    = [c for c in df.columns
                         if c not in numeric_cols and c not in cat_cols and c not in date_cols]

        # ── Missing data ───────────────────────────────────────────────────
        missing_series  = df.isnull().sum()
        total_missing   = int(missing_series.sum())
        total_cells     = n_rows * n_cols if n_rows and n_cols else 1
        missing_pct     = total_missing / total_cells * 100
        incomplete_vars = int((missing_series > 0).sum())
        top_missing     = missing_series[missing_series > 0].sort_values(ascending=False).head(8)

        # ── Quality scoring ─────────────────────────────────────────────
        q_score = 0
        q_items = []   # list of ("ok" | "warn" | "err", message)

        if missing_pct == 0:
            q_score += 1
            q_items.append(("ok",  "Complete dataset — no missing values found"))
        elif missing_pct < 5:
            q_score += 1
            q_items.append(("ok",  f"Low missingness ({missing_pct:.1f}%)"))
        elif missing_pct < 15:
            q_items.append(("warn", f"Moderate missingness ({missing_pct:.1f}%) — consider imputation or variable removal"))
        else:
            q_items.append(("err",  f"High missingness ({missing_pct:.1f}%) — data cleaning strongly recommended before analysis"))

        if n_rows >= 500:
            q_score += 1
            q_items.append(("ok",   f"Adequate sample size ({n_rows:,} records)"))
        elif n_rows >= 100:
            q_items.append(("warn",  f"Moderate sample size ({n_rows:,} records) — AI results may have limited generalisability"))
        else:
            q_items.append(("err",   f"Small sample size ({n_rows:,} records) — interpret AI model results with caution"))

        if numeric_cols and cat_cols:
            q_score += 1
            q_items.append(("ok",   f"Good variable mix ({len(numeric_cols)} numerical + {len(cat_cols)} categorical)"))
        elif not numeric_cols:
            q_items.append(("warn",  "No numerical variables detected — check variable types above"))
        elif not cat_cols:
            q_items.append(("warn",  "No categorical variables detected — check variable types above"))

        dup_rows = int(df.duplicated().sum())
        if dup_rows == 0:
            q_score += 1
            q_items.append(("ok",   "No duplicate records"))
        else:
            q_items.append(("warn",  f"{dup_rows} duplicate rows detected — consider removing them before training"))

        # ── Outcome candidates ──────────────────────────────────────────
        binary_cands      = []
        categorical_cands = []
        numerical_cands   = []
        for col in df.columns:
            ser = df[col].dropna()
            if ser.empty:
                continue
            n_unique = int(ser.nunique())
            if n_unique == 2:
                counts = ser.value_counts(normalize=True).mul(100)
                binary_cands.append((col, counts))
            elif pd.api.types.is_numeric_dtype(ser):
                has_decimals = pd.api.types.is_float_dtype(ser) and (ser % 1 != 0).any()
                if has_decimals or n_unique > max(10, len(ser) * 0.3):
                    numerical_cands.append(col)
                elif 3 <= n_unique <= 15:
                    categorical_cands.append((col, n_unique))
            elif 3 <= n_unique <= 15:
                categorical_cands.append((col, n_unique))

        # ── Build output ────────────────────────────────────────────────
        W     = 72
        SEP   = "─" * W
        SEP2  = "═" * W
        OK    = "✔"
        WARN  = "⚠"
        ERR   = "✘"
        DOT   = "·"

        L = []

        def add(text=""): L.append(text)

        add(SEP2)
        add("  Data Summary")
        add(SEP2)
        add()
        if file_name:
            add(f"  File    : {file_name}")
        add(f"  Records : {n_rows:,} patients / observations")
        add(f"  Variables: {n_cols}")
        add(f"  Memory  : {self._format_bytes(mem_bytes)}")
        add()

        add(SEP)
        add("  VARIABLE TYPES")
        add(SEP)
        if numeric_cols:
            add(f"  {DOT} {len(numeric_cols):>3}  numerical    — measurements, counts, scores")
            add(f"       e.g. {', '.join(numeric_cols[:4])}")
        if cat_cols:
            add(f"  {DOT} {len(cat_cols):>3}  categorical  — groups, labels, yes/no choices")
            add(f"       e.g. {', '.join(cat_cols[:4])}")
        if date_cols:
            add(f"  {DOT} {len(date_cols):>3}  date/time    — timestamps, event dates")
        if other_cols:
            add(f"  {DOT} {len(other_cols):>3}  other        — text, complex types")
        add()

        add(SEP)
        add("  DATA COMPLETENESS")
        add(SEP)
        if total_missing == 0:
            add(f"  {OK}  Complete — all {n_rows:,} records have values for every variable.")
        else:
            filled_pct = 100 - missing_pct
            add(f"  {WARN}  {total_missing:,} missing values detected  ({missing_pct:.1f}% of all data)")
            add(f"  {DOT}  Data completeness: {filled_pct:.1f}%")
            add(f"  {DOT}  {incomplete_vars} variable(s) have at least one missing value out of {n_cols}")
            add()
            add("  Variables most affected by missing data:")
            for col, miss in top_missing.items():
                pct_m = miss / n_rows * 100 if n_rows else 0.0
                bar   = "█" * min(int(pct_m / 5), 20)
                add(f"    {DOT} {col:<30}  {pct_m:5.1f}%  {bar}")
        add()

        add(SEP)
        add("  NUMERICAL VARIABLES — QUICK STATISTICS")
        add(SEP)
        if numeric_cols:
            add(f"  {'Variable':<30}  {'Avg':>8}  {'Min':>8}  {'Max':>8}")
            add(f"  {'─'*30}  {'─'*8}  {'─'*8}  {'─'*8}")
            for col in numeric_cols:
                s = df[col].dropna()
                if s.empty:
                    continue
                add(f"  {col:<30}  {s.mean():>8.2f}  {s.min():>8.2f}  {s.max():>8.2f}")
        else:
            add(f"  {WARN}  No numerical variables found.")
        add()

        add(SEP)
        add("  POSSIBLE OUTCOME VARIABLES FOR AI MODELS")
        add(SEP)
        add("  These variables could be chosen as the target to predict.")
        add()
        if binary_cands:
            add("  Binary outcomes  (yes / no, event / no-event):")
            for col, counts in sorted(binary_cands, key=lambda x: x[0]):
                vals = "  |  ".join([f"{v}: {p:.1f}%" for v, p in counts.items()])
                add(f"    {DOT} {col}   ({vals})")
        if categorical_cands:
            add("  Categorical outcomes  (2․13 distinct groups):")
            for col, n_u in sorted(categorical_cands, key=lambda x: x[1]):
                add(f"    {DOT} {col}   ({n_u} categories)")
        if numerical_cands:
            add("  Continuous outcomes  (regression — numerical):")
            for col in numerical_cands:
                s = df[col].dropna()
                add(f"    {DOT} {col}   range [{s.min():.2f} – {s.max():.2f}]")
        if not binary_cands and not categorical_cands and not numerical_cands:
            add(f"  {WARN}  No clear outcome variable detected automatically.")
            add("      Choose a target manually in the Training tab.")
        add()

        add(SEP)
        add("  OVERALL DATA QUALITY")
        add(SEP)
        for kind, msg in q_items:
            sym = OK if kind == "ok" else (WARN if kind == "warn" else ERR)
            add(f"  {sym}  {msg}")
        add()
        quality_label = (
            "Excellent"       if q_score >= 4 else
            "Good"            if q_score == 3 else
            "Acceptable"      if q_score == 2 else
            "Needs attention"
        )
        add(f"  Overall quality: {quality_label}  ({q_score}/4 checks passed)")
        add()

        add(SEP)
        add("  RECOMMENDATION")
        add(SEP)
        if q_score >= 4:
            add("  This dataset is in excellent shape.")
            add("  You can proceed to Table 1 generation and AI model training.")
        elif q_score == 3:
            add("  Good dataset. Review the warnings above before training.")
            add("  Inspect variables with missing values and decide whether to")
            add("  impute them or remove those variables.")
        elif q_score == 2:
            add("  Some issues detected. Address missing data and duplicates")
            add("  before training to obtain reliable results.")
        else:
            add("  Significant data quality issues found. Recommended steps:")
            add("    1. Remove or impute variables with >20% missing values.")
            add("    2. Check and remove duplicate records.")
            add("    3. Ensure sample size is large enough for your analysis.")
        add()
        add(SEP2)

        text = "\n".join(L)
        self._summary_label.setText(text)
        self._summary_card.setVisible(True)

        # Auto-save summary to the project's reports folder if a project is
        # active (it is a report, not a dataset: not in data/)
        try:
            if self._project_dir and file_name:
                proj_reports_dir = (Path(self._project_dir) / "results" / "reports").resolve()
                proj_reports_dir.mkdir(parents=True, exist_ok=True)
                summary_fname = f"{Path(file_name).stem}_summary.txt"
                summary_path = proj_reports_dir / summary_fname
                summary_path.write_text(text, encoding="utf-8")
        except Exception as exc:
            log.exception(f"Failed to save dataset summary: {exc}")
