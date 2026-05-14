import logging

from app.core.management_transfers import (
    CommercialManagerTransferManager,
    EngineSupplierTransferManager,
    TechnicalDirectorTransferManager,
    TitleSponsorTransferManager,
    TyreSupplierTransferManager,
)
from app.core.player_engine_negotiations import PlayerEngineNegotiationManager
from app.core.player_tyre_negotiations import PlayerTyreNegotiationManager
from app.core.player_title_sponsor_negotiations import PlayerTitleSponsorNegotiationManager
from app.core.player_driver_negotiations import PlayerDriverNegotiationManager
from app.core.transfers import TransferManager
from app.models.state import GameState


def _error_response(message: str, response_type: str | None = None):
    payload = {"status": "error", "message": message}
    if response_type:
        payload["type"] = response_type
    return payload


def _success_response(response_type: str, data):
    return {"type": response_type, "status": "success", "data": data}


def _state_error_response(state: GameState, message: str, response_type: str | None = None):
    return state, _error_response(message, response_type=response_type)


def _state_success_response(state: GameState, response_type: str, data):
    return state, _success_response(response_type, data)


def _require_value(value, message: str):
    if value is None:
        raise ValueError(message)
    return value


def _require_text(value: str | None, message: str):
    if not value:
        raise ValueError(message)
    return value


def _run_handler(logger: logging.Logger, error_message: str, action, response_type: str | None = None):
    try:
        return action()
    except ValueError as exc:
        return _error_response(str(exc), response_type=response_type)
    except Exception as exc:
        logger.error(f"{error_message}: {exc}")
        return _error_response(str(exc), response_type=response_type)


def _run_state_handler(
    state: GameState,
    logger: logging.Logger,
    error_message: str,
    action,
    response_type: str | None = None,
):
    try:
        return action()
    except ValueError as exc:
        return _state_error_response(state, str(exc), response_type=response_type)
    except Exception as exc:
        logger.error(f"{error_message}: {exc}")
        return _state_error_response(state, str(exc), response_type=response_type)


def handle_replace_driver(
    state: GameState,
    logger: logging.Logger,
    driver_id: int | None,
    incoming_driver_id: int | None = None,
):
    def action():
        driver_id_value = int(_require_value(driver_id, "Driver id is required"))
        signing = TransferManager().sign_player_replacement(
            state,
            outgoing_driver_id=driver_id_value,
            incoming_driver_id=int(incoming_driver_id) if incoming_driver_id is not None else None,
        )
        return _state_success_response(state, "driver_replaced", signing)

    return _run_state_handler(state, logger, "Error replacing driver", action)


def handle_get_replacement_candidates(state: GameState, logger: logging.Logger, driver_id: int | None):
    def action():
        driver_id_value = int(_require_value(driver_id, "Driver id is required"))
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
        return _success_response("replacement_candidates", payload)

    return _run_handler(logger, "Error loading replacement candidates", action)


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
            outgoing_driver_id=int(_require_value(driver_id, "Driver id is required")),
            incoming_driver_id=int(_require_value(incoming_driver_id, "Incoming driver id is required")),
            salary_offer=int(_require_value(salary_offer, "Salary offer is required")),
            contract_length=int(_require_value(contract_length, "Contract length is required")),
        )
        return _state_success_response(state, "driver_offer_result", result)

    return _run_state_handler(state, logger, "Error offering contract to driver", action)


def handle_replace_commercial_manager(
    state: GameState,
    logger: logging.Logger,
    manager_id: int | None,
    incoming_manager_id: int | None = None,
):
    def action():
        manager_id_value = int(_require_value(manager_id, "Commercial manager id is required"))
        signing = CommercialManagerTransferManager().sign_player_replacement(
            state,
            outgoing_manager_id=manager_id_value,
            incoming_manager_id=int(incoming_manager_id) if incoming_manager_id is not None else None,
        )
        return _state_success_response(state, "commercial_manager_replaced", signing)

    return _run_state_handler(state, logger, "Error replacing commercial manager", action)


def handle_replace_technical_director(
    state: GameState,
    logger: logging.Logger,
    director_id: int | None,
    incoming_director_id: int | None = None,
):
    def action():
        director_id_value = int(_require_value(director_id, "Technical director id is required"))
        signing = TechnicalDirectorTransferManager().sign_player_replacement(
            state,
            outgoing_director_id=director_id_value,
            incoming_director_id=int(incoming_director_id) if incoming_director_id is not None else None,
        )
        return _state_success_response(state, "technical_director_replaced", signing)

    return _run_state_handler(state, logger, "Error replacing technical director", action)


def handle_get_manager_replacement_candidates(state: GameState, logger: logging.Logger, manager_id: int | None):
    def action():
        manager_id_value = int(_require_value(manager_id, "Commercial manager id is required"))
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
        return _success_response("manager_replacement_candidates", payload)

    return _run_handler(logger, "Error loading commercial manager replacement candidates", action)


def handle_get_technical_director_replacement_candidates(
    state: GameState,
    logger: logging.Logger,
    director_id: int | None,
):
    def action():
        director_id_value = int(_require_value(director_id, "Technical director id is required"))
        outgoing = next((d for d in state.technical_directors if d.id == director_id_value), None)
        if outgoing is None:
            raise ValueError("Technical director not found")

        candidates = TechnicalDirectorTransferManager().get_player_replacement_candidates(state, director_id_value)
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
        return _success_response("manager_replacement_candidates", payload)

    return _run_handler(logger, "Error loading technical director replacement candidates", action)


def handle_replace_title_sponsor(
    state: GameState,
    logger: logging.Logger,
    sponsor_name: str | None,
    incoming_sponsor_id: int | None = None,
):
    def action():
        sponsor_name_value = _require_text(sponsor_name, "Title sponsor name is required")
        signing = TitleSponsorTransferManager().sign_player_replacement(
            state,
            outgoing_sponsor_name=str(sponsor_name_value),
            incoming_sponsor_id=int(incoming_sponsor_id) if incoming_sponsor_id is not None else None,
        )
        return _state_success_response(state, "title_sponsor_replaced", signing)

    return _run_state_handler(state, logger, "Error replacing title sponsor", action)


def handle_get_title_sponsor_replacement_candidates(
    state: GameState,
    logger: logging.Logger,
    sponsor_name: str | None,
):
    def action():
        sponsor_name_value = _require_text(sponsor_name, "Title sponsor name is required")
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
        return _success_response("title_sponsor_replacement_candidates", payload)

    return _run_handler(logger, "Error loading title sponsor replacement candidates", action)


def handle_get_title_sponsor_negotiation_market(
    state: GameState,
    logger: logging.Logger,
):
    def action():
        payload = PlayerTitleSponsorNegotiationManager().get_market_payload(state)
        return _success_response("title_sponsor_negotiation_market", payload)

    return _run_handler(logger, "Error loading title sponsor negotiation market", action)


def handle_start_title_sponsor_negotiation(
    state: GameState,
    logger: logging.Logger,
    sponsor_id: int | None,
):
    def action():
        sponsor_id_value = int(_require_value(sponsor_id, "Title sponsor id is required"))
        manager = PlayerTitleSponsorNegotiationManager()
        manager.start_negotiation(state, sponsor_id_value)
        return _state_success_response(
            state,
            "title_sponsor_negotiation_updated",
            manager.get_market_payload(state),
        )

    return _run_state_handler(state, logger, "Error starting title sponsor negotiation", action)


def handle_update_title_sponsor_negotiation_staff(
    state: GameState,
    logger: logging.Logger,
    assigned_staff: int | None,
):
    def action():
        manager = PlayerTitleSponsorNegotiationManager()
        manager.update_assigned_staff(state, int(_require_value(assigned_staff, "Assigned staff is required")))
        return _state_success_response(
            state,
            "title_sponsor_negotiation_updated",
            manager.get_market_payload(state),
        )

    return _run_state_handler(state, logger, "Error updating title sponsor negotiation staff", action)


def handle_sign_title_sponsor_negotiated_deal(
    state: GameState,
    logger: logging.Logger,
):
    def action():
        signing = PlayerTitleSponsorNegotiationManager().sign_deal(state)
        return _state_success_response(state, "title_sponsor_negotiation_signed", signing)

    return _run_state_handler(state, logger, "Error signing negotiated title sponsor deal", action)


def handle_book_title_sponsor_hospitality(
    state: GameState,
    logger: logging.Logger,
):
    def action():
        data = PlayerTitleSponsorNegotiationManager().book_hospitality(state)
        return _state_success_response(state, "title_sponsor_negotiation_updated", data)

    return _run_state_handler(
        state,
        logger,
        "Error booking title sponsor hospitality",
        action,
        response_type="title_sponsor_negotiation_updated",
    )


def handle_replace_tyre_supplier(
    state: GameState,
    logger: logging.Logger,
    supplier_name: str | None,
    incoming_supplier_id: int | None = None,
):
    def action():
        supplier_name_value = _require_text(supplier_name, "Tyre supplier name is required")
        signing = TyreSupplierTransferManager().sign_player_replacement(
            state,
            outgoing_supplier_name=str(supplier_name_value),
            incoming_supplier_id=int(incoming_supplier_id) if incoming_supplier_id is not None else None,
        )
        return _state_success_response(state, "tyre_supplier_replaced", signing)

    return _run_state_handler(state, logger, "Error replacing tyre supplier", action)


def handle_get_tyre_supplier_replacement_candidates(
    state: GameState,
    logger: logging.Logger,
    supplier_name: str | None,
):
    def action():
        supplier_name_value = _require_text(supplier_name, "Tyre supplier name is required")
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
        return _success_response("tyre_supplier_replacement_candidates", payload)

    return _run_handler(logger, "Error loading tyre supplier replacement candidates", action)


def handle_replace_engine_supplier(
    state: GameState,
    logger: logging.Logger,
    supplier_name: str | None,
    incoming_supplier_id: int | None = None,
):
    def action():
        supplier_name_value = _require_text(supplier_name, "Engine supplier name is required")
        signing = EngineSupplierTransferManager().sign_player_replacement(
            state,
            outgoing_supplier_name=str(supplier_name_value),
            incoming_supplier_id=int(incoming_supplier_id) if incoming_supplier_id is not None else None,
        )
        return _state_success_response(state, "engine_supplier_replaced", signing)

    return _run_state_handler(state, logger, "Error replacing engine supplier", action)


def handle_get_engine_supplier_replacement_candidates(
    state: GameState,
    logger: logging.Logger,
    supplier_name: str | None,
):
    def action():
        supplier_name_value = _require_text(supplier_name, "Engine supplier name is required")
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
        return _success_response("engine_supplier_replacement_candidates", payload)

    return _run_handler(logger, "Error loading engine supplier replacement candidates", action)


def handle_get_engine_negotiation_market(
    state: GameState,
    logger: logging.Logger,
):
    def action():
        payload = PlayerEngineNegotiationManager().get_market_payload(state)
        return _success_response("engine_negotiation_market", payload)

    return _run_handler(logger, "Error loading engine negotiation market", action)


def handle_get_tyre_negotiation_market(
    state: GameState,
    logger: logging.Logger,
):
    def action():
        payload = PlayerTyreNegotiationManager().get_market_payload(state)
        return _success_response("tyre_negotiation_market", payload)

    return _run_handler(logger, "Error loading tyre negotiation market", action)


def handle_start_engine_negotiation(
    state: GameState,
    logger: logging.Logger,
    supplier_id: int | None,
):
    def action():
        supplier_id_value = int(_require_value(supplier_id, "Engine supplier id is required"))
        manager = PlayerEngineNegotiationManager()
        manager.start_negotiation(state, supplier_id_value)
        return _state_success_response(state, "engine_negotiation_updated", manager.get_market_payload(state))

    return _run_state_handler(state, logger, "Error starting engine negotiation", action)


def handle_start_tyre_negotiation(
    state: GameState,
    logger: logging.Logger,
    supplier_id: int | None,
):
    def action():
        supplier_id_value = int(_require_value(supplier_id, "Tyre supplier id is required"))
        manager = PlayerTyreNegotiationManager()
        manager.start_negotiation(state, supplier_id_value)
        return _state_success_response(state, "tyre_negotiation_updated", manager.get_market_payload(state))

    return _run_state_handler(state, logger, "Error starting tyre negotiation", action)


def handle_update_engine_negotiation_staff(
    state: GameState,
    logger: logging.Logger,
    assigned_staff: int | None,
):
    def action():
        manager = PlayerEngineNegotiationManager()
        manager.update_assigned_staff(state, int(_require_value(assigned_staff, "Assigned staff is required")))
        return _state_success_response(state, "engine_negotiation_updated", manager.get_market_payload(state))

    return _run_state_handler(state, logger, "Error updating engine negotiation staff", action)


def handle_update_tyre_negotiation_staff(
    state: GameState,
    logger: logging.Logger,
    assigned_staff: int | None,
):
    def action():
        manager = PlayerTyreNegotiationManager()
        manager.update_assigned_staff(state, int(_require_value(assigned_staff, "Assigned staff is required")))
        return _state_success_response(state, "tyre_negotiation_updated", manager.get_market_payload(state))

    return _run_state_handler(state, logger, "Error updating tyre negotiation staff", action)


def handle_sign_engine_negotiated_deal(
    state: GameState,
    logger: logging.Logger,
    tier: str | None,
):
    def action():
        signing = PlayerEngineNegotiationManager().sign_deal(
            state,
            str(_require_text(tier, "Negotiated tier is required")),
        )
        return _state_success_response(state, "engine_negotiation_signed", signing)

    return _run_state_handler(state, logger, "Error signing negotiated engine deal", action)


def handle_sign_tyre_negotiated_deal(
    state: GameState,
    logger: logging.Logger,
    tier: str | None,
):
    def action():
        signing = PlayerTyreNegotiationManager().sign_deal(
            state,
            str(_require_text(tier, "Negotiated tier is required")),
        )
        return _state_success_response(state, "tyre_negotiation_signed", signing)

    return _run_state_handler(state, logger, "Error signing negotiated tyre deal", action)


def handle_book_engine_negotiation_hospitality(
    state: GameState,
    logger: logging.Logger,
):
    def action():
        data = PlayerEngineNegotiationManager().book_hospitality(state)
        return _state_success_response(state, "engine_negotiation_updated", data)

    return _run_state_handler(
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
        return _state_success_response(state, "tyre_negotiation_updated", data)

    return _run_state_handler(
        state,
        logger,
        "Error booking tyre hospitality",
        action,
        response_type="tyre_negotiation_updated",
    )
