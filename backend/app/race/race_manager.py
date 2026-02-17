import random
from typing import List, Dict, Any
from app.models.state import GameState
from app.race.stats_manager import DriverStatsManager

# 1998 F1 Points System: 10-6-4-3-2-1
POINTS_TABLE = {1: 10, 2: 6, 3: 4, 4: 3, 5: 2, 6: 1}


class RaceManager:
    """
    Handles race weekend simulation.
    Lives in its own package (app.race) to keep race logic
    separate from the main game loop.
    """

    def __init__(self):
        self.stats_manager = DriverStatsManager()

    def _get_performance_weight(self, driver_speed: int, car_speed: int) -> int:
        """
        Blend driver and car speeds into a simple race performance weight.
        Driver skill has a slightly higher impact than car speed for now.
        """
        return max(1, int((driver_speed * 0.65) + (car_speed * 0.35)))

    def _weighted_finish_order(self, participants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Build a finishing order by repeatedly drawing one participant
        with weighted probability, without replacement.
        """
        remaining = list(participants)
        ordered = []

        while remaining:
            weights = [entry["performance_weight"] for entry in remaining]
            picked = random.choices(remaining, weights=weights, k=1)[0]
            ordered.append(picked)
            remaining.remove(picked)

        return ordered

    def simulate_race(self, state: GameState) -> Dict[str, Any]:
        """
        Simulates a race with a random result.
        Returns a dict with the race results and updated standings info.
        """
        # 1. Build list of racing drivers (only those assigned to teams)
        participants = []
        driver_lookup = {d.id: d for d in state.drivers}
        team_lookup = {t.id: t for t in state.teams}

        for team in state.teams:
            for did in [team.driver1_id, team.driver2_id]:
                if did and did in driver_lookup:
                    driver = driver_lookup[did]
                    driver_speed = getattr(driver, "speed", 50)
                    car_speed = getattr(team, "car_speed", 50)
                    participants.append({
                        "driver_id": did,
                        "driver_name": driver.name,
                        "team_id": team.id,
                        "team_name": team.name,
                        "performance_weight": self._get_performance_weight(driver_speed, car_speed),
                    })

        # 2. Weighted random result (higher speed => better chance).
        participants = self._weighted_finish_order(participants)

        # 3. Assign positions and points
        results = []
        for pos, entry in enumerate(participants, start=1):
            pts = POINTS_TABLE.get(pos, 0)
            results.append({
                "position": pos,
                "driver_name": entry["driver_name"],
                "driver_id": entry["driver_id"],
                "team_name": entry["team_name"],
                "team_id": entry["team_id"],
                "points": pts,
            })

        # 4. Apply points to GameState
        for r in results:
            if r["points"] > 0:
                # Update driver points
                driver = driver_lookup[r["driver_id"]]
                driver.points += r["points"]

                # Update constructor points
                team = team_lookup[r["team_id"]]
                team.points += r["points"]

        # 5. Apply career stats (starts, wins, etc.).
        self.stats_manager.apply_race_results(state, results)

        # 6. Mark event as processed
        event = state.calendar.current_event
        if event:
            event_id = f"{event.week}_{event.name}"
            if event_id not in state.events_processed:
                state.events_processed.append(event_id)

        # 7. Get event name for display
        event_name = ""
        if event:
            event_name = event.name

        return {
            "event_name": event_name,
            "results": results,
        }
