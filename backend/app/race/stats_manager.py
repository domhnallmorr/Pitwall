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
        for entry in results:
            driver = driver_lookup.get(entry.get("driver_id"))
            if driver:
                driver.race_starts += 1
                if entry.get("position") == 1:
                    driver.wins += 1
