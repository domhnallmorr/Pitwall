from app.models.chassis import Chassis
from app.models.state import GameState


MAX_CHASSIS_WEAR = 100


def player_chassis_fail_probability(wear: int) -> float:
    return min(0.35, max(0.0, int(wear or 0) * 0.002))


def get_player_test_chassis(state: GameState) -> Chassis | None:
    if not state.player_chassis:
        return None
    if state.player_test_chassis_id is not None:
        selected = next((chassis for chassis in state.player_chassis if chassis.id == state.player_test_chassis_id), None)
        if selected:
            return selected
    fallback = state.player_chassis[0]
    state.player_test_chassis_id = fallback.id
    return fallback


def get_player_race_chassis_assignments(state: GameState) -> dict[int, int]:
    player_team = state.player_team
    if not player_team or len(state.player_chassis) < 2:
        return {}

    driver_ids = [player_team.driver1_id, player_team.driver2_id]
    available_ids = [chassis.id for chassis in state.player_chassis]
    cleaned: dict[int, int] = {}
    used_chassis_ids: set[int] = set()

    for driver_id in driver_ids:
        chassis_id = state.player_race_chassis_assignments.get(driver_id)
        if chassis_id in available_ids and chassis_id not in used_chassis_ids:
            cleaned[driver_id] = chassis_id
            used_chassis_ids.add(chassis_id)

    remaining_ids = [chassis_id for chassis_id in available_ids if chassis_id not in used_chassis_ids]
    for driver_id in driver_ids:
        if driver_id not in cleaned and remaining_ids:
            cleaned[driver_id] = remaining_ids.pop(0)

    state.player_race_chassis_assignments = cleaned
    return cleaned


def get_player_driver_chassis(state: GameState, driver_id: int) -> Chassis | None:
    assignments = get_player_race_chassis_assignments(state)
    chassis_id = assignments.get(driver_id)
    if chassis_id is None:
        return None
    return next((chassis for chassis in state.player_chassis if chassis.id == chassis_id), None)


def apply_player_test_wear(state: GameState, kms: int) -> int:
    chassis = get_player_test_chassis(state)
    if chassis is None:
        return 0
    increment = max(0, int(kms)) // 100
    chassis.wear = min(MAX_CHASSIS_WEAR, max(0, int(chassis.wear or 0)) + increment)
    return chassis.wear


def apply_player_race_wear(state: GameState, wear_increase: int) -> dict[int, int]:
    updated: dict[int, int] = {}
    for driver_id, chassis_id in get_player_race_chassis_assignments(state).items():
        chassis = next((item for item in state.player_chassis if item.id == chassis_id), None)
        if chassis is None:
            continue
        chassis.wear = min(MAX_CHASSIS_WEAR, max(0, int(chassis.wear or 0)) + wear_increase)
        updated[driver_id] = chassis.wear
    return updated
