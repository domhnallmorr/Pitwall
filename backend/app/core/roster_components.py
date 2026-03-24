from typing import Dict, List

from app.models.calendar import Event, EventType
from app.models.circuit import Circuit
from app.models.commercial_manager import CommercialManager
from app.models.driver import Driver
from app.models.engine_supplier import EngineSupplier
from app.models.enums import DriverRole
from app.models.fuel_supplier import FuelSupplier
from app.models.team import Team
from app.models.technical_director import TechnicalDirector
from app.models.title_sponsor import TitleSponsor
from app.models.tyre_supplier import TyreSupplier


def load_drivers(cursor, start_year: int) -> tuple[List[Driver], Dict[str, Driver]]:
    cursor.execute("PRAGMA table_info(drivers)")
    driver_columns = {row[1] for row in cursor.fetchall()}
    has_speed = "speed" in driver_columns
    has_race_starts = "race_starts" in driver_columns
    has_wins = "wins" in driver_columns
    has_contract_length = "contract_length" in driver_columns

    speed_expr = "speed" if has_speed else "50"
    race_starts_expr = "race_starts" if has_race_starts else "0"
    wins_expr = "wins" if has_wins else "0"
    contract_length_expr = "contract_length" if has_contract_length else "2"
    cursor.execute(
        f"SELECT id, name, age, country, wage, pay_driver, {speed_expr} AS speed, {race_starts_expr} AS race_starts, {wins_expr} AS wins, {contract_length_expr} AS contract_length "
        "FROM drivers WHERE start_year = ? OR start_year = 0 ORDER BY id ASC",
        (start_year,),
    )
    drivers: List[Driver] = []
    driver_map: Dict[str, Driver] = {}
    for row in cursor.fetchall():
        speed = row[6] if row[6] is not None else 50
        race_starts = row[7] if row[7] is not None else 0
        wins = row[8] if row[8] is not None else 0
        contract_length = row[9] if row[9] is not None else 2
        driver = Driver(
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
        drivers.append(driver)
        driver_map[driver.name] = driver
    return drivers, driver_map


def load_teams(cursor, start_year: int, driver_map: Dict[str, Driver]) -> List[Team]:
    cursor.execute("PRAGMA table_info(teams)")
    team_columns = {row[1] for row in cursor.fetchall()}
    has_car_speed = "car_speed" in team_columns
    has_workforce = "workforce" in team_columns
    has_title_sponsor_name = "title_sponsor_name" in team_columns
    has_title_sponsor_yearly = "title_sponsor_yearly" in team_columns
    has_title_sponsor_contract_length = "title_sponsor_contract_length" in team_columns
    has_other_sponsorship_yearly = "other_sponsorship_yearly" in team_columns
    has_engine_supplier_name = "engine_supplier_name" in team_columns
    has_engine_supplier_deal = "engine_supplier_deal" in team_columns
    has_engine_supplier_yearly_cost = "engine_supplier_yearly_cost" in team_columns
    has_tyre_supplier_name = "tyre_supplier_name" in team_columns
    has_tyre_supplier_deal = "tyre_supplier_deal" in team_columns
    has_tyre_supplier_yearly_cost = "tyre_supplier_yearly_cost" in team_columns
    has_fuel_supplier_name = "fuel_supplier_name" in team_columns
    has_fuel_supplier_deal = "fuel_supplier_deal" in team_columns
    has_fuel_supplier_yearly_cost = "fuel_supplier_yearly_cost" in team_columns
    car_speed_expr = "car_speed" if has_car_speed else "50"
    workforce_expr = "workforce" if has_workforce else "0"
    title_sponsor_name_expr = "title_sponsor_name" if has_title_sponsor_name else "NULL"
    title_sponsor_yearly_expr = "title_sponsor_yearly" if has_title_sponsor_yearly else "0"
    title_sponsor_contract_length_expr = "title_sponsor_contract_length" if has_title_sponsor_contract_length else "0"
    other_sponsorship_yearly_expr = "other_sponsorship_yearly" if has_other_sponsorship_yearly else "0"
    engine_supplier_name_expr = "engine_supplier_name" if has_engine_supplier_name else "NULL"
    engine_supplier_deal_expr = "engine_supplier_deal" if has_engine_supplier_deal else "NULL"
    engine_supplier_yearly_cost_expr = "engine_supplier_yearly_cost" if has_engine_supplier_yearly_cost else "0"
    tyre_supplier_name_expr = "tyre_supplier_name" if has_tyre_supplier_name else "NULL"
    tyre_supplier_deal_expr = "tyre_supplier_deal" if has_tyre_supplier_deal else "NULL"
    tyre_supplier_yearly_cost_expr = "tyre_supplier_yearly_cost" if has_tyre_supplier_yearly_cost else "0"
    fuel_supplier_name_expr = "fuel_supplier_name" if has_fuel_supplier_name else "NULL"
    fuel_supplier_deal_expr = "fuel_supplier_deal" if has_fuel_supplier_deal else "NULL"
    fuel_supplier_yearly_cost_expr = "fuel_supplier_yearly_cost" if has_fuel_supplier_yearly_cost else "0"

    cursor.execute(
        f"SELECT id, name, country, driver1_name, driver2_name, balance, facilities, {car_speed_expr} AS car_speed, {workforce_expr} AS workforce, "
        f"{title_sponsor_name_expr} AS title_sponsor_name, {title_sponsor_yearly_expr} AS title_sponsor_yearly, {title_sponsor_contract_length_expr} AS title_sponsor_contract_length, {other_sponsorship_yearly_expr} AS other_sponsorship_yearly, "
        f"{engine_supplier_name_expr} AS engine_supplier_name, {engine_supplier_deal_expr} AS engine_supplier_deal, {engine_supplier_yearly_cost_expr} AS engine_supplier_yearly_cost, "
        f"{tyre_supplier_name_expr} AS tyre_supplier_name, {tyre_supplier_deal_expr} AS tyre_supplier_deal, {tyre_supplier_yearly_cost_expr} AS tyre_supplier_yearly_cost, "
        f"{fuel_supplier_name_expr} AS fuel_supplier_name, {fuel_supplier_deal_expr} AS fuel_supplier_deal, {fuel_supplier_yearly_cost_expr} AS fuel_supplier_yearly_cost "
        "FROM teams WHERE start_year = ? OR start_year = 0 ORDER BY id ASC",
        (start_year,),
    )
    teams: List[Team] = []
    for row in cursor.fetchall():
        team = Team(
            id=row[0],
            name=row[1],
            country=row[2],
            balance=row[5],
            facilities=row[6],
            car_speed=row[7] if row[7] is not None else 50,
            workforce=row[8] if row[8] is not None else 0,
            title_sponsor_name=row[9] if row[9] is not None else None,
            title_sponsor_yearly=row[10] if row[10] is not None else 0,
            title_sponsor_contract_length=row[11] if row[11] is not None else 0,
            other_sponsorship_yearly=row[12] if row[12] is not None else 0,
            engine_supplier_name=row[13] if row[13] is not None else None,
            engine_supplier_deal=row[14] if row[14] is not None else None,
            engine_supplier_yearly_cost=row[15] if row[15] is not None else 0,
            tyre_supplier_name=row[16] if row[16] is not None else None,
            tyre_supplier_deal=row[17] if row[17] is not None else None,
            tyre_supplier_yearly_cost=row[18] if row[18] is not None else 0,
            fuel_supplier_name=row[19] if row[19] is not None else None,
            fuel_supplier_deal=row[20] if row[20] is not None else None,
            fuel_supplier_yearly_cost=row[21] if row[21] is not None else 0,
        )

        d1_name = row[3]
        d2_name = row[4]
        if d1_name and d1_name in driver_map:
            d1 = driver_map[d1_name]
            team.driver1_id = d1.id
            d1.team_id = team.id
            d1.role = DriverRole.DRIVER_1
        if d2_name and d2_name in driver_map:
            d2 = driver_map[d2_name]
            team.driver2_id = d2.id
            d2.team_id = team.id
            d2.role = DriverRole.DRIVER_2
        teams.append(team)
    return teams


def load_technical_directors(
    cursor, start_year: int, teams: List[Team], include: bool
) -> List[TechnicalDirector]:
    technical_directors: List[TechnicalDirector] = []
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='technical_directors'")
        has_td_table = cursor.fetchone() is not None
        if has_td_table:
            cursor.execute(
                "SELECT id, name, country, age, skill, contract_length, salary, team_name "
                "FROM technical_directors WHERE start_year = ? OR start_year = 0",
                (start_year,),
            )
            rows = cursor.fetchall()
            team_by_name = {t.name: t for t in teams}
            for td_id, td_name, td_country, td_age, td_skill, td_contract_length, td_salary, team_name in rows:
                team = team_by_name.get(team_name)
                if team:
                    team.technical_director_id = td_id
                if include:
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
    return technical_directors


def load_commercial_managers(
    cursor, start_year: int, teams: List[Team], include: bool
) -> List[CommercialManager]:
    commercial_managers: List[CommercialManager] = []
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commercial_managers'")
        has_cm_table = cursor.fetchone() is not None
        if has_cm_table:
            cursor.execute(
                "SELECT id, name, country, age, skill, contract_length, salary, team_name "
                "FROM commercial_managers WHERE start_year = ? OR start_year = 0",
                (start_year,),
            )
            rows = cursor.fetchall()
            team_by_name = {t.name: t for t in teams}
            for cm_id, cm_name, cm_country, cm_age, cm_skill, cm_contract_length, cm_salary, team_name in rows:
                team = team_by_name.get(team_name)
                if team:
                    team.commercial_manager_id = cm_id
                if include:
                    commercial_managers.append(
                        CommercialManager(
                            id=cm_id,
                            name=cm_name,
                            country=cm_country,
                            age=cm_age,
                            skill=cm_skill,
                            contract_length=cm_contract_length if cm_contract_length is not None else 0,
                            salary=cm_salary if cm_salary is not None else 0,
                            team_id=team.id if team else None,
                        )
                    )
    except Exception as e:
        print(f"Error linking commercial managers: {e}")
    return commercial_managers


def load_title_sponsors(cursor, start_year: int, include: bool) -> List[TitleSponsor]:
    title_sponsors: List[TitleSponsor] = []
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='title_sponsors'")
        has_table = cursor.fetchone() is not None
        if has_table and include:
            cursor.execute(
                "SELECT id, name, wealth, start_year FROM title_sponsors "
                "WHERE start_year = ? OR start_year = 0 ORDER BY id ASC",
                (start_year,),
            )
            title_sponsors = [
                TitleSponsor(
                    id=row[0],
                    name=row[1],
                    wealth=row[2] if row[2] is not None else 0,
                    start_year=row[3] if row[3] is not None else 0,
                )
                for row in cursor.fetchall()
            ]
    except Exception as e:
        print(f"Error loading title sponsors: {e}")
    return title_sponsors


def load_engine_suppliers(cursor, start_year: int, include: bool) -> List[EngineSupplier]:
    engine_suppliers: List[EngineSupplier] = []
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='engine_suppliers'")
        has_table = cursor.fetchone() is not None
        if has_table and include:
            cursor.execute(
                "SELECT id, name, country, resources, power, start_year FROM engine_suppliers "
                "WHERE start_year = ? OR start_year = 0 ORDER BY id ASC",
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
                for row in cursor.fetchall()
            ]
    except Exception as e:
        print(f"Error loading engine suppliers: {e}")
    return engine_suppliers


def load_tyre_suppliers(cursor, start_year: int, include: bool) -> List[TyreSupplier]:
    tyre_suppliers: List[TyreSupplier] = []
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tyre_suppliers'")
        has_table = cursor.fetchone() is not None
        if has_table and include:
            cursor.execute(
                "SELECT id, name, country, wear, grip, start_year FROM tyre_suppliers "
                "WHERE start_year = ? OR start_year = 0 ORDER BY id ASC",
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
                for row in cursor.fetchall()
            ]
    except Exception as e:
        print(f"Error loading tyre suppliers: {e}")
    return tyre_suppliers


def load_fuel_suppliers(cursor, start_year: int, include: bool) -> List[FuelSupplier]:
    fuel_suppliers: List[FuelSupplier] = []
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fuel_suppliers'")
        has_table = cursor.fetchone() is not None
        if has_table and include:
            cursor.execute(
                "SELECT id, name, country, resources, r_and_d, start_year FROM fuel_suppliers "
                "WHERE start_year = ? OR start_year = 0 ORDER BY id ASC",
                (start_year,),
            )
            fuel_suppliers = [
                FuelSupplier(
                    id=row[0],
                    name=row[1],
                    country=row[2] if row[2] is not None else "",
                    resources=row[3] if row[3] is not None else 0,
                    r_and_d=row[4] if row[4] is not None else 0,
                    start_year=row[5] if row[5] is not None else 0,
                )
                for row in cursor.fetchall()
            ]
    except Exception as e:
        print(f"Error loading fuel suppliers: {e}")
    return fuel_suppliers


def load_events(cursor, start_year: int) -> List[Event]:
    try:
        cursor.execute("SELECT name, week, type FROM calendar WHERE year = ? ORDER BY week ASC", (start_year,))
        return [Event(name=row[0], week=row[1], type=EventType(row[2])) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error loading calendar: {e}")
        return []


def load_circuits(cursor) -> List[Circuit]:
    try:
        cursor.execute(
            "SELECT id, name, country, location, laps, base_laptime_ms, length_km, overtaking_delta, power_factor, track_map_path FROM circuits"
        )
        return [
            Circuit(
                id=row[0],
                name=row[1],
                country=row[2],
                location=row[3],
                laps=row[4],
                base_laptime_ms=row[5],
                length_km=row[6],
                overtaking_delta=row[7],
                power_factor=row[8],
                track_map_path=row[9],
            )
            for row in cursor.fetchall()
        ]
    except Exception as e:
        print(f"Error loading circuits: {e}")
        return []
