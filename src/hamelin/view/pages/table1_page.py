"""
Table 1 Page
~~~~~~~~~~~~

Table 1 (baseline characteristics) generation - embedded as a section
inside DataPage rather than its own top-level nav page, since it's just
another view over the same loaded dataset.
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QTextBrowser,
    QListWidget, QListWidgetItem, QAbstractItemView,
    QCheckBox,
)
from PySide6.QtCore import Qt
from qfluentwidgets import (
    TitleLabel, StrongBodyLabel, BodyLabel, CardWidget,
    PushButton, PrimaryPushButton, ComboBox,
    FluentIcon, InfoBar, InfoBarPosition
)

from hamelin.utils.logger import log
from hamelin.utils.usage_logger import usage_log
from hamelin.utils.export_paths import default_export_path
from hamelin.model.data_model import DataModel
from hamelin.analytics.table1_generator import Table1Generator
from hamelin.view.widgets import HelpButton, attach_help_popup
from hamelin.view.widgets.theme_colors import bind_style, colors, isDarkTheme, list_item_qss, on_theme_changed, scrollbar_qss
from hamelin.i18n import t


class Table1Page(QWidget):
    """
    Table 1 generation section, embedded inside DataPage.

    Workflow:
    1. Receives the DataModel already loaded by DataPage (set_data_model()).
    2. Columns are listed; user can deselect variables to exclude.
    3. Optionally picks a grouping variable.
    4. Clicks Generate → Table 1 is shown as styled HTML.
    5. Exports to HTML or CSV.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Table1Page")
        self._data_model: DataModel | None = None
        self._generator: Table1Generator | None = None
        self._table_df = None
        self._project_metadata = None
        self._project_dir = None
        # column -> its row's checkbox in _var_list (custom row widgets,
        # not native checkable QListWidgetItems - needed to show a
        # recommendation hint on the right side of each row)
        self._var_checkboxes: dict = {}
        # (label, "exclude" | "grouping") for each row's recommendation
        # hint - re-themed alongside the checkboxes, see _apply_checkbox_theme
        self._var_hints: list = []
        self._rec_exclude: list = []
        self._rec_exclude_reasons: dict = {}
        self._rec_grouping: str | None = None
        self._rec_grouping_reason: str = ''
        log.debug("Initializing Table 1 Page")
        self._init_ui()
        on_theme_changed(self._apply_checkbox_theme)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _init_ui(self):
        """Build the user interface. No own scroll area / page title -
        this widget is embedded inside DataPage's own scrolling layout,
        under a "Table 1" section header DataPage provides."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # ── Select Variables for Table 1 (variable list + settings,
        # merged into one card - recommendations are shown inline on the
        # right of each row instead of a separate block) ────────────────
        vars_card = CardWidget()
        vars_layout = QVBoxLayout(vars_card)
        vars_layout.setContentsMargins(20, 20, 20, 20)
        vars_layout.setSpacing(10)

        vars_header = QHBoxLayout()
        vars_title = StrongBodyLabel(t("table1.txt.select_variables_for_table_1"))
        vars_help = HelpButton(
            t("table1.txt.tick_which_variables_to_include_in")
        )
        vars_header.addWidget(vars_title)
        vars_header.addWidget(vars_help)
        vars_header.addStretch()
        vars_layout.addLayout(vars_header)

        self._var_list = QListWidget()
        self._var_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self._var_list.setMaximumHeight(220)
        self._var_list.addItem("— load a dataset to see variables —")
        self._var_list.setEnabled(False)
        # Alternating row shades match style_table_widget's zebra striping
        # (#FFFFFF / #F7F7F7), same rounded scroll bar as the rest of the
        # app. Each row is a custom widget (see set_data_model below), not
        # plain item text - a bare QWidget has no background of its own,
        # so the item's own (alternating) background still shows through.
        self._var_list.setAlternatingRowColors(True)
        on_theme_changed(
            lambda: self._var_list.setStyleSheet(list_item_qss() + scrollbar_qss())
        )
        vars_layout.addWidget(self._var_list)

        sel_row = QHBoxLayout()
        self._select_all_btn = PushButton(t("training.btn.select.all"), self)
        self._select_all_btn.clicked.connect(self._select_all_vars)
        self._select_all_btn.setEnabled(False)
        self._select_none_btn = PushButton(t("training.btn.deselect.all"), self)
        self._select_none_btn.clicked.connect(self._select_none_vars)
        self._select_none_btn.setEnabled(False)
        self._apply_rec_btn = PushButton(t("table1.txt.apply_all_recommendations"), self)
        self._apply_rec_btn.setIcon(FluentIcon.ACCEPT)
        self._apply_rec_btn.clicked.connect(self._apply_recommendations)
        self._apply_rec_btn.setEnabled(False)
        sel_row.addWidget(self._select_all_btn)
        sel_row.addWidget(self._select_none_btn)
        sel_row.addWidget(self._apply_rec_btn)
        sel_row.addStretch()
        vars_layout.addLayout(sel_row)

        vars_layout.addSpacing(6)
        settings_header = QHBoxLayout()
        settings_title = StrongBodyLabel(t("table1.txt.table_settings"))
        settings_help = HelpButton(
            t("table1.txt.grouping_variable_pick_a_categorical_col")
        )
        settings_header.addWidget(settings_title)
        settings_header.addWidget(settings_help)
        settings_header.addStretch()
        vars_layout.addLayout(settings_header)

        group_row = QHBoxLayout()
        group_label = BodyLabel(t("table1.txt.grouping_variable"))
        group_label.setFixedWidth(160)
        self._group_combo = ComboBox()
        self._group_combo.addItem("None")
        group_row.addWidget(group_label)
        group_row.addWidget(self._group_combo)
        group_row.addStretch()
        vars_layout.addLayout(group_row)

        config_info = BodyLabel(
            t("table1.txt.select_a_categorical_variable_to_compare")
        )
        bind_style(config_info, lambda c: f"color: {c.text_secondary}; font-size: 12px;")
        config_info.setWordWrap(True)
        vars_layout.addWidget(config_info)

        # Missing data handling
        missing_row = QHBoxLayout()
        missing_label = BodyLabel(t("table1.txt.missing_data"))
        missing_label.setFixedWidth(160)
        self._missing_combo = ComboBox()
        self._missing_combo.addItem("Keep all patients (show missing values)")
        self._missing_combo.addItem("Drop patients with any missing value")
        missing_row.addWidget(missing_label)
        missing_row.addWidget(self._missing_combo)
        missing_row.addStretch()
        vars_layout.addLayout(missing_row)

        # Show p-values
        self._pvalue_check = QCheckBox("Show p-values (needs 'Compare groups by')")
        self._pvalue_check.setChecked(True)
        vars_layout.addWidget(self._pvalue_check)
        self._group_combo.currentIndexChanged.connect(self._update_pvalue_availability)
        self._update_pvalue_availability()

        layout.addWidget(vars_card)

        # ── Action Buttons ─────────────────────────────────────────────
        button_row = QHBoxLayout()
        button_row.addStretch()

        self._generate_btn = PrimaryPushButton(t("table1.btn.generate"), self)
        self._generate_btn.setIcon(FluentIcon.PLAY)
        self._generate_btn.clicked.connect(self._generate_table)
        self._generate_btn.setEnabled(False)
        button_row.addWidget(self._generate_btn)

        # Format picker + Export button grouped tightly together (same
        # pattern as the dataset export control in DataPage) instead of
        # two separate "Export HTML" / "Export CSV" buttons.
        export_group = QHBoxLayout()
        export_group.setSpacing(0)

        self._export_format_combo = ComboBox()
        self._export_format_combo.addItems(["CSV", "Excel (.xlsx)", "Word (.docx)"])
        attach_help_popup(self._export_format_combo, t("data.txt.file_format_used_by_the_export"))
        export_group.addWidget(self._export_format_combo)

        self._export_btn = PushButton(t("table1.btn.export"), self)
        self._export_btn.setIcon(FluentIcon.SAVE)
        self._export_btn.clicked.connect(self._export_table1)
        self._export_btn.setEnabled(False)
        export_group.addWidget(self._export_btn)

        button_row.addLayout(export_group)
        layout.addLayout(button_row)

        # ── Results ────────────────────────────────────────────────────
        results_card = CardWidget()
        results_layout = QVBoxLayout(results_card)
        results_layout.setContentsMargins(20, 20, 20, 20)
        results_layout.setSpacing(10)

        results_title = StrongBodyLabel(t("table1.heading.results"))
        results_layout.addWidget(results_title)

        self._results_browser = QTextBrowser()
        self._results_browser.setMinimumHeight(300)
        self._results_browser.setPlaceholderText(
            t("table1.placeholder.results")
        )
        # A bare QTextBrowser has no styling of its own, so it falls back
        # to the native platform palette instead of Hamelin's theme - on a
        # system whose native palette is dark, that made its text
        # unreadable (same root cause as every other plain-Qt-widget case
        # already fixed elsewhere in this app - see theme_colors.py).
        on_theme_changed(lambda: self._results_browser.setStyleSheet(
            f"QTextBrowser {{ background: {colors().card_background}; "
            f"color: {colors().text_primary}; border: none; }}"
        ))
        # The HTML itself is generated once (see _render_results) with
        # colours baked in at that point, so a later theme switch would
        # otherwise leave an already-generated table's colours stale.
        on_theme_changed(self._render_results)
        results_layout.addWidget(self._results_browser)

        layout.addWidget(results_card)
        layout.addStretch()

        log.debug("Table 1 Page initialized successfully")

    def _apply_checkbox_theme(self) -> None:
        """Give each variable-row QCheckBox an explicit, readable text
        colour. A plain QCheckBox has no qfluentwidgets theming of its
        own and falls back to Qt's inherited palette - left unset, the
        label text can end up invisible against its own row. Registered
        with on_theme_changed in __init__, so this re-runs (and re-reads
        the current _var_checkboxes) on every theme change too."""
        for checkbox in self._var_checkboxes.values():
            checkbox.setStyleSheet(f"color: {colors().text_primary};")
        # Amber/blue recommendation hints need a lighter variant to stay
        # readable on a dark row background.
        dark = isDarkTheme()
        exclude_color = "#FBBF24" if dark else "#b45309"
        grouping_color = "#60A5FA" if dark else "#2563eb"
        for hint, kind in self._var_hints:
            color = exclude_color if kind == "exclude" else grouping_color
            hint.setStyleSheet(f"color: {color}; font-size: 11px; font-style: italic;")

    def set_project_dir(self, project_dir) -> None:
        """Where Export opens by default (results/tables/ of the project)."""
        self._project_dir = project_dir

    def set_project_metadata(self, metadata) -> None:
        """Receive the current project's ProjectMetadata (see MainWindow),
        so the next Table 1 export can carry study name/protocol/
        objectives/ethics approval as a header instead of the exported
        file being anonymous - see _generate_table()."""
        self._project_metadata = metadata

    def set_data_model(self, dm: DataModel) -> None:
        """
        Receive the DataModel loaded by the parent DataPage.

        Updates the variable list and grouping combo. Called directly by
        DataPage whenever a dataset finishes loading.
        """
        self._data_model = dm

        # Compute recommendations first so each row below can show its
        # own inline hint instead of a separate recommendations block.
        self._compute_recommendations(dm)

        self._var_list.clear()
        self._var_checkboxes.clear()
        self._var_hints.clear()
        self._var_list.setEnabled(True)
        self._select_all_btn.setEnabled(True)
        self._select_none_btn.setEnabled(True)
        self._apply_rec_btn.setEnabled(True)
        for col in dm.df.columns:
            # Show inferred type as suffix, if available
            meta = dm.column_metadata.get(col, {})
            inferred = meta.get('inferred_type') or meta.get('assigned_type') or ''
            label_text = f"{col}  [{inferred}]" if inferred else col

            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(6, 2, 6, 2)

            checkbox = QCheckBox(label_text)
            checkbox.setChecked(True)
            row_layout.addWidget(checkbox)
            row_layout.addStretch()

            reason = self._rec_exclude_reasons.get(col)
            if reason:
                hint = BodyLabel(t("table1.txt.recommendation_exclude_0").format(reason))
                self._var_hints.append((hint, "exclude"))
                row_layout.addWidget(hint)
            elif col == self._rec_grouping:
                hint = BodyLabel(t("table1.txt.recommendation_grouping_variable_0").format(self._rec_grouping_reason))
                self._var_hints.append((hint, "grouping"))
                row_layout.addWidget(hint)

            item = QListWidgetItem()
            item.setSizeHint(row_widget.sizeHint())
            self._var_list.addItem(item)
            self._var_list.setItemWidget(item, row_widget)
            self._var_checkboxes[col] = checkbox

        self._apply_checkbox_theme()

        self._group_combo.clear()
        self._group_combo.addItem("None")
        for col in dm.get_categorical_columns():
            self._group_combo.addItem(col)

        self._generate_btn.setEnabled(True)
        self._export_btn.setEnabled(False)
        self._results_browser.clear()
        log.info(f"Table1Page received DataModel: {dm.n_rows}r × {dm.n_columns}c")

    # ------------------------------------------------------------------
    # Smart recommendations
    # ------------------------------------------------------------------

    # Keywords that identify non-clinical / administrative columns
    _EXCLUDE_KEYWORDS = (
        'record id', 'paciente', ' id', 'id ', 'identifier',
        'complete?', 'complete ?', 'fecha', 'date', 'hora', 'time',
        'inicio', 'fin', 'salida', 'entrada',
    )
    # Keywords that hint at an outcome / grouping column
    _OUTCOME_KEYWORDS = (
        'riesgo', 'tipo', 'outcome', 'resultado', 'grupo', 'estado',
        'complication', 'complicacion', 'lesion', 'lpp', 'clase',
        'category', 'categoria',
    )

    def _compute_recommendations(self, dm: DataModel) -> None:
        """Analyse dm.df and cache per-column recommendations - shown
        inline in the variable list (set_data_model) rather than in a
        separate block, and applied in bulk by _apply_recommendations()."""
        df = dm.df
        n = len(df)

        exclude_cols: list[str] = []
        exclude_reasons: dict[str, str] = {}
        grouping_candidate: str | None = None
        grouping_reason: str = ''
        best_score = -1

        for col in df.columns:
            col_lower = col.lower().strip()
            series = df[col]
            n_unique = series.nunique(dropna=True)
            n_null = series.isna().sum()
            dtype = series.dtype

            # ── Exclusion heuristics ───────────────────────────────────────
            # 1. Administrative name match
            if any(kw in col_lower for kw in self._EXCLUDE_KEYWORDS):
                exclude_cols.append(col)
                exclude_reasons[col] = 'administrative / identifier'
                continue
            # 2. Unique-per-row → identifier
            if n_unique >= n * 0.9 and n_unique > 10:
                exclude_cols.append(col)
                exclude_reasons[col] = 'unique per row (likely identifier)'
                continue
            # 3. Zero variance
            if n_unique <= 1:
                exclude_cols.append(col)
                exclude_reasons[col] = 'zero variance (all values equal)'
                continue
            # 4. Datetime column
            if hasattr(dtype, 'tz') or 'datetime' in str(dtype):
                exclude_cols.append(col)
                exclude_reasons[col] = 'datetime column'
                continue
            # 5. Free-text: object column with almost all unique values
            if dtype == object and n_unique > max(10, n * 0.3):
                exclude_cols.append(col)
                exclude_reasons[col] = 'free-text (too many unique values)'
                continue

            # ── Grouping candidate score ─────────────────────────────────
            if dtype == object and 2 <= n_unique <= 5:
                valid = series.dropna()
                counts = valid.value_counts()
                # Balance score: 1 = perfectly balanced, 0 = all in one group
                max_c, min_c = counts.max(), counts.min()
                balance = min_c / max_c if max_c > 0 else 0
                # Penalise high missing
                completeness = 1 - (n_null / n)
                # Bonus for clinical outcome keywords
                keyword_bonus = 2 if any(kw in col_lower for kw in self._OUTCOME_KEYWORDS) else 0
                # Prefer binary (2 groups)
                cardinality_bonus = 1 if n_unique == 2 else 0
                score = balance * 3 + completeness * 2 + keyword_bonus + cardinality_bonus
                if score > best_score:
                    best_score = score
                    grouping_candidate = col
                    grouping_reason = (
                        f"{n_unique} groups, balance {balance:.0%}, "
                        f"{completeness:.0%} complete"
                        + (' — clinical outcome keyword' if keyword_bonus else '')
                    )

        self._rec_exclude = exclude_cols
        self._rec_exclude_reasons = exclude_reasons
        self._rec_grouping = grouping_candidate
        self._rec_grouping_reason = grouping_reason
        log.debug(f"Recommendations: exclude={exclude_cols}, grouping={grouping_candidate}")

    def _apply_recommendations(self) -> None:
        """Apply computed recommendations to the UI controls."""
        usage_log.event("Table 1", "click", "Apply All Recommendations button")
        if self._data_model is None:
            return
        exclude_set = set(self._rec_exclude)
        grouping = self._rec_grouping

        # Check/uncheck variables
        for col, checkbox in self._var_checkboxes.items():
            checkbox.setChecked(col not in exclude_set)

        # Set grouping combo
        if grouping:
            idx = self._group_combo.findText(grouping)
            if idx >= 0:
                self._group_combo.setCurrentIndex(idx)

        InfoBar.success(
            title=t("table1.txt.recommendations_applied"),
            content=t("table1.txt.0_variables_excluded_grouping_set_to").format(len(exclude_set), grouping or 'None'),
            orient=Qt.Horizontal,
            isClosable=True,
            duration=4000,
            position=InfoBarPosition.TOP,
            parent=self,
        )

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _render_results(self):
        """(Re)render the results browser's HTML from self._generator's
        current result_table - its own colours (see
        Table1Generator._generate_styled_html) are read fresh from
        theme_colors on every call, so this also re-renders the already-
        generated table to match a theme switch, not just a fresh
        Generate click."""
        if self._generator is None or self._table_df is None:
            return
        try:
            html = self._generator._generate_styled_html()
        except Exception:
            # Fallback: plain DataFrame HTML
            html = self._table_df.to_html(border=1)
        self._results_browser.setHtml(html)

    def _generate_table(self):
        """Build Table1Generator, run generate(), render HTML."""
        usage_log.event("Table 1", "click", "Generate Table 1 button")
        if self._data_model is None or self._data_model.df is None:
            return

        # Collect checked variables
        checked = [col for col, cb in self._var_checkboxes.items() if cb.isChecked()]

        # Grouping variable
        group_text = self._group_combo.currentText()
        stratify_by = group_text if group_text != "None" else None

        # Remove grouping var from the variable list to avoid including it
        variables = [v for v in checked if v != stratify_by]

        try:
            df_work = self._data_model.df
            # Apply missing data handling
            if self._missing_combo.currentIndex() == 1:
                df_work = df_work.dropna(subset=variables)
                # With many checked variables that each have real (if
                # partial) missingness, requiring every one of them to be
                # non-missing on the SAME row can plausibly leave zero rows
                # - e.g. two variables each 80% missing but never missing
                # together on any given patient. Table1Generator's own
                # "dataframe cannot be empty" is accurate but doesn't say
                # why, so catch this case here with the actual cause.
                if df_work.empty:
                    InfoBar.error(
                        title=t("table1.msg.generation.error"),
                        content=(
                            t("table1.txt.no_rows_remain_after_excluding_any").format(len(variables))
                        ),
                        orient=Qt.Horizontal,
                        isClosable=True,
                        duration=8000,
                        position=InfoBarPosition.TOP,
                        parent=self,
                    )
                    return

            gen = Table1Generator(df_work)
            if self._project_metadata is not None:
                meta = self._project_metadata
                gen.set_study_info({
                    "Study": meta.name,
                    "Protocol Number": meta.protocol_number,
                    "Primary Objective": meta.primary_objective,
                    "Secondary Objectives": "; ".join(meta.secondary_objectives) or None,
                    "Ethics Committee": meta.ethics_committee,
                    "Ethics Approval Number": meta.ethics_approval_number,
                })
            # Build exclude list = all columns NOT in 'variables' + stratify_by
            all_cols = list(self._data_model.df.columns)
            checked_set = set(variables)
            excluded = [c for c in all_cols if c not in checked_set]
            if stratify_by and stratify_by not in excluded:
                excluded.append(stratify_by)
            gen.auto_detect_variables(exclude=excluded if excluded else None)

            self._table_df = gen.generate(stratify_by=stratify_by)
            self._generator = gen
        except Exception as exc:
            InfoBar.error(
                title=t("table1.msg.generation.error"),
                content=str(exc),
                orient=Qt.Horizontal,
                isClosable=True,
                duration=6000,
                position=InfoBarPosition.TOP,
                parent=self,
            )
            log.error(f"Table 1 generation failed: {exc}")
            return

        # Hide p-value column if user opted out
        if not self._pvalue_check.isChecked() and self._table_df is not None:
            if 'p-value' in self._table_df.columns:
                self._table_df = self._table_df.drop(columns=['p-value'])
                gen.result_table = self._table_df

        self._render_results()

        self._export_btn.setEnabled(True)

        n_vars = len(self._table_df)
        InfoBar.success(
            title=t("table1.txt.table_1_generated"),
            content=t("table1.txt.0_variables_processed_successfully").format(n_vars),
            orient=Qt.Horizontal,
            isClosable=True,
            duration=3000,
            position=InfoBarPosition.TOP,
            parent=self,
        )
        log.info(f"Table 1 generated: {n_vars} variables")
        table1_fields = {
            "Variables Selected": f"{len(variables)} of {len(self._var_checkboxes)}",
            "Grouping Variable": stratify_by or "",
            "Missing Data": self._missing_combo.currentText(),
            "Show p-values": self._pvalue_check.isChecked(),
        }
        for element, value in table1_fields.items():
            if value:
                usage_log.event("Table 1", "field_filled", element, str(value))
        usage_log.event("Table 1", "created", "Table 1", f"{n_vars} variables")

    # File format choices for _export_table1(), keyed by the export format
    # combo's text - same three formats as the dataset export on DataPage.
    _EXPORT_FORMATS = {
        "CSV": ("Table1.csv", "CSV files (*.csv);;All files (*.*)"),
        "Excel (.xlsx)": ("Table1.xlsx", "Excel files (*.xlsx);;All files (*.*)"),
        "Word (.docx)": ("Table1.doc", "Word files (*.doc);;All files (*.*)"),
    }

    def _export_table1(self):
        """Save the generated Table 1, in whichever format is selected
        in the export format dropdown (CSV, Excel, or Word)."""
        usage_log.event("Table 1", "click", "Export button", self._export_format_combo.currentText())
        if self._generator is None:
            return

        fmt = self._export_format_combo.currentText()
        default_name, file_filter = self._EXPORT_FORMATS.get(fmt, self._EXPORT_FORMATS["CSV"])
        path, _ = QFileDialog.getSaveFileName(
            self.window(), t("table1.btn.export"),
            default_export_path(self._project_dir, "tables", default_name), file_filter,
        )
        if not path:
            return

        try:
            if fmt == "Excel (.xlsx)":
                self._generator.export_to_excel(path)
            elif fmt == "Word (.docx)":
                # Same trick as the dataset export: Word opens a styled
                # HTML table saved as .doc just fine, no python-docx needed.
                self._generator.export_to_html(path)
            else:
                self._generator.export_to_csv(path)
            InfoBar.success(
                title=t("table1.msg.exported"),
                content=t("table1.txt.0_saved_to_1").format(fmt, path),
                orient=Qt.Horizontal,
                isClosable=True,
                duration=4000,
                position=InfoBarPosition.TOP,
                parent=self,
            )
            log.info(f"Table 1 exported to {fmt}: {path}")
            usage_log.event("Table 1", "exported", Path(path).name, fmt)
        except Exception as exc:
            InfoBar.error(
                title=t("table1.msg.export.error"),
                content=str(exc),
                orient=Qt.Horizontal,
                isClosable=True,
                duration=6000,
                position=InfoBarPosition.TOP,
                parent=self,
            )
            log.error(f"{fmt} export failed: {exc}")

    # ------------------------------------------------------------------
    # Helper slots (select-all / deselect-all)
    # ------------------------------------------------------------------

    def _select_all_vars(self):
        usage_log.event("Table 1", "click", "Select All button")
        for checkbox in self._var_checkboxes.values():
            checkbox.setChecked(True)

    def _update_pvalue_availability(self, *_args) -> None:
        """P-values compare groups, so they only make sense with a grouping variable."""
        self._pvalue_check.setEnabled(self._group_combo.currentIndex() > 0)

    def _select_none_vars(self):
        usage_log.event("Table 1", "click", "Deselect All button")
        for checkbox in self._var_checkboxes.values():
            checkbox.setChecked(False)
