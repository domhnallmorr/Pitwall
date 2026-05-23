import logging

from app.commands.market_command_helpers import (
    require_value,
    run_handler,
    run_state_handler,
    state_success_response,
    success_response,
)
from app.core.player_driver_negotiations import PlayerDriverNegotiationManager
from app.core.transfers import TransferManager
from app.models.state import GameState


def handle_replace_driver(
    state: GameState,
    logger: logging.Logger,
    driver_id: int | None,
    incoming_driver_id: int | None = None,
):
    def action():
        driver_id_value = int(require_value(driver_id, "Driver id is required"))
        signing = TransferManager().sign_player_replacement(
            state,
            outgoing_driver_id=driver_id_value,
            incoming_driver_id=int(incoming_driver_id) if incoming_driver_id is not None else None,
        )
        return state_success_response(state, "driver_replaced", signing)

    return run_state_handler(state, logger, "Error replacing driver", action)


def handle_get_replacement_candidates(state: GameState, logger: logging.Logger, driver_id: int | None):
    def action():
        driver_id_value = int(require_value(driver_id, "Driver id is required"))
        outgoing = next((d for d in state.drivers if d.id == driver_id_value), None)
        if outgoing is None:
            raise ValueError("Driver not found")

        candidates = TransferManager().get_player_replacement_candidates(state, driver_id_value)
        driver_team_lookup = {}
        for team in state.teams:
            if team.driver1_id is not None:
                driver_team_lookup[team.driver1_id] = team.name
            if team.driver2_id is not None:
                driver_team_lookup[team.driver2_id] = team.name
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
                    "consistency": getattr(d, "consistency", 50),
                    "qualifying": getattr(d, "qualifying", 3),
                    "racecraft": getattr(d, "racecraft", 3),
                    "wage": d.wage,
                    "pay_driver": d.pay_driver,
                    "contract_length": d.contract_length,
                    "team_name": driver_team_lookup.get(d.id),
                }
                for d in candidates
            ],
        }
        return success_response("replacement_candidates", payload)

    return run_handler(logger, "Error loading replacement candidates", action)


def handle_offer_driver(
    state: GameState,
    logger: logging.Logger,
    driver_id: int | None,
    incoming_driver_id: int | None,
    salary_offer: int | None,
    contract_length: int | None,
):
    def action():
        result = PlayerDriverNegotiationManager().submit_offer(
            state,
            outgoing_driver_id=int(require_value(driver_id, "Driver id is required")),
            incoming_driver_id=int(require_value(incoming_driver_id, "Incoming driver id is required")),
            salary_offer=int(require_value(salary_offer, "Salary offer is required")),
            contract_length=int(require_value(contract_length, "Contract length is required")),
        )
        return state_success_response(state, "driver_offer_result", result)

    return run_state_handler(state, logger, "Error offering contract to driver", action)
