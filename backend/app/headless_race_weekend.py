"""
Headless Single Race Weekend Simulation
Runs forward to one race weekend, then prints qualifying, lap-one events,
and the final classification.

Usage:
    uv run python -m app.headless_race_weekend [target_week]

Default:
    first race weekend of the starting season
"""

import sys

from app.core.engine import GameEngine
from app.core.roster import load_roster
from app.models.calendar import Calendar, EventType
from app.models.state import GameState
from app.race.race_manager import RaceManager


def build_headless_state() -> GameState:
    (
        teams,
        drivers,
        year,
        events,
        circuits,
        team_principals,
        technical_directors,
        commercial_managers,
        title_sponsors,
        engine_suppliers,
        tyre_suppliers,
        fuel_suppliers,
    ) = load_roster(
        year=0,
        include_team_principals=True,
        include_technical_directors=True,
        include_commercial_managers=True,
        include_title_sponsors=True,
        include_engine_suppliers=True,
        include_tyre_suppliers=True,
        include_fuel_suppliers=True,
    )
    return GameState(
        year=year,
        teams=teams,
        drivers=drivers,
        team_principals=team_principals,
        technical_directors=technical_directors,
        commercial_managers=commercial_managers,
        title_sponsors=title_sponsors,
        engine_suppliers=engine_suppliers,
        tyre_suppliers=tyre_suppliers,
        fuel_suppliers=fuel_suppliers,
        calendar=Calendar(events=events, current_week=1),
        circuits=circuits,
    )


def advance_to_target_race(state: GameState, engine: GameEngine, target_week: int | None) -> None:
    while True:
        event = state.calendar.current_event
        if event and event.type == EventType.RACE:
            if target_week is None or event.week == target_week:
                return
        if event and event.type != EventType.RACE:
            engine.handle_event_action(state, "skip")
        engine.advance_week(state)


def print_qualifying(result: dict) -> None:
    print("\nQualifying:")
    for row in result["qualifying_results"][:10]:
        lap_seconds = row["best_lap_ms"] / 1000.0
        print(
            f"  P{row['position']:>2}  {row['driver_name']:<22} "
            f"{row['team_name']:<14} {lap_seconds:>8.3f}s"
        )


def print_lap_one_events(result: dict) -> None:
    lap_one = result["lap_history"][0] if result["lap_history"] else {"events": []}
    events = lap_one.get("events", [])
    print("\nLap 1 Events:")
    if not events:
        print("  None")
        return
    for event in events:
        event_type = event.get("type", "unknown")
        if event_type == "turn_one_leader":
            print(f"  Turn 1 leader: {event['driver_name']} ({event['team_name']})")
        elif event_type in {"turn_one_pushed_wide", "turn_one_checked_up", "turn_one_spin"}:
            print(
                f"  {event_type.replace('_', ' ').title()}: "
                f"{event['driver_name']} lost {event.get('positions_lost', '?')} place(s) "
                f"(P{event.get('from_position', '?')} -> P{event.get('to_position', '?')})"
            )
        elif event_type == "turn_one_crash":
            print(f"  Turn one crash: {event['driver_name']} ({event['team_name']})")
        elif event_type == "position_change":
            print(
                f"  Position change: {event['driver_name']} "
                f"P{event.get('from_position', '?')} -> P{event.get('to_position', '?')}"
            )
        elif event_type == "fastest_lap":
            lap_time_ms = event.get("lap_time_ms")
            lap_seconds = f"{lap_time_ms / 1000.0:.3f}s" if isinstance(lap_time_ms, int) else "unknown"
            print(f"  Fastest lap: {event['driver_name']} ({lap_seconds})")
        elif event_type == "retirement":
            print(
                f"  Retirement: {event['driver_name']} "
                f"({event.get('reason', 'unknown')})"
            )
        elif event_type == "pit_stop":
            print(
                f"  Pit stop: {event['driver_name']} "
                f"(stop {event.get('stop_number', '?')})"
            )
        else:
            print(f"  {event_type}: {event}")


def print_race_result(result: dict) -> None:
    print("\nRace Result:")
    for row in result["results"]:
        if row["status"] == "DNF":
            print(f"  DNF  {row['driver_name']:<22} {row['team_name']:<14} {row['status']}")
            continue
        print(
            f"  P{row['position']:>2}  {row['driver_name']:<22} "
            f"{row['team_name']:<14} {row['points']:>2} pts"
        )


def run_headless_race_weekend(target_week: int | None = None) -> None:
    state = build_headless_state()
    engine = GameEngine()
    race_manager = RaceManager()

    advance_to_target_race(state, engine, target_week)
    event = state.calendar.current_event
    if event is None or event.type != EventType.RACE:
        raise RuntimeError("No race weekend found for the requested target.")

    print("=== Headless Race Weekend ===")
    print(f"Year: {state.year}")
    print(f"Week: {event.week}")
    print(f"Event: {event.name}")

    qualifying = race_manager.simulate_qualifying(state)
    race = race_manager.simulate_race(state)

    print_qualifying(qualifying)
    print_lap_one_events(race)
    print_race_result(race)


if __name__ == "__main__":
    target_week = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run_headless_race_weekend(target_week)
