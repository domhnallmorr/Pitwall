import random
from typing import List, Dict, Any
from app.models.state import GameState
from app.race.stats_manager import DriverStatsManager

# 1998 F1 Points System: 10-6-4-3-2-1
POINTS_TABLE = {1: 10, 2: 6, 3: 4, 4: 3, 5: 2, 6: 1}
MAX_CRASH_OUTS = 5
PLAYER_RACE_WEAR_INCREASE = 8
PLAYER_FAILURE_PROB_PER_WEAR = 0.002
PLAYER_MAX_FAILURE_PROBABILITY = 0.35
AI_MECHANICAL_FAILURE_PROBABILITY = 0.05
MAX_CAR_WEAR = 100


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

    def _pick_crash_count(self, participant_count: int) -> int:
        """
        Choose how many drivers crash out this race.
        Keep at least one classified finisher.
        """
        if participant_count <= 1:
            return 0
        return random.randint(0, min(MAX_CRASH_OUTS, participant_count - 1))

    def _mechanical_failure_probability(self, state: GameState, team_id: int, team_lookup: Dict[int, Any]) -> float:
        # Keep deterministic legacy behavior in tests/headless states without a player team selected.
        if state.player_team_id is None:
            return 0.0
        if team_id == state.player_team_id:
            player_team = team_lookup.get(team_id)
            wear = max(0, int(getattr(player_team, "car_wear", 0) or 0))
            return min(PLAYER_MAX_FAILURE_PROBABILITY, wear * PLAYER_FAILURE_PROB_PER_WEAR)
        return AI_MECHANICAL_FAILURE_PROBABILITY

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

        # 2. Random crash-outs for future incident/cost modeling.
        crash_count = self._pick_crash_count(len(participants))
        crashed_participants = random.sample(participants, crash_count) if crash_count > 0 else []
        crashed_driver_ids = {entry["driver_id"] for entry in crashed_participants}

        # Player wear increases every race weekend and drives player mechanical risk.
        if state.player_team_id is not None and state.player_team_id in team_lookup:
            player_team = team_lookup[state.player_team_id]
            current_wear = max(0, int(getattr(player_team, "car_wear", 0) or 0))
            player_team.car_wear = min(MAX_CAR_WEAR, current_wear + PLAYER_RACE_WEAR_INCREASE)

        # 3. Mechanical failures for non-crashed participants.
        finishers = []
        mechanical_participants = []
        for entry in participants:
            if entry["driver_id"] in crashed_driver_ids:
                continue
            fail_prob = self._mechanical_failure_probability(state, entry["team_id"], team_lookup)
            if random.random() < fail_prob:
                mechanical_participants.append(entry)
            else:
                finishers.append(entry)

        # Ensure at least one classified finisher.
        if not finishers and mechanical_participants:
            rescued = random.choice(mechanical_participants)
            mechanical_participants.remove(rescued)
            finishers.append(rescued)

        # 4. Weighted random result for classified finishers.
        finishers = self._weighted_finish_order(finishers)

        # 5. Assign positions and points
        results = []
        for pos, entry in enumerate(finishers, start=1):
            pts = POINTS_TABLE.get(pos, 0)
            results.append({
                "position": pos,
                "driver_name": entry["driver_name"],
                "driver_id": entry["driver_id"],
                "team_name": entry["team_name"],
                "team_id": entry["team_id"],
                "points": pts,
                "status": "FINISHED",
                "crash_out": False,
                "mechanical_out": False,
            })

        # Add DNFs to results for incident tracking and UI display.
        for entry in crashed_participants:
            results.append({
                "position": None,
                "driver_name": entry["driver_name"],
                "driver_id": entry["driver_id"],
                "team_name": entry["team_name"],
                "team_id": entry["team_id"],
                "points": 0,
                "status": "DNF",
                "crash_out": True,
                "mechanical_out": False,
            })

        for entry in mechanical_participants:
            results.append({
                "position": None,
                "driver_name": entry["driver_name"],
                "driver_id": entry["driver_id"],
                "team_name": entry["team_name"],
                "team_id": entry["team_id"],
                "points": 0,
                "status": "DNF",
                "crash_out": False,
                "mechanical_out": True,
            })

        # 6. Apply points to GameState
        for r in results:
            if r["points"] > 0:
                # Update driver points
                driver = driver_lookup[r["driver_id"]]
                driver.points += r["points"]

                # Update constructor points
                team = team_lookup[r["team_id"]]
                team.points += r["points"]

        # 7. Apply career stats (starts, wins, etc.).
        self.stats_manager.apply_race_results(state, results)

        # 8. Mark event as processed
        event = state.calendar.current_event
        if event:
            event_id = f"{event.week}_{event.name}"
            if event_id not in state.events_processed:
                state.events_processed.append(event_id)

        # 9. Get event name for display
        event_name = ""
        if event:
            event_name = event.name

        crash_outs = [
            {
                "driver_id": entry["driver_id"],
                "driver_name": entry["driver_name"],
                "team_id": entry["team_id"],
                "team_name": entry["team_name"],
            }
            for entry in crashed_participants
        ]
        mechanical_outs = [
            {
                "driver_id": entry["driver_id"],
                "driver_name": entry["driver_name"],
                "team_id": entry["team_id"],
                "team_name": entry["team_name"],
            }
            for entry in mechanical_participants
        ]
        state.latest_race_incidents = crash_outs

        return {
            "event_name": event_name,
            "results": results,
            "crash_outs": crash_outs,
            "mechanical_outs": mechanical_outs,
        }
