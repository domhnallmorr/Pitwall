import random

from app.models.circuit import Circuit
from app.race.constants import (
	DIRTY_AIR_GAP_THRESHOLD_MS,
	DIRTY_AIR_LAP_PENALTY_MS,
	FUEL_PENALTY_MS_PER_KG,
	LAP_JITTER_RANGE_MS,
	OVERTAKE_SUCCESS_PROBABILITY,
	PACE_CENTER,
	PACE_TO_MS_FACTOR,
	TYRE_DEGRADATION_MS_PER_LAP,
)


def get_performance_weight(driver_speed: int, car_speed: int) -> int:
	return max(1, int((driver_speed * 0.65) + (car_speed * 0.35)))


def grid_score(entrant: dict, grid_jitter_range_ms: int) -> int:
	return entrant["performance_weight"] * 1000 + random.randint(-grid_jitter_range_ms, grid_jitter_range_ms)


def tyre_wear_penalty_ms(stint_laps: int) -> int:
	return max(0, int(stint_laps)) * TYRE_DEGRADATION_MS_PER_LAP


def lap_time_ms(entrant: dict, circuit: Circuit) -> int:
	base_bonus_ms = int((entrant["performance_weight"] - PACE_CENTER) * PACE_TO_MS_FACTOR)
	jitter_ms = random.randint(-LAP_JITTER_RANGE_MS, LAP_JITTER_RANGE_MS)
	power_adjustment_ms = int((float(circuit.power_factor) - 1.0) * entrant["car_speed"] * 3)
	fuel_penalty_ms = int((entrant.get("fuel_kg", 0.0) or 0.0) * FUEL_PENALTY_MS_PER_KG)
	degradation_ms = tyre_wear_penalty_ms(entrant.get("stint_laps", 0))
	dirty_air_penalty_ms = int(entrant.get("dirty_air_penalty_ms", 0) or 0)
	return max(
		45_000,
		circuit.base_laptime_ms - base_bonus_ms - power_adjustment_ms
		+ fuel_penalty_ms + degradation_ms + dirty_air_penalty_ms + jitter_ms,
	)


def dirty_air_penalty_ms(gap_ahead_ms: int | None, same_lap: bool) -> int:
	if not same_lap or gap_ahead_ms is None:
		return 0
	if gap_ahead_ms <= DIRTY_AIR_GAP_THRESHOLD_MS:
		return DIRTY_AIR_LAP_PENALTY_MS
	return 0


def overtaking_delta_ms(circuit: Circuit) -> int:
	raw_delta = float(circuit.overtaking_delta or 0)
	return int(raw_delta * 1000) if raw_delta < 50 else int(raw_delta)


def should_attempt_pass(lap_time_gain_ms: int, overtake_delta_ms: float) -> bool:
	return lap_time_gain_ms > 0 and lap_time_gain_ms >= int(overtake_delta_ms)


def pass_succeeds() -> bool:
	return random.randint(1, 1000) <= int(OVERTAKE_SUCCESS_PROBABILITY * 1000)
