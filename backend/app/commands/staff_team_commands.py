import logging
import random

from app.core.player_car_development import PlayerCarDevelopmentManager
from app.core.player_spares import (
    PLAYER_SPARE_BUILD_COST,
    PLAYER_MECHANICS_REPAIR_PERCENT_PER_SPARE,
    PLAYER_SPARE_REPAIR_MAX_WEAR,
    PLAYER_SPARE_REPAIR_MIN_WEAR,
    PLAYER_SPARES_MAX,
    estimate_spares_for_wear_repair,
    estimate_mechanics_percent_for_spares,
    get_player_maintenance_data,
    get_player_spares_construction_data,
    sync_player_mechanics_usage_period,
    sync_player_construction_usage_period,
)
from app.models.chassis import Chassis
from app.models.email import EmailCategory
from app.models.finance import TransactionCategory
from app.models.state import GameState


def _build_car_development_response_data(state: GameState) -> dict:
    return PlayerCarDevelopmentManager().get_payload(state)


def handle_start_car_development(state: GameState, logger: logging.Logger, development_type: str | None):
    try:
        scope = development_type or "current_year"
        PlayerCarDevelopmentManager().start(state, scope)
        return {
            "type": "car_development_started",
            "status": "success",
            "data": _build_car_development_response_data(state),
        }
    except ValueError as ve:
        return {"type": "car_development_started", "status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error starting car development: {e}")
        return {"type": "car_development_started", "status": "error", "message": str(e)}


def handle_finish_car_development_stage(state: GameState, logger: logging.Logger):
    try:
        PlayerCarDevelopmentManager().finish_current_stage(state, "current_year")
        return {
            "type": "car_development_stage_finished",
            "status": "success",
            "data": _build_car_development_response_data(state),
        }
    except ValueError as ve:
        return {"type": "car_development_stage_finished", "status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error finishing car development stage: {e}")
        return {"type": "car_development_stage_finished", "status": "error", "message": str(e)}


def handle_finish_car_development_project_stage(state: GameState, logger: logging.Logger, scope: str | None):
    try:
        PlayerCarDevelopmentManager().finish_current_stage(state, scope or "current_year")
        return {
            "type": "car_development_stage_finished",
            "status": "success",
            "data": _build_car_development_response_data(state),
        }
    except ValueError as ve:
        return {"type": "car_development_stage_finished", "status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error finishing car development stage: {e}")
        return {"type": "car_development_stage_finished", "status": "error", "message": str(e)}


def handle_set_car_development_allocation(
    state: GameState,
    logger: logging.Logger,
    scope: str | None,
    allocation_percent: int | None,
):
    try:
        PlayerCarDevelopmentManager().set_allocation(state, scope or "current_year", allocation_percent)
        return {
            "type": "car_development_allocation_updated",
            "status": "success",
            "data": _build_car_development_response_data(state),
        }
    except ValueError as ve:
        return {"type": "car_development_allocation_updated", "status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error updating car development allocation: {e}")
        return {"type": "car_development_allocation_updated", "status": "error", "message": str(e)}


def _get_player_chassis(state: GameState, chassis_id: int | None) -> Chassis:
    player_team = state.player_team
    if not player_team:
        raise ValueError("No player team assigned")
    if chassis_id is None:
        raise ValueError("chassis_id is required")
    chassis = next((item for item in state.player_chassis if item.id == int(chassis_id)), None)
    if not chassis or chassis.team_id != player_team.id:
        raise ValueError("Chassis not found")
    return chassis


def _build_player_race_assignment_data(state: GameState) -> dict:
    player_team = state.player_team
    if not player_team:
        return {}
    driver_lookup = {
        driver.id: driver.name
        for driver in state.drivers
        if driver.id in {player_team.driver1_id, player_team.driver2_id}
    }
    return {
        str(driver_id): {
            "driver_id": driver_id,
            "driver_name": driver_lookup.get(driver_id, f"Driver {driver_id}"),
            "chassis_id": chassis_id,
            "chassis_name": next((item.name for item in state.player_chassis if item.id == chassis_id), None),
        }
        for driver_id, chassis_id in state.player_race_chassis_assignments.items()
    }


def handle_set_test_chassis(state: GameState, logger: logging.Logger, chassis_id: int | None):
    try:
        chassis = _get_player_chassis(state, chassis_id)
        state.player_test_chassis_id = chassis.id
        return {
            "type": "test_chassis_updated",
            "status": "success",
            "data": {
                "test_chassis_id": chassis.id,
                "test_chassis_name": chassis.name,
            },
        }
    except ValueError as ve:
        return {"type": "test_chassis_updated", "status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error setting test chassis: {e}")
        return {"type": "test_chassis_updated", "status": "error", "message": str(e)}


def handle_set_race_chassis_assignments(
    state: GameState,
    logger: logging.Logger,
    driver1_chassis_id: int | None,
    driver2_chassis_id: int | None,
):
    try:
        player_team = state.player_team
        if not player_team:
            return {"type": "race_chassis_assignments_updated", "status": "error", "message": "No player team assigned"}
        chassis_one = _get_player_chassis(state, driver1_chassis_id)
        chassis_two = _get_player_chassis(state, driver2_chassis_id)
        if chassis_one.id == chassis_two.id:
            return {
                "type": "race_chassis_assignments_updated",
                "status": "error",
                "message": "Each driver must be assigned a different chassis",
            }
        state.player_race_chassis_assignments = {
            player_team.driver1_id: chassis_one.id,
            player_team.driver2_id: chassis_two.id,
        }
        return {
            "type": "race_chassis_assignments_updated",
            "status": "success",
            "data": {
                "assignments": _build_player_race_assignment_data(state),
            },
        }
    except ValueError as ve:
        return {"type": "race_chassis_assignments_updated", "status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error updating race chassis assignments: {e}")
        return {"type": "race_chassis_assignments_updated", "status": "error", "message": str(e)}


def handle_repair_chassis_wear(
    state: GameState,
    logger: logging.Logger,
    chassis_id: int | None,
    wear_points: int | None,
):
    try:
        chassis = _get_player_chassis(state, chassis_id)
        current_wear = max(0, int(getattr(chassis, "wear", 0) or 0))
        if current_wear <= 0:
            return {"type": "chassis_wear_repaired", "status": "error", "message": "No wear to repair"}
        if wear_points is None:
            return {"type": "chassis_wear_repaired", "status": "error", "message": "wear_points is required"}
        requested = max(0, int(wear_points))
        if requested <= 0:
            return {"type": "chassis_wear_repaired", "status": "error", "message": "Repair amount must be greater than zero"}
        available_spares = max(0, int(getattr(state, "player_spares", 0) or 0))
        if available_spares <= 0:
            return {"type": "chassis_wear_repaired", "status": "error", "message": "No spare sets available"}
        sync_player_mechanics_usage_period(state)
        maintenance_data = get_player_maintenance_data(state)
        if int(maintenance_data["mechanics_staff_available"]) <= 0:
            return {"type": "chassis_wear_repaired", "status": "error", "message": "No mechanics staff available"}

        target_repair = min(requested, current_wear)
        estimated_spares = estimate_spares_for_wear_repair(target_repair)
        estimated_mechanics_percent = estimate_mechanics_percent_for_spares(estimated_spares)
        mechanics_remaining = int(maintenance_data["mechanics_capacity_remaining"])
        if estimated_mechanics_percent > mechanics_remaining:
            return {"type": "chassis_wear_repaired", "status": "error", "message": "Insufficient mechanics capacity remaining this week"}
        remaining_target = target_repair
        spares_used = 0
        repair_capacity = 0
        while remaining_target > 0 and spares_used < available_spares:
            repair_gain = random.randint(PLAYER_SPARE_REPAIR_MIN_WEAR, PLAYER_SPARE_REPAIR_MAX_WEAR)
            repair_capacity += repair_gain
            remaining_target -= repair_gain
            spares_used += 1

        applied = min(target_repair, repair_capacity)
        if applied <= 0:
            return {"type": "chassis_wear_repaired", "status": "error", "message": "Unable to complete wear repairs"}
        cost = applied * 3_200
        chassis.wear = current_wear - applied
        state.player_spares = max(0, available_spares - spares_used)
        mechanics_usage_before = max(0, int(getattr(state, "player_mechanics_usage_percent", 0) or 0))
        mechanics_percent_used = estimate_mechanics_percent_for_spares(spares_used)
        if mechanics_usage_before + mechanics_percent_used > 100:
            return {"type": "chassis_wear_repaired", "status": "error", "message": "Insufficient mechanics capacity remaining this week"}
        state.player_mechanics_usage_percent = min(100, mechanics_usage_before + mechanics_percent_used)
        state.player_mechanics_usage_week = state.calendar.current_week
        state.player_mechanics_usage_year = state.year

        state.finance.add_transaction(
            week=state.calendar.current_week,
            year=state.year,
            amount=-cost,
            category=TransactionCategory.MAINTENANCE,
            description=f"{chassis.name} wear repair ({applied} wear, {spares_used} spare set{'s' if spares_used != 1 else ''})",
        )
        state.add_email(
            sender="Chief Mechanic",
            subject=f"{chassis.name} Wear Repairs Completed",
            body=(
                f"Wear repairs have been completed.\n\n"
                f"Chassis: {chassis.name}\n"
                f"Wear repaired: {applied}\n"
                f"Wear before: {current_wear}\n"
                f"Wear after: {chassis.wear}\n"
                f"Spare sets used: {spares_used}\n"
                f"Spare sets remaining: {state.player_spares}\n"
                f"Mechanics allocation used: {mechanics_percent_used}%\n"
                f"Mechanics capacity remaining this week: {max(0, 100 - state.player_mechanics_usage_percent)}%\n"
                f"Cost: ${cost:,}"
            ),
            category=EmailCategory.GENERAL,
        )
        return {
            "type": "chassis_wear_repaired",
            "status": "success",
            "data": {
                "chassis_id": chassis.id,
                "chassis_name": chassis.name,
                "applied_wear_repair": applied,
                "cost": cost,
                "wear_before": current_wear,
                "wear_after": chassis.wear,
                "spares_before": available_spares,
                "spares_used": spares_used,
                "spares_after": state.player_spares,
                "estimated_spares_requested": estimated_spares,
                "mechanics_usage_percent_before": mechanics_usage_before,
                "mechanics_usage_percent_used": mechanics_percent_used,
                "mechanics_usage_percent_after": state.player_mechanics_usage_percent,
                "estimated_mechanics_percent_requested": estimated_mechanics_percent,
            },
        }
    except ValueError as ve:
        return {"type": "chassis_wear_repaired", "status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error repairing chassis wear: {e}")
        return {"type": "chassis_wear_repaired", "status": "error", "message": str(e)}


def handle_build_spare_set(state: GameState, logger: logging.Logger):
    try:
        player_team = state.player_team
        if not player_team:
            return {"type": "spare_set_built", "status": "error", "message": "No player team assigned"}

        sync_player_construction_usage_period(state)
        construction = get_player_spares_construction_data(state)
        if not construction["can_build"]:
            return {
                "type": "spare_set_built",
                "status": "error",
                "message": str(construction["blocking_reason"] or "Unable to build spare set"),
            }

        before = max(0, int(getattr(state, "player_spares", 0) or 0))
        usage_before = max(0, int(getattr(state, "player_construction_usage_percent", 0) or 0))
        usage_added = int(construction["engineering_required_percentage"] or 0)
        if before >= PLAYER_SPARES_MAX:
            return {"type": "spare_set_built", "status": "error", "message": "Spare stock is already full"}

        state.player_spares = before + 1
        state.player_construction_usage_percent = min(100, usage_before + usage_added)
        state.player_construction_usage_week = state.calendar.current_week
        state.player_construction_usage_year = state.year
        state.finance.add_transaction(
            week=state.calendar.current_week,
            year=state.year,
            amount=-PLAYER_SPARE_BUILD_COST,
            category=TransactionCategory.CONSTRUCTION,
            description=f"Built 1 spare set ({state.player_spares}/{PLAYER_SPARES_MAX})",
        )
        state.add_email(
            sender="Chief Engineer",
            subject="Spare Set Completed",
            body=(
                "Engineering has completed a new set of spares.\n\n"
                f"Available spares: {state.player_spares} / {PLAYER_SPARES_MAX}\n"
                f"Engineering allocation required: {construction['engineering_required_percentage']}%\n"
                f"Construction capacity used this week: {state.player_construction_usage_percent}% / 100%\n"
                f"Cost: ${PLAYER_SPARE_BUILD_COST:,}"
            ),
            category=EmailCategory.GENERAL,
        )
        return {
            "type": "spare_set_built",
            "status": "success",
            "data": {
                "spares_before": before,
                "spares_after": state.player_spares,
                "max_spares": PLAYER_SPARES_MAX,
                "cost": PLAYER_SPARE_BUILD_COST,
                "engineering_required_percentage": construction["engineering_required_percentage"],
                "engineering_required_staff": construction["engineering_required_staff"],
                "construction_usage_percent_before": usage_before,
                "construction_usage_percent_after": state.player_construction_usage_percent,
            },
        }
    except Exception as e:
        logger.error(f"Error building spare set: {e}")
        return {"type": "spare_set_built", "status": "error", "message": str(e)}
