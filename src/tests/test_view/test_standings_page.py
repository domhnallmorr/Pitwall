import pytest
import pandas as pd
import flet as ft
from unittest.mock import MagicMock
from pw_view.standings_page import StandingsPage

@pytest.fixture
def mock_view():
    """Fixture for creating a mock View object."""
    mock_view = MagicMock()
    mock_view.page_header_style = "H1"
    mock_view.main_app = MagicMock()
    mock_view.clicked_button_style = "clicked_style"
    mock_view.background_image = MagicMock()
    return mock_view

@pytest.fixture
def standings_page(mock_view):
    """Fixture for initializing the StandingsPage."""
    return StandingsPage(view=mock_view)

def test_initialization(standings_page):
    """Test if the StandingsPage initializes correctly."""
    assert standings_page.drivers_table is not None
    assert standings_page.buttons_row is not None

def test_display_drivers(standings_page, mock_view):
    """Test the display_drivers method."""
    drivers_df, constructors_df = update_standings(standings_page)
    standings_page.display_drivers(None)
    assert standings_page.drivers_btn.style == mock_view.clicked_button_style

def test_display_constructors(standings_page, mock_view):
    """Test the display_constructors method."""
    drivers_df, constructors_df = update_standings(standings_page)
    standings_page.display_constructors(None)
    assert standings_page.contructors_btn.style == mock_view.clicked_button_style

def test_update_standings(standings_page):
    drivers_df, constructors_df = update_standings(standings_page)

    assert standings_page.drivers_table is not None
    assert len(standings_page.drivers_table.rows) == len(drivers_df)

    assert standings_page.constructors_table is not None
    assert len(standings_page.constructors_table.rows) == len(constructors_df)

def test_reset_tab_buttons(standings_page):
    """Test the reset_tab_buttons method."""
    standings_page.reset_tab_buttons()
    assert standings_page.drivers_btn.style is None
    assert standings_page.contructors_btn.style is None

def update_standings(standings_page):
    """Test the update_standings method."""
    drivers_data = {
        "Driver": ["Lewis Hamilton", "Max Verstappen"],
        "Team": ["Mercedes", "Red Bull"],
        "Points": [250, 245],
    }
    constructors_data = {
        "Constructor": ["Mercedes", "Red Bull"],
        "Points": [500, 490],
    }

    drivers_df = pd.DataFrame(drivers_data)
    constructors_df = pd.DataFrame(constructors_data)

    standings_page.update_standings(drivers_standings_df=drivers_df, constructors_standings_df=constructors_df)
    
    return drivers_df, constructors_df