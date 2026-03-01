import logging

from app.core.player_car_development import PlayerCarDevelopmentManager
from app.core.transfers import TransferManager
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
