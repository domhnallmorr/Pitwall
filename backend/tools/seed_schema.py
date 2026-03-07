import os
import sqlite3


def create_schema(conn):
    c = conn.cursor()

    # Create Tables
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            country TEXT,
            start_year INTEGER DEFAULT 0,
            wage INTEGER DEFAULT 0,
            pay_driver INTEGER DEFAULT 0,
            contract_length INTEGER DEFAULT 2,
            speed INTEGER DEFAULT 50,
            race_starts INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0
        )
    '''
    )

    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT,
            driver1_name TEXT,
            driver2_name TEXT,
            start_year INTEGER DEFAULT 0,
            balance INTEGER DEFAULT 0,
            facilities INTEGER DEFAULT 0,
            car_speed INTEGER DEFAULT 50,
            workforce INTEGER DEFAULT 0,
            title_sponsor_name TEXT,
            title_sponsor_yearly INTEGER DEFAULT 0,
            other_sponsorship_yearly INTEGER DEFAULT 0,
            engine_supplier_name TEXT,
            engine_supplier_deal TEXT,
            engine_supplier_yearly_cost INTEGER DEFAULT 0,
            tyre_supplier_name TEXT,
            tyre_supplier_deal TEXT,
            tyre_supplier_yearly_cost INTEGER DEFAULT 0,
            fuel_supplier_name TEXT,
            fuel_supplier_deal TEXT,
            fuel_supplier_yearly_cost INTEGER DEFAULT 0
        )
    '''
    )

    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS technical_directors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT,
            age INTEGER,
            skill INTEGER DEFAULT 50,
            contract_length INTEGER DEFAULT 0,
            salary INTEGER DEFAULT 0,
            team_name TEXT,
            start_year INTEGER DEFAULT 0
        )
    '''
    )

    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS commercial_managers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            skill INTEGER DEFAULT 50,
            contract_length INTEGER DEFAULT 0,
            salary INTEGER DEFAULT 0,
            team_name TEXT,
            start_year INTEGER DEFAULT 0
        )
    '''
    )

    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS title_sponsors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            wealth INTEGER DEFAULT 0,
            start_year INTEGER DEFAULT 0
        )
    '''
    )

    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS engine_suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT,
            resources INTEGER DEFAULT 0,
            power INTEGER DEFAULT 0,
            start_year INTEGER DEFAULT 0
        )
    '''
    )

    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS tyre_suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT,
            wear INTEGER DEFAULT 0,
            grip INTEGER DEFAULT 0,
            start_year INTEGER DEFAULT 0
        )
    '''
    )

    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS fuel_suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT,
            resources INTEGER DEFAULT 0,
            r_and_d INTEGER DEFAULT 0,
            start_year INTEGER DEFAULT 0
        )
    '''
    )

    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    '''
    )

    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            week INTEGER,
            name TEXT,
            type TEXT
        )
    '''
    )

    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS circuits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            country TEXT,
            location TEXT,
            laps INTEGER,
            base_laptime_ms INTEGER,
            length_km REAL,
            overtaking_delta INTEGER,
            power_factor INTEGER,
            track_map_path TEXT
        )
    '''
    )

    # Backwards-compatible migration for existing DBs.
    c.execute("PRAGMA table_info(drivers)")
    driver_columns = {row[1] for row in c.fetchall()}
    if "speed" not in driver_columns:
        c.execute("ALTER TABLE drivers ADD COLUMN speed INTEGER DEFAULT 50")
    if "contract_length" not in driver_columns:
        c.execute("ALTER TABLE drivers ADD COLUMN contract_length INTEGER DEFAULT 2")
    if "race_starts" not in driver_columns:
        c.execute("ALTER TABLE drivers ADD COLUMN race_starts INTEGER DEFAULT 0")
    if "wins" not in driver_columns:
        c.execute("ALTER TABLE drivers ADD COLUMN wins INTEGER DEFAULT 0")

    c.execute("PRAGMA table_info(teams)")
    team_columns = {row[1] for row in c.fetchall()}
    if "car_speed" not in team_columns:
        c.execute("ALTER TABLE teams ADD COLUMN car_speed INTEGER DEFAULT 50")
    if "workforce" not in team_columns:
        c.execute("ALTER TABLE teams ADD COLUMN workforce INTEGER DEFAULT 0")
    if "title_sponsor_name" not in team_columns:
        c.execute("ALTER TABLE teams ADD COLUMN title_sponsor_name TEXT")
    if "title_sponsor_yearly" not in team_columns:
        c.execute("ALTER TABLE teams ADD COLUMN title_sponsor_yearly INTEGER DEFAULT 0")
    if "other_sponsorship_yearly" not in team_columns:
        c.execute("ALTER TABLE teams ADD COLUMN other_sponsorship_yearly INTEGER DEFAULT 0")
    if "engine_supplier_name" not in team_columns:
        c.execute("ALTER TABLE teams ADD COLUMN engine_supplier_name TEXT")
    if "engine_supplier_deal" not in team_columns:
        c.execute("ALTER TABLE teams ADD COLUMN engine_supplier_deal TEXT")
    if "engine_supplier_yearly_cost" not in team_columns:
        c.execute("ALTER TABLE teams ADD COLUMN engine_supplier_yearly_cost INTEGER DEFAULT 0")
    if "tyre_supplier_name" not in team_columns:
        c.execute("ALTER TABLE teams ADD COLUMN tyre_supplier_name TEXT")
    if "tyre_supplier_deal" not in team_columns:
        c.execute("ALTER TABLE teams ADD COLUMN tyre_supplier_deal TEXT")
    if "tyre_supplier_yearly_cost" not in team_columns:
        c.execute("ALTER TABLE teams ADD COLUMN tyre_supplier_yearly_cost INTEGER DEFAULT 0")
    if "fuel_supplier_name" not in team_columns:
        c.execute("ALTER TABLE teams ADD COLUMN fuel_supplier_name TEXT")
    if "fuel_supplier_deal" not in team_columns:
        c.execute("ALTER TABLE teams ADD COLUMN fuel_supplier_deal TEXT")
    if "fuel_supplier_yearly_cost" not in team_columns:
        c.execute("ALTER TABLE teams ADD COLUMN fuel_supplier_yearly_cost INTEGER DEFAULT 0")

    c.execute("PRAGMA table_info(technical_directors)")
    td_columns = {row[1] for row in c.fetchall()}
    if "skill" not in td_columns:
        c.execute("ALTER TABLE technical_directors ADD COLUMN skill INTEGER DEFAULT 50")
    if "country" not in td_columns:
        c.execute("ALTER TABLE technical_directors ADD COLUMN country TEXT")
    if "contract_length" not in td_columns:
        c.execute("ALTER TABLE technical_directors ADD COLUMN contract_length INTEGER DEFAULT 0")
    if "salary" not in td_columns:
        c.execute("ALTER TABLE technical_directors ADD COLUMN salary INTEGER DEFAULT 0")
    if "team_name" not in td_columns:
        c.execute("ALTER TABLE technical_directors ADD COLUMN team_name TEXT")
    if "start_year" not in td_columns:
        c.execute("ALTER TABLE technical_directors ADD COLUMN start_year INTEGER DEFAULT 0")

    c.execute("PRAGMA table_info(commercial_managers)")
    cm_columns = {row[1] for row in c.fetchall()}
    if "country" not in cm_columns:
        c.execute("ALTER TABLE commercial_managers ADD COLUMN country TEXT")
    if "skill" not in cm_columns:
        c.execute("ALTER TABLE commercial_managers ADD COLUMN skill INTEGER DEFAULT 50")
    if "age" not in cm_columns:
        c.execute("ALTER TABLE commercial_managers ADD COLUMN age INTEGER")
    if "contract_length" not in cm_columns:
        c.execute("ALTER TABLE commercial_managers ADD COLUMN contract_length INTEGER DEFAULT 0")
    if "salary" not in cm_columns:
        c.execute("ALTER TABLE commercial_managers ADD COLUMN salary INTEGER DEFAULT 0")
    if "team_name" not in cm_columns:
        c.execute("ALTER TABLE commercial_managers ADD COLUMN team_name TEXT")
    if "start_year" not in cm_columns:
        c.execute("ALTER TABLE commercial_managers ADD COLUMN start_year INTEGER DEFAULT 0")

    c.execute("PRAGMA table_info(title_sponsors)")
    sponsor_columns = {row[1] for row in c.fetchall()}
    if "wealth" not in sponsor_columns:
        c.execute("ALTER TABLE title_sponsors ADD COLUMN wealth INTEGER DEFAULT 0")
    if "start_year" not in sponsor_columns:
        c.execute("ALTER TABLE title_sponsors ADD COLUMN start_year INTEGER DEFAULT 0")

    c.execute("PRAGMA table_info(engine_suppliers)")
    engine_columns = {row[1] for row in c.fetchall()}
    if "country" not in engine_columns:
        c.execute("ALTER TABLE engine_suppliers ADD COLUMN country TEXT")
    if "resources" not in engine_columns:
        c.execute("ALTER TABLE engine_suppliers ADD COLUMN resources INTEGER DEFAULT 0")
    if "power" not in engine_columns:
        c.execute("ALTER TABLE engine_suppliers ADD COLUMN power INTEGER DEFAULT 0")
    if "start_year" not in engine_columns:
        c.execute("ALTER TABLE engine_suppliers ADD COLUMN start_year INTEGER DEFAULT 0")

    c.execute("PRAGMA table_info(tyre_suppliers)")
    tyre_columns = {row[1] for row in c.fetchall()}
    if "country" not in tyre_columns:
        c.execute("ALTER TABLE tyre_suppliers ADD COLUMN country TEXT")
    if "wear" not in tyre_columns:
        c.execute("ALTER TABLE tyre_suppliers ADD COLUMN wear INTEGER DEFAULT 0")
    if "grip" not in tyre_columns:
        c.execute("ALTER TABLE tyre_suppliers ADD COLUMN grip INTEGER DEFAULT 0")
    if "start_year" not in tyre_columns:
        c.execute("ALTER TABLE tyre_suppliers ADD COLUMN start_year INTEGER DEFAULT 0")

    c.execute("PRAGMA table_info(fuel_suppliers)")
    fuel_columns = {row[1] for row in c.fetchall()}
    if "country" not in fuel_columns:
        c.execute("ALTER TABLE fuel_suppliers ADD COLUMN country TEXT")
    if "resources" not in fuel_columns:
        c.execute("ALTER TABLE fuel_suppliers ADD COLUMN resources INTEGER DEFAULT 0")
    if "r_and_d" not in fuel_columns:
        c.execute("ALTER TABLE fuel_suppliers ADD COLUMN r_and_d INTEGER DEFAULT 0")
    if "start_year" not in fuel_columns:
        c.execute("ALTER TABLE fuel_suppliers ADD COLUMN start_year INTEGER DEFAULT 0")

    conn.commit()


def init_db(db_path: str):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    create_schema(conn)
    return conn
