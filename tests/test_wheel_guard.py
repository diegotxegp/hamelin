"""The mouse wheel must not change spin boxes / combo boxes / sliders."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")
from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication, QComboBox, QDoubleSpinBox, QSpinBox, QVBoxLayout, QWidget

from hamelin.view.widgets import WheelGuard


def _wheel(widget, delta=120):
    pos = QPointF(widget.rect().center())
    ev = QWheelEvent(pos, widget.mapToGlobal(pos), QPoint(0, 0), QPoint(0, delta),
                     Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False)
    QApplication.sendEvent(widget, ev)


def test_wheel_leaves_values_alone():
    app = QApplication.instance() or QApplication([])
    guard = WheelGuard(app)
    app.installEventFilter(guard)
    try:
        host = QWidget()
        lay = QVBoxLayout(host)
        spin, dspin, combo = QSpinBox(), QDoubleSpinBox(), QComboBox()
        spin.setRange(0, 100); spin.setValue(5)
        dspin.setRange(0, 100); dspin.setValue(5.0)
        combo.addItems(["a", "b", "c"]); combo.setCurrentIndex(1)
        for w in (spin, dspin, combo):
            lay.addWidget(w)
        host.show()
        for w in (spin, dspin, combo):
            _wheel(w)
        assert (spin.value(), dspin.value(), combo.currentIndex()) == (5, 5.0, 1)
    finally:
        app.removeEventFilter(guard)


def test_scroll_areas_still_scroll():
    """QScrollBar is a slider too: the guard must not swallow the wheel there,
    or no page could scroll at all."""
    from PySide6.QtWidgets import QLabel, QScrollArea
    app = QApplication.instance() or QApplication([])
    guard = WheelGuard(app)
    app.installEventFilter(guard)
    try:
        body = QWidget()
        lay = QVBoxLayout(body)
        for i in range(60):
            lay.addWidget(QLabel(f"row {i}"))
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(body)
        area.resize(300, 200)
        area.show()
        app.processEvents()
        _wheel(area.viewport(), -120)
        assert area.verticalScrollBar().value() > 0
    finally:
        app.removeEventFilter(guard)


def test_guarded_widget_leaves_the_event_unaccepted_for_its_parent():
    app = QApplication.instance() or QApplication([])
    guard = WheelGuard(app)
    app.installEventFilter(guard)
    try:
        spin = QSpinBox()
        spin.show()
        pos = QPointF(spin.rect().center())
        ev = QWheelEvent(pos, spin.mapToGlobal(pos), QPoint(0, 0), QPoint(0, 120),
                         Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False)
        QApplication.sendEvent(spin, ev)
        assert not ev.isAccepted()
    finally:
        app.removeEventFilter(guard)
