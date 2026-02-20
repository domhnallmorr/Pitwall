"""
Headless Multi-Season Simulation
Runs the game loop without any UI for testing and validation.

Usage:
    uv run python -m app.headless [num_seasons]
    
Default: 2 seasons
"""

import sys
from app.core.roster import load_roster
from app.core.engine import GameEngine
from app.race.race_manager import RaceManager
from app.models.calendar import Calendar, EventType
from app.models.state import GameState


def run_headless(num_seasons: int = 2):
    print(f"=== Headless Simulation: {num_seasons} Season(s) ===\n")

    # 1. Load roster
    teams, drivers, year, events, circuits, technical_directors = load_roster(
        year=0,
        include_technical_directors=True,
    )
    calendar = Calendar(events=events, current_week=1)
    state = GameState(
        year=year,
        teams=teams,
        drivers=drivers,
        technical_directors=technical_directors,
        calendar=calendar,
        circuits=circuits,
    )

    engine = GameEngine()
    race_manager = RaceManager()

    print(f"Loaded {len(teams)} teams, {len(drivers)} drivers, {len(technical_directors)} technical directors")
    print(f"Calendar: {len(events)} events, last event week {calendar.last_event_week}")
    print(f"Starting Year: {year}\n")

    for season in range(num_seasons):
        season_year = state.year
        print(f"{'='*50}")
        print(f"  SEASON {season_year}")
        print(f"{'='*50}")
        races_run = 0

        while True:
            # Process current week's event before advancing
            event = state.calendar.current_event
            if event:
                event_id = f"{event.week}_{event.name}"
                if event_id not in state.events_processed:
                    if event.type == EventType.RACE:
                        result = race_manager.simulate_race(state)
                        races_run += 1
                        winner = result["results"][0]
                        print(f"  Rd {races_run:>2} | Week {state.calendar.current_week:>2} | "
                              f"{event.name:<25} | {winner['driver_name']} ({winner['team_name']})")
                    else:
                        engine.handle_event_action(state, "skip")

            # Advance week
            summary = engine.advance_week(state)

            if summary.get("season_rollover"):
                info = summary["rollover_info"]
                print(f"\n  --- {info['old_year']} Final Standings ---")
                print(f"\n  Drivers' Championship:")
                for i, d in enumerate(info["final_driver_standings"], 1):
                    print(f"    {i:>2}. {d['name']:<25} {d['points']:>4} pts")
                print(f"\n  Constructors' Championship:")
                for i, t in enumerate(info["final_constructor_standings"], 1):
                    print(f"    {i:>2}. {t['name']:<25} {t['points']:>4} pts")
                print()
                break

    print(f"=== Simulation Complete ===")
    print(f"Final State: Year {state.year}, Week {state.calendar.current_week}")


if __name__ == "__main__":
    seasons = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    run_headless(seasons)
