from app.core.standings import StandingsManager
from app.core.player_car_development import PlayerCarDevelopmentManager
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
        }
        for d in state.drivers
        if d.team_id == player_team.id
    ]
    team_td = next((td for td in state.technical_directors if td.team_id == player_team.id), None)
    team_cm = next((cm for cm in state.commercial_managers if cm.team_id == player_team.id), None)

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
            }
            if team_td
            else None
        ),
        "commercial_manager": (
            {
                "id": team_cm.id,
                "name": team_cm.name,
                "age": team_cm.age,
                "skill": team_cm.skill,
                "contract_length": team_cm.contract_length,
                "salary": team_cm.salary,
            }
            if team_cm
            else None
        ),
        "player_workforce": player_team.workforce,
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
        "development_catalog": PlayerCarDevelopmentManager().get_catalog(),
        "player_team_name": player_team.name if player_team else None,
        "player_car_speed": player_team.car_speed if player_team else 0,
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
