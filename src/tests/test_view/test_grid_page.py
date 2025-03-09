import pytest
import pandas as pd
import flet as ft
from pw_view.grid_page import GridPage

# Dummy main_app that tracks update calls
class DummyMainApp:
    def __init__(self):
        self.update_called = False

    def update(self):
        self.update_called = True

# Dummy view with the minimal attributes required by GridPage
class DummyView:
    def __init__(self):
        self.page_header_style = ft.TextThemeStyle.DISPLAY_MEDIUM
        self.background_image = ft.Image(src="dummy_image.png")
        self.main_app = DummyMainApp()
        self.dark_grey = "#23232A"

@pytest.fixture
def dummy_view():
    return DummyView()

@pytest.fixture
def sample_dataframes():
    # Sample dataframe for grid_this_year_df
    df_this_year = pd.DataFrame({
        "Column1": ["row1_col1", "row2_col1"],
        "Column2": ["row1_col2", "row2_col2"]
    })
    # Sample dataframe for grid_next_year_announced_df
    df_next_year = pd.DataFrame({
        "Column1": ["row1_col1_next", "row2_col1_next"],
        "Column2": ["row1_col2_next", "row2_col2_next"]
    })
    return df_this_year, df_next_year

def test_update_page(dummy_view, sample_dataframes):
    df_this_year, df_next_year = sample_dataframes

    # Create the GridPage instance using the dummy view.
    grid_page_obj = GridPage(dummy_view)

    # Check initial placeholder tab texts
    assert grid_page_obj.current_year_tab.text == "1998"
    assert grid_page_obj.next_year_tab.text == "1999"

    # Reset the dummy main_app update flag.
    dummy_view.main_app.update_called = False

    # Call update_page with a specific year and the sample dataframes.
    grid_page_obj.update_page(2022, df_this_year, df_next_year)

    # Verify that the tab texts are updated correctly.
    assert grid_page_obj.current_year_tab.text == "2022"
    assert grid_page_obj.next_year_tab.text == "2023"

    # Verify that the content of each tab is updated with the corresponding list_view.
    list_view_this_year = grid_page_obj.grid_this_year_table.list_view
    list_view_next_year = grid_page_obj.grid_next_year_table.list_view
    assert grid_page_obj.current_year_tab.content.content == list_view_this_year
    assert grid_page_obj.next_year_tab.content.content == list_view_next_year

    # Verify that the tabs' selected index is reset to 0.
    assert grid_page_obj.tabs.selected_index == 0

    # Verify that the view.main_app.update() was called.
    assert dummy_view.main_app.update_called is True
