from typing import Any

from app.models.circuit import Circuit
from app.race.constants import GRID_JITTER_RANGE_MS, PIT_LANE_TIME_LOSS_MS


def format_gap(leader_laps: int, entrant_laps: int, gap_ms: int | None) -> str:
	lap_delta = leader_laps - entrant_laps
	if lap_delta > 0:
		return f"+{lap_delta} Lap" if lap_delta == 1 else f"+{lap_delta} Laps"
	if gap_ms is None:
		return "LEADER"
	return f"+{gap_ms / 1000:.3f}s"


def build_timing_rows(entrants: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
			"gap_display": "LEADER" if idx == 1 else format_gap(
				leader["laps_completed"],
				entrant["classification_laps"],
				gap_to_leader_ms,
			),
			"status": entrant["status"],
		})
		previous = entrant

	return rows


def lap_events(
	lap: int,
	entrants: list[dict[str, Any]],
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


def simulate_lap_race(
	participants: list[dict[str, Any]],
	circuit: Circuit,
	grid_score_fn,
	assign_fuel_strategy_fn,
	dirty_air_penalty_fn,
	lap_time_fn,
	fuel_per_lap_fn,
	fuel_for_stint_fn,
	should_attempt_pass_fn,
	overtaking_delta_ms_fn,
	pass_succeeds_fn,
) -> dict[str, Any]:
	entrants = [dict(entry) for entry in participants]
	seeded_grid = sorted(entrants, key=lambda entry: grid_score_fn(entry), reverse=True)
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
		assign_fuel_strategy_fn(entrant, circuit)

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
			entrant["dirty_air_penalty_ms"] = dirty_air_penalty_fn(gap_ahead_ms, same_lap=True)

		for entrant in entrants:
			entrant["last_pit_lap"] = None
			entrant["last_fuel_added_kg"] = 0.0
			if entrant.get("retirement_lap") == lap:
				entrant["status"] = "DNF"
				continue
			if entrant["status"] == "DNF":
				continue

			lap_time_ms = lap_time_fn(entrant, circuit)
			fuel_before_burn = entrant.get("fuel_kg", 0.0)
			entrant["fuel_kg"] = max(0.0, fuel_before_burn - fuel_per_lap_fn(circuit))

			pit_laps = entrant.get("planned_pit_laps", [])
			if pit_laps and lap == pit_laps[0]:
				lap_time_ms += PIT_LANE_TIME_LOSS_MS
				entrant["completed_stops"] += 1
				entrant["last_pit_lap"] = lap
				pit_laps.pop(0)
				next_stop = pit_laps[0] if pit_laps else circuit.laps
				laps_needed = max(0, next_stop - lap)
				fuel_target = fuel_for_stint_fn(circuit, laps_needed)
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

		running_after_lap = [entrant for entrant in entrants if entrant["status"] != "DNF"]
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
			if should_attempt_pass_fn(lap_time_gain_ms, overtaking_delta_ms_fn(circuit)) and pass_succeeds_fn():
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

		timing_rows = build_timing_rows(entrants)
		lap_event_rows = list(overtakes_by_lap.get(lap, []))
		lap_event_rows.extend(lap_events(lap, entrants, fastest_events_by_lap.get(lap)))
		lap_history.append({
			"lap": lap,
			"order": timing_rows,
			"events": lap_event_rows,
		})

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
