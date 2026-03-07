from typing import List, Tuple

from app.core.db import get_connection
from app.core.roster_components import (
    load_circuits,
    load_commercial_managers as load_commercial_managers_for_roster,
    load_drivers,
    load_engine_suppliers,
    load_events,
    load_fuel_suppliers,
    load_teams,
    load_technical_directors as load_technical_directors_for_roster,
    load_title_sponsors,
    load_tyre_suppliers,
)
from app.models.commercial_manager import CommercialManager
from app.models.team import Team
from app.models.technical_director import TechnicalDirector


def _resolve_start_year(cursor, year: int) -> int:
    if year == 0:
        cursor.execute("SELECT value FROM metadata WHERE key='start_year'")
        result = cursor.fetchone()
        return int(result[0]) if result else 1998
    return year


def load_technical_directors(year: int = 0, teams: List[Team] | None = None) -> List[TechnicalDirector]:
    """
    Loads technical directors for the supplied year (or metadata default).
    Optionally links directors to supplied Team objects.
    """
    conn = get_connection()
    c = conn.cursor()
    start_year = _resolve_start_year(c, year)
    linked_teams = teams or []
    technical_directors = load_technical_directors_for_roster(
        c, start_year, linked_teams, include=True
    )
    conn.close()
    return technical_directors


def load_commercial_managers(year: int = 0, teams: List[Team] | None = None) -> List[CommercialManager]:
    """
    Loads commercial managers for the supplied year (or metadata default).
    Optionally links managers to supplied Team objects.
    """
    conn = get_connection()
    c = conn.cursor()
    start_year = _resolve_start_year(c, year)
    linked_teams = teams or []
    commercial_managers = load_commercial_managers_for_roster(
        c, start_year, linked_teams, include=True
    )
    conn.close()
    return commercial_managers


def load_roster(
    year: int = 0,
    include_technical_directors: bool = False,
    include_commercial_managers: bool = False,
    include_title_sponsors: bool = False,
    include_engine_suppliers: bool = False,
    include_tyre_suppliers: bool = False,
    include_fuel_suppliers: bool = False,
) -> Tuple:
    """
    Loads teams, drivers, calendar, and circuits.
    Returns: (Teams, Drivers, StartYear, Events, Circuits)
    """
    conn = get_connection()
    c = conn.cursor()
    start_year = _resolve_start_year(c, year)

    drivers, driver_map = load_drivers(c, start_year)
    teams = load_teams(c, start_year, driver_map)

    technical_directors = load_technical_directors_for_roster(
        c, start_year, teams, include_technical_directors
    )
    commercial_managers = load_commercial_managers_for_roster(
        c, start_year, teams, include_commercial_managers
    )
    title_sponsors = load_title_sponsors(c, start_year, include_title_sponsors)
    engine_suppliers = load_engine_suppliers(c, start_year, include_engine_suppliers)
    tyre_suppliers = load_tyre_suppliers(c, start_year, include_tyre_suppliers)
    fuel_suppliers = load_fuel_suppliers(c, start_year, include_fuel_suppliers)
    events = load_events(c, start_year)
    circuits = load_circuits(c)

    conn.close()
    result = [teams, drivers, start_year, events, circuits]
    if include_technical_directors:
        result.append(technical_directors)
    if include_commercial_managers:
        result.append(commercial_managers)
    if include_title_sponsors:
        result.append(title_sponsors)
    if include_engine_suppliers:
        result.append(engine_suppliers)
    if include_tyre_suppliers:
        result.append(tyre_suppliers)
    if include_fuel_suppliers:
        result.append(fuel_suppliers)
    return tuple(result)
