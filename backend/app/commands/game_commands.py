import json
import logging

from app.core.ai_car_development import AICarDevelopmentManager
from app.core.grid import GridManager
from app.core.prize_money import PrizeMoneyManager
from app.core.retirement import RetirementManager
from app.core.roster import load_roster
from app.core.transfers import TransferManager
from app.core.management_transfers import (
    CommercialManagerTransferManager,
    TechnicalDirectorTransferManager,
    TitleSponsorTransferManager,
)
from app.commands.facilities_commands import (
    handle_facilities_upgrade_preview,
    handle_start_facilities_upgrade,
)
from app.commands.finance_commands import build_finance_payload
from app.commands.race_commands import (
    handle_get_race_weekend,
    handle_simulate_qualifying,
    handle_simulate_race,
)
from app.commands.staff_commands import (
    handle_get_technical_director_replacement_candidates,
    handle_get_manager_replacement_candidates,
    handle_get_title_sponsor_replacement_candidates,
    handle_get_replacement_candidates,
    handle_repair_car_wear,
    handle_replace_commercial_manager,
    handle_replace_technical_director,
    handle_replace_title_sponsor,
    handle_replace_driver,
    handle_start_car_development,
    handle_update_workforce,
)
from app.models.calendar import Calendar
from app.models.email import EmailCategory
from app.models.finance import Finance
from app.models.state import GameState


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
        TechnicalDirectorTransferManager().recompute_ai_signings(current_state)
        TitleSponsorTransferManager().recompute_ai_signings(current_state)
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
            },
        }
    except Exception as e:
        logger.error(f"Error starting career: {e}")
        return state, {"status": "error", "message": str(e)}
