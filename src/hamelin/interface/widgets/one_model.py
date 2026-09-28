from datetime import datetime

from PySide6.QtCore import Qt, QSize, QEvent
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QPlainTextEdit
)

from hamelin.interface.widgets.dropdowns import SimpleDropdown
from hamelin.interface.utils.widgets import RoundedButton, Popup, ErrorPopup, build_glossary_widget, set_asset_icon
from hamelin.interface.utils.colors import COLORS, INFO_YELLOW, INFO_YELLOW_HOVER, themed, themed_add
from hamelin.interface.utils.metrix_extractor import load_run_metrics, get_target_column
from hamelin.interface.utils.metric_labels import get_metric_info, get_metric_glossary_entries
from hamelin.interface.utils.favorites import is_favorite, toggle_favorite
from hamelin.interface.utils.notes import load_note, save_note
from hamelin.interface.utils.export import make_export_button, export_csv
from hamelin.interface.utils.bootstrap_ci import bootstrap_ci, is_supported as ci_is_supported
import hamelin.interface.utils.get_model_paths as gmp


# Output feature types get_output_feature_info() can report where "accuracy"
# (exact y_true == y_pred match) is a meaningful per-subgroup number -
# regression's continuous targets would just show ~0% for everyone.
_CLASSIFICATION_TYPES = {"binary", "category", "set"}

# Below this many patients, a subgroup's accuracy is flagged rather than
# presented as a plain number - these test sets are already small (often
# under 30 patients total), so a subgroup can easily drop to a handful.
_SMALL_SUBGROUP_N = 10


def metric_name(key):
    name = key.split("/")[-2].lower()
    return "accuracy" if name in ("acc", "accuracy") else name


def _format_trained_at(raw):
    """Ludwig's training_report 'generated_at' rendered as a plain date, or
    the raw value untouched if it isn't an ISO timestamp."""
    if not raw:
        return None
    text = str(raw)
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).strftime("%d %b %Y")
    except ValueError:
        return text


class _NotesEdit(QPlainTextEdit):
    """QPlainTextEdit that runs a callback when it loses focus, so a note is
    saved the moment the user clicks away - no explicit Save button."""

    def __init__(self, on_commit=None, parent=None):
        super().__init__(parent)
        self._on_commit = on_commit

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self._on_commit is not None:
            self._on_commit()


class VisualiseOneModel(QWidget):
    """One model's own test-set numbers, as a clean grid of cards - one
    tile per metric. Used to also offer a radar chart comparing this model
    to the average of whichever other models happened to be selected, but
    that comparison belongs with the actual multi-model comparison tools
    (see widgets/visualise_comparison_radar.py, reachable from the landing
    page) rather than bolted onto a single-model page - this page's whole
    point is just showing what one model reported."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.initial_model = None
        self.popup = None
        self.last_labels = []
        self.last_model_raw = {}
        self._predictions_df = None

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(30, 15, 30, 15)
        self.root.setSpacing(10)

        top = QHBoxLayout()
        self.btn_home = RoundedButton("  Dashboard", 300, 80, 40)
        self.btn_back = RoundedButton("  Back", 220, 80, 40)
        set_asset_icon(self.btn_home, "home.svg")
        self.btn_home.setIconSize(QSize(32, 32))
        set_asset_icon(self.btn_back, "back.svg")
        self.btn_back.setIconSize(QSize(32, 32))
        top.addWidget(self.btn_home)
        top.addStretch()
        top.addWidget(self.btn_back)
        self.root.addLayout(top)

        self.title = QLabel("Model Metrics")
        self.title.setAlignment(Qt.AlignCenter)
        themed(self.title, lambda c: f"""
            background: {c.surface};
            color: {c.text_pure};
            border: 2px solid {c.border_pure};
            padding: 10px 18px;
            font-size: 34px;
            font-weight: 700;
            border-radius: 10px;
        """)
        self.title.setMaximumWidth(500)

        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(self.title)
        title_layout.addStretch()
        self.root.addLayout(title_layout)

        selector_row = QHBoxLayout()

        self.model_selector = SimpleDropdown(
            "Select Model", [], favorite_check=is_favorite, annotate=self._annotate_model
        )
        self.model_selector.currentIndexChanged.connect(self.update_graph)
        themed_add(self.model_selector.button, lambda c: f"QPushButton {{ background: {c.page}; }}")
        selector_row.addWidget(self.model_selector, stretch=1)

        self.favorite_btn = RoundedButton("☆", 70, 70, 35)
        self.favorite_btn.setToolTip("Mark this model as a favorite")
        self.favorite_btn.clicked.connect(self._toggle_favorite)
        selector_row.addWidget(self.favorite_btn)

        self.root.addLayout(selector_row)

        # When it was trained, which dataset, seed, epochs, Ludwig version -
        # see _render_meta. Always the full technical detail on this page
        # (unlike the comparison views, this one's whole point is one
        # model's own numbers, so there's no "simple mode" reason to hide
        # any of it - no Advanced mode toggle here any more).
        self.meta_label = QLabel("")
        self.meta_label.setWordWrap(True)
        themed(self.meta_label, lambda c: f"color: {c.subtle}; font-size: 13px;")
        self.meta_label.hide()
        self.root.addWidget(self.meta_label)

        # Break down this model's own numbers by a patient attribute (e.g.
        # sex) instead of just the overall aggregate - only offered when
        # test_predictions.csv has a usable column for it (see
        # gmp.get_subgroup_columns) and the model is a classifier (accuracy
        # as computed here - exact match - isn't a meaningful number for
        # regression). "None" is a real, selectable choice here (not just
        # a placeholder), same as confusion_matrix.py's condition_dropdown.
        self.subgroup_row_widget = QWidget()
        subgroup_col_layout = QVBoxLayout(self.subgroup_row_widget)
        subgroup_col_layout.setContentsMargins(0, 0, 0, 0)
        subgroup_col_layout.setSpacing(4)
        subgroup_label = QLabel("Break down by:")
        themed(subgroup_label, lambda c: f"color: {c.text_pure}; font-size: 15px; font-weight: 600;")
        subgroup_col_layout.addWidget(subgroup_label)

        self.subgroup_dropdown = SimpleDropdown("Break down by", ["None"])
        self.subgroup_dropdown.currentIndexChanged.connect(self._render_metrics)
        subgroup_col_layout.addWidget(self.subgroup_dropdown)
        self.subgroup_row_widget.setVisible(False)
        self.root.addWidget(self.subgroup_row_widget)

        card = QWidget()
        self.card = card
        card.setAttribute(Qt.WA_StyledBackground, True)
        themed(card, lambda c: f"""
            QWidget {{
                background: {c.page};
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)

        self.no_metrics_label = QLabel("No metrics available for this model.")
        self.no_metrics_label.setAlignment(Qt.AlignCenter)
        themed(self.no_metrics_label, lambda c: f"font-size: 15px; color: {c.text_pure}; padding: 12px;")
        self.no_metrics_label.hide()
        layout.addWidget(self.no_metrics_label)

        # One tile per metric (plain-language name, raw value, a 95% CI
        # when available). Built fresh from whatever metrics the loaded
        # run actually has, so a regression
        # run shows R²/RMSE/MAE and a classification run shows
        # accuracy/precision/recall/... without this page needing to know
        # in advance which kind of model it's looking at.
        self.cards_section = QWidget()
        cards_section_layout = QVBoxLayout(self.cards_section)
        cards_section_layout.setContentsMargins(0, 4, 0, 4)
        self.cards_grid = QGridLayout()
        self.cards_grid.setHorizontalSpacing(10)
        self.cards_grid.setVerticalSpacing(10)
        cards_section_layout.addLayout(self.cards_grid)
        layout.addWidget(self.cards_section)

        # Subgroup breakdown: replaces the cards above with a small table
        # (one row per group value) when "Break down by" picks a column -
        # see _populate_subgroup_table.
        self.subgroup_section = QWidget()
        subgroup_section_layout = QVBoxLayout(self.subgroup_section)
        subgroup_section_layout.setContentsMargins(0, 4, 0, 4)
        subgroup_section_layout.setSpacing(8)

        self.subgroup_warning = QLabel("")
        self.subgroup_warning.setWordWrap(True)
        themed(self.subgroup_warning, "color: #D13438; font-size: 13px; font-style: italic;")
        self.subgroup_warning.hide()
        subgroup_section_layout.addWidget(self.subgroup_warning)

        # Same look as confusion_matrix.py's table (and every other table
        # in the app) instead of Qt's unstyled default - which also left
        # its columns individually drag-resizable (Interactive, the
        # default resize mode), showing a resize cursor on hover over the
        # header for no reason: this table's columns should always just
        # fill the available width instead.
        self.subgroup_table = QTableWidget()
        self.subgroup_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.subgroup_table.verticalHeader().setVisible(False)
        self.subgroup_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.subgroup_table.setMinimumHeight(220)
        self.subgroup_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.subgroup_table.verticalHeader().setDefaultSectionSize(40)
        themed(self.subgroup_table, lambda c: f"""
            QTableWidget {{
                background-color: {c.surface};
                color: {c.text_pure};
                gridline-color: {c.muted};
                border: 2px solid {c.border_pure};
                border-radius: 10px;
                font-size: 15px;
            }}
            QHeaderView::section {{
                background-color: {c.header_pure};
                color: white;
                padding: 6px;
                border: 1px solid {c.muted};
                font-weight: 600;
            }}
            QTableCornerButton::section {{
                background-color: {c.header_pure};
                border: 1px solid {c.muted};
            }}
        """)
        subgroup_section_layout.addWidget(self.subgroup_table)

        self.subgroup_section.hide()
        layout.addWidget(self.subgroup_section)

        self.root.addWidget(card, stretch=1)

        # Free-text notes for this model, saved into its run folder (see
        # utils/notes.py) when the field loses focus.
        self._note_model = None
        notes_label = QLabel("Notes")
        themed(notes_label, lambda c: f"color: {c.text_pure}; font-size: 14px; font-weight: 600;")
        self.root.addWidget(notes_label)

        self.notes_edit = _NotesEdit(on_commit=self._save_note)
        self.notes_edit.setPlaceholderText("Notes about this model")
        self.notes_edit.setFixedHeight(80)
        themed(self.notes_edit, lambda c: f"""
            QPlainTextEdit {{
                background: {c.surface};
                color: {c.text_pure};
                border: 2px solid {c.border_pure};
                border-radius: 10px;
                padding: 6px 10px;
                font-size: 14px;
            }}
        """)
        self.root.addWidget(self.notes_edit)

        info_row = QHBoxLayout()
        self.export_btn = make_export_button()
        self.export_btn.clicked.connect(self._on_export_clicked)
        info_row.addWidget(self.export_btn)
        info_row.addStretch()
        self.info_btn = RoundedButton("?", 48, 48, 24)
        self.info_btn.clicked.connect(self.show_popup)
        self._set_info_btn_style(INFO_YELLOW)
        info_row.addWidget(self.info_btn)
        self.root.addLayout(info_row)

    def _set_info_btn_style(self, background_color):
        themed(self.info_btn, lambda c, background_color=background_color: f"""
            QPushButton {{
                font-size: 24px;
                font-weight: 700;
                background: {background_color};
                color: black;
                border: none;
                border-radius: 24px;
            }}
            QPushButton:hover {{
                background: {INFO_YELLOW_HOVER};
            }}
        """)

    def show_popup(self):
        if self.popup is not None:
            self.popup.close()

        self.popup = Popup(
            parent=self,
            width=820,
            height=520,
            x=(self.width() - 820) // 2,
            y=(self.height() - 520) // 2,
            background=COLORS['yellow'],
        )
        self.popup.installEventFilter(self)

        entries = get_metric_glossary_entries(self.last_labels or [])
        content = build_glossary_widget(
            entries,
            intro="Metrics shown:",
            empty_text="Select a model to see explanations.",
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        themed(scroll, "QScrollArea { background: transparent; }")
        scroll.setWidget(content)

        self.popup.layout.addSpacing(20)
        self.popup.layout.addWidget(scroll)
        self.popup.close_btn.raise_()

        self._set_info_btn_style(INFO_YELLOW)
        self.popup.show()

    def eventFilter(self, obj, event):
        if self.popup is not None and obj is self.popup and event.type() == QEvent.Hide:
            self._set_info_btn_style(INFO_YELLOW)
        return super().eventFilter(obj, event)

    def set_data(self, model, criterion=None, view_mode=None):
        self.initial_model = model
        self.update_ui()

    def update_ui(self):
        models = gmp.get_model_names()
        self.model_selector.clear()
        self.model_selector.addItems(models)

        if self.initial_model in models:
            self.model_selector.selected = self.initial_model
            self.model_selector._update_label()

        self.update_graph()

    def _on_export_clicked(self):
        model = self.model_selector.currentText()
        if not model or not self.last_model_raw:
            ErrorPopup(self, "Select a model with metrics first.").show()
            return

        # A full report, not just the metrics on screen - the project this
        # model belongs to, what it actually is, then its numbers - so the
        # file makes sense on its own without the app open next to it.
        model_path = gmp.model_path_from_name(model)
        project = gmp.get_project_info()
        meta = gmp.get_run_metadata(model_path) if model_path else {}
        target = gmp.get_output_feature_info(model_path).get("name") if model_path else None
        features = gmp.get_input_feature_names(model_path) if model_path else []
        size, is_exact = gmp.get_evaluated_size(model_path) if model_path else (None, False)
        model_type = gmp.detect_model_type_from_ludwig(model_path) if model_path else None

        rows = [
            ("Project name", project.get("name")),
            ("Protocol number", project.get("protocol_number")),
            ("Institution", project.get("institution")),
            ("Principal investigator", project.get("principal_investigator")),
            ("Study type", project.get("study_type")),
            ("Primary objective", project.get("primary_objective")),
            ("Secondary objectives", "; ".join(project.get("secondary_objectives") or []) or None),
            ("Model name", model),
            ("Model type", model_type),
            ("Trained", _format_trained_at(meta.get("generated_at"))),
            ("Dataset", meta.get("dataset_name")),
            ("Target variable", target),
            ("Predictive variables", ", ".join(features) if features else None),
            ("Number of predictive variables", len(features) if features else None),
            ("Evaluated on (patients)", size),
            ("Evaluation set is exact held-out test set", is_exact if size is not None else None),
        ]
        for label in self.last_labels:
            rows.append((get_metric_info(label)["label"], self.last_model_raw.get(label)))

        note = load_note(model)
        if note:
            rows.append(("Notes", note))

        export_csv(self, model.replace("/", "_"), ["field", "value"], rows,
                   title=f"Model report — {model}")

    @staticmethod
    def _annotate_model(model_name):
        # Shown next to each model in "Select Model" so it's harder to pick
        # one without noticing what it actually predicts - see
        # get_target_column().
        target = get_target_column(model_name)
        return f"Predicts: {target}" if target else None

    def _toggle_favorite(self):
        model = self.model_selector.currentText()
        if not model:
            return
        self._update_favorite_button(toggle_favorite(model))
        self.model_selector.refresh_favorites()

    def _update_favorite_button(self, is_fav):
        self.favorite_btn.setText("★" if is_fav else "☆")
        self.favorite_btn.set_accent(COLORS['yellow'] if is_fav else None)

    # RUN METADATA + NOTES

    def _render_meta(self, model_path):
        meta = gmp.get_run_metadata(model_path) if model_path else {}
        parts = []

        trained = _format_trained_at(meta.get("generated_at"))
        if trained:
            parts.append(f"Trained {trained}")
        if meta.get("dataset_name"):
            parts.append(f"Dataset: {meta['dataset_name']}")

        if meta.get("epochs_trained") is not None:
            parts.append(f"{meta['epochs_trained']} epochs")
        if meta.get("random_seed") is not None:
            parts.append(f"seed {meta['random_seed']}")
        if meta.get("ludwig_version"):
            parts.append(f"Ludwig {meta['ludwig_version']}")

        self.meta_label.setText("   ·   ".join(parts))
        self.meta_label.setVisible(bool(parts))

    def _load_note(self, model):
        self._note_model = model
        self.notes_edit.setPlainText(load_note(model) if model else "")

    def _save_note(self):
        if self._note_model:
            save_note(self._note_model, self.notes_edit.toPlainText())

    def _clear_cards_grid(self):
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    _CARDS_PER_ROW = 3

    def _build_metric_tile(self, label_text, value_text, tooltip=None):
        tile = QWidget()
        tile.setAttribute(Qt.WA_StyledBackground, True)
        themed(tile, lambda c: f"""
            QWidget {{
                background: {c.accent_fill};
                border: 2px solid {c.accent_edge_pure};
                border-radius: 12px;
            }}
        """)
        tile_layout = QVBoxLayout(tile)
        tile_layout.setContentsMargins(14, 10, 14, 10)
        tile_layout.setSpacing(2)

        name_lbl = QLabel(label_text.upper())
        name_lbl.setWordWrap(True)
        themed(name_lbl, lambda c: f"font-size: 12px; font-weight: 700; color: {c.subtle}; "
            f"background: transparent; border: none; letter-spacing: 1px;")
        tile_layout.addWidget(name_lbl)

        value_row = QHBoxLayout()
        value_lbl = QLabel(value_text)
        value_lbl.setWordWrap(True)
        themed(value_lbl, lambda c: f"font-size: 20px; font-weight: 700; color: {c.text_pure}; "
            f"background: transparent; border: none;")
        if tooltip:
            value_lbl.setToolTip(tooltip)
        value_row.addWidget(value_lbl)
        value_row.addStretch()
        tile_layout.addLayout(value_row)

        return tile

    def _populate_metric_cards(self, labels, model_raw, predictions_df=None):
        """One tile per metric: plain-language name, raw value (with a 95%
        confidence interval alongside it when predictions_df - the model's
        saved test_predictions.csv, see utils.get_model_paths.
        load_test_predictions - makes one computable, see
        utils.bootstrap_ci).

        predictions_df is None for runs saved before test_predictions.csv
        existed (or non-Ludwig backends) - the CI is simply omitted for
        those, same value display as before."""
        self._clear_cards_grid()

        for i, metric in enumerate(labels):
            value = model_raw.get(metric)
            info = get_metric_info(metric)

            value_text = f"{value:.4f}" if isinstance(value, (int, float)) else "N/A"
            tooltip = None
            if predictions_df is not None and ci_is_supported(metric) and len(predictions_df) > 0:
                _, ci_low, ci_high = bootstrap_ci(predictions_df, metric)
                if ci_low is not None:
                    value_text += f"\n[{ci_low:.3f}–{ci_high:.3f}]"
                    tooltip = (
                        "95% confidence interval in brackets: if this model "
                        "were re-evaluated on a different sample of similar "
                        "patients, the true value would typically fall in "
                        "this range."
                    )

            label_text = info["label"]
            if info.get("jargon"):
                label_text = f"{label_text} ({info['jargon']})"

            tile = self._build_metric_tile(label_text, value_text, tooltip)
            row, col = divmod(i, self._CARDS_PER_ROW)
            self.cards_grid.addWidget(tile, row, col)

    def update_graph(self):
        model = self.model_selector.currentText()

        # Persist the note for whichever model was showing before this
        # switch - focusOut usually covers it, but not a keyboard-driven
        # dropdown change that never touched the editor.
        if self._note_model and self._note_model != model:
            save_note(self._note_model, self.notes_edit.toPlainText())

        if not model:
            self._update_favorite_button(False)
            self.subgroup_row_widget.setVisible(False)
            self.meta_label.hide()
            self._load_note(None)
            return

        self._update_favorite_button(is_favorite(model))

        model_path = gmp.model_path_from_name(model)
        self._predictions_df = gmp.load_test_predictions(model_path) if model_path else None
        self._render_meta(model_path)
        self._load_note(model)

        # "Break down by" options - only for a classifier with a usable
        # column in its saved predictions (see gmp.get_subgroup_columns).
        # Repopulated on every full refresh (this method), not on the
        # dropdown's own selection changing - see _render_metrics().
        output_type = gmp.get_output_feature_info(model_path).get("type") if model_path else None
        subgroup_columns = (
            gmp.get_subgroup_columns(model_path)
            if model_path and output_type in _CLASSIFICATION_TYPES
            else []
        )
        previous_subgroup = self.subgroup_dropdown.currentText()
        self.subgroup_dropdown.clear()
        self.subgroup_dropdown.addItems(["None"] + subgroup_columns)
        self.subgroup_dropdown.selected = previous_subgroup if previous_subgroup in subgroup_columns else "None"
        self.subgroup_dropdown._update_label()
        self.subgroup_row_widget.setVisible(bool(subgroup_columns))

        current_metrics = load_run_metrics(model) or {}

        current_by_metric = {}
        for k, v in current_metrics.items():
            if k.startswith("test/") and isinstance(v, (int, float)):
                current_by_metric.setdefault(metric_name(k), float(v))

        if not current_by_metric:
            self.last_labels = []
            self.last_model_raw = {}
            self._clear_cards_grid()
            self.cards_section.hide()
            self.subgroup_section.hide()
            self.no_metrics_label.show()
            return

        own_labels = sorted(current_by_metric.keys())
        self.last_labels = own_labels
        self.last_model_raw = current_by_metric
        self.no_metrics_label.hide()

        self._render_metrics()

    def _render_metrics(self):
        """Shows either the metric cards (aggregate over the whole test
        set) or the subgroup table, depending on "Break down by" - the
        target of that dropdown's own change signal, so picking a
        subgroup column re-renders without repopulating any dropdowns
        (see update_graph(), which does the repopulating on a real model
        change)."""
        if not self.last_labels:
            return

        subgroup_col = self.subgroup_dropdown.currentText()
        if subgroup_col and subgroup_col != "None" and self._predictions_df is not None:
            self.cards_section.hide()
            self._populate_subgroup_table(subgroup_col)
            self.subgroup_section.show()
            return

        self.subgroup_section.hide()
        self.cards_section.show()

        # One tile per metric this model actually reported - no narrowing,
        # so nothing needs a toggle to become visible.
        self._populate_metric_cards(self.last_labels, self.last_model_raw, self._predictions_df)

    def _populate_subgroup_table(self, subgroup_col):
        """One row per value of subgroup_col, with the group's size and
        its accuracy computed directly from the saved predictions - not
        read from training_report.json, which only ever has the
        whole-test-set aggregate."""
        df = self._predictions_df
        groups = sorted(df[subgroup_col].dropna().unique(), key=str)

        self.subgroup_table.clear()
        self.subgroup_table.setColumnCount(3)
        self.subgroup_table.setHorizontalHeaderLabels(["Group", "N", "Accuracy"])
        self.subgroup_table.setRowCount(len(groups))

        has_small_group = False
        for row, group_value in enumerate(groups):
            subset = df[df[subgroup_col] == group_value]
            n = len(subset)
            is_small = n < _SMALL_SUBGROUP_N
            has_small_group = has_small_group or is_small
            accuracy = (subset["y_true"].astype(str) == subset["y_pred"].astype(str)).mean() if n else None

            # The "!" sits right on the group it's actually about, instead
            # of a separate sentence above the table listing group names -
            # easier to tell at a glance which row(s) it's warning about,
            # especially with more than one small group.
            group_item = QTableWidgetItem(f"⚠ {group_value}" if is_small else str(group_value))
            if is_small:
                group_item.setToolTip(
                    f"Fewer than {_SMALL_SUBGROUP_N} patients in this group - "
                    "treat this number with caution."
                )
            self.subgroup_table.setItem(row, 0, group_item)

            n_item = QTableWidgetItem(str(n))
            n_item.setTextAlignment(Qt.AlignCenter)
            self.subgroup_table.setItem(row, 1, n_item)
            acc_item = QTableWidgetItem(f"{accuracy:.4f}" if accuracy is not None else "N/A")
            acc_item.setTextAlignment(Qt.AlignCenter)
            self.subgroup_table.setItem(row, 2, acc_item)

        if has_small_group:
            self.subgroup_warning.setText(
                f"⚠ Fewer than {_SMALL_SUBGROUP_N} patients - treat its number with caution."
            )
            self.subgroup_warning.show()
        else:
            self.subgroup_warning.hide()
