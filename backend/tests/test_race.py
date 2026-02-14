import pytest
from app.race.race_manager import RaceManager, POINTS_TABLE
from app.models.state import GameState
from app.models.calendar import Calendar, Event, EventType
from app.models.driver import Driver
from app.models.team import Team


def create_race_state():
    """Creates a minimal state with 2 teams and 4 drivers for testing."""
    teams = [
        Team(id=1, name="Team A", country="UK", driver1_id=1, driver2_id=2, points=0),
        Team(id=2, name="Team B", country="IT", driver1_id=3, driver2_id=4, points=0),
    ]
    drivers = [
        Driver(id=1, name="Driver A1", age=25, country="UK", team_id=1, points=0),
        Driver(id=2, name="Driver A2", age=28, country="FR", team_id=1, points=0),
        Driver(id=3, name="Driver B1", age=30, country="DE", team_id=2, points=0),
        Driver(id=4, name="Driver B2", age=22, country="BR", team_id=2, points=0),
    ]
    event = Event(name="Test GP", week=1, type=EventType.RACE)
    calendar = Calendar(events=[event], current_week=1)
    return GameState(year=1998, teams=teams, drivers=drivers, calendar=calendar, circuits=[])


def test_simulate_race_returns_all_drivers():
    state = create_race_state()
    manager = RaceManager()
    result = manager.simulate_race(state)

    assert len(result["results"]) == 4
    positions = [r["position"] for r in result["results"]]
    assert positions == [1, 2, 3, 4]


def test_simulate_race_awards_points():
    state = create_race_state()
    manager = RaceManager()
    result = manager.simulate_race(state)

    # Total points awarded should equal sum of top positions available
    # With 4 drivers: P1=10, P2=6, P3=4, P4=3 = 23
    total_driver_points = sum(d.points for d in state.drivers)
    total_team_points = sum(t.points for t in state.teams)

    assert total_driver_points == 23  # 10+6+4+3
    assert total_team_points == 23


def test_simulate_race_marks_event_processed():
    state = create_race_state()
    manager = RaceManager()
    manager.simulate_race(state)

    assert len(state.events_processed) == 1
    assert "1_Test GP" in state.events_processed


def test_simulate_race_winner_gets_10_points():
    state = create_race_state()
    manager = RaceManager()
    result = manager.simulate_race(state)

    winner = result["results"][0]
    assert winner["points"] == 10
