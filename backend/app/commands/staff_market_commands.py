import logging

from app.core.management_transfers import (
    CommercialManagerTransferManager,
    EngineSupplierTransferManager,
    TechnicalDirectorTransferManager,
    TitleSponsorTransferManager,
    TyreSupplierTransferManager,
)
from app.core.player_engine_negotiations import PlayerEngineNegotiationManager
from app.core.player_title_sponsor_negotiations import PlayerTitleSponsorNegotiationManager
from app.core.player_driver_negotiations import PlayerDriverNegotiationManager
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
        return state, {"type": "driver_replaced", "status": "success", "data": signing}
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
                    "wage": d.wage,
                    "pay_driver": d.pay_driver,
                    "contract_length": d.contract_length,
                    "team_name": driver_team_lookup.get(d.id),
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


def handle_offer_driver(
    state: GameState,
    logger: logging.Logger,
    driver_id: int | None,
    incoming_driver_id: int | None,
    salary_offer: int | None,
    contract_length: int | None,
):
    try:
        if driver_id is None:
            return state, {"status": "error", "message": "Driver id is required"}
        if incoming_driver_id is None:
            return state, {"status": "error", "message": "Incoming driver id is required"}
        if salary_offer is None:
            return state, {"status": "error", "message": "Salary offer is required"}
        if contract_length is None:
            return state, {"status": "error", "message": "Contract length is required"}

        result = PlayerDriverNegotiationManager().submit_offer(
            state,
            outgoing_driver_id=int(driver_id),
            incoming_driver_id=int(incoming_driver_id),
            salary_offer=int(salary_offer),
            contract_length=int(contract_length),
        )
        return state, {"type": "driver_offer_result", "status": "success", "data": result}
    except ValueError as ve:
        return state, {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error offering contract to driver: {e}")
        return state, {"status": "error", "message": str(e)}


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
        return state, {"type": "commercial_manager_replaced", "status": "success", "data": signing}
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
        return state, {"type": "technical_director_replaced", "status": "success", "data": signing}
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


def handle_replace_title_sponsor(
    state: GameState,
    logger: logging.Logger,
    sponsor_name: str | None,
    incoming_sponsor_id: int | None = None,
):
    try:
        if not sponsor_name:
            return state, {"status": "error", "message": "Title sponsor name is required"}
        signing = TitleSponsorTransferManager().sign_player_replacement(
            state,
            outgoing_sponsor_name=str(sponsor_name),
            incoming_sponsor_id=int(incoming_sponsor_id) if incoming_sponsor_id is not None else None,
        )
        return state, {"type": "title_sponsor_replaced", "status": "success", "data": signing}
    except ValueError as ve:
        return state, {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error replacing title sponsor: {e}")
        return state, {"status": "error", "message": str(e)}


def handle_get_title_sponsor_replacement_candidates(
    state: GameState,
    logger: logging.Logger,
    sponsor_name: str | None,
):
    try:
        if not sponsor_name:
            return {"status": "error", "message": "Title sponsor name is required"}

        team = state.player_team
        if team is None or getattr(team, "title_sponsor_name", None) != str(sponsor_name):
            return {"status": "error", "message": "Title sponsor not found"}

        candidates = TitleSponsorTransferManager().get_player_replacement_candidates(state, str(sponsor_name))
        payload = {
            "market_type": "title_sponsor",
            "outgoing_sponsor": {
                "name": sponsor_name,
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
        return {"type": "title_sponsor_replacement_candidates", "status": "success", "data": payload}
    except ValueError as ve:
        return {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error loading title sponsor replacement candidates: {e}")
        return {"status": "error", "message": str(e)}


def handle_get_title_sponsor_negotiation_market(
    state: GameState,
    logger: logging.Logger,
):
    try:
        payload = PlayerTitleSponsorNegotiationManager().get_market_payload(state)
        return {"type": "title_sponsor_negotiation_market", "status": "success", "data": payload}
    except ValueError as ve:
        return {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error loading title sponsor negotiation market: {e}")
        return {"status": "error", "message": str(e)}


def handle_start_title_sponsor_negotiation(
    state: GameState,
    logger: logging.Logger,
    sponsor_id: int | None,
):
    try:
        if sponsor_id is None:
            return state, {"status": "error", "message": "Title sponsor id is required"}
        manager = PlayerTitleSponsorNegotiationManager()
        manager.start_negotiation(state, int(sponsor_id))
        return state, {"type": "title_sponsor_negotiation_updated", "status": "success", "data": manager.get_market_payload(state)}
    except ValueError as ve:
        return state, {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error starting title sponsor negotiation: {e}")
        return state, {"status": "error", "message": str(e)}


def handle_update_title_sponsor_negotiation_staff(
    state: GameState,
    logger: logging.Logger,
    assigned_staff: int | None,
):
    try:
        if assigned_staff is None:
            return state, {"status": "error", "message": "Assigned staff is required"}
        manager = PlayerTitleSponsorNegotiationManager()
        manager.update_assigned_staff(state, int(assigned_staff))
        return state, {"type": "title_sponsor_negotiation_updated", "status": "success", "data": manager.get_market_payload(state)}
    except ValueError as ve:
        return state, {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error updating title sponsor negotiation staff: {e}")
        return state, {"status": "error", "message": str(e)}


def handle_sign_title_sponsor_negotiated_deal(
    state: GameState,
    logger: logging.Logger,
):
    try:
        signing = PlayerTitleSponsorNegotiationManager().sign_deal(state)
        return state, {"type": "title_sponsor_negotiation_signed", "status": "success", "data": signing}
    except ValueError as ve:
        return state, {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error signing negotiated title sponsor deal: {e}")
        return state, {"status": "error", "message": str(e)}


def handle_book_title_sponsor_hospitality(
    state: GameState,
    logger: logging.Logger,
):
    try:
        data = PlayerTitleSponsorNegotiationManager().book_hospitality(state)
        return state, {"type": "title_sponsor_negotiation_updated", "status": "success", "data": data}
    except ValueError as ve:
        return state, {"type": "title_sponsor_negotiation_updated", "status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error booking title sponsor hospitality: {e}")
        return state, {"type": "title_sponsor_negotiation_updated", "status": "error", "message": str(e)}


def handle_replace_tyre_supplier(
    state: GameState,
    logger: logging.Logger,
    supplier_name: str | None,
    incoming_supplier_id: int | None = None,
):
    try:
        if not supplier_name:
            return state, {"status": "error", "message": "Tyre supplier name is required"}
        signing = TyreSupplierTransferManager().sign_player_replacement(
            state,
            outgoing_supplier_name=str(supplier_name),
            incoming_supplier_id=int(incoming_supplier_id) if incoming_supplier_id is not None else None,
        )
        return state, {"type": "tyre_supplier_replaced", "status": "success", "data": signing}
    except ValueError as ve:
        return state, {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error replacing tyre supplier: {e}")
        return state, {"status": "error", "message": str(e)}


def handle_get_tyre_supplier_replacement_candidates(
    state: GameState,
    logger: logging.Logger,
    supplier_name: str | None,
):
    try:
        if not supplier_name:
            return {"status": "error", "message": "Tyre supplier name is required"}

        team = state.player_team
        if team is None or getattr(team, "tyre_supplier_name", None) != str(supplier_name):
            return {"status": "error", "message": "Tyre supplier not found"}

        candidates = TyreSupplierTransferManager().get_player_replacement_candidates(state, str(supplier_name))
        payload = {
            "market_type": "tyre_supplier",
            "outgoing_supplier": {
                "name": supplier_name,
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
        return {"type": "tyre_supplier_replacement_candidates", "status": "success", "data": payload}
    except ValueError as ve:
        return {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error loading tyre supplier replacement candidates: {e}")
        return {"status": "error", "message": str(e)}


def handle_replace_engine_supplier(
    state: GameState,
    logger: logging.Logger,
    supplier_name: str | None,
    incoming_supplier_id: int | None = None,
):
    try:
        if not supplier_name:
            return state, {"status": "error", "message": "Engine supplier name is required"}
        signing = EngineSupplierTransferManager().sign_player_replacement(
            state,
            outgoing_supplier_name=str(supplier_name),
            incoming_supplier_id=int(incoming_supplier_id) if incoming_supplier_id is not None else None,
        )
        return state, {"type": "engine_supplier_replaced", "status": "success", "data": signing}
    except ValueError as ve:
        return state, {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error replacing engine supplier: {e}")
        return state, {"status": "error", "message": str(e)}


def handle_get_engine_supplier_replacement_candidates(
    state: GameState,
    logger: logging.Logger,
    supplier_name: str | None,
):
    try:
        if not supplier_name:
            return {"status": "error", "message": "Engine supplier name is required"}

        team = state.player_team
        if team is None or getattr(team, "engine_supplier_name", None) != str(supplier_name):
            return {"status": "error", "message": "Engine supplier not found"}

        candidates = EngineSupplierTransferManager().get_player_replacement_candidates(state, str(supplier_name))
        payload = {
            "market_type": "engine_supplier",
            "outgoing_supplier": {
                "name": supplier_name,
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
        return {"type": "engine_supplier_replacement_candidates", "status": "success", "data": payload}
    except ValueError as ve:
        return {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error loading engine supplier replacement candidates: {e}")
        return {"status": "error", "message": str(e)}


def handle_get_engine_negotiation_market(
    state: GameState,
    logger: logging.Logger,
):
    try:
        payload = PlayerEngineNegotiationManager().get_market_payload(state)
        return {"type": "engine_negotiation_market", "status": "success", "data": payload}
    except ValueError as ve:
        return {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error loading engine negotiation market: {e}")
        return {"status": "error", "message": str(e)}


def handle_start_engine_negotiation(
    state: GameState,
    logger: logging.Logger,
    supplier_id: int | None,
):
    try:
        if supplier_id is None:
            return state, {"status": "error", "message": "Engine supplier id is required"}
        manager = PlayerEngineNegotiationManager()
        manager.start_negotiation(state, int(supplier_id))
        return state, {"type": "engine_negotiation_updated", "status": "success", "data": manager.get_market_payload(state)}
    except ValueError as ve:
        return state, {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error starting engine negotiation: {e}")
        return state, {"status": "error", "message": str(e)}


def handle_update_engine_negotiation_staff(
    state: GameState,
    logger: logging.Logger,
    assigned_staff: int | None,
):
    try:
        if assigned_staff is None:
            return state, {"status": "error", "message": "Assigned staff is required"}
        manager = PlayerEngineNegotiationManager()
        manager.update_assigned_staff(state, int(assigned_staff))
        return state, {"type": "engine_negotiation_updated", "status": "success", "data": manager.get_market_payload(state)}
    except ValueError as ve:
        return state, {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error updating engine negotiation staff: {e}")
        return state, {"status": "error", "message": str(e)}


def handle_sign_engine_negotiated_deal(
    state: GameState,
    logger: logging.Logger,
    tier: str | None,
):
    try:
        if not tier:
            return state, {"status": "error", "message": "Negotiated tier is required"}
        signing = PlayerEngineNegotiationManager().sign_deal(state, str(tier))
        return state, {"type": "engine_negotiation_signed", "status": "success", "data": signing}
    except ValueError as ve:
        return state, {"status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error signing negotiated engine deal: {e}")
        return state, {"status": "error", "message": str(e)}


def handle_book_engine_negotiation_hospitality(
    state: GameState,
    logger: logging.Logger,
):
    try:
        data = PlayerEngineNegotiationManager().book_hospitality(state)
        return state, {"type": "engine_negotiation_updated", "status": "success", "data": data}
    except ValueError as ve:
        return state, {"type": "engine_negotiation_updated", "status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error booking engine hospitality: {e}")
        return state, {"type": "engine_negotiation_updated", "status": "error", "message": str(e)}
