import json
import logging

from app.core.ai_car_development import AICarDevelopmentManager
from app.core.grid import GridManager
from app.core.prize_money import PrizeMoneyManager
from app.core.retirement import RetirementManager
from app.core.roster import load_roster
from app.core.transfers import TransferManager
from app.core.tyre_compounds import TyreCompoundManager
from app.core.management_transfers import (
    CommercialManagerTransferManager,
    EngineSupplierTransferManager,
    TeamPrincipalTransferManager,
    TechnicalDirectorTransferManager,
    TitleSponsorTransferManager,
    TyreSupplierTransferManager,
)
from app.commands.facilities_commands import (
    handle_facilities_upgrade_preview,
    handle_start_facilities_upgrade,
)
from app.commands.finance_commands import build_finance_payload
from app.commands.race_commands import (
    handle_get_race_weekend,
    handle_set_race_strategy,
    handle_simulate_qualifying,
    handle_simulate_race,
)
from app.commands.staff_commands import (
    handle_get_title_sponsor_negotiation_market,
    handle_get_tyre_negotiation_market,
    handle_book_title_sponsor_hospitality,
    handle_book_tyre_negotiation_hospitality,
    handle_sign_title_sponsor_negotiated_deal,
    handle_sign_tyre_negotiated_deal,
    handle_start_title_sponsor_negotiation,
    handle_start_tyre_negotiation,
    handle_update_title_sponsor_negotiation_staff,
    handle_update_tyre_negotiation_staff,
    handle_offer_driver,
    handle_offer_technical_director,
    handle_get_engine_negotiation_market,
    handle_get_technical_director_replacement_candidates,
    handle_get_engine_supplier_replacement_candidates,
    handle_get_manager_replacement_candidates,
    handle_get_tyre_supplier_replacement_candidates,
    handle_get_title_sponsor_replacement_candidates,
    handle_get_replacement_candidates,
    handle_build_spare_set,
    handle_finish_car_development_stage,
    handle_finish_car_development_project_stage,
    handle_repair_chassis_wear,
    handle_set_construction_allocation,
    handle_start_construction_project,
    handle_replace_commercial_manager,
    handle_replace_engine_supplier,
    handle_replace_technical_director,
    handle_replace_tyre_supplier,
    handle_replace_title_sponsor,
    handle_replace_driver,
    handle_set_race_chassis_assignments,
    handle_set_car_development_allocation,
    handle_set_test_chassis,
    handle_start_car_development,
    handle_book_engine_negotiation_hospitality,
    handle_start_engine_negotiation,
    handle_sign_engine_negotiated_deal,
    handle_update_engine_negotiation_staff,
)
from app.models.calendar import Calendar
from app.models.chassis import Chassis
from app.models.email import EmailCategory
from app.models.finance import Finance
from app.models.state import GameState


def _create_player_chassis(team_id: int, count: int = 3) -> list[Chassis]:
    return [
        Chassis(
            id=index,
            team_id=team_id,
            name=f"Chassis {index}",
            wear=0,
        )
        for index in range(1, count + 1)
    ]


def load_default_state() -> GameState:
    (
        teams,
        drivers,
        year,
        events,
        circuits,
        team_principals,
        technical_directors,
        commercial_managers,
        title_sponsors,
        engine_suppliers,
        tyre_suppliers,
        fuel_suppliers,
    ) = load_roster(
        year=0,
        include_team_principals=True,
        include_technical_directors=True,
        include_commercial_managers=True,
        include_title_sponsors=True,
        include_engine_suppliers=True,
        include_tyre_suppliers=True,
        include_fuel_suppliers=True,
    )
    calendar = Calendar(events=events, current_week=1)
    return GameState(
        year=year,
        teams=teams,
        drivers=drivers,
        team_principals=team_principals,
        technical_directors=technical_directors,
        commercial_managers=commercial_managers,
        title_sponsors=title_sponsors,
        engine_suppliers=engine_suppliers,
        tyre_suppliers=tyre_suppliers,
        fuel_suppliers=fuel_suppliers,
        calendar=calendar,
        circuits=circuits,
    )


def handle_load_roster(logger: logging.Logger):
    try:
        state = load_default_state()
        grid_json = GridManager().get_grid_json(state)
        grid_data = json.loads(grid_json)
        return state, {
            "status": "success",
            "message": f"Roster loaded for {state.year}",
            "data": grid_data,
        }
    except Exception as e:
        logger.error(f"Error loading roster: {e}")
        return None, {"status": "error", "message": str(e)}


def handle_start_career(state: GameState | None, logger: logging.Logger, team_name: str | None = None):
    try:
        current_state = state or load_default_state()
        selected_team_name = (team_name or "Warrick").strip()
        selected_team = next((t for t in current_state.teams if t.name == selected_team_name), None)
        if not selected_team:
            return current_state, {"status": "error", "message": f"Team '{selected_team_name}' not found in roster."}

        current_state.player_team_id = selected_team.id
        current_state.player_spares = 0
        current_state.player_construction_usage_percent = 0
        current_state.player_construction_usage_week = current_state.calendar.current_week
        current_state.player_construction_usage_year = current_state.year
        current_state.player_mechanics_usage_percent = 0
        current_state.player_mechanics_usage_week = current_state.calendar.current_week
        current_state.player_mechanics_usage_year = current_state.year
        current_state.player_chassis = _create_player_chassis(selected_team.id)
        current_state.player_chassis_year = current_state.year
        current_state.player_setup_knowledge = 1
        current_state.player_test_chassis_id = current_state.player_chassis[0].id if current_state.player_chassis else None
        current_state.player_race_chassis_assignments = {}
        TyreCompoundManager().generate_for_new_career(current_state)
        released_principal = next(
            (principal for principal in current_state.team_principals if principal.team_id == selected_team.id),
            None,
        )
        if released_principal:
            released_principal.team_id = None
            selected_team.team_principal_id = None
        current_state.finance = Finance(balance=selected_team.balance)
        PrizeMoneyManager().assign_initial_entitlement_from_roster_order(current_state)

        current_state.add_email(
            sender="Board of Directors",
            subject="Welcome to Pitwall",
            body=(
                f"Welcome to {selected_team.name}! As the new Team Principal, you have full control over the team's "
                "strategy, development, and driver lineup. We're counting on you to lead us to glory. Good luck!"
            ),
            category=EmailCategory.GENERAL,
        )

        final_season_drivers = RetirementManager().mark_final_season_drivers(current_state)
        if final_season_drivers:
            lines = [f"- {d['name']} ({d['team_name']}), age {d['age']}" for d in final_season_drivers]
            current_state.add_email(
                sender="Competition Office",
                subject=f"Retirement Watch: {current_state.year} Final Seasons",
                body=("The following drivers have announced this will be their final season:\n\n" + "\n".join(lines)),
                category=EmailCategory.SEASON,
            )

        GridManager().capture_season_snapshot(current_state, year=current_state.year)
        TransferManager().recompute_ai_signings(current_state)
        CommercialManagerTransferManager().recompute_ai_signings(current_state)
        TeamPrincipalTransferManager().recompute_ai_signings(current_state)
        TechnicalDirectorTransferManager().recompute_ai_signings(current_state)
        TitleSponsorTransferManager().recompute_ai_signings(current_state)
        EngineSupplierTransferManager().recompute_ai_signings(current_state)
        TyreSupplierTransferManager().recompute_ai_signings(current_state)
        AICarDevelopmentManager().generate_for_season(current_state)
        return current_state, {
            "type": "game_started",
            "status": "success",
            "data": {
                "team_name": selected_team.name,
                "week_display": current_state.week_display,
                "next_event_display": current_state.next_event_display,
                "year": current_state.year,
                "balance": current_state.finance.balance,
                "unread_count": sum(1 for e in current_state.emails if not e.read),
                "game_over": current_state.game_over,
                "game_over_reason": current_state.game_over_reason,
                "game_completed": current_state.game_completed,
                "completion_year": current_state.completion_year,
            },
        }
    except Exception as e:
        logger.error(f"Error starting career: {e}")
        return state, {"status": "error", "message": str(e)}
