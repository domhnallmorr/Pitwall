import math

from app.models.state import GameState


PLAYER_SPARES_MAX = 10
PLAYER_SPARE_BUILD_COST = 52_500
PLAYER_SPARE_REPAIR_MIN_WEAR = 25
PLAYER_SPARE_REPAIR_MAX_WEAR = 27
PLAYER_SPARE_REPAIR_AVERAGE_WEAR = 26
PLAYER_MECHANICS_REPAIR_PERCENT_PER_SPARE = 22

FACTORY_SIZE_TO_SPARE_BUILD_PERCENT = {
    1: 45,
    2: 36,
    3: 27,
    4: 18,
    5: 9,
}


def get_spare_build_percentage(factory_size: int | None) -> int:
    size = min(max(int(factory_size or 1), 1), 5)
    return FACTORY_SIZE_TO_SPARE_BUILD_PERCENT[size]


def sync_player_construction_usage_period(state: GameState) -> None:
    current_week = int(getattr(state.calendar, "current_week", 1) or 1)
    current_year = int(getattr(state, "year", 0) or 0)
    if (
        getattr(state, "player_construction_usage_week", None) != current_week
        or getattr(state, "player_construction_usage_year", None) != current_year
    ):
        state.player_construction_usage_percent = 0
        state.player_construction_usage_week = current_week
        state.player_construction_usage_year = current_year


def sync_player_mechanics_usage_period(state: GameState) -> None:
    current_week = int(getattr(state.calendar, "current_week", 1) or 1)
    current_year = int(getattr(state, "year", 0) or 0)
    if (
        getattr(state, "player_mechanics_usage_week", None) != current_week
        or getattr(state, "player_mechanics_usage_year", None) != current_year
    ):
        state.player_mechanics_usage_percent = 0
        state.player_mechanics_usage_week = current_week
        state.player_mechanics_usage_year = current_year


def get_spare_build_requirements(engineering_staff: int | None, factory_size: int | None) -> dict[str, int | bool | str | None]:
    available_staff = max(0, int(engineering_staff or 0))
    percentage = get_spare_build_percentage(factory_size)
    required_staff = max(1, math.ceil(available_staff * (percentage / 100))) if available_staff > 0 else 1
    enough_engineering_staff = available_staff > 0 and available_staff >= required_staff
    return {
        "engineering_required_percentage": percentage,
        "engineering_required_staff": required_staff,
        "engineering_staff_available": available_staff,
        "enough_engineering_staff": enough_engineering_staff,
    }


def get_player_spares_construction_data(state: GameState) -> dict[str, int | bool | str | None]:
    player_team = state.player_team
    available_spares = max(0, int(getattr(state, "player_spares", 0) or 0))
    sync_player_construction_usage_period(state)
    current_usage = max(0, min(100, int(getattr(state, "player_construction_usage_percent", 0) or 0)))
    if not player_team:
        return {
            "available": available_spares,
            "max": PLAYER_SPARES_MAX,
            "build_cost": PLAYER_SPARE_BUILD_COST,
            "construction_usage_percent": current_usage,
            "construction_capacity_remaining": max(0, 100 - current_usage),
            "engineering_required_percentage": None,
            "engineering_required_staff": None,
            "engineering_staff_available": 0,
            "enough_engineering_staff": False,
            "can_build": False,
            "blocking_reason": "No player team assigned",
        }

    requirements = get_spare_build_requirements(getattr(player_team, "engineering_staff", 0), getattr(player_team, "factory_size", 1))
    blocking_reason = None
    if available_spares >= PLAYER_SPARES_MAX:
        blocking_reason = "Spare stock is already full"
    elif state.finance.balance < PLAYER_SPARE_BUILD_COST:
        blocking_reason = "Insufficient funds"
    elif not requirements["enough_engineering_staff"]:
        blocking_reason = "Insufficient engineering staff"
    elif current_usage + int(requirements["engineering_required_percentage"] or 0) > 100:
        blocking_reason = "Construction capacity fully allocated this week"

    return {
        "available": available_spares,
        "max": PLAYER_SPARES_MAX,
        "build_cost": PLAYER_SPARE_BUILD_COST,
        "construction_usage_percent": current_usage,
        "construction_capacity_remaining": max(0, 100 - current_usage),
        "engineering_required_percentage": requirements["engineering_required_percentage"],
        "engineering_required_staff": requirements["engineering_required_staff"],
        "engineering_staff_available": requirements["engineering_staff_available"],
        "enough_engineering_staff": requirements["enough_engineering_staff"],
        "can_build": blocking_reason is None,
        "blocking_reason": blocking_reason,
    }


def estimate_spares_for_wear_repair(wear_points: int | None) -> int:
    requested = max(0, int(wear_points or 0))
    if requested <= 0:
        return 0
    return max(1, math.ceil(requested / PLAYER_SPARE_REPAIR_AVERAGE_WEAR))


def estimate_mechanics_percent_for_spares(spare_sets: int | None) -> int:
    spare_count = max(0, int(spare_sets or 0))
    if spare_count <= 0:
        return 0
    return spare_count * PLAYER_MECHANICS_REPAIR_PERCENT_PER_SPARE


def get_player_maintenance_data(state: GameState) -> dict[str, int | bool]:
    sync_player_mechanics_usage_period(state)
    player_team = state.player_team
    available_staff = max(0, int(getattr(player_team, "mechanics_staff", 0) or 0)) if player_team else 0
    current_usage = max(0, min(100, int(getattr(state, "player_mechanics_usage_percent", 0) or 0)))
    return {
        "mechanics_usage_percent": current_usage,
        "mechanics_capacity_remaining": max(0, 100 - current_usage),
        "mechanics_staff_available": available_staff,
        "mechanics_required_percent_per_spare": PLAYER_MECHANICS_REPAIR_PERCENT_PER_SPARE,
        "can_repair": available_staff > 0 and current_usage < 100,
    }
