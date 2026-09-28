from hamelin.interface.utils.app_state import AppState, app_state


def test_advanced_mode_defaults_to_false():
    state = AppState()
    assert state.advanced_mode is False


def test_set_advanced_mode_updates_value():
    state = AppState()
    state.set_advanced_mode(True)
    assert state.advanced_mode is True


def test_set_advanced_mode_emits_signal_on_change():
    state = AppState()
    received = []
    state.advancedModeChanged.connect(received.append)

    state.set_advanced_mode(True)

    assert received == [True]


def test_set_advanced_mode_does_not_re_emit_for_the_same_value():
    state = AppState()
    state.set_advanced_mode(True)

    received = []
    state.advancedModeChanged.connect(received.append)
    state.set_advanced_mode(True)

    assert received == []


def test_set_advanced_mode_coerces_truthy_values_to_bool():
    state = AppState()
    state.set_advanced_mode(1)
    assert state.advanced_mode is True


def test_module_level_singleton_exists():
    assert isinstance(app_state, AppState)
