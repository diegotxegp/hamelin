"""
Help Button Widget
~~~~~~~~~~~~~~~~~~

Reusable help button, opening a small popup with guidance on click.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from qfluentwidgets import FluentIcon, getIconColor, Theme

from hamelin.view.widgets.theme_colors import bind_style
from hamelin.view.widgets.page_help import HelpPopup, _position_popup
from hamelin.utils.usage_logger import usage_log, infer_page_name


class HelpButton(QPushButton):
    """
    Help icon button that opens a HelpPopup on click.

    Not a native QToolTip, deliberately - see HelpPopup's own docstring in
    page_help.py for why (some platform themes paint QToolTip natively,
    ignoring this app's own light/dark styling entirely). Click, not
    hover, to open it - a hover version was tried and dropped: it
    flickered open/closed from ordinary mouse movement near the button's
    edge. Same mechanism as PageHelpButton (the bigger page-title "?"),
    which never had that problem.

    Usage:
        help_btn = HelpButton("This is what this section does...")
        layout.addWidget(help_btn)
    """

    def __init__(self, help_text: str, parent=None):
        super().__init__(parent)
        self.help_text = help_text

        # Set icon
        icon = FluentIcon.HELP.icon()
        self.setIcon(icon)
        self.setIconSize(QSize(14, 14))
        self.setFixedSize(20, 20)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Make it flat (no button appearance)
        self.setFlat(True)

        # Style
        self.setStyleSheet("""
            QPushButton {
                color: #0078D4;
                border: none;
                border-radius: 10px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 120, 212, 0.1);
            }
        """)

        self.clicked.connect(self._show_popup)

    def _show_popup(self):
        usage_log.event(infer_page_name(self), "click", "Help button (inline)", self.help_text[:60])
        popup = HelpPopup(self.help_text, self)
        _position_popup(popup, self)
        popup.show()


class SectionHeader(QWidget):
    """
    Section header with title and help button.
    
    Usage:
        header = SectionHeader(
            "Variable Selection",
            "Choose your primary outcome variable and features for the model"
        )
        layout.addWidget(header)
    """
    
    def __init__(self, title: str, help_text: str, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(title)
        bind_style(
            title_label,
            lambda c: f"QLabel {{ font-size: 14px; font-weight: 600; color: {c.text_primary}; }}",
        )
        layout.addWidget(title_label)
        
        # Help button
        help_btn = HelpButton(help_text)
        layout.addWidget(help_btn)
        
        layout.addStretch()
