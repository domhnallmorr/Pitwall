from app.race.stats_manager import DriverStatsManager
from app.models.state import GameState
from app.models.calendar import Calendar, Event, EventType
from app.models.driver import Driver
from app.models.team import Team
from app.models.circuit import Circuit


def create_state_with_race_event() -> GameState:
    return GameState(
        year=1998,
        teams=[Team(id=1, name="Warrick", country="United Kingdom", driver1_id=1, driver2_id=2)],
        drivers=[
            Driver(id=1, name="John Newhouse", age=27, country="Canada", team_id=1, race_starts=33, wins=11),
            Driver(id=2, name="Henrik Friedrich", age=31, country="Germany", team_id=1, race_starts=65, wins=1),
        ],
        calendar=Calendar(events=[Event(name="Albert Park", week=10, type=EventType.RACE)], current_week=10),
        circuits=[
            Circuit(
                id=1,
                name="Albert Park",
                country="Australia",
                location="Melbourne",
                laps=58,
                base_laptime_ms=84000,
                length_km=5.303,
                overtaking_delta=1200,
                power_factor=6,
            )
        ],
    )


def test_apply_race_results_upserts_same_round_without_duplicate_entries():
    state = create_state_with_race_event()
    manager = DriverStatsManager()

    manager.apply_race_results(state, [{"driver_id": 1, "position": 2}, {"driver_id": 2, "position": 1}])
    manager.apply_race_results(state, [{"driver_id": 1, "position": 1}, {"driver_id": 2, "position": 2}])

    season = state.driver_season_results[1998]
    assert len(season[1]) == 1
    assert len(season[2]) == 1
    assert season[1][0]["round"] == 1
    assert season[1][0]["position"] == 1


def test_apply_race_results_without_current_event_skips_result_history():
    state = create_state_with_race_event()
    state.calendar.current_week = 1  # no event at this week
    manager = DriverStatsManager()

    manager.apply_race_results(state, [{"driver_id": 1, "position": 1}])

    assert state.drivers[0].race_starts == 34
    assert state.drivers[0].wins == 12
    assert state.driver_season_results.get(1998, {}) == {}


def test_apply_race_results_persists_status_for_dnf_entries():
    state = create_state_with_race_event()
    manager = DriverStatsManager()

    manager.apply_race_results(state, [{"driver_id": 1, "position": None, "status": "DNF"}])

    season = state.driver_season_results[1998]
    assert season[1][0]["status"] == "DNF"
    assert season[1][0]["position"] is None
