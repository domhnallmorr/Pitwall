import random
from typing import Any

from app.models.circuit import Circuit
from app.models.state import GameState
from app.race.constants import (
	AI_MECHANICAL_FAILURE_PROBABILITY,
	MAX_CAR_WEAR,
	MAX_CRASH_OUTS,
	PLAYER_FAILURE_PROB_PER_WEAR,
	PLAYER_MAX_FAILURE_PROBABILITY,
	PLAYER_RACE_WEAR_INCREASE,
)


def pick_crash_count(participant_count: int) -> int:
	if participant_count <= 1:
		return 0
	return random.randint(0, min(MAX_CRASH_OUTS, participant_count - 1))


def mechanical_failure_probability(
	state: GameState,
	team_id: int,
	team_lookup: dict[int, Any],
) -> float:
	if state.player_team_id is None:
		return 0.0
	if team_id == state.player_team_id:
		player_team = team_lookup.get(team_id)
		wear = max(0, int(getattr(player_team, "car_wear", 0) or 0))
		return min(PLAYER_MAX_FAILURE_PROBABILITY, wear * PLAYER_FAILURE_PROB_PER_WEAR)
	return AI_MECHANICAL_FAILURE_PROBABILITY


def prepare_participants(
	state: GameState,
	circuit: Circuit,
	participants: list[dict[str, Any]],
	team_lookup: dict[int, Any],
	pick_crash_count_fn,
	mechanical_failure_probability_fn,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
	crash_count = pick_crash_count_fn(len(participants))
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

		fail_prob = mechanical_failure_probability_fn(state, entry["team_id"], team_lookup)
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
