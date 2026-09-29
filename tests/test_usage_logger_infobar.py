"""Warning/error banners are recorded in the usage log."""
import csv

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
from qfluentwidgets import InfoBar, InfoBarPosition

from hamelin.utils import usage_logger


def test_infobar_warning_and_error_are_logged(qtbot):
    usage_logger.install_infobar_logging()
    usage_logger.install_infobar_logging()  # idempotent: must not double-wrap
    page = QWidget()
    page.setObjectName("TrainingPage")
    qtbot.addWidget(page)
    InfoBar.warning(title="No model name", content="Enter a name", orient=Qt.Horizontal,
                    position=InfoBarPosition.TOP, duration=10, parent=page)
    InfoBar.error(title="Boom", content="bad", parent=page)
    InfoBar.success(title="fine", content="ok", parent=page)   # not logged
    with open(usage_logger.usage_log._path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    mine = [r for r in rows if r["action"] in ("warning_shown", "error_shown")]
    assert [(r["page"], r["action"], r["element"]) for r in mine][-2:] == [
        ("Training", "warning_shown", "No model name"), ("Training", "error_shown", "Boom")]
