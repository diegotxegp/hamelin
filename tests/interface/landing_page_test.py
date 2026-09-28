from hamelin.interface.widgets.landing_page import LandingPage


def test_models_badge_shows_actual_model_count(qtbot):
    import hamelin.interface.utils.get_model_paths as gmp

    widget = LandingPage()
    qtbot.addWidget(widget)

    count = len(gmp.get_model_names())
    label = "model" if count == 1 else "models"
    assert widget.models_badge.text() == f"{count} {label} available"


def test_empty_hint_only_shown_when_there_are_no_models(qtbot, monkeypatch):
    from PySide6.QtWidgets import QLabel
    import hamelin.interface.widgets.landing_page as landing_mod

    monkeypatch.setattr(landing_mod.gmp, "get_model_names", lambda *a, **k: [])
    widget = LandingPage()
    qtbot.addWidget(widget)

    assert widget.models_badge.text() == "0 models available"
    assert any("No trained models found" in c.text() for c in widget.findChildren(QLabel))


def test_open_models_folder_creates_dir_and_opens_it(qtbot, monkeypatch, tmp_path):
    import hamelin.interface.widgets.landing_page as landing_mod

    monkeypatch.setattr(landing_mod.gmp, "RESULTS_DIR", str(tmp_path / "fresh_results"))
    opened = {}
    monkeypatch.setattr(
        landing_mod.QDesktopServices, "openUrl",
        lambda url: opened.setdefault("url", url.toLocalFile()),
    )

    widget = LandingPage()
    qtbot.addWidget(widget)
    widget.open_models_folder()

    assert (tmp_path / "fresh_results").is_dir()
    assert opened["url"] == str(tmp_path / "fresh_results")


def test_help_popup_opens_and_closes(qtbot):
    widget = LandingPage()
    qtbot.addWidget(widget)

    widget.show_help_popup()
    assert widget.popup is not None
    assert widget.popup.isHidden() is False

    widget.popup.close_btn.click()
    assert widget.popup.isHidden() is True


def test_create_nav_button_sets_text_icon_and_width(qtbot):
    widget = LandingPage()
    qtbot.addWidget(widget)

    btn = widget.create_nav_button("Do The Thing", icon_name="home.svg", width=250)
    qtbot.addWidget(btn)

    assert btn.text() == "Do The Thing"
    assert btn.width() == 250
    assert btn.icon().isNull() is False


def test_create_nav_button_without_icon_has_no_icon(qtbot):
    widget = LandingPage()
    qtbot.addWidget(widget)

    btn = widget.create_nav_button("Plain Button", width=200)
    qtbot.addWidget(btn)

    assert btn.icon().isNull() is True


def test_radar_comparison_button_exists_next_to_comparison_dashboard(qtbot):
    widget = LandingPage()
    qtbot.addWidget(widget)

    assert widget.btn_radar_comparison.text() == "Radar Chart Comparison"
    assert widget.btn_comparison.text() == "Comparison Dashboard"
