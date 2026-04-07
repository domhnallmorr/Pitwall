import random

from app.core.roster import load_roster
from app.models.state import GameState


AI_WORKFORCE_MIN = 90
AI_WORKFORCE_MAX = 250


def update_drivers(state: GameState):
    for driver in state.drivers:
        if driver.active:
            driver.age += 1


def update_management_staff(state: GameState) -> dict:
    teams_by_id = {team.id: team for team in state.teams}
    expired_team_principals = []
    expired_technical_directors = []
    expired_commercial_managers = []

    for principal in state.team_principals:
        if not getattr(principal, "active", True):
            continue
        principal.age += 1
        if principal.team_id is None:
            continue
        if getattr(principal, "owns_team", False):
            continue
        if principal.contract_length > 1:
            principal.contract_length -= 1
            continue

        team = teams_by_id.get(principal.team_id)
        if team and team.team_principal_id == principal.id:
            team.team_principal_id = None
        expired_team_principals.append(
            {"id": principal.id, "name": principal.name, "team_id": principal.team_id, "team_name": team.name if team else None}
        )
        principal.team_id = None
        principal.contract_length = 0

    for director in state.technical_directors:
        if not getattr(director, "active", True):
            continue
        director.age += 1
        if director.team_id is None:
            continue
        if director.contract_length > 1:
            director.contract_length -= 1
            continue

        team = teams_by_id.get(director.team_id)
        if team and team.technical_director_id == director.id:
            team.technical_director_id = None
        expired_technical_directors.append(
            {"id": director.id, "name": director.name, "team_id": director.team_id, "team_name": team.name if team else None}
        )
        director.team_id = None
        director.contract_length = 0

    for manager in state.commercial_managers:
        if not getattr(manager, "active", True):
            continue
        manager.age += 1
        if manager.team_id is None:
            continue
        if manager.contract_length > 1:
            manager.contract_length -= 1
            continue

        team = teams_by_id.get(manager.team_id)
        if team and team.commercial_manager_id == manager.id:
            team.commercial_manager_id = None
        expired_commercial_managers.append(
            {"id": manager.id, "name": manager.name, "team_id": manager.team_id, "team_name": team.name if team else None}
        )
        manager.team_id = None
        manager.contract_length = 0

    return {
        "expired_team_principals": expired_team_principals,
        "expired_technical_directors": expired_technical_directors,
        "expired_commercial_managers": expired_commercial_managers,
    }


def degrade_facilities(state: GameState) -> list[dict]:
    updates = []
    for team in state.teams:
        old_value = team.facilities if team.facilities is not None else 0
        team.facilities = max(1, old_value - 4)
        updates.append(
            {
                "team_id": team.id,
                "team_name": team.name,
                "old_facilities": old_value,
                "new_facilities": team.facilities,
            }
        )
    return updates


def apply_ai_facilities_upgrades(state: GameState, random_module=random) -> list[dict]:
    updates = []
    for team in state.teams:
        if state.player_team_id is not None and team.id == state.player_team_id:
            continue
        if random_module.random() >= 0.2:
            continue
        old_value = team.facilities if team.facilities is not None else 0
        increase = random_module.randint(20, 40)
        team.facilities = min(100, old_value + increase)
        updates.append(
            {
                "team_id": team.id,
                "team_name": team.name,
                "old_facilities": old_value,
                "increase": increase,
                "new_facilities": team.facilities,
            }
        )
    return updates


def update_ai_workforce(
    state: GameState,
    ai_workforce_min: int = AI_WORKFORCE_MIN,
    ai_workforce_max: int = AI_WORKFORCE_MAX,
    random_module=random,
) -> list[dict]:
    updates = []
    for team in state.teams:
        if state.player_team_id is not None and team.id == state.player_team_id:
            continue

        old_workforce = int(team.workforce if team.workforce is not None else ai_workforce_min)
        bounded_old = min(ai_workforce_max, max(ai_workforce_min, old_workforce))

        trend = random_module.choices(
            ["increase", "decrease", "flat"],
            weights=[0.45, 0.25, 0.30],
            k=1,
        )[0]

        delta = 0
        if trend == "increase":
            delta = random_module.choice([3, 5, 7, 10, 12, 15])
        elif trend == "decrease":
            delta = -random_module.choice([3, 5, 7, 9, 12])

        new_workforce = min(ai_workforce_max, max(ai_workforce_min, bounded_old + delta))
        applied_delta = new_workforce - bounded_old
        team.workforce = new_workforce

        if applied_delta != 0:
            updates.append(
                {
                    "team_id": team.id,
                    "team_name": team.name,
                    "old_workforce": bounded_old,
                    "new_workforce": new_workforce,
                    "delta": applied_delta,
                }
            )

    return updates


def add_new_season_drivers(state: GameState, load_roster_func=load_roster) -> list[dict]:
    _, season_drivers, _, _, _ = load_roster_func(year=state.year)
    existing_ids = {d.id for d in state.drivers}
    new_entrants = []

    for driver in season_drivers:
        if driver.id in existing_ids:
            continue
        driver.team_id = None
        driver.role = None
        driver.active = True
        driver.retirement_year = None
        driver.retired_year = None
        state.drivers.append(driver)
        new_entrants.append(
            {
                "id": driver.id,
                "name": driver.name,
                "country": driver.country,
                "age": driver.age,
                "pay_driver": driver.pay_driver,
            }
        )

    return new_entrants


def add_new_season_title_sponsors(state: GameState, load_roster_func=load_roster) -> list[dict]:
    roster_data = load_roster_func(
        year=state.year,
        include_title_sponsors=True,
    )
    season_title_sponsors = roster_data[5] if len(roster_data) > 5 else []
    existing_ids = {s.id for s in state.title_sponsors}
    new_sponsors = []

    for sponsor in season_title_sponsors:
        if sponsor.id in existing_ids:
            continue
        state.title_sponsors.append(sponsor)
        new_sponsors.append(
            {
                "id": sponsor.id,
                "name": sponsor.name,
                "wealth": sponsor.wealth,
                "start_year": sponsor.start_year,
            }
        )

    return new_sponsors
