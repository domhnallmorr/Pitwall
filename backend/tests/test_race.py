import random

from app.models.calendar import Calendar, Event, EventType
from app.models.circuit import Circuit
from app.models.driver import Driver
from app.models.state import GameState
from app.models.team import Team
from app.race.race_manager import RaceManager


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
    circuits = [
        Circuit(
            id=1,
            name="Test GP",
            country="Nowhere",
            location="Testville",
            laps=12,
            base_laptime_ms=84_000,
            length_km=4.2,
            overtaking_delta=1.2,
            power_factor=1.0,
        )
    ]
    return GameState(year=1998, teams=teams, drivers=drivers, calendar=calendar, circuits=circuits)


def test_simulate_race_returns_all_drivers_and_lap_history():
    state = create_race_state()
    manager = RaceManager()
    manager._pick_crash_count = lambda _: 0
    result = manager.simulate_race(state)

    assert len(result["results"]) == 4
    assert result["total_laps"] == 12
    assert len(result["lap_history"]) == 12
    assert result["lap_history"][0]["lap"] == 1
    assert len(result["lap_history"][0]["order"]) == 4
    positions = [r["position"] for r in result["results"]]
    assert positions == [1, 2, 3, 4]


def test_simulate_race_awards_points():
    state = create_race_state()
    manager = RaceManager()
    manager._pick_crash_count = lambda _: 0
    manager.simulate_race(state)

    total_driver_points = sum(d.points for d in state.drivers)
    total_team_points = sum(t.points for t in state.teams)

    assert total_driver_points == 23
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

    for driver in state.drivers:
        expected = before[driver.id] + (1 if driver.id in participant_ids else 0)
        assert driver.race_starts == expected


def test_simulate_race_increments_wins_for_winner_only():
    state = create_race_state()
    manager = RaceManager()
    manager._pick_crash_count = lambda _: 0

    before = {d.id: d.wins for d in state.drivers}
    result = manager.simulate_race(state)
    winner_id = result["results"][0]["driver_id"]

    for driver in state.drivers:
        expected = before[driver.id] + (1 if driver.id == winner_id else 0)
        assert driver.wins == expected


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
        state.drivers[0].speed = 100
        state.teams[0].car_speed = 95
        state.drivers[1].speed = 25
        state.drivers[2].speed = 30
        state.drivers[3].speed = 20
        state.teams[1].car_speed = 30
        manager._pick_crash_count = lambda _: 0

        result = manager.simulate_race(state)
        if result["results"][0]["driver_id"] == 1:
            wins_for_fastest += 1

    assert wins_for_fastest > 150


def test_simulate_race_can_include_crash_outs_and_marks_dnf():
    state = create_race_state()
    manager = RaceManager()
    manager._pick_crash_count = lambda _: 2

    result = manager.simulate_race(state)

    crash_results = [r for r in result["results"] if r.get("crash_out")]
    finished_results = [r for r in result["results"] if r.get("status") == "FINISHED"]

    assert len(crash_results) == 2
    assert len(finished_results) == 2
    assert all(r["position"] is None for r in crash_results)
    assert all(r["points"] == 0 for r in crash_results)
    assert len(result["crash_outs"]) == 2
    assert len(state.latest_race_incidents) == 2


def test_simulate_race_can_include_mechanical_outs_with_player_team():
    state = create_race_state()
    state.player_team_id = 1
    manager = RaceManager()
    manager._pick_crash_count = lambda _: 0
    random.seed(1)

    original_random = random.random
    values = iter([
        0.0,
        0.99,
        0.0,
        0.99,
    ])
    random.random = lambda: next(values)
    try:
        result = manager.simulate_race(state)
    finally:
        random.random = original_random

    assert state.teams[0].car_wear == 8
    mechanical_results = [r for r in result["results"] if r.get("mechanical_out")]
    assert len(mechanical_results) == 2
    assert all(r["status"] == "DNF" for r in mechanical_results)
    assert len(result["mechanical_outs"]) == 2


def test_simulate_race_marks_lapped_cars_on_timing_screen():
    state = create_race_state()
    state.circuits[0].laps = 40
    state.drivers[0].speed = 100
    state.teams[0].car_speed = 100
    state.drivers[3].speed = 5
    state.teams[1].car_speed = 5
    manager = RaceManager()
    manager._pick_crash_count = lambda _: 0

    result = manager.simulate_race(state)
    final_order = result["lap_history"][-1]["order"]

    assert any(row["gap_display"].endswith("Lap") or row["gap_display"].endswith("Laps") for row in final_order[1:])


def test_simulate_race_keeps_second_place_on_time_gap_early_in_race():
    state = create_race_state()
    manager = RaceManager()
    manager._pick_crash_count = lambda _: 0

    result = manager.simulate_race(state)
    lap_two_order = result["lap_history"][1]["order"]

    assert lap_two_order[1]["gap_display"].endswith('s')


def test_heavier_fuel_load_makes_lap_time_slower():
    state = create_race_state()
    manager = RaceManager()
    circuit = state.circuits[0]
    entrant = {
        "performance_weight": 50,
        "car_speed": 50,
        "fuel_kg": 100.0,
        "stint_laps": 0,
    }

    original_randint = random.randint
    random.randint = lambda a, b: 0
    try:
        heavy = manager._lap_time_ms(entrant, circuit)
        entrant["fuel_kg"] = 30.0
        light = manager._lap_time_ms(entrant, circuit)
    finally:
        random.randint = original_randint

    assert heavy > light


def test_tyre_wear_makes_lap_time_slower():
    state = create_race_state()
    manager = RaceManager()
    circuit = state.circuits[0]
    entrant = {
        "performance_weight": 50,
        "car_speed": 50,
        "fuel_kg": 0.0,
        "stint_laps": 0,
    }

    original_randint = random.randint
    random.randint = lambda a, b: 0
    try:
        fresh = manager._lap_time_ms(entrant, circuit)
        entrant["stint_laps"] = 12
        worn = manager._lap_time_ms(entrant, circuit)
    finally:
        random.randint = original_randint

    assert worn > fresh


def test_assign_strategy_generates_valid_pit_windows():
    state = create_race_state()
    manager = RaceManager()
    circuit = state.circuits[0]
    entrant = {"driver_id": 1}

    for _ in range(25):
        manager._assign_fuel_strategy(entrant, circuit)
        stops = entrant["planned_pit_laps"]
        assert entrant["planned_stops"] in (1, 2, 3)
        assert len(stops) == entrant["planned_stops"]
        assert stops == sorted(stops)
        assert all(1 < lap < circuit.laps - 1 for lap in stops)


def test_simulate_race_emits_pit_stop_events():
    state = create_race_state()
    manager = RaceManager()
    manager._pick_crash_count = lambda _: 0

    original_assign = manager._assign_fuel_strategy

    def forced_strategy(entrant, circuit):
        original_assign(entrant, circuit)
        entrant["planned_stops"] = 1
        entrant["planned_pit_laps"] = [4]
        entrant["completed_stops"] = 0
        entrant["fuel_kg"] = manager._fuel_for_stint(circuit, 4)

    manager._assign_fuel_strategy = forced_strategy
    result = manager.simulate_race(state)

    pit_events = [
        event
        for lap in result["lap_history"]
        for event in lap.get("events", [])
        if event.get("type") == "pit_stop"
    ]

    assert len(pit_events) == 4
    assert all(event["lap"] == 4 for event in pit_events)


def test_pit_stop_resets_tyre_wear_for_next_lap():
    state = create_race_state()
    state.circuits[0].laps = 6
    manager = RaceManager()
    manager._pick_crash_count = lambda _: 0

    original_assign = manager._assign_fuel_strategy

    def forced_strategy(entrant, circuit):
        original_assign(entrant, circuit)
        entrant["planned_stops"] = 1
        entrant["planned_pit_laps"] = [4]
        entrant["completed_stops"] = 0
        entrant["fuel_kg"] = 0
        entrant["stint_laps"] = 0

    manager._assign_fuel_strategy = forced_strategy
    original_randint = random.randint
    random.randint = lambda a, b: 0
    try:
        result = manager.simulate_race(state)
    finally:
        manager._assign_fuel_strategy = original_assign
        random.randint = original_randint

    driver_one_rows = [
        next(row for row in lap["order"] if row["driver_id"] == 1)
        for lap in result["lap_history"]
    ]
    lap4 = next(row for row in driver_one_rows if row["laps_completed"] == 4)
    lap5 = next(row for row in driver_one_rows if row["laps_completed"] == 5)

    assert lap4["last_lap_ms"] > lap5["last_lap_ms"]


def test_dirty_air_penalty_applies_within_threshold():
    manager = RaceManager()
    assert manager._dirty_air_penalty_ms(1_200, same_lap=True) == 500
    assert manager._dirty_air_penalty_ms(1_500, same_lap=True) == 500
    assert manager._dirty_air_penalty_ms(1_501, same_lap=True) == 0


def test_dirty_air_penalty_does_not_apply_off_lap():
    manager = RaceManager()
    assert manager._dirty_air_penalty_ms(500, same_lap=False) == 0


def test_overtake_attempt_requires_track_delta():
    manager = RaceManager()
    assert manager._should_attempt_pass(1_999, 2_000) is False
    assert manager._should_attempt_pass(2_000, 2_000) is True


def test_overtake_success_uses_roll():
    manager = RaceManager()
    original_randint = random.randint
    try:
        random.randint = lambda a, b: 200
        assert manager._pass_succeeds() is True
        random.randint = lambda a, b: 950
        assert manager._pass_succeeds() is False
    finally:
        random.randint = original_randint


def test_simulate_race_emits_overtake_event_when_pass_succeeds():
    state = create_race_state()
    state.circuits[0].overtaking_delta = 0
    manager = RaceManager()
    manager._pick_crash_count = lambda _: 0

    original_success = manager._pass_succeeds
    original_lap_time = manager._lap_time_ms
    original_assign = manager._assign_fuel_strategy
    original_grid = manager._grid_score

    def forced_success():
        return True

    lap_times = {
        1: [83_500, 84_500],
        2: [84_500, 83_000],
        3: [84_000, 84_000],
        4: [84_000, 84_000],
    }

    def forced_lap_time(entrant, circuit):
        sequence = lap_times.get(entrant["driver_id"], [84_000])
        index = entrant.get("laps_completed", 0)
        return sequence[min(index, len(sequence) - 1)]

    def forced_strategy(entrant, circuit):
        entrant["planned_stops"] = 0
        entrant["planned_pit_laps"] = []
        entrant["completed_stops"] = 0
        entrant["fuel_kg"] = 0

    def forced_grid(entrant):
        return {
            1: 1000,
            2: 900,
            3: 800,
            4: 700,
        }[entrant["driver_id"]]

    manager._pass_succeeds = forced_success
    manager._lap_time_ms = forced_lap_time
    manager._assign_fuel_strategy = forced_strategy
    manager._grid_score = forced_grid
    try:
        result = manager.simulate_race(state)
    finally:
        manager._pass_succeeds = original_success
        manager._lap_time_ms = original_lap_time
        manager._assign_fuel_strategy = original_assign
        manager._grid_score = original_grid

    overtake_events = [
        event
        for lap in result["lap_history"]
        for event in lap.get("events", [])
        if event.get("type") == "position_change"
    ]
    assert len(overtake_events) > 0
    assert result["lap_history"][1]["order"][0]["driver_id"] == 2
