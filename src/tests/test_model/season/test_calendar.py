import pytest
import pandas as pd
from unittest.mock import MagicMock
from pw_model.season.calendar import Calendar

@pytest.fixture
def mock_season():
    # Create a mock SeasonModel
    mock_model = MagicMock()
    mock_season = MagicMock()
    mock_season.model = mock_model
    return mock_season

@pytest.fixture
def sample_dataframe():
    # Create a sample dataframe to initialize the Calendar
    data = {
        "Week": [1, 3, 5],
        "Track": ["Monaco", "Silverstone", "Spa"],
        "Country": ["Monaco", "UK", "Belgium"],
        "Location": ["Monte Carlo", "Northamptonshire", "Stavelot"],
        "Winner": [None, None, None],
    }
    return pd.DataFrame(data)

@pytest.fixture
def calendar(mock_season, sample_dataframe):
    # Initialize the Calendar with mocked season and sample dataframe
	calendar = Calendar(mock_season, sample_dataframe)
	calendar.setup_new_season()
    
	return calendar

def test_race_weeks(calendar):
    assert calendar.race_weeks == [1, 3, 5]

def test_in_race_week(calendar):
    calendar.current_week = 1
    assert calendar.in_race_week is True
    calendar.current_week = 2
    assert calendar.in_race_week is False

def test_current_track_model(calendar):
    calendar.current_week = 1
    calendar.model.get_track_model.return_value.title = "Circuit de Monaco"
    assert calendar.current_track_model.title == "Circuit de Monaco"
    calendar.model.get_track_model.assert_called_once_with("Monaco")

def test_next_race(calendar):
    calendar.next_race_idx = 0
    calendar.model.get_track_model.return_value.title = "Circuit de Monaco"
    assert calendar.next_race == "Circuit de Monaco"

def test_next_race_week(calendar):
    calendar.next_race_idx = 1
    assert calendar.next_race_week == "3"

def test_setup_new_season(calendar):
    calendar.setup_new_season()
    assert calendar.current_week == 1
    assert calendar.next_race_idx == 0
    assert all(winner is None for winner in calendar.dataframe["Winner"])

def test_advance_one_week(calendar):
    calendar.current_week = 1
    calendar.advance_one_week()
    assert calendar.current_week == 2

def test_update_next_race(calendar):
    calendar.next_race_idx = 1
    calendar.update_next_race()
    assert calendar.next_race_idx == 2
    calendar.update_next_race()
    calendar.update_next_race()
    assert calendar.next_race_idx is None

def test_post_race_actions(calendar):
    calendar.next_race_idx = 0
    calendar.post_race_actions("Driver A")
    assert calendar.dataframe.iloc[0]["Winner"] == "Driver A"
    assert calendar.next_race_idx == 1
