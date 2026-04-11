from app.core.standings import StandingsManager
from app.core.commercial_staff_costs import CommercialStaffCostManager
from app.core.player_car_development import PlayerCarDevelopmentManager
from app.core.workforce_costs import WorkforceCostManager
from app.core.finance_reporting import build_finance_report
from app.models.calendar import EventType
from app.models.state import GameState


def get_grid_payload(state: GameState, year: int | None, grid_manager) -> dict:
    grid_json = grid_manager.get_grid_json(state, year=year)
    return {"grid_json": grid_json, "year": year if year is not None else state.year}


def get_home_payload(state: GameState) -> dict:
    player_team = state.player_team
    if not player_team:
        raise ValueError("No player team assigned")

    standings_manager = StandingsManager()
    constructor_standings = standings_manager.get_constructor_standings(state)
    driver_standings = standings_manager.get_driver_standings(state)
    finance_report = build_finance_report(state)

    constructors_position = next(
        (index + 1 for index, team in enumerate(constructor_standings) if team.id == player_team.id),
        None,
    )
    constructors_points = next((team.points for team in constructor_standings if team.id == player_team.id), 0)

    team_driver_ids = {player_team.driver1_id, player_team.driver2_id}
    lead_driver = next((driver for driver in driver_standings if driver.id in team_driver_ids), None)
    lead_driver_position = next(
        (index + 1 for index, driver in enumerate(driver_standings) if lead_driver and driver.id == lead_driver.id),
        None,
    )

    season_results = state.driver_season_results.get(state.year, {})
    player_results = []
    for driver_id in team_driver_ids:
        player_results.extend(season_results.get(driver_id, []))
    player_results.sort(key=lambda result: result.get("round", 0))
    wins = sum(1 for result in player_results if result.get("position") == 1)
    podiums = sum(1 for result in player_results if 1 <= int(result.get("position", 99) or 99) <= 3)
    latest_result = player_results[-1] if player_results else None

    technical_director = next((td for td in state.technical_directors if td.team_id == player_team.id), None)
    commercial_manager = next((cm for cm in state.commercial_managers if cm.team_id == player_team.id), None)
    team_principal = next((tp for tp in state.team_principals if tp.team_id == player_team.id), None)

    event = state.calendar.current_event
    event_active = False
    sidebar_action = "ADVANCE"
    if event:
        event_id = f"{event.week}_{event.name}"
        if event_id not in state.events_processed:
            event_active = True
            sidebar_action = "GO TO RACE" if event.type == EventType.RACE else "GO TO TEST"

    alerts = []
    unread_count = sum(1 for email in state.emails if not email.read)
    if unread_count:
        alerts.append(f"{unread_count} unread email{'s' if unread_count != 1 else ''}")
    for driver in state.drivers:
        if driver.team_id != player_team.id:
            continue
        if getattr(driver, "contract_length", 0) == 1:
            alerts.append(f"{driver.name} contract expires this season")
    if technical_director and technical_director.contract_length == 1:
        alerts.append(f"{technical_director.name} contract expires this season")
    if commercial_manager and commercial_manager.contract_length == 1:
        alerts.append(f"{commercial_manager.name} contract expires this season")
    if player_team.title_sponsor_name and getattr(player_team, "title_sponsor_contract_length", 0) == 1:
        alerts.append(f"{player_team.title_sponsor_name} title sponsor deal expires this season")
    if player_team.engine_supplier_name and not getattr(player_team, "builds_own_engine", False) and getattr(player_team, "engine_supplier_contract_length", 0) == 1:
        alerts.append(f"{player_team.engine_supplier_name} engine deal expires this season")
    if player_team.tyre_supplier_name and getattr(player_team, "tyre_supplier_contract_length", 0) == 1:
        alerts.append(f"{player_team.tyre_supplier_name} tyre deal expires this season")
    if int(getattr(player_team, "car_wear", 0) or 0) > 0:
        alerts.append(f"Car wear at {int(player_team.car_wear)} points")
    if state.finance.facilities_upgrade_active:
        alerts.append("Facilities upgrade installments in progress")

    recent_news = [
        {
            "subject": email.subject,
            "sender": email.sender,
            "week": email.week,
            "year": email.year,
        }
        for email in list(reversed(state.emails))[:5]
    ]

    return {
        "top_summary": {
            "team_name": player_team.name,
            "week_display": state.week_display,
            "balance": state.finance.balance,
            "constructors_position": constructors_position,
            "constructors_points": constructors_points,
            "next_event_display": state.next_event_display,
        },
        "next_up": {
            "sidebar_action": sidebar_action,
            "event_active": event_active,
            "event_name": event.name if event else None,
            "event_type": event.type.value if event else None,
        },
        "alerts": alerts,
        "season_snapshot": {
            "lead_driver_name": lead_driver.name if lead_driver else None,
            "lead_driver_position": lead_driver_position,
            "lead_driver_points": lead_driver.points if lead_driver else 0,
            "wins": wins,
            "podiums": podiums,
            "latest_result": latest_result,
        },
        "team_snapshot": {
            "drivers": [
                driver.name
                for driver in state.drivers
                if driver.team_id == player_team.id
            ],
            "team_principal": team_principal.name if team_principal else "You",
            "technical_director": technical_director.name if technical_director else "VACANT",
            "commercial_manager": commercial_manager.name if commercial_manager else "VACANT",
            "title_sponsor": player_team.title_sponsor_name or "VACANT",
            "engine_supplier": player_team.engine_supplier_name or "VACANT",
            "tyre_supplier": player_team.tyre_supplier_name or "VACANT",
            "fuel_supplier": player_team.fuel_supplier_name or "VACANT",
        },
        "finance_snapshot": {
            "balance": state.finance.balance,
            "season_net": finance_report["summary"]["net_profit_loss"],
            "prize_money_total": finance_report["summary"]["prize_money_total"],
            "sponsorship_total": finance_report["summary"]["sponsorship_total"],
        },
        "recent_news": recent_news,
    }


def get_standings_payload(state: GameState) -> dict:
    manager = StandingsManager()
    driver_standings = manager.get_driver_standings(state)
    constructor_standings = manager.get_constructor_standings(state)
    driver_countback_notes = manager.build_driver_countback_notes(state, driver_standings)
    constructor_countback_notes = manager.build_constructor_countback_notes(state, constructor_standings)
    try:
        d_standings = [d.model_dump() for d in driver_standings]
        c_standings = [t.model_dump() for t in constructor_standings]
    except AttributeError:
        d_standings = [d.dict() for d in driver_standings]
        c_standings = [t.dict() for t in constructor_standings]
    for row in d_standings:
        row["countback_note"] = driver_countback_notes.get(row.get("id")) if isinstance(row, dict) else None
    for row in c_standings:
        row["countback_note"] = constructor_countback_notes.get(row.get("id")) if isinstance(row, dict) else None
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
    commercial_staff_manager = CommercialStaffCostManager()
    races_in_season = max(1, sum(1 for e in state.calendar.events if e.type == EventType.RACE))
    projected_race_payroll = workforce_manager.calculate_race_cost(player_team.workforce, races_in_season)
    projected_annual_payroll = max(0, int(player_team.workforce or 0)) * workforce_manager.annual_avg_wage
    projected_commercial_race_payroll = commercial_staff_manager.calculate_race_cost(player_team.commercial_staff, races_in_season)
    projected_commercial_annual_payroll = max(0, int(player_team.commercial_staff or 0)) * commercial_staff_manager.annual_avg_wage

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
        "player_commercial_staff": player_team.commercial_staff,
        "workforce_limits": {"min": 0, "max": 250},
        "annual_avg_wage": workforce_manager.annual_avg_wage,
        "projected_workforce_race_cost": projected_race_payroll,
        "projected_workforce_annual_cost": projected_annual_payroll,
        "commercial_staff_annual_avg_wage": commercial_staff_manager.annual_avg_wage,
        "projected_commercial_staff_race_cost": projected_commercial_race_payroll,
        "projected_commercial_staff_annual_cost": projected_commercial_annual_payroll,
        "races_in_season": races_in_season,
        "teams": [
            {"id": t.id, "name": t.name, "country": t.country, "workforce": t.workforce, "commercial_staff": t.commercial_staff}
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
        "podiums": driver.podiums,
        "poles": driver.poles,
        "fastest_laps": driver.fastest_laps,
        "championships": driver.championships,
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
