from unittest.mock import patch

from app.core.engine import GameEngine
from app.core.grid import GridManager
from app.core.transfers import TransferManager
from app.models.calendar import Calendar, Event, EventType
from app.models.driver import Driver
from app.models.state import GameState
from app.models.team import Team


def create_transfer_state() -> GameState:
    teams = [
        Team(id=1, name="Player Team", country="UK", driver1_id=1, driver2_id=2),
        Team(id=2, name="AI Team", country="IT", driver1_id=3, driver2_id=4),
    ]
    drivers = [
        Driver(id=1, name="Player Expiring", age=30, country="UK", team_id=1, contract_length=1),
        Driver(id=2, name="Player Secure", age=29, country="UK", team_id=1, contract_length=3),
        Driver(id=3, name="AI Expiring", age=28, country="IT", team_id=2, contract_length=1),
        Driver(id=4, name="AI Secure", age=27, country="IT", team_id=2, contract_length=2),
        Driver(id=5, name="Free Agent", age=24, country="DE", team_id=None, contract_length=0),
    ]
    calendar = Calendar(events=[Event(name="Finale", week=52, type=EventType.RACE)], current_week=1)
    return GameState(
        year=1998,
        teams=teams,
        drivers=drivers,
        calendar=calendar,
        circuits=[],
        player_team_id=1,
    )


@patch("app.core.transfers.random.shuffle", side_effect=lambda x: None)
@patch("app.core.transfers.random.randint", return_value=6)
@patch("app.core.transfers.random.choice", side_effect=lambda choices: choices[0])
def test_recompute_ai_signings_plans_only_ai_vacancies(mock_choice, mock_randint, mock_shuffle):
    state = create_transfer_state()

    planned = TransferManager().recompute_ai_signings(state)

    assert len(planned) == 1
    assert planned[0]["team_id"] == 2
    assert planned[0]["seat"] == "driver1_id"
    assert planned[0]["status"] == "planned"
    assert planned[0]["announce_week"] == 6


def test_publish_due_announcements_moves_planned_to_announced_and_emails():
    state = create_transfer_state()
    state.calendar.current_week = 3
    state.planned_ai_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "driver1_id",
            "seat_label": "Driver 1",
            "driver_id": 5,
            "driver_name": "Free Agent",
            "announce_week": 3,
            "announce_year": 1998,
            "status": "planned",
        }
    ]

    published = TransferManager().publish_due_announcements(state)

    assert len(published) == 1
    assert len(state.planned_ai_signings) == 0
    assert len(state.announced_ai_signings) == 1
    assert state.announced_ai_signings[0]["status"] == "announced"
    assert any(e.subject == "Transfer Confirmed: Free Agent to AI Team" for e in state.emails)


def test_engine_advance_week_publishes_due_transfer_announcements():
    state = create_transfer_state()
    state.planned_ai_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "driver1_id",
            "seat_label": "Driver 1",
            "driver_id": 5,
            "driver_name": "Free Agent",
            "announce_week": 2,
            "announce_year": 1998,
            "status": "planned",
        }
    ]

    GameEngine().advance_week(state)

    assert len(state.announced_ai_signings) == 1
    assert len(state.planned_ai_signings) == 0
    assert any(e.subject == "Transfer Confirmed: Free Agent to AI Team" for e in state.emails)


def test_grid_next_year_projection_uses_announced_transfer_signings():
    state = create_transfer_state()
    state.announced_ai_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "driver1_id",
            "seat_label": "Driver 1",
            "driver_id": 5,
            "driver_name": "Free Agent",
            "announce_week": 2,
            "announce_year": 1998,
            "status": "announced",
        }
    ]

    df = GridManager().get_grid_dataframe(state, year=1999)
    row = df[df["Team"] == "AI Team"].iloc[0]
    assert row["Driver1"] == "Free Agent"
    assert row["Driver1Country"] == "DE"
    assert row["Driver2"] == "AI Secure"


@patch("app.core.transfers.random.shuffle", side_effect=lambda x: None)
@patch("app.core.transfers.random.choice", side_effect=lambda choices: choices[0])
def test_recompute_ai_signings_announce_after_first_race(mock_choice, mock_shuffle):
    state = create_transfer_state()
    state.calendar.events = [
        Event(name="Preseason Test", week=5, type=EventType.TEST),
        Event(name="Round 1", week=10, type=EventType.RACE),
        Event(name="Round 2", week=12, type=EventType.RACE),
    ]
    state.calendar.current_week = 1

    planned = TransferManager().recompute_ai_signings(state)

    assert len(planned) == 1
    assert planned[0]["announce_week"] >= 11
