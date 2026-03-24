from app.core.standings import StandingsManager
from app.core.player_car_development import PlayerCarDevelopmentManager
from app.core.workforce_costs import WorkforceCostManager
from app.models.calendar import EventType
from app.models.state import GameState


def get_grid_payload(state: GameState, year: int | None, grid_manager) -> dict:
    grid_json = grid_manager.get_grid_json(state, year=year)
    return {"grid_json": grid_json, "year": year if year is not None else state.year}


def get_standings_payload(state: GameState) -> dict:
    manager = StandingsManager()
    try:
        d_standings = [d.model_dump() for d in manager.get_driver_standings(state)]
        c_standings = [t.model_dump() for t in manager.get_constructor_standings(state)]
    except AttributeError:
        d_standings = [d.dict() for d in manager.get_driver_standings(state)]
        c_standings = [t.dict() for t in manager.get_constructor_standings(state)]
    return {"drivers": d_standings, "constructors": c_standings}


def get_staff_payload(state: GameState) -> dict:
    player_team = next((t for t in state.teams if t.id == state.player_team_id), None)
    if not player_team:
        raise ValueError("No player team assigned")
    pending_driver_seats = {
        s.get("seat")
        for s in state.announced_ai_signings
        if s.get("status") == "announced" and s.get("team_id") == player_team.id
    }
    pending_cm = any(
        s.get("status") == "announced" and s.get("team_id") == player_team.id
        for s in state.announced_ai_cm_signings
    )
    pending_td = any(
        s.get("status") == "announced" and s.get("team_id") == player_team.id
        for s in state.announced_ai_td_signings
    )

    team_drivers = [
        {
            "id": d.id,
            "name": d.name,
            "age": d.age,
            "country": d.country,
            "speed": d.speed,
            "points": d.points,
            "wage": d.wage,
            "pay_driver": d.pay_driver,
            "contract_length": d.contract_length,
            "pending_replacement": (
                ("driver1_id" in pending_driver_seats and d.id == player_team.driver1_id)
                or ("driver2_id" in pending_driver_seats and d.id == player_team.driver2_id)
            ),
        }
        for d in state.drivers
        if d.team_id == player_team.id
    ]
    team_td = next((td for td in state.technical_directors if td.team_id == player_team.id), None)
    team_cm = next((cm for cm in state.commercial_managers if cm.team_id == player_team.id), None)
    workforce_manager = WorkforceCostManager()
    races_in_season = max(1, sum(1 for e in state.calendar.events if e.type == EventType.RACE))
    projected_race_payroll = workforce_manager.calculate_race_cost(player_team.workforce, races_in_season)
    projected_annual_payroll = max(0, int(player_team.workforce or 0)) * workforce_manager.annual_avg_wage

    return {
        "team_name": player_team.name,
        "drivers": team_drivers,
        "technical_director": (
            {
                "id": team_td.id,
                "name": team_td.name,
                "country": team_td.country,
                "age": team_td.age,
                "skill": team_td.skill,
                "contract_length": team_td.contract_length,
                "salary": team_td.salary,
                "pending_replacement": pending_td,
            }
            if team_td
            else None
        ),
        "commercial_manager": (
            {
                "id": team_cm.id,
                "name": team_cm.name,
                "country": team_cm.country,
                "age": team_cm.age,
                "skill": team_cm.skill,
                "contract_length": team_cm.contract_length,
                "salary": team_cm.salary,
                "pending_replacement": pending_cm,
            }
            if team_cm
            else None
        ),
        "player_workforce": player_team.workforce,
        "workforce_limits": {"min": 0, "max": 250},
        "annual_avg_wage": workforce_manager.annual_avg_wage,
        "projected_workforce_race_cost": projected_race_payroll,
        "projected_workforce_annual_cost": projected_annual_payroll,
        "races_in_season": races_in_season,
        "teams": [
            {"id": t.id, "name": t.name, "country": t.country, "workforce": t.workforce}
            for t in state.teams
        ],
    }


def get_driver_payload(state: GameState, driver_name: str) -> dict:
    driver = next((d for d in state.drivers if d.name == driver_name), None)
    if not driver:
        raise ValueError(f"Driver '{driver_name}' not found")
    team = next((t for t in state.teams if t.id == driver.team_id), None)
    team_name = team.name if team else "Free Agent"
    state_year_results = state.driver_season_results.get(state.year, {})
    return {
        "id": driver.id,
        "name": driver.name,
        "age": driver.age,
        "country": driver.country,
        "team_name": team_name,
        "speed": driver.speed,
        "race_starts": driver.race_starts,
        "wins": driver.wins,
        "points": driver.points,
        "wage": driver.wage,
        "pay_driver": driver.pay_driver,
        "season_results": sorted(state_year_results.get(driver.id, []), key=lambda r: r.get("round", 0)),
    }


def get_facilities_payload(state: GameState) -> dict:
    player_team = state.player_team
    if not player_team:
        raise ValueError("No player team assigned")
    return {
        "team_name": player_team.name,
        "facilities": player_team.facilities,
        "upgrade_financing": {
            "active": state.finance.facilities_upgrade_active,
            "total_cost": state.finance.facilities_upgrade_total_cost,
            "paid": state.finance.facilities_upgrade_paid,
            "remaining": max(state.finance.facilities_upgrade_total_cost - state.finance.facilities_upgrade_paid, 0),
            "races_paid": state.finance.facilities_upgrade_races_paid,
            "total_races": state.finance.facilities_upgrade_total_races,
            "years": state.finance.facilities_upgrade_years,
            "points": state.finance.facilities_upgrade_points,
        },
        "teams": [
            {
                "id": t.id,
                "name": t.name,
                "country": t.country,
                "facilities": t.facilities,
            }
            for t in state.teams
        ],
    }


def get_car_payload(state: GameState) -> dict:
    engine_power_by_supplier = {e.name: e.power for e in state.engine_suppliers}
    player_project = state.player_car_development
    player_team = state.player_team
    player_wear = int(player_team.car_wear) if player_team else 0
    player_mech_fail_probability = min(0.35, max(0.0, player_wear * 0.002))
    return {
        "teams": [
            {
                "id": t.id,
                "name": t.name,
                "country": t.country,
                "car_speed": t.car_speed,
                "engine_supplier_name": t.engine_supplier_name,
                "engine_power": engine_power_by_supplier.get(t.engine_supplier_name, 0),
            }
            for t in state.teams
        ],
        "development_catalog": PlayerCarDevelopmentManager().get_catalog(
            workforce=player_team.workforce if player_team else 250
        ),
        "player_team_name": player_team.name if player_team else None,
        "player_car_speed": player_team.car_speed if player_team else 0,
        "player_car_wear": player_wear,
        "player_mechanical_fail_probability": player_mech_fail_probability,
        "player_development": (
            {
                "active": player_project.active,
                "development_type": player_project.development_type,
                "total_weeks": player_project.total_weeks,
                "weeks_remaining": player_project.weeks_remaining,
                "speed_delta": player_project.speed_delta,
                "total_cost": player_project.total_cost,
                "weekly_cost": player_project.weekly_cost,
                "paid": player_project.paid,
            }
            if player_project
            else {
                "active": False,
                "development_type": None,
                "total_weeks": 0,
                "weeks_remaining": 0,
                "speed_delta": 0,
                "total_cost": 0,
                "weekly_cost": 0,
                "paid": 0,
            }
        ),
    }


def get_emails_payload(state: GameState) -> dict:
    emails_data = [e.model_dump() for e in reversed(state.emails)]
    unread_count = sum(1 for e in state.emails if not e.read)
    return {"emails": emails_data, "unread_count": unread_count}


def read_email_payload(state: GameState, email_id: int | None) -> dict:
    for email in state.emails:
        if email.id == email_id:
            email.read = True
            break
    unread_count = sum(1 for e in state.emails if not e.read)
    return {"email_id": email_id, "unread_count": unread_count}
