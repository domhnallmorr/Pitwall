import pytest
from unittest.mock import Mock, MagicMock
import pandas as pd
import flet as ft
from pw_view.grid_page import GridPage
from pw_view.custom_widgets.custom_datatable import CustomDataTable

@pytest.fixture
def mock_view():
    """Fixture to mock the View object."""
    view = Mock()
    view.page_header_style = "headlineLarge"
    view.clicked_button_style = ft.ButtonStyle(color=ft.Colors.RED)
    view.main_app = Mock()
    view.main_app.update = Mock()
    view.background_image = ft.Container()  # Mock background image
    return view

@pytest.fixture
def sample_dataframes():
    """Fixture to provide sample dataframes for testing."""
    df_this_year = pd.DataFrame({"Col1": [1, 2], "Col2": ["A", "B"]})
    df_next_year = pd.DataFrame({"Col3": [3, 4], "Col4": ["C", "D"]})
    return df_this_year, df_next_year

@pytest.fixture
def grid_page(mock_view):
    """Fixture to create a GridPage instance."""
    return GridPage(view=mock_view)

def test_initialization(grid_page):
    """Test if the GridPage is initialized correctly."""
    assert grid_page.view is not None
    assert isinstance(grid_page.current_year_btn, ft.TextButton)
    assert isinstance(grid_page.next_year_btn, ft.TextButton)
    assert grid_page.current_year_btn.text == "1998"
    assert grid_page.next_year_btn.text == "1999"

def test_reset_tab_buttons(grid_page):
    """Test the reset_tab_buttons method."""
    grid_page.current_year_btn.style = ft.ButtonStyle(color=ft.Colors.GREEN)
    grid_page.next_year_btn.style = ft.ButtonStyle(color=ft.Colors.BLUE)
    grid_page.reset_tab_buttons()
    assert grid_page.current_year_btn.style is None
    assert grid_page.next_year_btn.style is None

def test_change_display(grid_page, sample_dataframes):
    """Test the change_display method."""
    df_this_year, df_next_year = sample_dataframes
    grid_page.update_page(2023, df_this_year, df_next_year)
    
    mock_event = Mock()
    mock_event.control.data = "next"
    grid_page.change_display(mock_event)
    assert grid_page.next_year_btn.style == grid_page.view.clicked_button_style
    assert grid_page.current_year_btn.style is None

    mock_event.control.data = "current"
    grid_page.change_display(mock_event)
    assert grid_page.current_year_btn.style == grid_page.view.clicked_button_style
    assert grid_page.next_year_btn.style is None

def test_update_page(grid_page, sample_dataframes):
    """Test the update_page method with sample data."""
    df_this_year, df_next_year = sample_dataframes
    grid_page.update_page(2023, df_this_year, df_next_year)
    
    # Verify button text updates
    assert grid_page.current_year_btn.text == "2023"
    assert grid_page.next_year_btn.text == "2024"
    
    # Verify DataTable for this year
    assert isinstance(grid_page.grid_this_year_table, CustomDataTable)
    assert len(grid_page.grid_this_year_table.data_table.rows) == len(df_this_year)

    # Verify DataTable for next year
    assert isinstance(grid_page.grid_next_year_table, CustomDataTable)
    assert len(grid_page.grid_next_year_table.data_table.rows) == len(df_next_year)
