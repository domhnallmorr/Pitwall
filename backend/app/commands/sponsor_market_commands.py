import logging

from app.commands.market_command_helpers import (
    require_text,
    require_value,
    run_handler,
    run_state_handler,
    state_success_response,
    success_response,
)
from app.core.management_transfers import TitleSponsorTransferManager
from app.core.player_title_sponsor_negotiations import PlayerTitleSponsorNegotiationManager
from app.models.state import GameState


def handle_replace_title_sponsor(
    state: GameState,
    logger: logging.Logger,
    sponsor_name: str | None,
    incoming_sponsor_id: int | None = None,
):
    def action():
        sponsor_name_value = require_text(sponsor_name, "Title sponsor name is required")
        signing = TitleSponsorTransferManager().sign_player_replacement(
            state,
            outgoing_sponsor_name=str(sponsor_name_value),
            incoming_sponsor_id=int(incoming_sponsor_id) if incoming_sponsor_id is not None else None,
        )
        return state_success_response(state, "title_sponsor_replaced", signing)

    return run_state_handler(state, logger, "Error replacing title sponsor", action)


def handle_get_title_sponsor_replacement_candidates(
    state: GameState,
    logger: logging.Logger,
    sponsor_name: str | None,
):
    def action():
        sponsor_name_value = require_text(sponsor_name, "Title sponsor name is required")
        team = state.player_team
        if team is None or getattr(team, "title_sponsor_name", None) != str(sponsor_name_value):
            raise ValueError("Title sponsor not found")

        candidates = TitleSponsorTransferManager().get_player_replacement_candidates(state, str(sponsor_name_value))
        payload = {
            "market_type": "title_sponsor",
            "outgoing_sponsor": {
                "name": sponsor_name_value,
                "contract_length": int(getattr(team, "title_sponsor_contract_length", 0) or 0),
                "annual_value": int(getattr(team, "title_sponsor_yearly", 0) or 0),
            },
            "candidates": [
                {
                    "id": s.id,
                    "name": s.name,
                    "wealth": s.wealth,
                    "start_year": s.start_year,
                }
                for s in candidates
            ],
        }
        return success_response("title_sponsor_replacement_candidates", payload)

    return run_handler(logger, "Error loading title sponsor replacement candidates", action)


def handle_get_title_sponsor_negotiation_market(
    state: GameState,
    logger: logging.Logger,
):
    def action():
        payload = PlayerTitleSponsorNegotiationManager().get_market_payload(state)
        return success_response("title_sponsor_negotiation_market", payload)

    return run_handler(logger, "Error loading title sponsor negotiation market", action)


def handle_start_title_sponsor_negotiation(
    state: GameState,
    logger: logging.Logger,
    sponsor_id: int | None,
):
    def action():
        sponsor_id_value = int(require_value(sponsor_id, "Title sponsor id is required"))
        manager = PlayerTitleSponsorNegotiationManager()
        manager.start_negotiation(state, sponsor_id_value)
        return state_success_response(
            state,
            "title_sponsor_negotiation_updated",
            manager.get_market_payload(state),
        )

    return run_state_handler(state, logger, "Error starting title sponsor negotiation", action)


def handle_update_title_sponsor_negotiation_staff(
    state: GameState,
    logger: logging.Logger,
    assigned_staff: int | None,
):
    def action():
        manager = PlayerTitleSponsorNegotiationManager()
        manager.update_assigned_staff(state, int(require_value(assigned_staff, "Assigned staff is required")))
        return state_success_response(
            state,
            "title_sponsor_negotiation_updated",
            manager.get_market_payload(state),
        )

    return run_state_handler(state, logger, "Error updating title sponsor negotiation staff", action)


def handle_sign_title_sponsor_negotiated_deal(
    state: GameState,
    logger: logging.Logger,
):
    def action():
        signing = PlayerTitleSponsorNegotiationManager().sign_deal(state)
        return state_success_response(state, "title_sponsor_negotiation_signed", signing)

    return run_state_handler(state, logger, "Error signing negotiated title sponsor deal", action)


def handle_book_title_sponsor_hospitality(
    state: GameState,
    logger: logging.Logger,
):
    def action():
        data = PlayerTitleSponsorNegotiationManager().book_hospitality(state)
        return state_success_response(state, "title_sponsor_negotiation_updated", data)

    return run_state_handler(
        state,
        logger,
        "Error booking title sponsor hospitality",
        action,
        response_type="title_sponsor_negotiation_updated",
    )
