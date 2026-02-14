import random
from typing import List, Dict, Any
from app.models.state import GameState

# 1998 F1 Points System: 10-6-4-3-2-1
POINTS_TABLE = {1: 10, 2: 6, 3: 4, 4: 3, 5: 2, 6: 1}


class RaceManager:
    """
    Handles race weekend simulation.
    Lives in its own package (app.race) to keep race logic
    separate from the main game loop.
    """

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
                    participants.append({
                        "driver_id": did,
                        "driver_name": driver_lookup[did].name,
                        "team_id": team.id,
                        "team_name": team.name,
                    })

        # 2. Shuffle for random result
        random.shuffle(participants)

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

        # 5. Mark event as processed
        event = state.calendar.current_event
        if event:
            event_id = f"{event.week}_{event.name}"
            if event_id not in state.events_processed:
                state.events_processed.append(event_id)

        # 6. Get event name for display
        event_name = ""
        if event:
            event_name = event.name

        return {
            "event_name": event_name,
            "results": results,
        }
