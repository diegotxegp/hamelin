import pytest
from PySide6.QtGui import QImage

from hamelin.interface.widgets.cnn_visualisation import (
    CNNVisualisationWidget, ConvolutionDiagram, PipelineDiagram,
    TrainingLoopDiagram as CNNTrainingLoopDiagram,
)
from hamelin.interface.widgets.mlp_visualisation import (
    MLPVisualisationWidget, NetworkDiagram, NeuronDiagram,
    TrainingLoopDiagram as MLPTrainingLoopDiagram,
)
from hamelin.interface.widgets.lstm_visualisation import (
    LSTMVisualisationWidget, LstmNetworkDiagram, LstmCellDiagram,
    TrainingLoopDiagram as LSTMTrainingLoopDiagram,
)

WIDGET_CLASSES = [CNNVisualisationWidget, MLPVisualisationWidget, LSTMVisualisationWidget]

DIAGRAM_CLASSES = [
    ConvolutionDiagram, PipelineDiagram, CNNTrainingLoopDiagram,
    NetworkDiagram, NeuronDiagram, MLPTrainingLoopDiagram,
    LstmNetworkDiagram, LstmCellDiagram, LSTMTrainingLoopDiagram,
]


@pytest.mark.parametrize("diagram_cls", DIAGRAM_CLASSES)
def test_diagram_paints_without_crashing(qtbot, diagram_cls):
    widget = diagram_cls()
    qtbot.addWidget(widget)
    widget.resize(400, 300)
    widget.show()

    img = QImage(widget.size(), QImage.Format_ARGB32)
    widget.render(img)  # forces a real paintEvent - would raise if it crashed


@pytest.mark.parametrize("widget_cls", WIDGET_CLASSES)
def test_widget_constructs_with_four_pages(qtbot, widget_cls):
    widget = widget_cls()
    qtbot.addWidget(widget)
    assert widget.stack.count() == 4
    assert widget.stack.currentIndex() == 0


@pytest.mark.parametrize("widget_cls", WIDGET_CLASSES)
def test_left_button_disabled_on_first_page(qtbot, widget_cls):
    widget = widget_cls()
    qtbot.addWidget(widget)
    assert widget.left_btn.isEnabled() is False
    assert widget.right_btn.isEnabled() is True


@pytest.mark.parametrize("widget_cls", WIDGET_CLASSES)
def test_next_page_advances_and_enables_left_button(qtbot, widget_cls):
    widget = widget_cls()
    qtbot.addWidget(widget)

    widget.next_page()

    assert widget.stack.currentIndex() == 1
    assert widget.left_btn.isEnabled() is True
    assert widget.right_btn.isEnabled() is True


@pytest.mark.parametrize("widget_cls", WIDGET_CLASSES)
def test_next_page_stops_at_the_last_page(qtbot, widget_cls):
    widget = widget_cls()
    qtbot.addWidget(widget)

    for _ in range(10):
        widget.next_page()

    assert widget.stack.currentIndex() == widget.stack.count() - 1
    assert widget.right_btn.isEnabled() is False
    assert widget.left_btn.isEnabled() is True


@pytest.mark.parametrize("widget_cls", WIDGET_CLASSES)
def test_prev_page_stops_at_the_first_page(qtbot, widget_cls):
    widget = widget_cls()
    qtbot.addWidget(widget)

    widget.prev_page()

    assert widget.stack.currentIndex() == 0
    assert widget.left_btn.isEnabled() is False


@pytest.mark.parametrize("widget_cls", WIDGET_CLASSES)
def test_prev_and_next_are_symmetric(qtbot, widget_cls):
    widget = widget_cls()
    qtbot.addWidget(widget)

    widget.next_page()
    widget.next_page()
    widget.prev_page()

    assert widget.stack.currentIndex() == 1
