import random
from typing import Any

from app.models.circuit import Circuit
from app.models.state import GameState
from app.race.constants import GRID_JITTER_RANGE_MS, POINTS_TABLE, QUALIFYING_ATTEMPTS
from app.race.lap_simulator import simulate_lap_race
from app.race.pace import (
	dirty_air_penalty_ms,
	get_performance_weight,
	grid_score,
	qualifying_lap_time_ms,
	lap_time_ms,
	overtaking_delta_ms,
	pass_succeeds,
	should_attempt_pass,
	tyre_wear_penalty_ms,
)
from app.race.retirements import (
	mechanical_failure_probability,
	pick_crash_count,
	prepare_participants,
)
from app.race.stats_manager import DriverStatsManager
from app.race.strategy import (
	assign_fuel_strategy,
	fuel_for_stint,
	fuel_per_lap,
	pick_planned_stops,
	strategy_windows,
)


class RaceManager:
	"""
	Handles race weekend simulation.
	Lives in its own package (app.race) to keep race logic
	separate from the main game loop.
	"""

	def __init__(self):
		self.stats_manager = DriverStatsManager()

	def _get_performance_weight(self, driver_speed: int, car_speed: int) -> int:
		return get_performance_weight(driver_speed, car_speed)

	def _pick_crash_count(self, participant_count: int) -> int:
		return pick_crash_count(participant_count)

	def _mechanical_failure_probability(
		self,
		state: GameState,
		team_id: int,
		team_lookup: dict[int, Any],
	) -> float:
		return mechanical_failure_probability(state, team_id, team_lookup)

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

	def _current_event_key(self, state: GameState) -> str | None:
		event = state.calendar.current_event
		if event is None:
			return None
		return f"{state.year}_{event.week}_{event.name}"

	def _build_participants(self, state: GameState) -> tuple[list[dict[str, Any]], Circuit]:
		participants: list[dict[str, Any]] = []
		driver_lookup = {d.id: d for d in state.drivers}
		engine_supplier_lookup = {supplier.name: supplier for supplier in state.engine_suppliers}
		tyre_supplier_lookup = {supplier.name: supplier for supplier in state.tyre_suppliers}
		circuit = self._get_circuit(state)

		for team in state.teams:
			for did in [team.driver1_id, team.driver2_id]:
				if did and did in driver_lookup:
					driver = driver_lookup[did]
					driver_speed = getattr(driver, "speed", 50)
					car_speed = getattr(team, "car_speed", 50)
					engine_supplier = engine_supplier_lookup.get(getattr(team, "engine_supplier_name", None))
					engine_power = getattr(engine_supplier, "power", 50) if engine_supplier else 50
					tyre_supplier = tyre_supplier_lookup.get(getattr(team, "tyre_supplier_name", None))
					tyre_grip = getattr(tyre_supplier, "grip", 50) if tyre_supplier else 50
					tyre_wear = getattr(tyre_supplier, "wear", 50) if tyre_supplier else 50
					participants.append({
						"driver_id": did,
						"driver_name": driver.name,
						"team_id": team.id,
						"team_name": team.name,
						"driver_speed": driver_speed,
						"car_speed": car_speed,
						"engine_power": engine_power,
						"tyre_grip": tyre_grip,
						"tyre_wear": tyre_wear,
						"performance_weight": self._get_performance_weight(driver_speed, car_speed),
					})

		return participants, circuit

	def _grid_score(self, entrant: dict[str, Any]) -> int:
		return grid_score(entrant, GRID_JITTER_RANGE_MS)

	def _lap_time_ms(self, entrant: dict[str, Any], circuit: Circuit) -> int:
		return lap_time_ms(entrant, circuit)

	def _qualifying_lap_time_ms(self, entrant: dict[str, Any], circuit: Circuit) -> int:
		return qualifying_lap_time_ms(entrant, circuit)

	def _dirty_air_penalty_ms(self, gap_ahead_ms: int | None, same_lap: bool) -> int:
		return dirty_air_penalty_ms(gap_ahead_ms, same_lap)

	def _overtaking_delta_ms(self, circuit: Circuit) -> int:
		return overtaking_delta_ms(circuit)

	def _should_attempt_pass(self, lap_time_gain_ms: int, overtaking_delta_ms_value: float) -> bool:
		return should_attempt_pass(lap_time_gain_ms, overtaking_delta_ms_value)

	def _pass_succeeds(self) -> bool:
		return pass_succeeds()

	def _fuel_per_lap(self, circuit: Circuit) -> float:
		return fuel_per_lap(circuit)

	def _fuel_for_stint(self, circuit: Circuit, stint_laps: int) -> float:
		return fuel_for_stint(circuit, stint_laps)

	def _tyre_wear_penalty_ms(self, stint_laps: int) -> int:
		return tyre_wear_penalty_ms(stint_laps)

	def _pick_planned_stops(self) -> int:
		return pick_planned_stops()

	def _strategy_windows(self, stop_count: int, total_laps: int) -> list[tuple[int, int]]:
		return strategy_windows(stop_count, total_laps)

	def _assign_fuel_strategy(self, entrant: dict[str, Any], circuit: Circuit):
		assign_fuel_strategy(entrant, circuit)

	def _prepare_participants(
		self,
		state: GameState,
		circuit: Circuit,
		participants: list[dict[str, Any]],
		team_lookup: dict[int, Any],
	) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
		return prepare_participants(
			state,
			circuit,
			participants,
			team_lookup,
			self._pick_crash_count,
			self._mechanical_failure_probability,
		)

	def _simulate_lap_race(
		self,
		participants: list[dict[str, Any]],
		circuit: Circuit,
		starting_grid: list[int] | None = None,
	) -> dict[str, Any]:
		return simulate_lap_race(
			participants,
			circuit,
			self._grid_score,
			self._assign_fuel_strategy,
			self._dirty_air_penalty_ms,
			self._lap_time_ms,
			self._fuel_per_lap,
			self._fuel_for_stint,
			self._should_attempt_pass,
			self._overtaking_delta_ms,
			self._pass_succeeds,
			starting_grid,
		)

	def _simulate_qualifying(
		self,
		participants: list[dict[str, Any]],
		circuit: Circuit,
	) -> list[dict[str, Any]]:
		results: list[dict[str, Any]] = []
		for entrant in participants:
			best_lap_ms = min(
				self._qualifying_lap_time_ms(entrant, circuit)
				for _ in range(QUALIFYING_ATTEMPTS)
			)
			results.append({
				"driver_id": entrant["driver_id"],
				"driver_name": entrant["driver_name"],
				"team_id": entrant["team_id"],
				"team_name": entrant["team_name"],
				"best_lap_ms": best_lap_ms,
			})

		results.sort(key=lambda row: (row["best_lap_ms"], row["driver_id"]))
		for idx, row in enumerate(results, start=1):
			row["position"] = idx
		return results

	def simulate_qualifying(self, state: GameState) -> dict[str, Any]:
		participants, circuit = self._build_participants(state)
		qualifying_results = self._simulate_qualifying(participants, circuit)
		event_key = self._current_event_key(state)
		if event_key is not None:
			state.qualifying_results_by_event[event_key] = qualifying_results

		event = state.calendar.current_event
		return {
			"event_name": event.name if event else circuit.name,
			"week": event.week if event else state.calendar.current_week,
			"circuit_name": circuit.name,
			"circuit_location": circuit.location,
			"circuit_country": circuit.country,
			"laps": circuit.laps,
			"qualifying_complete": True,
			"qualifying_results": qualifying_results,
		}

	def simulate_race(self, state: GameState) -> dict[str, Any]:
		"""
		Simulates a race lap by lap and returns lap history plus final classification.
		"""
		team_lookup = {t.id: t for t in state.teams}
		driver_lookup = {d.id: d for d in state.drivers}
		participants, circuit = self._build_participants(state)

		crashed_participants, mechanical_participants = self._prepare_participants(
			state,
			circuit,
			participants,
			team_lookup,
		)
		event_key = self._current_event_key(state)
		qualifying_results = []
		if event_key is not None:
			qualifying_results = list(state.qualifying_results_by_event.get(event_key, []))
		if not qualifying_results:
			qualifying_results = self._simulate_qualifying(participants, circuit)
			if event_key is not None:
				state.qualifying_results_by_event[event_key] = qualifying_results
		starting_grid = [row["driver_id"] for row in qualifying_results]
		race_run = self._simulate_lap_race(participants, circuit, starting_grid)

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
			"qualifying_results": qualifying_results,
			"total_laps": race_run["total_laps"],
			"lap_history": race_run["lap_history"],
			"results": results,
			"crash_outs": crash_outs,
			"mechanical_outs": mechanical_outs,
		}
