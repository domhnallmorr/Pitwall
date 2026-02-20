from typing import Dict, Any, List

from app.models.state import GameState


class DriverStatsManager:
    """
    Central place for applying career stat updates from race outcomes.
    """

    def apply_race_results(self, state: GameState, results: List[Dict[str, Any]]):
        """
        Update driver career stats based on race participants/results.
        """
        driver_lookup = {d.id: d for d in state.drivers}
        event = state.calendar.current_event
        country = "Unknown"
        race_round = None
        if event:
            circuit = next((c for c in state.circuits if c.name == event.name), None)
            if circuit:
                country = circuit.country
            race_round = sum(
                1 for e in state.calendar.events
                if e.type.value == "RACE" and e.week <= event.week
            )

        year_bucket = state.driver_season_results.setdefault(state.year, {})
        for entry in results:
            driver = driver_lookup.get(entry.get("driver_id"))
            if driver:
                driver.race_starts += 1
                if entry.get("position") == 1:
                    driver.wins += 1

                # Track per-season race results for driver profile pages.
                if event and race_round is not None:
                    driver_bucket = year_bucket.setdefault(driver.id, [])
                    new_result = {
                        "round": race_round,
                        "event_name": event.name,
                        "country": country,
                        "position": entry.get("position", 0),
                        "status": entry.get("status", "FINISHED"),
                    }
                    # Upsert by round to avoid duplicates if race is re-simulated.
                    replaced = False
                    for idx, existing in enumerate(driver_bucket):
                        if existing.get("round") == race_round:
                            driver_bucket[idx] = new_result
                            replaced = True
                            break
                    if not replaced:
                        driver_bucket.append(new_result)
