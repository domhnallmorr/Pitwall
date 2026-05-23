import logging

from app.commands.market_command_helpers import (
    require_text,
    require_value,
    run_handler,
    run_state_handler,
    state_success_response,
    success_response,
)
from app.core.management_transfers import EngineSupplierTransferManager, TyreSupplierTransferManager
from app.core.player_engine_negotiations import PlayerEngineNegotiationManager
from app.core.player_tyre_negotiations import PlayerTyreNegotiationManager
from app.models.state import GameState


def handle_replace_tyre_supplier(
    state: GameState,
    logger: logging.Logger,
    supplier_name: str | None,
    incoming_supplier_id: int | None = None,
):
    def action():
        supplier_name_value = require_text(supplier_name, "Tyre supplier name is required")
        signing = TyreSupplierTransferManager().sign_player_replacement(
            state,
            outgoing_supplier_name=str(supplier_name_value),
            incoming_supplier_id=int(incoming_supplier_id) if incoming_supplier_id is not None else None,
        )
        return state_success_response(state, "tyre_supplier_replaced", signing)

    return run_state_handler(state, logger, "Error replacing tyre supplier", action)


def handle_get_tyre_supplier_replacement_candidates(
    state: GameState,
    logger: logging.Logger,
    supplier_name: str | None,
):
    def action():
        supplier_name_value = require_text(supplier_name, "Tyre supplier name is required")
        team = state.player_team
        if team is None or getattr(team, "tyre_supplier_name", None) != str(supplier_name_value):
            raise ValueError("Tyre supplier not found")

        candidates = TyreSupplierTransferManager().get_player_replacement_candidates(state, str(supplier_name_value))
        payload = {
            "market_type": "tyre_supplier",
            "outgoing_supplier": {
                "name": supplier_name_value,
                "contract_length": int(getattr(team, "tyre_supplier_contract_length", 0) or 0),
                "deal": getattr(team, "tyre_supplier_deal", None),
                "annual_value": int(getattr(team, "tyre_supplier_yearly_cost", 0) or 0),
            },
            "candidates": [
                {
                    "id": s.id,
                    "name": s.name,
                    "country": s.country,
                    "wear": s.wear,
                    "grip": s.grip,
                    "start_year": s.start_year,
                }
                for s in candidates
            ],
        }
        return success_response("tyre_supplier_replacement_candidates", payload)

    return run_handler(logger, "Error loading tyre supplier replacement candidates", action)


def handle_replace_engine_supplier(
    state: GameState,
    logger: logging.Logger,
    supplier_name: str | None,
    incoming_supplier_id: int | None = None,
):
    def action():
        supplier_name_value = require_text(supplier_name, "Engine supplier name is required")
        signing = EngineSupplierTransferManager().sign_player_replacement(
            state,
            outgoing_supplier_name=str(supplier_name_value),
            incoming_supplier_id=int(incoming_supplier_id) if incoming_supplier_id is not None else None,
        )
        return state_success_response(state, "engine_supplier_replaced", signing)

    return run_state_handler(state, logger, "Error replacing engine supplier", action)


def handle_get_engine_supplier_replacement_candidates(
    state: GameState,
    logger: logging.Logger,
    supplier_name: str | None,
):
    def action():
        supplier_name_value = require_text(supplier_name, "Engine supplier name is required")
        team = state.player_team
        if team is None or getattr(team, "engine_supplier_name", None) != str(supplier_name_value):
            raise ValueError("Engine supplier not found")

        candidates = EngineSupplierTransferManager().get_player_replacement_candidates(state, str(supplier_name_value))
        payload = {
            "market_type": "engine_supplier",
            "outgoing_supplier": {
                "name": supplier_name_value,
                "contract_length": int(getattr(team, "engine_supplier_contract_length", 0) or 0),
                "deal": getattr(team, "engine_supplier_deal", None),
                "annual_value": int(getattr(team, "engine_supplier_yearly_cost", 0) or 0),
                "builds_own_engine": bool(getattr(team, "builds_own_engine", False)),
            },
            "candidates": [
                {
                    "id": s.id,
                    "name": s.name,
                    "country": s.country,
                    "resources": s.resources,
                    "power": s.power,
                    "start_year": s.start_year,
                }
                for s in candidates
            ],
        }
        return success_response("engine_supplier_replacement_candidates", payload)

    return run_handler(logger, "Error loading engine supplier replacement candidates", action)


def handle_get_engine_negotiation_market(
    state: GameState,
    logger: logging.Logger,
):
    def action():
        payload = PlayerEngineNegotiationManager().get_market_payload(state)
        return success_response("engine_negotiation_market", payload)

    return run_handler(logger, "Error loading engine negotiation market", action)


def handle_get_tyre_negotiation_market(
    state: GameState,
    logger: logging.Logger,
):
    def action():
        payload = PlayerTyreNegotiationManager().get_market_payload(state)
        return success_response("tyre_negotiation_market", payload)

    return run_handler(logger, "Error loading tyre negotiation market", action)


def handle_start_engine_negotiation(
    state: GameState,
    logger: logging.Logger,
    supplier_id: int | None,
):
    def action():
        supplier_id_value = int(require_value(supplier_id, "Engine supplier id is required"))
        manager = PlayerEngineNegotiationManager()
        manager.start_negotiation(state, supplier_id_value)
        return state_success_response(state, "engine_negotiation_updated", manager.get_market_payload(state))

    return run_state_handler(state, logger, "Error starting engine negotiation", action)


def handle_start_tyre_negotiation(
    state: GameState,
    logger: logging.Logger,
    supplier_id: int | None,
):
    def action():
        supplier_id_value = int(require_value(supplier_id, "Tyre supplier id is required"))
        manager = PlayerTyreNegotiationManager()
        manager.start_negotiation(state, supplier_id_value)
        return state_success_response(state, "tyre_negotiation_updated", manager.get_market_payload(state))

    return run_state_handler(state, logger, "Error starting tyre negotiation", action)


def handle_update_engine_negotiation_staff(
    state: GameState,
    logger: logging.Logger,
    assigned_staff: int | None,
):
    def action():
        manager = PlayerEngineNegotiationManager()
        manager.update_assigned_staff(state, int(require_value(assigned_staff, "Assigned staff is required")))
        return state_success_response(state, "engine_negotiation_updated", manager.get_market_payload(state))

    return run_state_handler(state, logger, "Error updating engine negotiation staff", action)


def handle_update_tyre_negotiation_staff(
    state: GameState,
    logger: logging.Logger,
    assigned_staff: int | None,
):
    def action():
        manager = PlayerTyreNegotiationManager()
        manager.update_assigned_staff(state, int(require_value(assigned_staff, "Assigned staff is required")))
        return state_success_response(state, "tyre_negotiation_updated", manager.get_market_payload(state))

    return run_state_handler(state, logger, "Error updating tyre negotiation staff", action)


def handle_sign_engine_negotiated_deal(
    state: GameState,
    logger: logging.Logger,
    tier: str | None,
):
    def action():
        signing = PlayerEngineNegotiationManager().sign_deal(
            state,
            str(require_text(tier, "Negotiated tier is required")),
        )
        return state_success_response(state, "engine_negotiation_signed", signing)

    return run_state_handler(state, logger, "Error signing negotiated engine deal", action)


def handle_sign_tyre_negotiated_deal(
    state: GameState,
    logger: logging.Logger,
    tier: str | None,
):
    def action():
        signing = PlayerTyreNegotiationManager().sign_deal(
            state,
            str(require_text(tier, "Negotiated tier is required")),
        )
        return state_success_response(state, "tyre_negotiation_signed", signing)

    return run_state_handler(state, logger, "Error signing negotiated tyre deal", action)


def handle_book_engine_negotiation_hospitality(
    state: GameState,
    logger: logging.Logger,
):
    def action():
        data = PlayerEngineNegotiationManager().book_hospitality(state)
        return state_success_response(state, "engine_negotiation_updated", data)

    return run_state_handler(
        state,
        logger,
        "Error booking engine hospitality",
        action,
        response_type="engine_negotiation_updated",
    )


def handle_book_tyre_negotiation_hospitality(
    state: GameState,
    logger: logging.Logger,
):
    def action():
        data = PlayerTyreNegotiationManager().book_hospitality(state)
        return state_success_response(state, "tyre_negotiation_updated", data)

    return run_state_handler(
        state,
        logger,
        "Error booking tyre hospitality",
        action,
        response_type="tyre_negotiation_updated",
    )
