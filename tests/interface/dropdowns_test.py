from hamelin.interface.widgets.dropdowns import SimpleDropdown, CheckBoxDropdown


# SimpleDropdown

def test_simple_dropdown_shows_title_when_nothing_selected(qtbot):
    dd = SimpleDropdown("Select model", ["run_a", "run_b"])
    qtbot.addWidget(dd)
    assert dd.button.text() == "Select model"
    assert dd.get_selected() is None


def test_simple_dropdown_click_selects_item(qtbot):
    dd = SimpleDropdown("Select model", ["run_a", "run_b"])
    qtbot.addWidget(dd)

    dd.buttons[1].click()

    assert dd.get_selected() == "run_b"
    assert dd.currentText() == "run_b"
    assert dd.button.text() == "run_b"


def test_simple_dropdown_select_emits_signal(qtbot):
    dd = SimpleDropdown("Select model", ["run_a"])
    qtbot.addWidget(dd)

    with qtbot.waitSignal(dd.currentIndexChanged, timeout=1000):
        dd.buttons[0].click()


def test_simple_dropdown_clear_resets_selection(qtbot):
    dd = SimpleDropdown("Select model", ["run_a"])
    qtbot.addWidget(dd)
    dd.buttons[0].click()

    dd.clear()

    assert dd.get_selected() is None
    assert dd.buttons == []


def test_simple_dropdown_add_items_after_clear(qtbot):
    dd = SimpleDropdown("Select model", [])
    qtbot.addWidget(dd)

    dd.addItems(["run_a", "run_b"])
    dd.buttons[0].click()

    assert dd.get_selected() == "run_a"


def test_simple_dropdown_search_box_hidden_for_short_lists(qtbot):
    dd = SimpleDropdown("Select model", ["run_a"])
    qtbot.addWidget(dd)
    assert dd.search.isHidden() is True


def test_simple_dropdown_search_box_visible_for_long_lists(qtbot):
    items = [f"run_{i}" for i in range(9)]
    dd = SimpleDropdown("Select model", items)
    qtbot.addWidget(dd)
    assert dd.search.isHidden() is False


def test_simple_dropdown_filter_items_hides_non_matching(qtbot):
    dd = SimpleDropdown("Select model", ["alpha", "beta", "gamma"])
    qtbot.addWidget(dd)

    dd._filter_items("al")

    visible = [b.text() for b in dd.buttons if not b.isHidden()]
    assert visible == ["alpha"]
    assert dd.no_results_label.isHidden() is True


def test_simple_dropdown_filter_no_matches_shows_no_results_label(qtbot):
    dd = SimpleDropdown("Select model", ["alpha", "beta"])
    qtbot.addWidget(dd)

    dd._filter_items("zzz")

    assert dd.no_results_label.isHidden() is False


def test_simple_dropdown_clear_hides_search_and_resets_text(qtbot):
    items = [f"run_{i}" for i in range(9)]
    dd = SimpleDropdown("Select model", items)
    qtbot.addWidget(dd)
    dd.search.setText("run_3")

    dd.clear()

    assert dd.search.text() == ""
    assert dd.search.isHidden() is True


def test_simple_dropdown_add_items_shows_search_once_over_threshold(qtbot):
    dd = SimpleDropdown("Select model", ["run_a"])
    qtbot.addWidget(dd)
    assert dd.search.isHidden() is True

    dd.addItems([f"run_{i}" for i in range(1, 9)])

    assert dd.search.isHidden() is False


# CheckBoxDropdown

def test_checkbox_dropdown_starts_with_nothing_selected(qtbot):
    cd = CheckBoxDropdown("Select models", ["run_a", "run_b"])
    qtbot.addWidget(cd)
    assert cd.get_selected() == []
    assert cd.button.text() == "Select models"


def test_checkbox_dropdown_toggle_updates_selection_and_label(qtbot):
    cd = CheckBoxDropdown("Select models", ["run_a", "run_b"])
    qtbot.addWidget(cd)

    cd.item_widgets[0].setChecked(True)

    assert cd.get_selected() == ["run_a"]
    assert cd.button.text() == "run_a"


def test_checkbox_dropdown_toggle_off_removes_selection(qtbot):
    cd = CheckBoxDropdown("Select models", ["run_a"])
    qtbot.addWidget(cd)

    cd.item_widgets[0].setChecked(True)
    cd.item_widgets[0].setChecked(False)

    assert cd.get_selected() == []


def test_checkbox_dropdown_label_truncates_after_two_selections(qtbot):
    cd = CheckBoxDropdown("Select models", ["run_a", "run_b", "run_c"])
    qtbot.addWidget(cd)

    for w in cd.item_widgets:
        w.setChecked(True)

    assert cd.button.text().endswith("...")


def test_checkbox_dropdown_search_box_hidden_for_short_lists(qtbot):
    cd = CheckBoxDropdown("Select models", ["run_a"])
    qtbot.addWidget(cd)
    assert cd.search.isVisible() is False


def test_checkbox_dropdown_search_box_visible_for_long_lists(qtbot):
    items = [f"run_{i}" for i in range(9)]
    cd = CheckBoxDropdown("Select models", items)
    qtbot.addWidget(cd)
    assert cd.search.isHidden() is False


def test_checkbox_dropdown_filter_items_hides_non_matching(qtbot):
    cd = CheckBoxDropdown("Select models", ["alpha", "beta", "gamma"])
    qtbot.addWidget(cd)

    cd._filter_items("al")

    visible = [w.text() for w in cd.item_widgets if not w.isHidden()]
    assert visible == ["alpha"]
    assert cd.no_results_label.isHidden() is True


def test_checkbox_dropdown_filter_no_matches_shows_no_results_label(qtbot):
    cd = CheckBoxDropdown("Select models", ["alpha", "beta"])
    qtbot.addWidget(cd)

    cd._filter_items("zzz")

    assert cd.no_results_label.isHidden() is False


def test_checkbox_dropdown_set_items_resets_selection(qtbot):
    cd = CheckBoxDropdown("Select models", ["run_a"])
    qtbot.addWidget(cd)
    cd.item_widgets[0].setChecked(True)

    cd.set_items(["run_x", "run_y"])

    assert cd.get_selected() == []
    assert [w.text() for w in cd.item_widgets] == ["run_x", "run_y"]


def test_checkbox_dropdown_set_items_emits_signal(qtbot):
    cd = CheckBoxDropdown("Select models", ["run_a"])
    qtbot.addWidget(cd)

    with qtbot.waitSignal(cd.selectionChanged, timeout=1000):
        cd.set_items(["run_b"])


# favorite_check (star prefix)

def test_simple_dropdown_without_favorite_check_has_plain_text(qtbot):
    dd = SimpleDropdown("Select model", ["run_a"])
    qtbot.addWidget(dd)
    assert dd.buttons[0].text() == "run_a"


def test_simple_dropdown_items_get_star_prefix(qtbot):
    dd = SimpleDropdown("Select model", ["run_a", "run_b"], favorite_check=lambda m: m == "run_a")
    qtbot.addWidget(dd)

    assert dd.buttons[0].text() == "★ run_a"
    assert dd.buttons[1].text() == "☆ run_b"


def test_simple_dropdown_selecting_a_starred_item_keeps_raw_value(qtbot):
    dd = SimpleDropdown("Select model", ["run_a"], favorite_check=lambda m: True)
    qtbot.addWidget(dd)

    dd.buttons[0].click()

    assert dd.get_selected() == "run_a"
    assert dd.currentText() == "run_a"
    assert dd.button.text() == "★ run_a"


def test_simple_dropdown_refresh_favorites_updates_items_and_closed_label(qtbot):
    favorites = set()
    dd = SimpleDropdown("Select model", ["run_a"], favorite_check=lambda m: m in favorites)
    qtbot.addWidget(dd)
    dd.buttons[0].click()
    assert dd.button.text() == "☆ run_a"

    favorites.add("run_a")
    dd.refresh_favorites()

    assert dd.buttons[0].text() == "★ run_a"
    assert dd.button.text() == "★ run_a"


def test_simple_dropdown_opening_popup_refreshes_favorites(qtbot):
    favorites = set()
    dd = SimpleDropdown("Select model", ["run_a"], favorite_check=lambda m: m in favorites)
    qtbot.addWidget(dd)

    favorites.add("run_a")
    dd._show_popup()

    assert dd.buttons[0].text() == "★ run_a"


def test_checkbox_dropdown_items_get_star_prefix(qtbot):
    cd = CheckBoxDropdown("Select models", ["run_a", "run_b"], favorite_check=lambda m: m == "run_a")
    qtbot.addWidget(cd)

    assert cd.item_widgets[0].text() == "★ run_a"
    assert cd.item_widgets[1].text() == "☆ run_b"


def test_checkbox_dropdown_selection_keeps_raw_values(qtbot):
    cd = CheckBoxDropdown("Select models", ["run_a"], favorite_check=lambda m: True)
    qtbot.addWidget(cd)

    cd.item_widgets[0].setChecked(True)

    assert cd.get_selected() == ["run_a"]
    assert cd.button.text() == "★ run_a"


def test_checkbox_dropdown_refresh_favorites_updates_items(qtbot):
    favorites = set()
    cd = CheckBoxDropdown("Select models", ["run_a"], favorite_check=lambda m: m in favorites)
    qtbot.addWidget(cd)

    favorites.add("run_a")
    cd.refresh_favorites()

    assert cd.item_widgets[0].text() == "★ run_a"


# annotate - optional per-row suffix (e.g. a model's predicted target),
# kept out of the collapsed header/summary so it doesn't clutter it once
# something is selected.

def test_simple_dropdown_without_annotate_has_plain_text(qtbot):
    dd = SimpleDropdown("Select model", ["run_a"])
    qtbot.addWidget(dd)
    assert dd.buttons[0].text() == "run_a"


def test_simple_dropdown_shows_annotation_suffix_on_rows_only(qtbot):
    dd = SimpleDropdown("Select model", ["run_a", "run_b"], annotate=lambda m: f"Predicts: {m}")
    qtbot.addWidget(dd)

    assert dd.buttons[0].text() == "run_a  —  Predicts: run_a"
    dd.buttons[0].click()

    # Selecting it must not leak the annotation into the closed-button label.
    assert dd.button.text() == "run_a"
    assert dd.currentText() == "run_a"


def test_simple_dropdown_annotate_returning_none_omits_suffix(qtbot):
    dd = SimpleDropdown("Select model", ["run_a"], annotate=lambda m: None)
    qtbot.addWidget(dd)
    assert dd.buttons[0].text() == "run_a"


def test_simple_dropdown_annotate_combines_with_favorite_star(qtbot):
    dd = SimpleDropdown(
        "Select model", ["run_a"],
        favorite_check=lambda m: True, annotate=lambda m: "Predicts: sentiment",
    )
    qtbot.addWidget(dd)
    assert dd.buttons[0].text() == "★ run_a  —  Predicts: sentiment"


def test_checkbox_dropdown_shows_annotation_suffix_on_rows_only(qtbot):
    cd = CheckBoxDropdown("Select models", ["run_a"], annotate=lambda m: f"Predicts: {m}")
    qtbot.addWidget(cd)

    assert cd.item_widgets[0].text() == "run_a  —  Predicts: run_a"
    cd.item_widgets[0].setChecked(True)

    assert cd.button.text() == "run_a"
    assert cd.get_selected() == ["run_a"]


def test_checkbox_dropdown_refresh_favorites_keeps_annotation(qtbot):
    cd = CheckBoxDropdown(
        "Select models", ["run_a"],
        favorite_check=lambda m: False, annotate=lambda m: "Predicts: sentiment",
    )
    qtbot.addWidget(cd)

    cd.refresh_favorites()

    assert cd.item_widgets[0].text() == "☆ run_a  —  Predicts: sentiment"
