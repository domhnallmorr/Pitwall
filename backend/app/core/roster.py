from app.core.db import get_connection
from app.models.driver import Driver
from app.models.team import Team
from app.models.enums import DriverRole
from app.models.calendar import Event, EventType
from typing import List, Tuple
from app.models.circuit import Circuit
from app.models.technical_director import TechnicalDirector
from app.models.commercial_manager import CommercialManager
from app.models.title_sponsor import TitleSponsor
from app.models.engine_supplier import EngineSupplier
from app.models.tyre_supplier import TyreSupplier


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

    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='technical_directors'")
    if c.fetchone() is None:
        conn.close()
        return []

    c.execute(
        'SELECT id, name, country, age, skill, contract_length, salary, team_name '
        'FROM technical_directors WHERE start_year = ? OR start_year = 0 ORDER BY id ASC',
        (start_year,),
    )

    team_by_name = {t.name: t for t in teams} if teams else {}
    technical_directors: List[TechnicalDirector] = []
    for row in c.fetchall():
        team_name = row[7]
        team = team_by_name.get(team_name) if team_name else None
        td = TechnicalDirector(
            id=row[0],
            name=row[1],
            country=row[2],
            age=row[3],
            skill=row[4],
            contract_length=row[5] if row[5] is not None else 0,
            salary=row[6] if row[6] is not None else 0,
            team_id=team.id if team else None,
        )
        if team:
            team.technical_director_id = td.id
        technical_directors.append(td)

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

    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commercial_managers'")
    if c.fetchone() is None:
        conn.close()
        return []

    c.execute(
        'SELECT id, name, age, skill, contract_length, salary, team_name '
        'FROM commercial_managers WHERE start_year = ? OR start_year = 0 ORDER BY id ASC',
        (start_year,),
    )

    team_by_name = {t.name: t for t in teams} if teams else {}
    commercial_managers: List[CommercialManager] = []
    for row in c.fetchall():
        team_name = row[6]
        team = team_by_name.get(team_name) if team_name else None
        manager = CommercialManager(
            id=row[0],
            name=row[1],
            age=row[2],
            skill=row[3],
            contract_length=row[4] if row[4] is not None else 0,
            salary=row[5] if row[5] is not None else 0,
            team_id=team.id if team else None,
        )
        if team:
            team.commercial_manager_id = manager.id
        commercial_managers.append(manager)

    conn.close()
    return commercial_managers

def load_roster(
    year: int = 0,
    include_technical_directors: bool = False,
    include_commercial_managers: bool = False,
    include_title_sponsors: bool = False,
    include_engine_suppliers: bool = False,
    include_tyre_suppliers: bool = False,
) -> Tuple:
    """
    Loads teams, drivers, calendar, and circuits.
    Returns: (Teams, Drivers, StartYear, Events, Circuits)
    """
    conn = get_connection()
    c = conn.cursor()

    # 1. Start Year
    start_year = _resolve_start_year(c, year)

    # 2. Drivers
    # Allow loading drivers assigned to specific year OR default (0)
    c.execute("PRAGMA table_info(drivers)")
    driver_columns = {row[1] for row in c.fetchall()}
    has_speed = "speed" in driver_columns
    has_race_starts = "race_starts" in driver_columns
    has_wins = "wins" in driver_columns
    has_contract_length = "contract_length" in driver_columns

    speed_expr = "speed" if has_speed else "50"
    race_starts_expr = "race_starts" if has_race_starts else "0"
    wins_expr = "wins" if has_wins else "0"
    contract_length_expr = "contract_length" if has_contract_length else "2"
    c.execute(
        f'SELECT id, name, age, country, wage, pay_driver, {speed_expr} AS speed, {race_starts_expr} AS race_starts, {wins_expr} AS wins, {contract_length_expr} AS contract_length '
        'FROM drivers WHERE start_year = ? OR start_year = 0 ORDER BY id ASC',
        (start_year,),
    )
    drivers = []
    driver_map = {} # Name -> ID mapping for assigning to teams
    for row in c.fetchall():
        speed = row[6] if row[6] is not None else 50
        race_starts = row[7] if row[7] is not None else 0
        wins = row[8] if row[8] is not None else 0
        contract_length = row[9] if row[9] is not None else 2
        d = Driver(
            id=row[0],
            name=row[1],
            age=row[2],
            country=row[3],
            wage=row[4],
            pay_driver=bool(row[5]),
            speed=speed,
            race_starts=race_starts,
            wins=wins,
            contract_length=contract_length,
        )
        drivers.append(d)
        driver_map[d.name] = d

    # 3. Teams
    # Link drivers to teams using the map
    c.execute("PRAGMA table_info(teams)")
    team_columns = {row[1] for row in c.fetchall()}
    has_car_speed = "car_speed" in team_columns
    has_workforce = "workforce" in team_columns
    has_title_sponsor_name = "title_sponsor_name" in team_columns
    has_title_sponsor_yearly = "title_sponsor_yearly" in team_columns
    has_engine_supplier_name = "engine_supplier_name" in team_columns
    has_engine_supplier_deal = "engine_supplier_deal" in team_columns
    has_engine_supplier_yearly_cost = "engine_supplier_yearly_cost" in team_columns
    has_tyre_supplier_name = "tyre_supplier_name" in team_columns
    has_tyre_supplier_deal = "tyre_supplier_deal" in team_columns
    has_tyre_supplier_yearly_cost = "tyre_supplier_yearly_cost" in team_columns
    car_speed_expr = "car_speed" if has_car_speed else "50"
    workforce_expr = "workforce" if has_workforce else "0"
    title_sponsor_name_expr = "title_sponsor_name" if has_title_sponsor_name else "NULL"
    title_sponsor_yearly_expr = "title_sponsor_yearly" if has_title_sponsor_yearly else "0"
    engine_supplier_name_expr = "engine_supplier_name" if has_engine_supplier_name else "NULL"
    engine_supplier_deal_expr = "engine_supplier_deal" if has_engine_supplier_deal else "NULL"
    engine_supplier_yearly_cost_expr = "engine_supplier_yearly_cost" if has_engine_supplier_yearly_cost else "0"
    tyre_supplier_name_expr = "tyre_supplier_name" if has_tyre_supplier_name else "NULL"
    tyre_supplier_deal_expr = "tyre_supplier_deal" if has_tyre_supplier_deal else "NULL"
    tyre_supplier_yearly_cost_expr = "tyre_supplier_yearly_cost" if has_tyre_supplier_yearly_cost else "0"

    c.execute(
        f'SELECT id, name, country, driver1_name, driver2_name, balance, facilities, {car_speed_expr} AS car_speed, {workforce_expr} AS workforce, '
        f'{title_sponsor_name_expr} AS title_sponsor_name, {title_sponsor_yearly_expr} AS title_sponsor_yearly, '
        f'{engine_supplier_name_expr} AS engine_supplier_name, {engine_supplier_deal_expr} AS engine_supplier_deal, {engine_supplier_yearly_cost_expr} AS engine_supplier_yearly_cost, '
        f'{tyre_supplier_name_expr} AS tyre_supplier_name, {tyre_supplier_deal_expr} AS tyre_supplier_deal, {tyre_supplier_yearly_cost_expr} AS tyre_supplier_yearly_cost '
        'FROM teams WHERE start_year = ? OR start_year = 0 ORDER BY id ASC',
        (start_year,),
    )
    teams = []
    for row in c.fetchall():
        car_speed = row[7] if row[7] is not None else 50
        workforce = row[8] if row[8] is not None else 0
        title_sponsor_name = row[9] if row[9] is not None else None
        title_sponsor_yearly = row[10] if row[10] is not None else 0
        engine_supplier_name = row[11] if row[11] is not None else None
        engine_supplier_deal = row[12] if row[12] is not None else None
        engine_supplier_yearly_cost = row[13] if row[13] is not None else 0
        tyre_supplier_name = row[14] if row[14] is not None else None
        tyre_supplier_deal = row[15] if row[15] is not None else None
        tyre_supplier_yearly_cost = row[16] if row[16] is not None else 0
        t = Team(
            id=row[0],
            name=row[1],
            country=row[2],
            balance=row[5],
            facilities=row[6],
            car_speed=car_speed,
            workforce=workforce,
            title_sponsor_name=title_sponsor_name,
            title_sponsor_yearly=title_sponsor_yearly,
            engine_supplier_name=engine_supplier_name,
            engine_supplier_deal=engine_supplier_deal,
            engine_supplier_yearly_cost=engine_supplier_yearly_cost,
            tyre_supplier_name=tyre_supplier_name,
            tyre_supplier_deal=tyre_supplier_deal,
            tyre_supplier_yearly_cost=tyre_supplier_yearly_cost,
        )
        
        # Link Drivers to Teams
        d1_name = row[3]
        d2_name = row[4]

        if d1_name and d1_name in driver_map:
            d1 = driver_map[d1_name]
            t.driver1_id = d1.id
            d1.team_id = t.id
            d1.role = DriverRole.DRIVER_1

        if d2_name and d2_name in driver_map:
            d2 = driver_map[d2_name]
            t.driver2_id = d2.id
            d2.team_id = t.id
            d2.role = DriverRole.DRIVER_2

        teams.append(t)

    # 4. Load Technical Directors and link to team ids (if table exists).
    technical_directors: List[TechnicalDirector] = []
    try:
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='technical_directors'")
        has_td_table = c.fetchone() is not None
        if has_td_table:
            c.execute(
                'SELECT id, name, country, age, skill, contract_length, salary, team_name '
                'FROM technical_directors WHERE start_year = ? OR start_year = 0',
                (start_year,),
            )
            td_rows = c.fetchall()
            team_by_name = {t.name: t for t in teams}
            for td_id, td_name, td_country, td_age, td_skill, td_contract_length, td_salary, team_name in td_rows:
                team = team_by_name.get(team_name)
                if team:
                    team.technical_director_id = td_id
                if include_technical_directors:
                    technical_directors.append(
                        TechnicalDirector(
                            id=td_id,
                            name=td_name,
                            country=td_country,
                            age=td_age,
                            skill=td_skill,
                            contract_length=td_contract_length if td_contract_length is not None else 0,
                            salary=td_salary if td_salary is not None else 0,
                            team_id=team.id if team else None,
                        )
                    )
    except Exception as e:
        print(f"Error linking technical directors: {e}")

    # 5. Load Commercial Managers and link to team ids (if table exists).
    commercial_managers: List[CommercialManager] = []
    try:
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commercial_managers'")
        has_cm_table = c.fetchone() is not None
        if has_cm_table:
            c.execute(
                'SELECT id, name, age, skill, contract_length, salary, team_name '
                'FROM commercial_managers WHERE start_year = ? OR start_year = 0',
                (start_year,),
            )
            cm_rows = c.fetchall()
            team_by_name = {t.name: t for t in teams}
            for cm_id, cm_name, cm_age, cm_skill, cm_contract_length, cm_salary, team_name in cm_rows:
                team = team_by_name.get(team_name)
                if team:
                    team.commercial_manager_id = cm_id
                if include_commercial_managers:
                    commercial_managers.append(
                        CommercialManager(
                            id=cm_id,
                            name=cm_name,
                            age=cm_age,
                            skill=cm_skill,
                            contract_length=cm_contract_length if cm_contract_length is not None else 0,
                            salary=cm_salary if cm_salary is not None else 0,
                            team_id=team.id if team else None,
                        )
                    )
    except Exception as e:
        print(f"Error linking commercial managers: {e}")

    # 6. Load Title Sponsors (optional).
    title_sponsors: List[TitleSponsor] = []
    try:
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='title_sponsors'")
        has_sponsor_table = c.fetchone() is not None
        if has_sponsor_table and include_title_sponsors:
            c.execute(
                'SELECT id, name, wealth, start_year FROM title_sponsors '
                'WHERE start_year = ? OR start_year = 0 ORDER BY id ASC',
                (start_year,),
            )
            title_sponsors = [
                TitleSponsor(
                    id=row[0],
                    name=row[1],
                    wealth=row[2] if row[2] is not None else 0,
                    start_year=row[3] if row[3] is not None else 0,
                )
                for row in c.fetchall()
            ]
    except Exception as e:
        print(f"Error loading title sponsors: {e}")

    # 7. Load Engine Suppliers (optional).
    engine_suppliers: List[EngineSupplier] = []
    try:
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='engine_suppliers'")
        has_engine_table = c.fetchone() is not None
        if has_engine_table and include_engine_suppliers:
            c.execute(
                'SELECT id, name, country, resources, power, start_year FROM engine_suppliers '
                'WHERE start_year = ? OR start_year = 0 ORDER BY id ASC',
                (start_year,),
            )
            engine_suppliers = [
                EngineSupplier(
                    id=row[0],
                    name=row[1],
                    country=row[2] if row[2] is not None else "",
                    resources=row[3] if row[3] is not None else 0,
                    power=row[4] if row[4] is not None else 0,
                    start_year=row[5] if row[5] is not None else 0,
                )
                for row in c.fetchall()
            ]
    except Exception as e:
        print(f"Error loading engine suppliers: {e}")

    # 7b. Load Tyre Suppliers (optional).
    tyre_suppliers: List[TyreSupplier] = []
    try:
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tyre_suppliers'")
        has_tyre_table = c.fetchone() is not None
        if has_tyre_table and include_tyre_suppliers:
            c.execute(
                'SELECT id, name, country, wear, grip, start_year FROM tyre_suppliers '
                'WHERE start_year = ? OR start_year = 0 ORDER BY id ASC',
                (start_year,),
            )
            tyre_suppliers = [
                TyreSupplier(
                    id=row[0],
                    name=row[1],
                    country=row[2] if row[2] is not None else "",
                    wear=row[3] if row[3] is not None else 0,
                    grip=row[4] if row[4] is not None else 0,
                    start_year=row[5] if row[5] is not None else 0,
                )
                for row in c.fetchall()
            ]
    except Exception as e:
        print(f"Error loading tyre suppliers: {e}")

    # 8. Load Calendar
    try:
        c.execute('SELECT name, week, type FROM calendar WHERE year = ? ORDER BY week ASC', (start_year,))
        calendar_data = c.fetchall()
        events = [
            Event(name=r[0], week=r[1], type=EventType(r[2]))
            for r in calendar_data
        ]
    except Exception as e:
        print(f"Error loading calendar: {e}")
        events = []

    # 9. Load Circuits
    try:
        c.execute('SELECT id, name, country, location, laps, base_laptime_ms, length_km, overtaking_delta, power_factor, track_map_path FROM circuits')
        circuit_data = c.fetchall()
        circuits = [
            Circuit(
                id=r[0], name=r[1], country=r[2], location=r[3], 
                laps=r[4], base_laptime_ms=r[5], length_km=r[6], 
                overtaking_delta=r[7], power_factor=r[8], track_map_path=r[9]
            )
            for r in circuit_data
        ]
    except Exception as e:
        print(f"Error loading circuits: {e}")
        circuits = []

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
    return tuple(result)
