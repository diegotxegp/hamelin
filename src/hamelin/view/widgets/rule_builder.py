"""Visual Rule Builder widget
"""
from hamelin.i18n import t
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QSizePolicy, QMessageBox
)
from PySide6.QtCore import Signal
from qfluentwidgets import BodyLabel, ComboBox, LineEdit, PushButton
from pathlib import Path
from typing import List

from hamelin.utils.rule_evaluator import apply_rules
from hamelin.view.widgets.table_theme import style_table_widget


class RuleRow(QWidget):
    def __init__(self, columns: List[str], parent=None):
        super().__init__(parent)
        self._columns = columns
        self._init_ui()

    def _init_ui(self):
        h = QHBoxLayout(self)
        self.col_cb = ComboBox(self)
        self.col_cb.addItems(self._columns)
        self.op_cb = ComboBox(self)
        self.op_cb.addItems(['==', '!=', '>=', '<=', '>', '<', 'contains', 'in', 'not in'])
        self.val_edit = LineEdit(self)
        self.del_btn = PushButton('✕', self)
        self.del_btn.setFixedWidth(40)

        h.addWidget(self.col_cb)
        h.addWidget(self.op_cb)
        h.addWidget(self.val_edit)
        h.addWidget(self.del_btn)

    def get_rule(self) -> str:
        col = self.col_cb.currentText()
        op = self.op_cb.currentText()
        val = self.val_edit.text().strip()
        return f"{col} {op} {val}"


class RuleBuilder(QWidget):
    """Widget allowing clinicians to add/edit rules and preview their impact."""

    rules_changed = Signal()

    def __init__(self, columns: List[str] = None, parent=None):
        super().__init__(parent)
        self.columns = columns or []
        self.rows: List[RuleRow] = []
        self._init_ui()

    def _init_ui(self):
        self.layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        self.add_btn = PushButton(t("common.txt.add_rule"))
        self.preview_btn = PushButton(t("common.txt.preview"))
        self.count_lbl = BodyLabel(t("common.txt.matches_0_2"))
        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.preview_btn)
        toolbar.addWidget(self.count_lbl)
        toolbar.addStretch()
        self.layout.addLayout(toolbar)

        self.list_container = QVBoxLayout()
        self.layout.addLayout(self.list_container)

        # sample table preview
        self.sample_table = QTableWidget()
        self.sample_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.sample_table.setFixedHeight(140)
        style_table_widget(self.sample_table)
        self.layout.addWidget(self.sample_table)

        # connections
        self.add_btn.clicked.connect(self._on_add)
        self.preview_btn.clicked.connect(self._on_preview)

    def set_columns(self, columns: List[str]):
        self.columns = columns or []
        for r in self.rows:
            r.col_cb.clear()
            r.col_cb.addItems(self.columns)

    def _on_add(self):
        if not self.columns:
            QMessageBox.warning(self, 'No columns', 'Load a dataset first to add rules.')
            return
        row = RuleRow(self.columns, parent=self)
        row.del_btn.clicked.connect(lambda _, r=row: self._remove_row(r))
        self.rows.append(row)
        self.list_container.addWidget(row)
        self.rules_changed.emit()

    def _remove_row(self, row: RuleRow):
        try:
            self.rows.remove(row)
            row.setParent(None)
            row.deleteLater()
            self.rules_changed.emit()
        except ValueError:
            pass

    def get_rules(self) -> List[str]:
        return [r.get_rule() for r in self.rows if r.get_rule().strip()]

    def set_rules(self, rules: List[str]):
        # clear existing
        for r in list(self.rows):
            self._remove_row(r)
        for rule in rules:
            self._on_add()
            if self.rows:
                last = self.rows[-1]
                try:
                    col, op, val = rule.split(maxsplit=2)
                    last.col_cb.setCurrentText(col)
                    last.op_cb.setCurrentText(op)
                    last.val_edit.setText(val)
                except Exception:
                    last.val_edit.setText(rule)

    def _on_preview(self):
        self.preview_with_df(None, mode='include')

    def preview_with_df(self, df, mode='include'):
        """Apply current rules to df and update count/sample. Mode: 'include'|'exclude'.

        If df is None, clears preview.
        """
        if df is None or df.empty:
            self.count_lbl.setText(t("common.txt.matches_0_2"))
            self.sample_table.clear()
            self.sample_table.setColumnCount(0)
            self.sample_table.setRowCount(0)
            return

        rules = self.get_rules()
        out = apply_rules(df, rules, mode=mode)
        self.count_lbl.setText(t("common.txt.matches_0").format(out['count']))
        sample = out['sample']
        if sample is None or sample.empty:
            self.sample_table.clear()
            self.sample_table.setColumnCount(0)
            self.sample_table.setRowCount(0)
            return

        self.sample_table.setColumnCount(len(sample.columns))
        self.sample_table.setHorizontalHeaderLabels(list(map(str, sample.columns)))
        self.sample_table.setRowCount(len(sample))
        for i, (_, row) in enumerate(sample.iterrows()):
            for j, col in enumerate(sample.columns):
                item = QTableWidgetItem(str(row[col]))
                self.sample_table.setItem(i, j, item)
