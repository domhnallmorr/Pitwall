import pytest
import pandas as pd
import flet as ft
from pw_view.standings_page import StandingsPage

# Create dummy objects for the view and main_app

class DummyMainApp:
    def __init__(self):
        self.updated = False
    def update(self):
        self.updated = True

class DummyView:
    def __init__(self):
        self.page_header_style = ft.TextThemeStyle.DISPLAY_MEDIUM
        # Create a dummy background image (could be any ft.Control, here we use a simple Text)
        self.background_image = ft.Text("dummy background")
        self.main_app = DummyMainApp()
        self.dark_grey = "#23232A"
        self.flags_small_path = ""

@pytest.fixture
def dummy_view():
    return DummyView()

def test_update_standings(dummy_view):
    # Instantiate the StandingsPage with our dummy view
    page = StandingsPage(dummy_view)
    
    # Create a sample drivers DataFrame
    drivers_df = pd.DataFrame({
        "Driver": ["Driver A", "Driver B"],
        "Team": ["Team1", "Team1"],
        "Points": [0, 0],
        "Wins": [0, 0],
        "Podiums": [0, 0],
        "Fastest Laps": [0, 0],
        "DNFs": [0, 0],
        "Starts": [0, 0]
    })
    
    # Create a sample constructors DataFrame with a zero-indexed "Rnd" column
    constructors_df = pd.DataFrame({
        "Team": ["Team1", "Team2"],
        "Points": [0, 0],
        "Wins": [0, 0],
        "Podiums": [0, 0],
        "Fastest Laps": [0, 0],
        "DNFs": [0, 0],
        "Best Result": [None, None],
        "Rnd": [0, 1]  # 0-indexed round values
    })
    
    # Create dummy flag lists
    drivers_flags = ["flag1", "flag2"]
    team_flags = ["team_flag1", "team_flag2"]
    
    # Call the method under test
    page.update_standings(drivers_df, constructors_df, drivers_flags, team_flags)
    
    # Check that the drivers and constructors tables were created
    assert page.drivers_table is not None
    assert page.constructors_table is not None
    
    # Verify that the drivers and constructors tabs have been updated with the tables' list_view
    assert page.drivers_tab.content.content == page.drivers_table.list_view
    assert page.constructors_tab.content.content == page.constructors_table.list_view
    
    # Check that the drivers table's underlying data_table has as many rows as in drivers_df
    assert len(page.drivers_table.data_table.rows) == len(drivers_df)
    
    # Check that the constructors table's underlying data_table has as many rows as in constructors_df
    assert len(page.constructors_table.data_table.rows) == len(constructors_df)
    
    # For the constructors table, verify that the "Rnd" column values were incremented by 1
    # Assuming the "Rnd" column is the last column (index 7)
    for idx, row in enumerate(page.constructors_table.data_table.rows):
        # Retrieve the cell corresponding to the "Rnd" column
        rnd_cell = row.cells[7]
        # The cell contains an ft.Text widget; its value is stored in the "value" attribute.
        cell_value = rnd_cell.content.value
        # Expected value: if not NaN, add 1 to the original value from constructors_df
        expected_value = constructors_df.iloc[idx]["Rnd"]
        if pd.notna(expected_value):
            expected_value += 1
        assert cell_value == expected_value, f"Row {idx}: expected {expected_value}, got {cell_value}"
        
    # Ensure that the tabs' selected_index is reset to 0 after updating
    assert page.tabs.selected_index == 0
    
    # Verify that the dummy main_app's update method was called
    assert dummy_view.main_app.updated is True
