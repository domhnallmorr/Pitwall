import logging

from app.core.player_car_development import PlayerCarDevelopmentManager
from app.core.management_transfers import CommercialManagerTransferManager, TechnicalDirectorTransferManager
from app.core.transfers import TransferManager
from app.core.workforce_costs import WorkforceCostManager
from app.models.calendar import EventType
from app.models.email import EmailCategory
from app.models.finance import TransactionCategory
from app.models.state import GameState


def handle_replace_driver(
    state: GameState,
    logger: logging.Logger,
    driver_id: int | None,
    incoming_driver_id: int | None = None,
):
    try:
        if driver_id is None:
            return state, {"status": "error", "message": "Driver id is required"}
        signing = TransferManager().sign_player_replacement(
            state,
            outgoing_driver_id=int(driver_id),
            incoming_driver_id=int(incoming_driver_id) if incoming_driver_id is not None else None,
        )
        return state, {
            "type": "driver_replaced",
            "status": "success",
            "data": signing,
        }
    except ValueError as ve:
        return state, {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error replacing driver: {e}")
        return state, {"status": "error", "message": str(e)}


def handle_get_replacement_candidates(state: GameState, logger: logging.Logger, driver_id: int | None):
    try:
        if driver_id is None:
            return {"status": "error", "message": "Driver id is required"}

        outgoing = next((d for d in state.drivers if d.id == int(driver_id)), None)
        if outgoing is None:
            return {"status": "error", "message": "Driver not found"}

        candidates = TransferManager().get_player_replacement_candidates(state, int(driver_id))
        payload = {
            "outgoing_driver": {
                "id": outgoing.id,
                "name": outgoing.name,
                "contract_length": outgoing.contract_length,
            },
            "candidates": [
                {
                    "id": d.id,
                    "name": d.name,
                    "age": d.age,
                    "country": d.country,
                    "speed": d.speed,
                    "wage": d.wage,
                    "pay_driver": d.pay_driver,
                }
                for d in candidates
            ],
        }
        return {"type": "replacement_candidates", "status": "success", "data": payload}
    except ValueError as ve:
        return {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error loading replacement candidates: {e}")
        return {"status": "error", "message": str(e)}


def handle_replace_commercial_manager(
    state: GameState,
    logger: logging.Logger,
    manager_id: int | None,
    incoming_manager_id: int | None = None,
):
    try:
        if manager_id is None:
            return state, {"status": "error", "message": "Commercial manager id is required"}
        signing = CommercialManagerTransferManager().sign_player_replacement(
            state,
            outgoing_manager_id=int(manager_id),
            incoming_manager_id=int(incoming_manager_id) if incoming_manager_id is not None else None,
        )
        return state, {
            "type": "commercial_manager_replaced",
            "status": "success",
            "data": signing,
        }
    except ValueError as ve:
        return state, {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error replacing commercial manager: {e}")
        return state, {"status": "error", "message": str(e)}


def handle_replace_technical_director(
    state: GameState,
    logger: logging.Logger,
    director_id: int | None,
    incoming_director_id: int | None = None,
):
    try:
        if director_id is None:
            return state, {"status": "error", "message": "Technical director id is required"}
        signing = TechnicalDirectorTransferManager().sign_player_replacement(
            state,
            outgoing_director_id=int(director_id),
            incoming_director_id=int(incoming_director_id) if incoming_director_id is not None else None,
        )
        return state, {
            "type": "technical_director_replaced",
            "status": "success",
            "data": signing,
        }
    except ValueError as ve:
        return state, {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error replacing technical director: {e}")
        return state, {"status": "error", "message": str(e)}


def handle_get_manager_replacement_candidates(state: GameState, logger: logging.Logger, manager_id: int | None):
    try:
        if manager_id is None:
            return {"status": "error", "message": "Commercial manager id is required"}

        outgoing = next((m for m in state.commercial_managers if m.id == int(manager_id)), None)
        if outgoing is None:
            return {"status": "error", "message": "Commercial manager not found"}

        candidates = CommercialManagerTransferManager().get_player_replacement_candidates(state, int(manager_id))
        payload = {
            "market_type": "commercial_manager",
            "outgoing_manager": {
                "id": outgoing.id,
                "name": outgoing.name,
                "contract_length": outgoing.contract_length,
            },
            "candidates": [
                {
                    "id": m.id,
                    "name": m.name,
                    "age": m.age,
                    "country": m.country,
                    "skill": m.skill,
                    "salary": m.salary,
                }
                for m in candidates
            ],
        }
        return {"type": "manager_replacement_candidates", "status": "success", "data": payload}
    except ValueError as ve:
        return {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error loading commercial manager replacement candidates: {e}")
        return {"status": "error", "message": str(e)}


def handle_get_technical_director_replacement_candidates(
    state: GameState,
    logger: logging.Logger,
    director_id: int | None,
):
    try:
        if director_id is None:
            return {"status": "error", "message": "Technical director id is required"}

        outgoing = next((d for d in state.technical_directors if d.id == int(director_id)), None)
        if outgoing is None:
            return {"status": "error", "message": "Technical director not found"}

        candidates = TechnicalDirectorTransferManager().get_player_replacement_candidates(state, int(director_id))
        payload = {
            "market_type": "technical_director",
            "outgoing_manager": {
                "id": outgoing.id,
                "name": outgoing.name,
                "contract_length": outgoing.contract_length,
            },
            "candidates": [
                {
                    "id": d.id,
                    "name": d.name,
                    "age": d.age,
                    "country": d.country,
                    "skill": d.skill,
                    "salary": d.salary,
                }
                for d in candidates
            ],
        }
        return {"type": "manager_replacement_candidates", "status": "success", "data": payload}
    except ValueError as ve:
        return {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error loading technical director replacement candidates: {e}")
        return {"status": "error", "message": str(e)}


def handle_start_car_development(state: GameState, logger: logging.Logger, development_type: str | None):
    try:
        if not development_type:
            return {"type": "car_development_started", "status": "error", "message": "development_type is required"}
        project = PlayerCarDevelopmentManager().start(state, development_type)
        return {
            "type": "car_development_started",
            "status": "success",
            "data": {
                "active": project.active,
                "development_type": project.development_type,
                "total_weeks": project.total_weeks,
                "weeks_remaining": project.weeks_remaining,
                "speed_delta": project.speed_delta,
                "total_cost": project.total_cost,
                "weekly_cost": project.weekly_cost,
                "paid": project.paid,
            },
        }
    except ValueError as ve:
        return {"type": "car_development_started", "status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error starting car development: {e}")
        return {"type": "car_development_started", "status": "error", "message": str(e)}


def handle_repair_car_wear(state: GameState, logger: logging.Logger, wear_points: int | None):
    try:
        team = state.player_team
        if not team:
            return {"type": "car_wear_repaired", "status": "error", "message": "No player team assigned"}
        current_wear = max(0, int(getattr(team, "car_wear", 0) or 0))
        if current_wear <= 0:
            return {"type": "car_wear_repaired", "status": "error", "message": "No wear to repair"}
        if wear_points is None:
            return {"type": "car_wear_repaired", "status": "error", "message": "wear_points is required"}
        requested = max(0, int(wear_points))
        if requested <= 0:
            return {"type": "car_wear_repaired", "status": "error", "message": "Repair amount must be greater than zero"}

        applied = min(requested, current_wear)
        cost = applied * 3_200  # 100 wear => 320,000
        team.car_wear = current_wear - applied

        state.finance.add_transaction(
            week=state.calendar.current_week,
            year=state.year,
            amount=-cost,
            category=TransactionCategory.MAINTENANCE,
            description=f"Car wear repair ({applied} wear)",
        )
        state.add_email(
            sender="Chief Mechanic",
            subject="Car Wear Repairs Completed",
            body=(
                f"Wear repairs have been completed.\n\n"
                f"Wear repaired: {applied}\n"
                f"Wear before: {current_wear}\n"
                f"Wear after: {team.car_wear}\n"
                f"Cost: ${cost:,}"
            ),
            category=EmailCategory.GENERAL,
        )
        return {
            "type": "car_wear_repaired",
            "status": "success",
            "data": {
                "applied_wear_repair": applied,
                "cost": cost,
                "wear_before": current_wear,
                "wear_after": team.car_wear,
            },
        }
    except Exception as e:
        logger.error(f"Error repairing car wear: {e}")
        return {"type": "car_wear_repaired", "status": "error", "message": str(e)}


def handle_update_workforce(state: GameState, logger: logging.Logger, workforce: int | None):
    try:
        team = state.player_team
        if not team:
            return {"type": "workforce_updated", "status": "error", "message": "No player team assigned"}
        if workforce is None:
            return {"type": "workforce_updated", "status": "error", "message": "workforce is required"}

        requested = int(workforce)
        if requested < 0 or requested > 250:
            return {"type": "workforce_updated", "status": "error", "message": "Workforce must be between 0 and 250"}

        previous = int(getattr(team, "workforce", 0) or 0)
        team.workforce = requested

        manager = WorkforceCostManager()
        races_in_season = max(1, sum(1 for e in state.calendar.events if e.type == EventType.RACE))
        projected_race_cost = manager.calculate_race_cost(team.workforce, races_in_season)
        annual_payroll = max(0, team.workforce) * manager.annual_avg_wage
        delta = team.workforce - previous

        state.add_email(
            sender="Human Resources",
            subject="Workforce Updated",
            body=(
                f"Workforce has been updated.\n\n"
                f"Previous staff count: {previous}\n"
                f"New staff count: {team.workforce}\n"
                f"Change: {delta:+}\n"
                f"Projected payroll per race: ${projected_race_cost:,}\n"
                f"Projected annual payroll: ${annual_payroll:,}"
            ),
            category=EmailCategory.GENERAL,
        )

        return {
            "type": "workforce_updated",
            "status": "success",
            "data": {
                "team_name": team.name,
                "previous_workforce": previous,
                "new_workforce": team.workforce,
                "delta": delta,
                "annual_avg_wage": manager.annual_avg_wage,
                "projected_race_cost": projected_race_cost,
                "projected_annual_payroll": annual_payroll,
                "races_in_season": races_in_season,
            },
        }
    except Exception as e:
        logger.error(f"Error updating workforce: {e}")
        return {"type": "workforce_updated", "status": "error", "message": str(e)}
