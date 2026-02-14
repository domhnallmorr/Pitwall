from app.core.rollover import SeasonRolloverManager
from app.core.engine import GameEngine
from app.models.state import GameState
from app.models.calendar import Calendar, Event, EventType
from app.models.driver import Driver
from app.models.team import Team


def create_end_of_season_state():
    """Creates a state near end of season (last event at week 3)."""
    teams = [
        Team(id=1, name="Team A", country="UK", driver1_id=1, driver2_id=2, points=50),
    ]
    drivers = [
        Driver(id=1, name="Driver A1", age=25, country="UK", team_id=1, points=30),
        Driver(id=2, name="Driver A2", age=28, country="FR", team_id=1, points=20),
    ]
    events = [
        Event(name="Race 1", week=1, type=EventType.RACE),
        Event(name="Race 2", week=3, type=EventType.RACE),
    ]
    calendar = Calendar(events=events, current_week=3)
    state = GameState(
        year=1998, teams=teams, drivers=drivers,
        calendar=calendar, circuits=[],
        events_processed=["1_Race 1", "3_Race 2"]
    )
    return state


def test_rollover_resets_points():
    state = create_end_of_season_state()
    manager = SeasonRolloverManager()
    result = manager.process_rollover(state)

    assert result["old_year"] == 1998
    assert result["new_year"] == 1999
    assert state.year == 1999
    assert state.drivers[0].points == 0
    assert state.drivers[1].points == 0
    assert state.teams[0].points == 0


def test_rollover_resets_calendar():
    state = create_end_of_season_state()
    manager = SeasonRolloverManager()
    manager.process_rollover(state)

    assert state.calendar.current_week == 1
    assert len(state.events_processed) == 0


def test_engine_triggers_rollover_after_last_event():
    state = create_end_of_season_state()
    engine = GameEngine()

    # Advance past last event (week 3 -> 4, which is past last event)
    summary = engine.advance_week(state)

    assert summary.get("season_rollover") is True
    assert summary["rollover_info"]["new_year"] == 1999
    assert summary["year"] == 1999
    assert summary["week"] == 1


def test_calendar_season_over_property():
    events = [Event(name="GP", week=5, type=EventType.RACE)]
    cal = Calendar(events=events, current_week=5)
    assert cal.season_over is False

    cal.current_week = 6
    assert cal.season_over is True


def test_rollover_increments_driver_ages():
    state = create_end_of_season_state()
    original_ages = [d.age for d in state.drivers]  # [25, 28]

    manager = SeasonRolloverManager()
    manager.process_rollover(state)

    for i, driver in enumerate(state.drivers):
        assert driver.age == original_ages[i] + 1
