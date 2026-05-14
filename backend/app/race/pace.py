import random

from app.models.circuit import Circuit
from app.race.constants import (
	CAR_PACE_MS_PER_POINT,
	CONSISTENCY_MAX_LAP_PENALTY_MAX_MS,
	CONSISTENCY_MIN_LAP_PENALTY_MAX_MS,
	DIRTY_AIR_GAP_THRESHOLD_MS,
	DIRTY_AIR_LAP_PENALTY_MS,
	DRIVER_PACE_MS_PER_POINT,
	ENGINE_POWER_MAX_EFFECT_MS,
	FUEL_PENALTY_MS_PER_KG,
	OVERTAKE_SUCCESS_PROBABILITY,
	PACE_CENTER,
	QUALIFYING_DRIVER_PACE_FACTOR,
	QUALIFYING_JITTER_RANGE_MS,
	QUALIFYING_REDUCTION_CAP_MS_BY_STAR,
	TYRE_DEGRADATION_MS_PER_LAP,
	TYRE_COMPOUND_GRIP_CLASS_EFFECT_MS,
	TYRE_COMPOUND_GRIP_QUALITY_MS_PER_POINT,
	TYRE_COMPOUND_QUALITY_REFERENCE,
	TYRE_COMPOUND_WEAR_CLASS_MULTIPLIER,
	TYRE_COMPOUND_WEAR_QUALITY_MULTIPLIER_DELTA,
	TYRE_GRIP_MAX_EFFECT_MS,
	TYRE_WEAR_MAX_MULTIPLIER_DELTA,
)


def driver_pace_bonus_ms(entrant: dict) -> int:
	driver_speed = float(entrant.get("driver_speed", PACE_CENTER) or PACE_CENTER)
	return int(round((driver_speed - PACE_CENTER) * DRIVER_PACE_MS_PER_POINT))


def qualifying_driver_pace_bonus_ms(entrant: dict) -> int:
	driver_speed = float(entrant.get("driver_speed", PACE_CENTER) or PACE_CENTER)
	return int(round((driver_speed - PACE_CENTER) * DRIVER_PACE_MS_PER_POINT * QUALIFYING_DRIVER_PACE_FACTOR))


def car_pace_bonus_ms(entrant: dict) -> int:
	car_speed = float(entrant.get("car_speed", PACE_CENTER) or PACE_CENTER)
	return int(round((car_speed - PACE_CENTER) * CAR_PACE_MS_PER_POINT))


def base_pace_bonus_ms(entrant: dict) -> int:
	return driver_pace_bonus_ms(entrant) + car_pace_bonus_ms(entrant)


def qualifying_reduction_cap_ms(entrant: dict) -> int:
	qualifying = entrant.get("driver_qualifying", 3)
	if qualifying is None:
		qualifying = 3
	qualifying = int(max(1, min(5, qualifying)))
	return QUALIFYING_REDUCTION_CAP_MS_BY_STAR[qualifying]


def qualifying_attribute_reduction_ms(entrant: dict) -> int:
	return random.randint(0, qualifying_reduction_cap_ms(entrant))


def consistency_max_lap_penalty_ms(entrant: dict) -> float:
	consistency = entrant.get("driver_consistency", PACE_CENTER)
	if consistency is None:
		consistency = PACE_CENTER
	consistency = float(consistency)
	consistency = max(1.0, min(100.0, consistency))
	scale = (consistency - 1.0) / 99.0
	range_ms = CONSISTENCY_MAX_LAP_PENALTY_MAX_MS - CONSISTENCY_MIN_LAP_PENALTY_MAX_MS
	return CONSISTENCY_MAX_LAP_PENALTY_MAX_MS - scale * range_ms


def consistency_lap_penalty_ms(entrant: dict) -> int:
	return random.randint(0, int(round(consistency_max_lap_penalty_ms(entrant))))


def grid_score(entrant: dict, grid_jitter_range_ms: int) -> int:
	return base_pace_bonus_ms(entrant) + random.randint(-grid_jitter_range_ms, grid_jitter_range_ms)


def tyre_grip_effect_ms(entrant: dict) -> int:
	if "tyre_compound_grip" in entrant:
		compound_name = str(entrant.get("tyre_compound_name", "Medium") or "Medium")
		class_effect_ms = TYRE_COMPOUND_GRIP_CLASS_EFFECT_MS.get(compound_name, 0)
		compound_grip = float(entrant.get("tyre_compound_grip", TYRE_COMPOUND_QUALITY_REFERENCE) or TYRE_COMPOUND_QUALITY_REFERENCE)
		quality_effect_ms = int(round((TYRE_COMPOUND_QUALITY_REFERENCE - compound_grip) * TYRE_COMPOUND_GRIP_QUALITY_MS_PER_POINT))
		return class_effect_ms + quality_effect_ms
	tyre_grip = float(entrant.get("tyre_grip", 50) or 50)
	return int(TYRE_GRIP_MAX_EFFECT_MS * (50.0 - tyre_grip) / 100.0)


def tyre_wear_multiplier(entrant: dict) -> float:
	if "tyre_compound_wear" in entrant:
		compound_name = str(entrant.get("tyre_compound_name", "Medium") or "Medium")
		class_multiplier = TYRE_COMPOUND_WEAR_CLASS_MULTIPLIER.get(compound_name, 1.0)
		compound_wear = float(entrant.get("tyre_compound_wear", TYRE_COMPOUND_QUALITY_REFERENCE) or TYRE_COMPOUND_QUALITY_REFERENCE)
		quality_multiplier = ((TYRE_COMPOUND_QUALITY_REFERENCE - compound_wear) / 50.0) * TYRE_COMPOUND_WEAR_QUALITY_MULTIPLIER_DELTA
		return max(0.5, class_multiplier + quality_multiplier)
	tyre_wear = float(entrant.get("tyre_wear", 50) or 50)
	return 1.0 + ((50.0 - tyre_wear) / 50.0) * TYRE_WEAR_MAX_MULTIPLIER_DELTA


def tyre_wear_penalty_ms(stint_laps: int, entrant: dict | None = None) -> int:
	multiplier = tyre_wear_multiplier(entrant or {})
	return int(max(0, int(stint_laps)) * TYRE_DEGRADATION_MS_PER_LAP * multiplier)


def engine_power_effect_ms(entrant: dict, circuit: Circuit) -> int:
	engine_power = float(entrant.get("engine_power", 50) or 50)
	track_power_sensitivity = float(circuit.power_factor or 0)
	max_power_effect = ENGINE_POWER_MAX_EFFECT_MS * track_power_sensitivity / 10.0
	return int(max_power_effect * (50.0 - engine_power) / 100.0)


def lap_time_ms(entrant: dict, circuit: Circuit) -> int:
	base_bonus_ms = base_pace_bonus_ms(entrant)
	consistency_penalty_ms = consistency_lap_penalty_ms(entrant)
	engine_adjustment_ms = engine_power_effect_ms(entrant, circuit)
	tyre_grip_adjustment_ms = tyre_grip_effect_ms(entrant)
	fuel_penalty_ms = int((entrant.get("fuel_kg", 0.0) or 0.0) * FUEL_PENALTY_MS_PER_KG)
	degradation_ms = tyre_wear_penalty_ms(entrant.get("stint_laps", 0), entrant)
	dirty_air_penalty_ms = int(entrant.get("dirty_air_penalty_ms", 0) or 0)
	return max(
		45_000,
		circuit.base_laptime_ms - base_bonus_ms + engine_adjustment_ms + tyre_grip_adjustment_ms
		+ fuel_penalty_ms + degradation_ms + dirty_air_penalty_ms + consistency_penalty_ms,
	)


def qualifying_lap_time_ms(entrant: dict, circuit: Circuit) -> int:
	base_bonus_ms = qualifying_driver_pace_bonus_ms(entrant) + car_pace_bonus_ms(entrant)
	qualifying_reduction_ms = qualifying_attribute_reduction_ms(entrant)
	jitter_ms = random.randint(-QUALIFYING_JITTER_RANGE_MS, QUALIFYING_JITTER_RANGE_MS)
	engine_adjustment_ms = engine_power_effect_ms(entrant, circuit)
	tyre_grip_adjustment_ms = tyre_grip_effect_ms(entrant)
	return max(
		45_000,
		circuit.base_laptime_ms - base_bonus_ms - qualifying_reduction_ms + engine_adjustment_ms + tyre_grip_adjustment_ms + jitter_ms,
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


def _racecraft_rating(entrant: dict) -> int:
	return max(1, min(5, int(entrant.get("driver_racecraft", 3) or 3)))


def overtake_success_probability(attacker: dict | None = None, defender: dict | None = None) -> float:
	if attacker is None or defender is None:
		return OVERTAKE_SUCCESS_PROBABILITY
	racecraft_delta = _racecraft_rating(attacker) - _racecraft_rating(defender)
	return max(0.35, min(0.85, OVERTAKE_SUCCESS_PROBABILITY + (racecraft_delta * 0.05)))


def pass_succeeds(attacker: dict | None = None, defender: dict | None = None) -> bool:
	return random.randint(1, 1000) <= int(overtake_success_probability(attacker, defender) * 1000)
