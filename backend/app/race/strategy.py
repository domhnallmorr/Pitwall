import random

from app.models.circuit import Circuit
from app.race.constants import PIT_STRATEGY_WEIGHTS, TOTAL_RACE_FUEL_KG


def fuel_per_lap(circuit: Circuit) -> float:
	return TOTAL_RACE_FUEL_KG / max(1, circuit.laps)


def fuel_for_stint(circuit: Circuit, stint_laps: int) -> float:
	return round(fuel_per_lap(circuit) * max(0, stint_laps), 3)


def pick_planned_stops() -> int:
	roll = random.uniform(0.0, 1.0)
	cumulative = 0.0
	for stops, weight in PIT_STRATEGY_WEIGHTS:
		cumulative += weight
		if roll <= cumulative:
			return stops
	return PIT_STRATEGY_WEIGHTS[-1][0]


def strategy_windows(stop_count: int, total_laps: int) -> list[tuple[int, int]]:
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


def assign_fuel_strategy(entrant: dict, circuit: Circuit):
	planned_stops = pick_planned_stops()
	windows = strategy_windows(planned_stops, circuit.laps)
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
	entrant["fuel_kg"] = fuel_for_stint(circuit, first_stint_end)
