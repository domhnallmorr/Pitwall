import pytest
import flet as ft
import pandas as pd
import types

import pw_view.grid_page as gp_mod

# Dummy CustomDataTable to capture initialization and updates
class DummyCustomDataTable:
    def __init__(self, view, column_names):
        self.view = view
        self.column_names = column_names
        self.update_calls = []
        self.list_view = f"list_{column_names}"

    def update_table_data(self, data):
        self.update_calls.append(data)

@pytest.fixture(autouse=True)
def patch_custom_datatable(monkeypatch):
    monkeypatch.setattr(gp_mod, 'CustomDataTable', DummyCustomDataTable)

@pytest.fixture
def dummy_view():
    class DummyMainApp:
        def __init__(self):
            self.update_calls = 0
        def update(self):
            self.update_calls += 1
    return types.SimpleNamespace(
        background_image="bg_image",
        page_header_style="header_style",
        main_app=DummyMainApp()
    )


def test_init_sets_up_tabs_and_controls(dummy_view):
    page = gp_mod.GridPage(dummy_view)

    # Initial tab labels and types
    assert isinstance(page.current_year_tab, ft.Tab)
    assert page.current_year_tab.text == "1998"
    assert isinstance(page.next_year_tab, ft.Tab)
    assert page.next_year_tab.text == "1999"
    assert isinstance(page.tabs, ft.Tabs)

    # Column root controls
    assert isinstance(page.controls[0], ft.Text)
    assert page.controls[0].value == "Grid"
    assert page.controls[1] is page.background_stack
    assert page.background_stack.expand is True


def test_update_page_and_show_staff_grid(dummy_view):
    page = gp_mod.GridPage(dummy_view)

    # Prepare sample dataframes
    df_staff = pd.DataFrame([[1, 2]], columns=["A", "B"])
    df_next_announce = pd.DataFrame([[3, 4]], columns=["C", "D"])
    df_sponsors = pd.DataFrame([[5, 6]], columns=["E", "F"])
    df_sponsors_next = pd.DataFrame([[7, 8]], columns=["G", "H"])

    # Call update_page
    page.update_page(2025, df_staff, df_next_announce, df_sponsors, df_sponsors_next)

    # Tabs should be relabeled
    assert page.current_year_tab.text == "2025"
    assert page.next_year_tab.text == "2026"

    # Staff filter active by default
    assert page.staff_button_container.data == "active"
    assert page.sponsor_button_container.data == "inactive"

    # Tables initialized and updated for staff view
    assert isinstance(page.grid_this_year_table, DummyCustomDataTable)
    assert page.grid_this_year_table.column_names == ["A", "B"]
    assert page.grid_this_year_table.update_calls == [df_staff.values.tolist()]

    assert isinstance(page.grid_next_year_table, DummyCustomDataTable)
    assert page.grid_next_year_table.column_names == ["C", "D"]
    assert page.grid_next_year_table.update_calls == [df_next_announce.values.tolist()]

    # main_app.update() called once
    assert dummy_view.main_app.update_calls == 1


def test_show_sponsor_grid_switches_and_updates(dummy_view):
    page = gp_mod.GridPage(dummy_view)

    # Prepare sample dataframes
    df_staff = pd.DataFrame([[1, 2]], columns=["A", "B"])
    df_next_announce = pd.DataFrame([[3, 4]], columns=["C", "D"])
    df_sponsors = pd.DataFrame([[5, 6]], columns=["E", "F"])
    df_sponsors_next = pd.DataFrame([[7, 8]], columns=["G", "H"])

    # Initialize page and reset update count
    page.update_page(2025, df_staff, df_next_announce, df_sponsors, df_sponsors_next)
    dummy_view.main_app.update_calls = 0

    # Switch to sponsor view
    page.show_sponsor_grid()

    # Sponsor filter should be active
    assert page.sponsor_button_container.data == "active"
    assert page.staff_button_container.data == "inactive"

    # Tables updated for sponsors view
    assert page.grid_this_year_table.column_names == ["E", "F"]
    assert page.grid_this_year_table.update_calls[-1] == df_sponsors.values.tolist()

    assert page.grid_next_year_table.column_names == ["G", "H"]
    assert page.grid_next_year_table.update_calls[-1] == df_sponsors_next.values.tolist()

    # main_app.update() called again
    assert dummy_view.main_app.update_calls == 1
