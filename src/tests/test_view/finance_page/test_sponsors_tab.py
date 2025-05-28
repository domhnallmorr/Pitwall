import pytest
import flet as ft
import pandas as pd

import pw_view.finance_page.sponsors_tab as sp_mod

class DummyCustomDataTable:
    def __init__(self, view, column_names):
        self.view = view
        self.column_names = column_names
        self.update_calls = []
        self.list_view = "dummy_list_view"

    def update_table_data(self, data):
        self.update_calls.append(data)

@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    # Stub out CustomDataTable dependency
    monkeypatch.setattr(sp_mod, 'CustomDataTable', DummyCustomDataTable)
    return {}


def test_init_sets_up_table_and_controls():
    """__init__ should create a CustomDataTable and configure controls correctly."""
    view = object()
    tab = sp_mod.SponsorsTab(view)

    # Verify sponsors_table instantiation
    assert isinstance(tab.sponsors_table, DummyCustomDataTable)
    assert tab.sponsors_table.view is view
    assert tab.sponsors_table.column_names == [
        "Sponsor Type",
        "Name",
        "Payment",
        "Contract Remaining"
    ]

    # Initial update_table_data call in setup_widgets
    assert tab.sponsors_table.update_calls == [[['-', '-', '-', '-']]]

    # Verify layout controls
    # SponsorsTab inherits from ft.Column, so its controls list should start with the content column
    assert hasattr(tab, 'controls')
    assert len(tab.controls) == 1
    content = tab.controls[0]
    # Content should itself have a 'controls' attribute containing the list_view
    assert hasattr(content, 'controls')
    assert content.controls == [tab.sponsors_table.list_view]
    assert content.expand is False


def test_update_tab_pushes_new_data():
    """update_tab should push DataFrame data to the table."""
    view = object()
    tab = sp_mod.SponsorsTab(view)
    # Clear initial call
    tab.sponsors_table.update_calls.clear()

    # Prepare sample DataFrame
    df = pd.DataFrame([
        ["A", "B", "C", "D"],
        ["E", "F", "G", "H"]
    ])
    data = {"summary_df": df}

    # Call update_tab
    tab.update_tab(data)

    # Expect exactly one update call with DataFrame converted to list of lists
    assert tab.sponsors_table.update_calls == [df.to_numpy().tolist()]
