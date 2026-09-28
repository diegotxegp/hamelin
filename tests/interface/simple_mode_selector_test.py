from hamelin.interface.widgets.simple_mode_selector import MetricPrioritySelector
from hamelin.interface.utils.metric_labels import SIMPLE_MODE_PRIORITIES


def test_shows_one_card_per_priority_option(qtbot):
    selector = MetricPrioritySelector()
    qtbot.addWidget(selector)

    assert set(selector._cards.keys()) == {o["key"] for o in SIMPLE_MODE_PRIORITIES}
    assert selector.selected_key() is None


def test_clicking_a_card_emits_prioritySelected_with_its_key(qtbot):
    selector = MetricPrioritySelector()
    qtbot.addWidget(selector)

    with qtbot.waitSignal(selector.prioritySelected, timeout=1000) as blocker:
        selector._cards["recall"].mousePressEvent(None)

    assert blocker.args == ["recall"]
    assert selector.selected_key() == "recall"


def test_selecting_a_card_updates_selected_key_on_reclick(qtbot):
    selector = MetricPrioritySelector()
    qtbot.addWidget(selector)

    selector._cards["recall"].mousePressEvent(None)
    assert selector.selected_key() == "recall"

    selector._cards["precision"].mousePressEvent(None)
    assert selector.selected_key() == "precision"


def test_reset_clears_selection(qtbot):
    selector = MetricPrioritySelector()
    qtbot.addWidget(selector)

    selector._cards["recall"].mousePressEvent(None)
    assert selector.selected_key() == "recall"

    selector.reset()
    assert selector.selected_key() is None
