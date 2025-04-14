import pytest
import pandas as pd
from unittest.mock import MagicMock

from pw_model.pw_model_enums import CalendarState
from pw_model.season.calendar import Calendar

@pytest.fixture
def mock_model():
    """
    Return a minimal mock of the base Model that can return a mocked TrackModel.
    """
    model = MagicMock()
    # Mocked track that gets returned by model.get_track_model(...)
    mock_track = MagicMock()
    mock_track.title = "Mock Track Title"
    model.get_track_model.return_value = mock_track
    return model

@pytest.fixture
def mock_season(mock_model):
    """
    Return a minimal mock of SeasonModel so we can pass it into Calendar.
    """
    season = MagicMock()
    season.model = mock_model
    return season

@pytest.fixture
def sample_calendar_df():
    """
    Provide a small DataFrame that includes both testing and race sessions.
    Column names match the Calendar class requirements:
    "Week", "Track", "Country", "Location", "Winner", "SessionType"
    """
    data = {
        "Week": [1, 2, 3, 4, 5],
        "Track": ["Melbourne", "Bahrain", "China", "Imola", "Monaco"],
        "Country": ["Australia", "Bahrain", "China", "Italy", "Monaco"],
        "Location": ["Albert Park", "Sakhir", "Shanghai", "Imola", "Monte Carlo"],
        "Winner": [None, None, None, None, None],
        "SessionType": ["Testing", "Race", "Testing", "Race", "Race"]
    }
    return pd.DataFrame(data)


@pytest.fixture
def calendar_obj(mock_season, sample_calendar_df):
    """
    Create a Calendar instance with the mock season and sample DataFrame.
    We’ll re-use this in multiple tests.
    """
    return Calendar(mock_season, sample_calendar_df)


def test_calendar_init(calendar_obj):
    """
    Confirm that initialization sets expected defaults.
    """
    assert calendar_obj.state == CalendarState.PRE_SEASON
    assert calendar_obj.dataframe.shape[0] == 5
    # By default, we haven't called setup_new_season yet, so current_week might not exist yet
    # or you might want to check that it’s not yet set:
    with pytest.raises(AttributeError):
        _ = calendar_obj.current_week


def test_setup_new_season(calendar_obj):
    """
    Test that setup_new_season properly initializes current_week, next_race_idx, etc.
    """
    calendar_obj.setup_new_season()
    assert calendar_obj.current_week == 1
    assert calendar_obj.next_race_idx == 0
    assert calendar_obj.state == CalendarState.PRE_SEASON
    # Confirm that the winners column got cleared (or set to None)
    # in practice it should already be None in the fixture, but we can still test
    assert calendar_obj.dataframe["Winner"].isnull().all()


def test_race_and_testing_weeks_properties(calendar_obj):
    """
    Check that race_weeks and testing_weeks come out as expected from sample_calendar_df.
    """
    # Our fixture data has races at weeks 2, 4, 5 and testing at weeks 1, 3
    assert calendar_obj.race_weeks == [2, 4, 5]
    assert calendar_obj.testing_weeks == [1, 3]
    assert calendar_obj.number_of_races == 3


def test_current_track_model(calendar_obj, mock_model):
    """
    Verify that current_track_model grabs the next upcoming race
    and calls model.get_track_model with the correct argument.
    """
    # Not calling setup_new_season yet means we have no current_week set.
    # The code tries to see if row["Week"] >= current_week. Let’s do:
    calendar_obj.setup_new_season()
    # current_week=1, so the “next upcoming race” is the row with Week >= 1, which is the first row (Week 1).
    # The track for that row is "Melbourne".
    current_track = calendar_obj.current_track_model
    # Make sure get_track_model was called with "Melbourne"
    mock_model.get_track_model.assert_called_once_with("Melbourne")
    # And we return the mocked track with title "Mock Track Title"
    assert current_track.title == "Mock Track Title"


def test_in_testing_week_property(calendar_obj):
    calendar_obj.setup_new_season()
    # start week=1, which is testing
    assert calendar_obj.in_testing_week is True
    # Now if we jump to week=2:
    calendar_obj.current_week = 2
    assert calendar_obj.in_testing_week is False


def test_session_type_property(calendar_obj):
    calendar_obj.setup_new_season()
    assert calendar_obj.session_type == "Testing"  # because week=1 is Testing
    calendar_obj.current_week = 2
    assert calendar_obj.session_type == "Race"
    calendar_obj.current_week = 99  # some random that isn't in race_weeks or testing_weeks
    assert calendar_obj.session_type == "None"


def test_next_race_info(calendar_obj, sample_calendar_df, mock_model):
    """
    Check next_race and next_race_week properties for both the normal case
    and for the post-season scenario (when next_race_idx is None).
    """
    calendar_obj.setup_new_season()
    assert calendar_obj.next_race_idx == 0

    # The next race in the DataFrame is at index=1 (week=2).
    # But next_race_idx is 0 initially, so that’s the row with Week=1 (Testing).
    # However, we only consider the row 0 if its SessionType is "Race"? Let’s see:
    # Actually, the code sets next_race_idx=0 on setup. The “next_race” property references
    # data at that row, so it might be "Melbourne"? Let’s confirm:
    expected_first_track = sample_calendar_df.loc[0, "Track"]
    # We'll call the property, which asks the mock Model for that track’s title
    next_race_title = calendar_obj.next_race
    assert next_race_title == "Mock Track Title"
    assert calendar_obj.next_race_week == "1"

    # If we simulate finishing that event with post_race_actions:
    calendar_obj.post_race_actions("Driver X")
    # next_race_idx should now be 1
    assert calendar_obj.next_race_idx == 1
    # So next race is the second row: week=2
    assert calendar_obj.next_race_week == "2"

    # Eventually if we keep updating next_race_idx past the last row, it becomes None
    # Let’s skip to the final row for demonstration
    calendar_obj.next_race_idx = len(sample_calendar_df) - 1
    calendar_obj.post_race_actions("Final Winner")
    assert calendar_obj.next_race_idx is None
    assert calendar_obj.next_race == "Post Season"
    assert calendar_obj.next_race_week == "-"


def test_advance_one_week_states(calendar_obj):
    """
    Make sure the CalendarState updates properly as we advance weeks.
    """
    calendar_obj.setup_new_season()
    # Initially we are in PRE_SEASON. Week=1 is Testing => pre-season testing
    calendar_obj.advance_one_week()
    # Because we just advanced from week=1->2, let's see how the code transitions the state.
    # The code checks old state, sees race_weeks, etc.
    # Let’s walk through a few steps:
    assert calendar_obj.current_week == 2  # advanced from 1 to 2

    # Checking how the code is structured:
    # If the week is in race_weeks, it sets RACE_WEEK.
    # Our sample data has race_weeks = [2, 4, 5].
    assert calendar_obj.state == CalendarState.RACE_WEEK

    # Advance to next week
    calendar_obj.advance_one_week()  # moves from 2->3
    # Week=3 is Testing, so state becomes IN_SEASON_TESTING or PRE_SEASON_TESTING
    # But at this point, we’re definitely in-season, so:
    assert calendar_obj.current_week == 3
    assert calendar_obj.state == CalendarState.IN_SEASON_TESTING

    # Then go from week=3->4
    calendar_obj.advance_one_week()
    assert calendar_obj.current_week == 4
    assert calendar_obj.state == CalendarState.RACE_WEEK

    # Then from week=4->5
    calendar_obj.advance_one_week()
    # That’s also a Race
    assert calendar_obj.current_week == 5
    assert calendar_obj.state == CalendarState.RACE_WEEK

    # Then from week=5->6
    calendar_obj.advance_one_week()
    # Our last race was week=5, so week=6 is beyond the final race => POST_SEASON
    assert calendar_obj.state == CalendarState.POST_SEASON


def test_post_race_actions_updates_winner(calendar_obj):
    """
    Check that post_race_actions updates the 'Winner' column and sets the right state.
    """
    calendar_obj.setup_new_season()
    # next_race_idx=0 => the row for week=1
    calendar_obj.post_race_actions("Test Winner")
    # We expect that row 0 in the DF now has 'Winner' == 'Test Winner'
    assert calendar_obj.dataframe.at[0, "Winner"] == "Test Winner"
    # And next_race_idx got incremented
    assert calendar_obj.next_race_idx == 1
    # And the state should be POST_RACE
    assert calendar_obj.state == CalendarState.POST_RACE

    # If we do it again:
    calendar_obj.post_race_actions("Another Winner")
    # row=1 now gets the winner
    assert calendar_obj.dataframe.at[1, "Winner"] == "Another Winner"
    # next_race_idx = 2
    assert calendar_obj.next_race_idx == 2
    assert calendar_obj.state == CalendarState.POST_RACE
