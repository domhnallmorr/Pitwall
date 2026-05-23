import logging

from app.commands.market_command_helpers import (
    require_value,
    run_handler,
    run_state_handler,
    state_success_response,
    success_response,
)
from app.core.management_transfers import CommercialManagerTransferManager, TechnicalDirectorTransferManager
from app.models.state import GameState


def handle_offer_technical_director(
    state: GameState,
    logger: logging.Logger,
    director_id: int | None,
    incoming_director_id: int | None,
    salary_offer: int | None,
    contract_length: int | None,
):
    def action():
        result = TechnicalDirectorTransferManager().submit_offer(
            state,
            outgoing_director_id=int(require_value(director_id, "Technical director id is required")),
            incoming_director_id=int(require_value(incoming_director_id, "Incoming technical director id is required")),
            salary_offer=int(require_value(salary_offer, "Salary offer is required")),
            contract_length=int(require_value(contract_length, "Contract length is required")),
        )
        return state_success_response(state, "technical_director_offer_result", result)

    return run_state_handler(state, logger, "Error offering contract to technical director", action)


def handle_replace_commercial_manager(
    state: GameState,
    logger: logging.Logger,
    manager_id: int | None,
    incoming_manager_id: int | None = None,
):
    def action():
        manager_id_value = int(require_value(manager_id, "Commercial manager id is required"))
        signing = CommercialManagerTransferManager().sign_player_replacement(
            state,
            outgoing_manager_id=manager_id_value,
            incoming_manager_id=int(incoming_manager_id) if incoming_manager_id is not None else None,
        )
        return state_success_response(state, "commercial_manager_replaced", signing)

    return run_state_handler(state, logger, "Error replacing commercial manager", action)


def handle_replace_technical_director(
    state: GameState,
    logger: logging.Logger,
    director_id: int | None,
    incoming_director_id: int | None = None,
):
    def action():
        director_id_value = int(require_value(director_id, "Technical director id is required"))
        signing = TechnicalDirectorTransferManager().sign_player_replacement(
            state,
            outgoing_director_id=director_id_value,
            incoming_director_id=int(incoming_director_id) if incoming_director_id is not None else None,
        )
        return state_success_response(state, "technical_director_replaced", signing)

    return run_state_handler(state, logger, "Error replacing technical director", action)


def handle_get_manager_replacement_candidates(state: GameState, logger: logging.Logger, manager_id: int | None):
    def action():
        manager_id_value = int(require_value(manager_id, "Commercial manager id is required"))
        outgoing = next((m for m in state.commercial_managers if m.id == manager_id_value), None)
        if outgoing is None:
            raise ValueError("Commercial manager not found")

        candidates = CommercialManagerTransferManager().get_player_replacement_candidates(state, manager_id_value)
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
        return success_response("manager_replacement_candidates", payload)

    return run_handler(logger, "Error loading commercial manager replacement candidates", action)


def handle_get_technical_director_replacement_candidates(
    state: GameState,
    logger: logging.Logger,
    director_id: int | None,
):
    def action():
        director_id_value = int(require_value(director_id, "Technical director id is required"))
        outgoing = next((d for d in state.technical_directors if d.id == director_id_value), None)
        if outgoing is None:
            raise ValueError("Technical director not found")

        candidates = TechnicalDirectorTransferManager().get_player_replacement_candidates(state, director_id_value)
        team_lookup = {team.technical_director_id: team.name for team in state.teams if team.technical_director_id is not None}
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
                    "contract_length": d.contract_length,
                    "team_name": team_lookup.get(d.id),
                }
                for d in candidates
            ],
        }
        return success_response("manager_replacement_candidates", payload)

    return run_handler(logger, "Error loading technical director replacement candidates", action)
