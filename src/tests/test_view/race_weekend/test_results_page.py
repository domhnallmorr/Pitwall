import pytest
from unittest.mock import Mock
import pandas as pd
import matplotlib.pyplot as plt

from pw_view.race_weekend.results_window import ResultsWindow
from race_weekend_model.race_model_enums import SessionNames
from pw_controller.race_controller import RaceSessionData
import flet as ft

@pytest.fixture
def mock_view():
    # Create a mock of the View object
    view_mock = Mock()
    view_mock.page_header_style = "title"
    view_mock.results_background_image = ft.Image(src="background.png")
    view_mock.clicked_button_style = {"color": "red"}
    view_mock.main_app = Mock()
    view_mock.main_app.update = Mock()
    view_mock.race_weekend_window = ft.View()
    return view_mock

@pytest.fixture
def results_window(mock_view):
    return ResultsWindow(mock_view)

@pytest.fixture(autouse=True)
def cleanup_figures():
    yield
    plt.close("all")  # Close all figures after each test

def test_initialization(results_window):
    # Test if the ResultsWindow initializes correctly
    assert results_window.header_text.value == "Results"
    assert isinstance(results_window.controls, list)
    assert len(results_window.controls) > 0


def gen_dummy_data():
    sample_data = {
        "Position": [1, 2],
        "Driver": ["Driver A", "Driver B"],
        "Team": ["Team A", "Team B"],
        "Fastest Lap": [90000, 91000],
        "Gap to Leader": [0, 1000],
        "Gap Ahead": [1200, 1800],
        "Lap": [60, 60],
        "Status": ["Running", "Running"],
        "Lapped Status": [None, None],
        "Pit": [2, 1],
        "Grid": [1, 2]
    }
    standings_df = pd.DataFrame(sample_data)
    driver_flags = ["Australia", "Japan"]
    
    return standings_df, driver_flags

def test_setup_classification_table(results_window):
    standings_df, driver_flags = gen_dummy_data()
    results_window.setup_classification_table(standings_df, current_session=SessionNames.RACE, driver_flags=driver_flags)
    assert results_window.results_table is not None
    assert len(results_window.results_table.data_table.rows) == len(standings_df)

def test_ms_to_min_sec(results_window):
    assert results_window.ms_to_min_sec(65000) == "1:05.000"
    assert results_window.ms_to_min_sec(30000, interval=True) == "+30.000"

def test_display_classification(results_window):
    standings_df, driver_flags = gen_dummy_data()
    data: RaceSessionData = {
        "current_session": SessionNames.QUALIFYING,
        "standings_df": standings_df,
        "driver_flags": driver_flags
    }
    results_window.update_page(data)
    # Instead of testing display_classification(), verify that the classification tab is set up correctly
    assert results_window.classification_tab.content.content == results_window.results_table.list_view
    # Verify that for qualifying session, only classification tab is shown
    assert len(results_window.tabs.tabs) == 1
    assert results_window.tabs.tabs[0] == results_window.classification_tab

