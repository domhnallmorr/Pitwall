import random
from typing import Any

from app.models.circuit import Circuit
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
GRID_JITTER_RANGE_MS = 450
LAP_JITTER_RANGE_MS = 300
PACE_CENTER = 50
PACE_TO_MS_FACTOR = 45
TOTAL_RACE_FUEL_KG = 155.0
FUEL_PENALTY_MS_PER_KG = 30.0
TYRE_DEGRADATION_MS_PER_LAP = 35
PIT_LANE_TIME_LOSS_MS = 25_000
PIT_STRATEGY_WEIGHTS = ((1, 0.45), (2, 0.4), (3, 0.15))
DIRTY_AIR_GAP_THRESHOLD_MS = 1_500
DIRTY_AIR_LAP_PENALTY_MS = 500
OVERTAKE_SUCCESS_PROBABILITY = 0.65


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

    def _pick_crash_count(self, participant_count: int) -> int:
        """
        Choose how many drivers crash out this race.
        Keep at least one classified finisher.
        """
        if participant_count <= 1:
            return 0
        return random.randint(0, min(MAX_CRASH_OUTS, participant_count - 1))

    def _mechanical_failure_probability(
        self,
        state: GameState,
        team_id: int,
        team_lookup: dict[int, Any],
    ) -> float:
        # Keep deterministic legacy behavior in tests/headless states without a player team selected.
        if state.player_team_id is None:
            return 0.0
        if team_id == state.player_team_id:
            player_team = team_lookup.get(team_id)
            wear = max(0, int(getattr(player_team, "car_wear", 0) or 0))
            return min(PLAYER_MAX_FAILURE_PROBABILITY, wear * PLAYER_FAILURE_PROB_PER_WEAR)
        return AI_MECHANICAL_FAILURE_PROBABILITY

    def _resolve_circuit(self, state: GameState) -> Circuit | None:
        event = state.calendar.current_event
        if event is None:
            return None
        return next((c for c in state.circuits if c.name == event.name), None)

    def _get_circuit(self, state: GameState) -> Circuit:
        circuit = self._resolve_circuit(state)
        if circuit is not None:
            return circuit
        event = state.calendar.current_event
        return Circuit(
            id=0,
            name=event.name if event else "Grand Prix",
            country="Unknown",
            location="Unknown",
            laps=50,
            base_laptime_ms=90_000,
            length_km=5.0,
            overtaking_delta=1.0,
            power_factor=1.0,
        )

    def _grid_score(self, entrant: dict[str, Any]) -> int:
        return entrant["performance_weight"] * 1000 + random.randint(-GRID_JITTER_RANGE_MS, GRID_JITTER_RANGE_MS)

    def _lap_time_ms(self, entrant: dict[str, Any], circuit: Circuit) -> int:
        base_bonus_ms = int((entrant["performance_weight"] - PACE_CENTER) * PACE_TO_MS_FACTOR)
        jitter_ms = random.randint(-LAP_JITTER_RANGE_MS, LAP_JITTER_RANGE_MS)
        power_adjustment_ms = int((float(circuit.power_factor) - 1.0) * entrant["car_speed"] * 3)
        fuel_penalty_ms = int((entrant.get("fuel_kg", 0.0) or 0.0) * FUEL_PENALTY_MS_PER_KG)
        tyre_wear_penalty_ms = self._tyre_wear_penalty_ms(entrant.get("stint_laps", 0))
        dirty_air_penalty_ms = int(entrant.get("dirty_air_penalty_ms", 0) or 0)
        return max(
            45_000,
            circuit.base_laptime_ms - base_bonus_ms - power_adjustment_ms
            + fuel_penalty_ms + tyre_wear_penalty_ms + dirty_air_penalty_ms + jitter_ms,
        )

    def _dirty_air_penalty_ms(self, gap_ahead_ms: int | None, same_lap: bool) -> int:
        if not same_lap or gap_ahead_ms is None:
            return 0
        if gap_ahead_ms <= DIRTY_AIR_GAP_THRESHOLD_MS:
            return DIRTY_AIR_LAP_PENALTY_MS
        return 0

    def _overtaking_delta_ms(self, circuit: Circuit) -> int:
        raw_delta = float(circuit.overtaking_delta or 0)
        return int(raw_delta * 1000) if raw_delta < 50 else int(raw_delta)

    def _should_attempt_pass(self, lap_time_gain_ms: int, overtaking_delta_ms: float) -> bool:
        return lap_time_gain_ms > 0 and lap_time_gain_ms >= int(overtaking_delta_ms)

    def _pass_succeeds(self) -> bool:
        return random.randint(1, 1000) <= int(OVERTAKE_SUCCESS_PROBABILITY * 1000)

    def _fuel_per_lap(self, circuit: Circuit) -> float:
        return TOTAL_RACE_FUEL_KG / max(1, circuit.laps)

    def _fuel_for_stint(self, circuit: Circuit, stint_laps: int) -> float:
        return round(self._fuel_per_lap(circuit) * max(0, stint_laps), 3)

    def _tyre_wear_penalty_ms(self, stint_laps: int) -> int:
        return max(0, int(stint_laps)) * TYRE_DEGRADATION_MS_PER_LAP

    def _pick_planned_stops(self) -> int:
        roll = random.uniform(0.0, 1.0)
        cumulative = 0.0
        for stops, weight in PIT_STRATEGY_WEIGHTS:
            cumulative += weight
            if roll <= cumulative:
                return stops
        return PIT_STRATEGY_WEIGHTS[-1][0]

    def _strategy_windows(self, stop_count: int, total_laps: int) -> list[tuple[int, int]]:
        if stop_count == 1:
            return [(max(2, int(total_laps * 0.40)), min(total_laps - 2, int(total_laps * 0.60)))]
        if stop_count == 2:
            return [
                (max(2, int(total_laps * 0.25)), min(total_laps - 4, int(total_laps * 0.35))),
                (max(4, int(total_laps * 0.60)), min(total_laps - 2, int(total_laps * 0.75))),
            ]
        return [
            (max(2, int(total_laps * 0.18)), min(total_laps - 6, int(total_laps * 0.28))),
            (max(4, int(total_laps * 0.45)), min(total_laps - 4, int(total_laps * 0.60))),
            (max(6, int(total_laps * 0.72)), min(total_laps - 2, int(total_laps * 0.85))),
        ]

    def _assign_fuel_strategy(self, entrant: dict[str, Any], circuit: Circuit):
        planned_stops = self._pick_planned_stops()
        windows = self._strategy_windows(planned_stops, circuit.laps)
        pit_laps: list[int] = []
        previous_stop = 1
        for start, end in windows:
            start = max(start, previous_stop + 2)
            end = max(start, end)
            stop_lap = random.randint(start, end)
            pit_laps.append(stop_lap)
            previous_stop = stop_lap

        entrant["planned_stops"] = planned_stops
        entrant["planned_pit_laps"] = pit_laps
        entrant["completed_stops"] = 0
        entrant["stint_laps"] = 0
        first_stint_end = pit_laps[0] if pit_laps else circuit.laps
        entrant["fuel_kg"] = self._fuel_for_stint(circuit, first_stint_end)

    def _format_gap(self, leader_laps: int, entrant_laps: int, gap_ms: int | None) -> str:
        lap_delta = leader_laps - entrant_laps
        if lap_delta > 0:
            return f"+{lap_delta} Lap" if lap_delta == 1 else f"+{lap_delta} Laps"
        if gap_ms is None:
            return "LEADER"
        return f"+{gap_ms / 1000:.3f}s"

    def _build_timing_rows(self, entrants: list[dict[str, Any]]) -> list[dict[str, Any]]:
        ordered = sorted(
            entrants,
            key=lambda entry: (
                -entry["classification_laps"],
                entry.get("snapshot_sort_time_ms", entry.get("snapshot_total_time_ms", entry["total_time_ms"])),
                entry["grid_position"],
            ),
        )
        if not ordered:
            return []

        leader = ordered[0]
        previous = None
        rows: list[dict[str, Any]] = []

        for idx, entrant in enumerate(ordered, start=1):
            entrant["position"] = idx
            leader_lap_delta = leader["classification_laps"] - entrant["classification_laps"]
            entrant_time_ms = entrant.get("snapshot_total_time_ms", entrant["total_time_ms"])
            if idx == 1:
                gap_to_leader_ms = 0
                interval_ahead_ms = None
            elif entrant.get("same_lap_as_leader"):
                gap_to_leader_ms = entrant.get("snapshot_gap_to_leader_ms")
                if previous and previous.get("same_lap_as_leader"):
                    interval_ahead_ms = gap_to_leader_ms - (previous.get("snapshot_gap_to_leader_ms") or 0)
                else:
                    interval_ahead_ms = None
            elif leader_lap_delta == 0:
                leader_time_ms = leader.get("snapshot_total_time_ms", leader["total_time_ms"])
                gap_to_leader_ms = entrant_time_ms - leader_time_ms
                if previous and previous["laps_completed"] == entrant["laps_completed"]:
                    previous_time_ms = previous.get("snapshot_total_time_ms", previous["total_time_ms"])
                    interval_ahead_ms = entrant_time_ms - previous_time_ms
                else:
                    interval_ahead_ms = None
            else:
                gap_to_leader_ms = None
                interval_ahead_ms = None

            rows.append({
                "driver_id": entrant["driver_id"],
                "driver_name": entrant["driver_name"],
                "team_id": entrant["team_id"],
                "team_name": entrant["team_name"],
                "position": idx,
                "laps_completed": entrant["classification_laps"],
                "total_time_ms": entrant.get("snapshot_sort_time_ms", entrant.get("snapshot_total_time_ms", entrant["total_time_ms"])),
                "last_lap_ms": entrant["last_lap_ms"],
                "best_lap_ms": entrant["best_lap_ms"],
                "gap_to_leader_ms": gap_to_leader_ms,
                "interval_ahead_ms": interval_ahead_ms,
                "gap_display": "LEADER" if idx == 1 else self._format_gap(
                    leader["laps_completed"],
                    entrant["classification_laps"],
                    gap_to_leader_ms,
                ),
                "status": entrant["status"],
            })
            previous = entrant

        return rows

    def _lap_events(
        self,
        lap: int,
        entrants: list[dict[str, Any]],
        prior_positions: dict[int, int],
        fastest_event: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        for entrant in entrants:
            if entrant.get("retirement_lap") == lap and entrant["status"] == "DNF":
                events.append({
                    "type": "retirement",
                    "lap": lap,
                    "driver_id": entrant["driver_id"],
                    "driver_name": entrant["driver_name"],
                    "reason": entrant.get("retirement_reason", "mechanical"),
                })
            if lap in entrant.get("pit_stop_history", []):
                events.append({
                    "type": "pit_stop",
                    "lap": lap,
                    "driver_id": entrant["driver_id"],
                    "driver_name": entrant["driver_name"],
                    "stop_number": entrant.get("pit_stop_history", []).index(lap) + 1,
                    "fuel_added_kg": round(entrant.get("pit_fuel_added_by_lap", {}).get(lap, 0.0), 1),
                })

        if fastest_event is not None:
            events.append(fastest_event)

        return events

    def _prepare_participants(
        self,
        state: GameState,
        circuit: Circuit,
        participants: list[dict[str, Any]],
        team_lookup: dict[int, Any],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        crash_count = self._pick_crash_count(len(participants))
        crashed_participants = random.sample(participants, crash_count) if crash_count > 0 else []
        crashed_driver_ids = {entry["driver_id"] for entry in crashed_participants}

        if state.player_team_id is not None and state.player_team_id in team_lookup:
            player_team = team_lookup[state.player_team_id]
            current_wear = max(0, int(getattr(player_team, "car_wear", 0) or 0))
            player_team.car_wear = min(MAX_CAR_WEAR, current_wear + PLAYER_RACE_WEAR_INCREASE)

        mechanical_participants: list[dict[str, Any]] = []
        finishers: list[dict[str, Any]] = []

        for entry in participants:
            if entry["driver_id"] in crashed_driver_ids:
                entry["retirement_lap"] = random.randint(1, circuit.laps)
                entry["retirement_reason"] = "crash"
                continue

            fail_prob = self._mechanical_failure_probability(state, entry["team_id"], team_lookup)
            if random.random() < fail_prob:
                entry["retirement_lap"] = random.randint(1, circuit.laps)
                entry["retirement_reason"] = "mechanical"
                mechanical_participants.append(entry)
            else:
                entry["retirement_lap"] = None
                entry["retirement_reason"] = None
                finishers.append(entry)

        if not finishers and participants:
            rescued = random.choice(participants)
            rescued["retirement_lap"] = None
            rescued["retirement_reason"] = None
            if rescued in crashed_participants:
                crashed_participants.remove(rescued)
            if rescued in mechanical_participants:
                mechanical_participants.remove(rescued)

        return crashed_participants, mechanical_participants

    def _simulate_lap_race(self, participants: list[dict[str, Any]], circuit: Circuit) -> dict[str, Any]:
        entrants = [dict(entry) for entry in participants]
        seeded_grid = sorted(entrants, key=self._grid_score, reverse=True)
        for idx, entrant in enumerate(seeded_grid, start=1):
            entrant["grid_position"] = idx
            entrant["position"] = idx
            entrant["last_lap_ms"] = None
            entrant["best_lap_ms"] = None
            entrant["total_time_ms"] = 0
            entrant["laps_completed"] = 0
            entrant["status"] = "RUNNING"
            entrant["lap_times_ms"] = []
            entrant["cumulative_times_ms"] = []
            entrant["last_pit_lap"] = None
            entrant["last_fuel_added_kg"] = 0.0
            entrant["pit_stop_history"] = []
            entrant["pit_fuel_added_by_lap"] = {}
            entrant["stint_laps"] = 0
            self._assign_fuel_strategy(entrant, circuit)

        if entrants and not any(entry.get("retirement_lap") is None for entry in entrants):
            rescued = min(entrants, key=lambda entry: entry.get("retirement_lap") or 10_000)
            rescued["retirement_lap"] = None
            rescued["retirement_reason"] = None

        best_lap_record: dict[str, Any] | None = None
        fastest_events_by_lap: dict[int, dict[str, Any]] = {}
        overtakes_by_lap: dict[int, list[dict[str, Any]]] = {}

        for lap in range(1, circuit.laps + 1):
            running_before_lap = [
                entrant for entrant in entrants
                if entrant["status"] != "DNF" and entrant.get("retirement_lap") != lap
            ]
            ordered_before_lap = sorted(
                running_before_lap,
                key=lambda entry: (entry["total_time_ms"], entry["grid_position"]),
            )
            for idx, entrant in enumerate(ordered_before_lap):
                if idx == 0:
                    entrant["dirty_air_penalty_ms"] = 0
                    continue
                car_ahead = ordered_before_lap[idx - 1]
                gap_ahead_ms = entrant["total_time_ms"] - car_ahead["total_time_ms"]
                entrant["dirty_air_penalty_ms"] = self._dirty_air_penalty_ms(gap_ahead_ms, same_lap=True)

            for entrant in entrants:
                entrant["last_pit_lap"] = None
                entrant["last_fuel_added_kg"] = 0.0
                if entrant.get("retirement_lap") == lap:
                    entrant["status"] = "DNF"
                    continue
                if entrant["status"] == "DNF":
                    continue

                lap_time_ms = self._lap_time_ms(entrant, circuit)
                fuel_before_burn = entrant.get("fuel_kg", 0.0)
                entrant["fuel_kg"] = max(0.0, fuel_before_burn - self._fuel_per_lap(circuit))

                pit_laps = entrant.get("planned_pit_laps", [])
                if pit_laps and lap == pit_laps[0]:
                    lap_time_ms += PIT_LANE_TIME_LOSS_MS
                    entrant["completed_stops"] += 1
                    entrant["last_pit_lap"] = lap
                    pit_laps.pop(0)
                    next_stop = pit_laps[0] if pit_laps else circuit.laps
                    laps_needed = max(0, next_stop - lap)
                    fuel_target = self._fuel_for_stint(circuit, laps_needed)
                    fuel_added = max(0.0, fuel_target - entrant["fuel_kg"])
                    entrant["fuel_kg"] += fuel_added
                    entrant["last_fuel_added_kg"] = fuel_added
                    entrant["pit_stop_history"].append(lap)
                    entrant["pit_fuel_added_by_lap"][lap] = fuel_added
                    entrant["stint_laps"] = 0

                entrant["lap_times_ms"].append(lap_time_ms)
                entrant["total_time_ms"] += lap_time_ms
                entrant["cumulative_times_ms"].append(entrant["total_time_ms"])
                entrant["last_lap_ms"] = lap_time_ms
                entrant["laps_completed"] = len(entrant["cumulative_times_ms"])
                entrant["stint_laps"] = int(entrant.get("stint_laps", 0)) + 1
                entrant["dirty_air_penalty_ms"] = 0
                if entrant["best_lap_ms"] is None or lap_time_ms < entrant["best_lap_ms"]:
                    entrant["best_lap_ms"] = lap_time_ms

                if best_lap_record is None or lap_time_ms < best_lap_record["lap_time_ms"]:
                    best_lap_record = {
                        "type": "fastest_lap",
                        "lap": lap,
                        "driver_id": entrant["driver_id"],
                        "driver_name": entrant["driver_name"],
                        "lap_time_ms": lap_time_ms,
                    }
                    fastest_events_by_lap[lap] = best_lap_record

            running_after_lap = [
                entrant for entrant in entrants
                if entrant["status"] != "DNF"
            ]
            ordered_after_lap = sorted(
                running_after_lap,
                key=lambda entry: (entry["total_time_ms"], entry["grid_position"]),
            )
            lap_overtakes: list[dict[str, Any]] = []
            index = 1
            while index < len(ordered_after_lap):
                attacker = ordered_after_lap[index]
                defender = ordered_after_lap[index - 1]
                lap_time_gain_ms = (defender.get("last_lap_ms") or 0) - (attacker.get("last_lap_ms") or 0)
                if self._should_attempt_pass(lap_time_gain_ms, self._overtaking_delta_ms(circuit)) and self._pass_succeeds():
                    ordered_after_lap[index - 1], ordered_after_lap[index] = attacker, defender
                    lap_overtakes.append({
                        "type": "position_change",
                        "lap": lap,
                        "driver_id": attacker["driver_id"],
                        "driver_name": attacker["driver_name"],
                        "from_position": index + 1,
                        "to_position": index,
                    })
                    if attacker["total_time_ms"] >= defender["total_time_ms"]:
                        attacker["total_time_ms"] = max(0, defender["total_time_ms"] - 1)
                        attacker["cumulative_times_ms"][-1] = attacker["total_time_ms"]
                    index = max(1, index - 1)
                    continue
                index += 1

            overtakes_by_lap[lap] = lap_overtakes

        lap_history: list[dict[str, Any]] = []
        prior_positions = {entrant["driver_id"]: entrant["position"] for entrant in entrants}

        for lap in range(1, circuit.laps + 1):
            contenders = [entrant for entrant in entrants if len(entrant["cumulative_times_ms"]) >= lap]
            if not contenders:
                break
            leader = min(contenders, key=lambda entry: entry["cumulative_times_ms"][lap - 1])
            reference_time_ms = leader["cumulative_times_ms"][lap - 1]

            for entrant in entrants:
                cumulative = entrant["cumulative_times_ms"]
                completed = 0
                for lap_end_time in cumulative:
                    if lap_end_time <= reference_time_ms:
                        completed += 1
                    else:
                        break
                same_lap_as_leader = False
                projected_gap_to_leader_ms = None
                if completed == lap:
                    same_lap_as_leader = True
                    projected_gap_to_leader_ms = cumulative[lap - 1] - reference_time_ms
                elif completed == lap - 1 and len(cumulative) >= lap:
                    same_lap_as_leader = True
                    projected_gap_to_leader_ms = cumulative[lap - 1] - reference_time_ms

                entrant["laps_completed"] = completed
                entrant["classification_laps"] = lap if same_lap_as_leader else completed
                entrant["same_lap_as_leader"] = same_lap_as_leader
                entrant["snapshot_gap_to_leader_ms"] = projected_gap_to_leader_ms
                entrant["snapshot_total_time_ms"] = cumulative[completed - 1] if completed > 0 else 0
                entrant["snapshot_sort_time_ms"] = cumulative[lap - 1] if same_lap_as_leader else entrant["snapshot_total_time_ms"]
                entrant["last_lap_ms"] = entrant["lap_times_ms"][completed - 1] if completed > 0 else None
                if entrant.get("retirement_reason") and entrant["retirement_lap"] <= lap:
                    entrant["status"] = "DNF"
                else:
                    entrant["status"] = "RUNNING" if completed < circuit.laps else "FINISHED"

            timing_rows = self._build_timing_rows(entrants)
            lap_events = list(overtakes_by_lap.get(lap, []))
            lap_events.extend(self._lap_events(lap, entrants, prior_positions, fastest_events_by_lap.get(lap)))
            lap_history.append({
                "lap": lap,
                "order": timing_rows,
                "events": lap_events,
            })
            prior_positions = {row["driver_id"]: row["position"] for row in timing_rows}

        final_snapshot = lap_history[-1]["order"] if lap_history else []
        final_lookup = {row["driver_id"]: row for row in final_snapshot}
        for entrant in entrants:
            snapshot = final_lookup.get(entrant["driver_id"])
            if snapshot is not None:
                entrant["laps_completed"] = snapshot["laps_completed"]
                entrant["classification_laps"] = snapshot["laps_completed"]
                entrant["snapshot_total_time_ms"] = snapshot["total_time_ms"]
                entrant["snapshot_sort_time_ms"] = snapshot["total_time_ms"]
                entrant["last_lap_ms"] = snapshot["last_lap_ms"]
                entrant["position"] = snapshot["position"]
                entrant["status"] = snapshot["status"]

        final_order = sorted(
            entrants,
            key=lambda entry: (
                -entry["classification_laps"],
                entry.get("snapshot_sort_time_ms", entry.get("snapshot_total_time_ms", entry["total_time_ms"])),
                entry["grid_position"],
            ),
        )
        return {
            "entrants": final_order,
            "lap_history": lap_history,
            "total_laps": circuit.laps,
        }

    def simulate_race(self, state: GameState) -> dict[str, Any]:
        """
        Simulates a race lap by lap and returns lap history plus final classification.
        """
        participants: list[dict[str, Any]] = []
        driver_lookup = {d.id: d for d in state.drivers}
        team_lookup = {t.id: t for t in state.teams}
        circuit = self._get_circuit(state)

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
                        "driver_speed": driver_speed,
                        "car_speed": car_speed,
                        "performance_weight": self._get_performance_weight(driver_speed, car_speed),
                    })

        crashed_participants, mechanical_participants = self._prepare_participants(
            state,
            circuit,
            participants,
            team_lookup,
        )
        race_run = self._simulate_lap_race(participants, circuit)

        results = []
        finishing_position = 1
        for entry in race_run["entrants"]:
            retired = entry.get("retirement_reason") is not None
            points = POINTS_TABLE.get(finishing_position, 0) if not retired else 0
            results.append({
                "position": None if retired else finishing_position,
                "driver_name": entry["driver_name"],
                "driver_id": entry["driver_id"],
                "team_name": entry["team_name"],
                "team_id": entry["team_id"],
                "points": points,
                "status": "DNF" if retired else "FINISHED",
                "crash_out": entry.get("retirement_reason") == "crash",
                "mechanical_out": entry.get("retirement_reason") == "mechanical",
                "laps_completed": entry["laps_completed"],
                "total_time_ms": entry.get("snapshot_total_time_ms", entry["total_time_ms"]),
                "best_lap_ms": entry["best_lap_ms"],
            })
            if not retired:
                finishing_position += 1

        for row in results:
            if row["points"] > 0:
                driver_lookup[row["driver_id"]].points += row["points"]
                team_lookup[row["team_id"]].points += row["points"]

        self.stats_manager.apply_race_results(state, results)

        event = state.calendar.current_event
        if event:
            event_id = f"{event.week}_{event.name}"
            if event_id not in state.events_processed:
                state.events_processed.append(event_id)

        event_name = event.name if event else ""
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
            "total_laps": race_run["total_laps"],
            "lap_history": race_run["lap_history"],
            "results": results,
            "crash_outs": crash_outs,
            "mechanical_outs": mechanical_outs,
        }
