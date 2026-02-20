import pytest
import random
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
    manager._pick_crash_count = lambda _: 0
    result = manager.simulate_race(state)

    assert len(result["results"]) == 4
    positions = [r["position"] for r in result["results"]]
    assert positions == [1, 2, 3, 4]


def test_simulate_race_awards_points():
    state = create_race_state()
    manager = RaceManager()
    manager._pick_crash_count = lambda _: 0
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
    manager._pick_crash_count = lambda _: 0
    manager.simulate_race(state)

    assert len(state.events_processed) == 1
    assert "1_Test GP" in state.events_processed


def test_simulate_race_winner_gets_10_points():
    state = create_race_state()
    manager = RaceManager()
    manager._pick_crash_count = lambda _: 0
    result = manager.simulate_race(state)

    winner = result["results"][0]
    assert winner["points"] == 10


def test_simulate_race_increments_race_starts_for_participants():
    state = create_race_state()
    manager = RaceManager()
    manager._pick_crash_count = lambda _: 0

    before = {d.id: d.race_starts for d in state.drivers}
    result = manager.simulate_race(state)
    participant_ids = {r["driver_id"] for r in result["results"]}

    for d in state.drivers:
        expected = before[d.id] + (1 if d.id in participant_ids else 0)
        assert d.race_starts == expected


def test_simulate_race_increments_wins_for_winner_only():
    state = create_race_state()
    manager = RaceManager()
    manager._pick_crash_count = lambda _: 0

    before = {d.id: d.wins for d in state.drivers}
    result = manager.simulate_race(state)
    winner_id = result["results"][0]["driver_id"]

    for d in state.drivers:
        expected = before[d.id] + (1 if d.id == winner_id else 0)
        assert d.wins == expected


def test_simulate_race_records_driver_season_results():
    state = create_race_state()
    manager = RaceManager()
    manager._pick_crash_count = lambda _: 0
    result = manager.simulate_race(state)

    assert state.year in state.driver_season_results
    season = state.driver_season_results[state.year]
    assert len(season) == 4

    for row in result["results"]:
        driver_id = row["driver_id"]
        entries = season.get(driver_id, [])
        assert len(entries) == 1
        assert entries[0]["position"] == row["position"]
        assert entries[0]["event_name"] == "Test GP"
        assert entries[0]["round"] == 1


def test_performance_weight_blends_driver_and_car_speed():
    manager = RaceManager()
    assert manager._get_performance_weight(100, 100) == 100
    assert manager._get_performance_weight(80, 40) == 66
    assert manager._get_performance_weight(0, 0) == 1


def test_simulate_race_weighting_favors_faster_driver_and_car():
    manager = RaceManager()
    random.seed(12345)
    wins_for_fastest = 0
    runs = 250

    for _ in range(runs):
        state = create_race_state()
        # Strong favorite: Driver A1 in a fast car.
        state.drivers[0].speed = 100
        state.teams[0].car_speed = 95

        # Keep everyone else slower.
        state.drivers[1].speed = 25
        state.drivers[2].speed = 30
        state.drivers[3].speed = 20
        state.teams[1].car_speed = 30
        manager._pick_crash_count = lambda _: 0

        result = manager.simulate_race(state)
        if result["results"][0]["driver_id"] == 1:
            wins_for_fastest += 1

    assert wins_for_fastest > 120


def test_simulate_race_can_include_crash_outs_and_marks_dnf():
    state = create_race_state()
    manager = RaceManager()
    manager._pick_crash_count = lambda _: 2

    result = manager.simulate_race(state)

    crash_results = [r for r in result["results"] if r.get("status") == "DNF"]
    finished_results = [r for r in result["results"] if r.get("status") == "FINISHED"]

    assert len(crash_results) == 2
    assert len(finished_results) == 2
    assert all(r["position"] is None for r in crash_results)
    assert all(r["points"] == 0 for r in crash_results)
    assert len(result["crash_outs"]) == 2
    assert len(state.latest_race_incidents) == 2
