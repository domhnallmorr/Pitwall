from unittest.mock import Mock, patch

from app.commands.game_commands import (
    handle_load_roster,
    handle_start_career,
    load_default_state,
)
from app.models.calendar import Calendar, Event, EventType
from app.models.state import GameState
from app.models.team import Team


def create_state() -> GameState:
    return GameState(
        year=1998,
        teams=[Team(id=1, name="Warrick", country="United Kingdom", balance=1_000_000)],
        drivers=[],
        calendar=Calendar(events=[Event(name="Albert Park", week=10, type=EventType.RACE)], current_week=1),
        circuits=[],
    )


@patch("app.commands.game_commands.load_roster")
def test_load_default_state_populates_all_roster_groups(mock_load_roster):
    mock_load_roster.return_value = (
        [Team(id=1, name="Warrick", country="United Kingdom")],
        [],
        1998,
        [Event(name="Albert Park", week=10, type=EventType.RACE)],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    state = load_default_state()
    assert state.year == 1998
    assert len(state.teams) == 1
    assert state.calendar.current_week == 1


@patch("app.commands.game_commands.GridManager.get_grid_json", return_value='[{"Team":"Warrick"}]')
@patch("app.commands.game_commands.load_default_state")
def test_handle_load_roster_success(mock_load_default_state, mock_grid_json):
    logger = Mock()
    mock_load_default_state.return_value = create_state()
    state, response = handle_load_roster(logger)
    assert state is not None
    assert response["status"] == "success"
    assert response["data"][0]["Team"] == "Warrick"


@patch("app.commands.game_commands.load_default_state", side_effect=RuntimeError("load failed"))
def test_handle_load_roster_error(mock_load_default_state):
    logger = Mock()
    state, response = handle_load_roster(logger)
    assert state is None
    assert response["status"] == "error"
    assert response["message"] == "load failed"
    logger.error.assert_called_once()


def test_handle_start_career_team_not_found_returns_error():
    logger = Mock()
    state = create_state()
    next_state, response = handle_start_career(state, logger, team_name="Nope")
    assert next_state is state
    assert response["status"] == "error"
    assert "not found" in response["message"]


@patch("app.commands.game_commands.AICarDevelopmentManager.generate_for_season")
@patch("app.commands.game_commands.CommercialManagerTransferManager.recompute_ai_signings")
@patch("app.commands.game_commands.TransferManager.recompute_ai_signings")
@patch("app.commands.game_commands.GridManager.capture_season_snapshot")
@patch("app.commands.game_commands.RetirementManager.mark_final_season_drivers", return_value=[])
@patch("app.commands.game_commands.PrizeMoneyManager.assign_initial_entitlement_from_roster_order")
def test_handle_start_career_success_without_retirement_email(
    mock_prize,
    mock_retirements,
    mock_grid_capture,
    mock_driver_signings,
    mock_cm_signings,
    mock_car_updates,
):
    logger = Mock()
    state = create_state()
    next_state, response = handle_start_career(state, logger, team_name="Warrick")
    assert response["status"] == "success"
    assert response["type"] == "game_started"
    assert next_state.player_team_id == 1
    subjects = [e.subject for e in next_state.emails]
    assert "Welcome to Pitwall" in subjects
    assert not any(s.startswith("Retirement Watch:") for s in subjects)


@patch("app.commands.game_commands.load_default_state", side_effect=RuntimeError("boom"))
def test_handle_start_career_exception_branch(mock_load_default_state):
    logger = Mock()
    state, response = handle_start_career(None, logger, team_name="Warrick")
    assert state is None
    assert response["status"] == "error"
    assert response["message"] == "boom"
    logger.error.assert_called_once()
