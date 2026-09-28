"""
KPI Card Widget
~~~~~~~~~~~~~~~

Individual KPI card for the status dashboard.
Displays a single metric with a large value, a descriptive label,
an optional subtitle, and a colour accent that reflects status.

Colours
-------
    "default"  → theme accent (neutral)
    "good"     → green  (#2ecc71)  — on-track / complete
    "warning"  → orange (#e67e22)  — at-risk / late
    "info"     → blue   (#3498db)  — informational

Usage
-----
    card = KPICardWidget("Recruited", "42", subtitle="of 100 target")
    card.set_status("good")
    card.update_value("43", subtitle="of 100 target")
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from qfluentwidgets import CardWidget, TitleLabel, StrongBodyLabel, BodyLabel, FluentIcon, IconWidget

from hamelin.view.widgets.theme_colors import bind_style

# ── Status colours ────────────────────────────────────────────────────────────

_STATUS_COLOURS: dict[str, str] = {
    "good":    "#2ecc71",
    "warning": "#e67e22",
    "info":    "#3498db",
    "default": "",          # empty → CSS inherits theme
}


class KPICardWidget(CardWidget):
    """
    Compact card for a single KPI.

    Parameters
    ----------
    label : str
        Short descriptive name shown below the value (e.g. "Recruited").
    value : str
        Initial value string (e.g. "42" or "63.3%").
    subtitle : str, optional
        Small grey note shown below the label (e.g. "of 100 target").
    icon : FluentIcon, optional
        Icon shown in the top-left corner.
    status : str, optional
        One of "default", "good", "warning", "info".  Controls the accent bar.
    parent : QWidget, optional
    """

    def __init__(
        self,
        label: str,
        value: str = "—",
        subtitle: str = "",
        icon: FluentIcon | None = None,
        status: str = "default",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setFixedSize(200, 130)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        # Top row: icon + label
        top_row = QHBoxLayout()
        top_row.setSpacing(6)
        if icon is not None:
            icon_widget = IconWidget(icon, self)
            icon_widget.setFixedSize(20, 20)
            top_row.addWidget(icon_widget)
        self._label_lbl = BodyLabel(label, self)
        bind_style(self._label_lbl, lambda c: f"color: {c.text_secondary}; font-size: 12px;")
        top_row.addWidget(self._label_lbl)
        top_row.addStretch()
        layout.addLayout(top_row)

        # Value (large)
        self._value_lbl = TitleLabel(value, self)
        self._value_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self._value_lbl)

        # Subtitle
        self._subtitle_lbl = BodyLabel(subtitle, self)
        bind_style(self._subtitle_lbl, lambda c: f"color: {c.text_secondary}; font-size: 11px;")
        self._subtitle_lbl.setVisible(bool(subtitle))
        layout.addWidget(self._subtitle_lbl)

        layout.addStretch()

        # Colour accent bar (bottom border)
        self._status = ""
        self.set_status(status)

    # ── Public API ─────────────────────────────────────────────────────

    def update_value(self, value: str, subtitle: str = "") -> None:
        """Update the displayed value and optionally the subtitle."""
        self._value_lbl.setText(value)
        if subtitle:
            self._subtitle_lbl.setText(subtitle)
            self._subtitle_lbl.setVisible(True)

    def set_status(self, status: str) -> None:
        """
        Set the card's colour status.

        Parameters
        ----------
        status : str
            "good" | "warning" | "info" | "default"
        """
        if status == self._status:
            return
        self._status = status
        colour = _STATUS_COLOURS.get(status, "")
        if colour:
            self.setStyleSheet(
                f"KPICardWidget {{ border-left: 4px solid {colour}; }}"
            )
        else:
            self.setStyleSheet("")   # reset to theme default

    def set_label(self, text: str) -> None:
        self._label_lbl.setText(text)
