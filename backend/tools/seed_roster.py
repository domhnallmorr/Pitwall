import sqlite3
import os

try:
    from tools.seed_payloads import (
        CALENDAR_EVENTS_BASE,
        CALENDAR_EVENTS_EXTRA_TESTS,
        COMMERCIAL_MANAGERS_DATA,
        DRIVER_CONTRACT_LENGTHS,
        DRIVER_RACE_STARTS,
        DRIVER_SPEEDS,
        DRIVER_WINS,
        DRIVERS_DATA,
        ENGINE_SUPPLIERS_DATA,
        FUEL_SUPPLIERS_DATA,
        FUTURE_DRIVERS_DATA,
        REQUIRED_CIRCUITS,
        TECHNICAL_DIRECTORS_DATA,
        TEAM_PRINCIPALS_DATA,
        TEAMS_DATA,
        TEAM_BALANCES,
        TEAM_BUILDS_OWN_ENGINE,
        TEAM_ENGINE_SUPPLIERS,
        TEAM_ENGINE_SUPPLIER_CONTRACT_LENGTHS,
        TEAM_OTHER_SPONSORSHIP,
        TEAM_SPEEDS,
        TEAM_TITLE_SPONSORS,
        TEAM_TITLE_SPONSOR_CONTRACT_LENGTHS,
        TEAM_TYRE_SUPPLIERS,
        TEAM_TYRE_SUPPLIER_CONTRACT_LENGTHS,
        TEAM_FUEL_SUPPLIERS,
        TEAM_WORKFORCE,
        TITLE_SPONSORS_DATA,
        TYRE_SUPPLIERS_DATA,
    )
    from tools.seed_schema import create_schema, init_db
except ModuleNotFoundError:
    from seed_payloads import (  # type: ignore
        CALENDAR_EVENTS_BASE,
        CALENDAR_EVENTS_EXTRA_TESTS,
        COMMERCIAL_MANAGERS_DATA,
        DRIVER_CONTRACT_LENGTHS,
        DRIVER_RACE_STARTS,
        DRIVER_SPEEDS,
        DRIVER_WINS,
        DRIVERS_DATA,
        ENGINE_SUPPLIERS_DATA,
        FUEL_SUPPLIERS_DATA,
        FUTURE_DRIVERS_DATA,
        REQUIRED_CIRCUITS,
        TECHNICAL_DIRECTORS_DATA,
        TEAM_PRINCIPALS_DATA,
        TEAMS_DATA,
        TEAM_BALANCES,
        TEAM_BUILDS_OWN_ENGINE,
        TEAM_ENGINE_SUPPLIERS,
        TEAM_ENGINE_SUPPLIER_CONTRACT_LENGTHS,
        TEAM_OTHER_SPONSORSHIP,
        TEAM_SPEEDS,
        TEAM_TITLE_SPONSORS,
        TEAM_TITLE_SPONSOR_CONTRACT_LENGTHS,
        TEAM_TYRE_SUPPLIERS,
        TEAM_TYRE_SUPPLIER_CONTRACT_LENGTHS,
        TEAM_FUEL_SUPPLIERS,
        TEAM_WORKFORCE,
        TITLE_SPONSORS_DATA,
        TYRE_SUPPLIERS_DATA,
    )
    from seed_schema import create_schema, init_db  # type: ignore

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'roster.db')


def sync_seed_table_names(conn, table_name, seed_rows):
    c = conn.cursor()
    names_by_year = {}
    for row in seed_rows:
        start_year = row[0]
        name = row[1]
        names_by_year.setdefault(start_year, set()).add(name)

    for start_year, allowed_names in names_by_year.items():
        placeholders = ", ".join("?" for _ in allowed_names)
        query = (
            f"DELETE FROM {table_name} "
            f"WHERE start_year = ? AND name NOT IN ({placeholders})"
        )
        c.execute(query, [start_year, *sorted(allowed_names)])


def seed_data(conn):
    c = conn.cursor()
    c.execute('SELECT name FROM circuits')
    existing_circuit_names = {row[0] for row in c.fetchall()}
    circuits_to_insert = [row for row in REQUIRED_CIRCUITS if row[0] not in existing_circuit_names]

    if circuits_to_insert:
        print(f"Seeding {len(circuits_to_insert)} missing circuit(s)...")
        c.executemany('''
            INSERT INTO circuits (name, country, location, laps, base_laptime_ms, length_km, overtaking_delta, power_factor, track_map_path) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', circuits_to_insert)
        conn.commit()
        print("Circuits seeded.")

    # Check if data exists
    c.execute('SELECT count(*) FROM drivers')

    drivers_exist = c.fetchone()[0] > 0
    
    if drivers_exist:
        print("Driver data already exists. Checking metadata...")
        # Ensure metadata exists even if drivers do
        c.execute('INSERT OR IGNORE INTO metadata (key, value) VALUES (?, ?)', ('start_year', '1998'))
        # Ensure future-season drivers exist for existing DBs
        future_drivers_data = FUTURE_DRIVERS_DATA
        c.execute('SELECT name, start_year FROM drivers')
        existing_driver_keys = {(row[0], row[1]) for row in c.fetchall()}
        drivers_to_insert = [d for d in future_drivers_data if (d[1], d[0]) not in existing_driver_keys]
        if drivers_to_insert:
            print(f"Seeding {len(drivers_to_insert)} future driver(s)...")
            drivers_to_insert_with_attrs = [
                (*d, DRIVER_CONTRACT_LENGTHS.get(d[1], 0 if d[0] > 0 else 2), DRIVER_SPEEDS.get(d[1], 50), DRIVER_RACE_STARTS.get(d[1], 0), DRIVER_WINS.get(d[1], 0))
                for d in drivers_to_insert
            ]
            c.executemany(
                'INSERT INTO drivers (start_year, name, age, country, wage, pay_driver, contract_length, speed, race_starts, wins) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                drivers_to_insert_with_attrs
            )
            conn.commit()

        sync_seed_table_names(conn, "drivers", DRIVERS_DATA)

        # Always refresh speed values for known names in existing DBs.
        c.executemany(
            'UPDATE drivers SET speed = ? WHERE name = ?',
            [(speed, name) for name, speed in DRIVER_SPEEDS.items()]
        )
        c.executemany(
            'UPDATE drivers SET race_starts = ? WHERE name = ?',
            [(starts, name) for name, starts in DRIVER_RACE_STARTS.items()]
        )
        c.executemany(
            'UPDATE drivers SET wins = ? WHERE name = ?',
            [(wins, name) for name, wins in DRIVER_WINS.items()]
        )
        c.executemany(
            'UPDATE drivers SET contract_length = ? WHERE name = ?',
            [(length, name) for name, length in DRIVER_CONTRACT_LENGTHS.items()]
        )
        c.executemany(
            'UPDATE teams SET car_speed = ? WHERE name = ?',
            [(speed, name) for name, speed in TEAM_SPEEDS.items()]
        )
        c.executemany(
            'UPDATE teams SET workforce = ? WHERE name = ?',
            [(workforce, name) for name, workforce in TEAM_WORKFORCE.items()]
        )
        c.executemany(
            'UPDATE teams SET balance = ? WHERE name = ? AND start_year = 0',
            [(balance, name) for name, balance in TEAM_BALANCES.items()]
        )
        c.executemany(
            'UPDATE teams SET title_sponsor_name = ?, title_sponsor_yearly = ?, title_sponsor_contract_length = ? WHERE name = ?',
            [
                (s[0], s[1], TEAM_TITLE_SPONSOR_CONTRACT_LENGTHS.get(team_name, 0), team_name)
                for team_name, s in TEAM_TITLE_SPONSORS.items()
            ]
        )
        c.executemany(
            'UPDATE teams SET other_sponsorship_yearly = ? WHERE name = ?',
            [(amount, name) for name, amount in TEAM_OTHER_SPONSORSHIP.items()]
        )
        c.executemany(
            'UPDATE teams SET engine_supplier_name = ?, engine_supplier_deal = ?, engine_supplier_yearly_cost = ?, engine_supplier_contract_length = ?, builds_own_engine = ? WHERE name = ?',
            [
                (s[0], s[1], s[2], TEAM_ENGINE_SUPPLIER_CONTRACT_LENGTHS.get(team_name, 0), TEAM_BUILDS_OWN_ENGINE.get(team_name, 0), team_name)
                for team_name, s in TEAM_ENGINE_SUPPLIERS.items()
            ]
        )
        c.executemany(
            'UPDATE teams SET tyre_supplier_name = ?, tyre_supplier_deal = ?, tyre_supplier_yearly_cost = ?, tyre_supplier_contract_length = ? WHERE name = ?',
            [
                (s[0], s[1], s[2], TEAM_TYRE_SUPPLIER_CONTRACT_LENGTHS.get(team_name, 0), team_name)
                for team_name, s in TEAM_TYRE_SUPPLIERS.items()
            ]
        )
        c.executemany(
            'UPDATE teams SET fuel_supplier_name = ?, fuel_supplier_deal = ?, fuel_supplier_yearly_cost = ? WHERE name = ?',
            [(s[0], s[1], s[2], team_name) for team_name, s in TEAM_FUEL_SUPPLIERS.items()]
        )

        c.execute('SELECT name, start_year FROM technical_directors')
        existing_td_keys = {(row[0], row[1]) for row in c.fetchall()}
        tds_to_insert = [td for td in TECHNICAL_DIRECTORS_DATA if (td[1], td[0]) not in existing_td_keys]
        if tds_to_insert:
            c.executemany(
                'INSERT INTO technical_directors (start_year, name, country, age, skill, contract_length, salary, team_name) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                tds_to_insert,
            )

        c.executemany(
            'UPDATE technical_directors SET country = ?, age = ?, skill = ?, contract_length = ?, salary = ?, team_name = ? WHERE name = ? AND start_year = ?',
            [(td[2], td[3], td[4], td[5], td[6], td[7], td[1], td[0]) for td in TECHNICAL_DIRECTORS_DATA],
        )
        sync_seed_table_names(conn, "technical_directors", TECHNICAL_DIRECTORS_DATA)

        c.execute('SELECT name, start_year FROM team_principals')
        existing_tp_keys = {(row[0], row[1]) for row in c.fetchall()}
        principals_to_insert = [tp for tp in TEAM_PRINCIPALS_DATA if (tp[1], tp[0]) not in existing_tp_keys]
        if principals_to_insert:
            c.executemany(
                'INSERT INTO team_principals (start_year, name, country, age, skill, contract_length, team_name, owns_team) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                principals_to_insert,
            )
        c.executemany(
            'UPDATE team_principals SET country = ?, age = ?, skill = ?, contract_length = ?, team_name = ?, owns_team = ? WHERE name = ? AND start_year = ?',
            [(tp[2], tp[3], tp[4], tp[5], tp[6], tp[7], tp[1], tp[0]) for tp in TEAM_PRINCIPALS_DATA],
        )
        sync_seed_table_names(conn, "team_principals", TEAM_PRINCIPALS_DATA)

        c.execute('SELECT name, start_year FROM commercial_managers')
        existing_cm_keys = {(row[0], row[1]) for row in c.fetchall()}
        cms_to_insert = [cm for cm in COMMERCIAL_MANAGERS_DATA if (cm[1], cm[0]) not in existing_cm_keys]
        if cms_to_insert:
            c.executemany(
                'INSERT INTO commercial_managers (start_year, name, country, age, skill, contract_length, salary, team_name) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                cms_to_insert,
            )

        c.executemany(
            'UPDATE commercial_managers SET country = ?, age = ?, skill = ?, contract_length = ?, salary = ?, team_name = ? WHERE name = ? AND start_year = ?',
            [(cm[2], cm[3], cm[4], cm[5], cm[6], cm[7], cm[1], cm[0]) for cm in COMMERCIAL_MANAGERS_DATA],
        )

        c.execute('SELECT name, start_year FROM title_sponsors')
        existing_sponsor_keys = {(row[0], row[1]) for row in c.fetchall()}
        sponsors_to_insert = [s for s in TITLE_SPONSORS_DATA if (s[1], s[0]) not in existing_sponsor_keys]
        if sponsors_to_insert:
            c.executemany(
                'INSERT INTO title_sponsors (start_year, name, wealth) VALUES (?, ?, ?)',
                sponsors_to_insert,
            )
        c.executemany(
            'UPDATE title_sponsors SET wealth = ? WHERE name = ? AND start_year = ?',
            [(s[2], s[1], s[0]) for s in TITLE_SPONSORS_DATA],
        )

        c.execute('SELECT name, start_year FROM engine_suppliers')
        existing_engine_keys = {(row[0], row[1]) for row in c.fetchall()}
        engines_to_insert = [e for e in ENGINE_SUPPLIERS_DATA if (e[1], e[0]) not in existing_engine_keys]
        if engines_to_insert:
            c.executemany(
                'INSERT INTO engine_suppliers (start_year, name, country, resources, power) VALUES (?, ?, ?, ?, ?)',
                engines_to_insert,
            )
        c.executemany(
            'UPDATE engine_suppliers SET country = ?, resources = ?, power = ? WHERE name = ? AND start_year = ?',
            [(e[2], e[3], e[4], e[1], e[0]) for e in ENGINE_SUPPLIERS_DATA],
        )

        c.execute('SELECT name, start_year FROM tyre_suppliers')
        existing_tyre_keys = {(row[0], row[1]) for row in c.fetchall()}
        tyres_to_insert = [t for t in TYRE_SUPPLIERS_DATA if (t[1], t[0]) not in existing_tyre_keys]
        if tyres_to_insert:
            c.executemany(
                'INSERT INTO tyre_suppliers (start_year, name, country, wear, grip) VALUES (?, ?, ?, ?, ?)',
                tyres_to_insert,
            )
        c.executemany(
            'UPDATE tyre_suppliers SET country = ?, wear = ?, grip = ? WHERE name = ? AND start_year = ?',
            [(t[2], t[3], t[4], t[1], t[0]) for t in TYRE_SUPPLIERS_DATA],
        )
        c.execute('SELECT name, start_year FROM fuel_suppliers')
        existing_fuel_keys = {(row[0], row[1]) for row in c.fetchall()}
        fuels_to_insert = [f for f in FUEL_SUPPLIERS_DATA if (f[1], f[0]) not in existing_fuel_keys]
        if fuels_to_insert:
            c.executemany(
                'INSERT INTO fuel_suppliers (start_year, name, country, resources, r_and_d) VALUES (?, ?, ?, ?, ?)',
                fuels_to_insert,
            )
        c.executemany(
            'UPDATE fuel_suppliers SET country = ?, resources = ?, r_and_d = ? WHERE name = ? AND start_year = ?',
            [(f[2], f[3], f[4], f[1], f[0]) for f in FUEL_SUPPLIERS_DATA],
        )
        conn.commit()
        
    # Check if Calendar exists
    c.execute('SELECT count(*) FROM calendar')
    calendar_exists = c.fetchone()[0] > 0
    
    if not calendar_exists:
        print("Seeding Calendar...")
        calendar_events = list(CALENDAR_EVENTS_BASE)
        calendar_events.extend(CALENDAR_EVENTS_EXTRA_TESTS)
        
        c.executemany('INSERT INTO calendar (year, week, name, type) VALUES (?, ?, ?, ?)', calendar_events)
        conn.commit()
        print("Calendar seeded.")

    # Always ensure technical directors are seeded and up to date.
    c.execute('SELECT name, start_year FROM technical_directors')
    existing_td_keys = {(row[0], row[1]) for row in c.fetchall()}
    tds_to_insert = [td for td in TECHNICAL_DIRECTORS_DATA if (td[1], td[0]) not in existing_td_keys]
    if tds_to_insert:
        c.executemany(
            'INSERT INTO technical_directors (start_year, name, country, age, skill, contract_length, salary, team_name) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            tds_to_insert,
        )
    c.executemany(
        'UPDATE technical_directors SET country = ?, age = ?, skill = ?, contract_length = ?, salary = ?, team_name = ? WHERE name = ? AND start_year = ?',
        [(td[2], td[3], td[4], td[5], td[6], td[7], td[1], td[0]) for td in TECHNICAL_DIRECTORS_DATA],
    )
    sync_seed_table_names(conn, "technical_directors", TECHNICAL_DIRECTORS_DATA)
    c.execute('SELECT name, start_year FROM team_principals')
    existing_tp_keys = {(row[0], row[1]) for row in c.fetchall()}
    principals_to_insert = [tp for tp in TEAM_PRINCIPALS_DATA if (tp[1], tp[0]) not in existing_tp_keys]
    if principals_to_insert:
        c.executemany(
            'INSERT INTO team_principals (start_year, name, country, age, skill, contract_length, team_name, owns_team) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            principals_to_insert,
        )
    c.executemany(
        'UPDATE team_principals SET country = ?, age = ?, skill = ?, contract_length = ?, team_name = ?, owns_team = ? WHERE name = ? AND start_year = ?',
        [(tp[2], tp[3], tp[4], tp[5], tp[6], tp[7], tp[1], tp[0]) for tp in TEAM_PRINCIPALS_DATA],
    )
    sync_seed_table_names(conn, "team_principals", TEAM_PRINCIPALS_DATA)
    c.execute('SELECT name, start_year FROM commercial_managers')
    existing_cm_keys = {(row[0], row[1]) for row in c.fetchall()}
    cms_to_insert = [cm for cm in COMMERCIAL_MANAGERS_DATA if (cm[1], cm[0]) not in existing_cm_keys]
    if cms_to_insert:
        c.executemany(
            'INSERT INTO commercial_managers (start_year, name, country, age, skill, contract_length, salary, team_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            cms_to_insert,
        )
    c.executemany(
        'UPDATE commercial_managers SET country = ?, age = ?, skill = ?, contract_length = ?, salary = ?, team_name = ? WHERE name = ? AND start_year = ?',
        [(cm[2], cm[3], cm[4], cm[5], cm[6], cm[7], cm[1], cm[0]) for cm in COMMERCIAL_MANAGERS_DATA],
    )
    c.execute('SELECT name, start_year FROM title_sponsors')
    existing_sponsor_keys = {(row[0], row[1]) for row in c.fetchall()}
    sponsors_to_insert = [s for s in TITLE_SPONSORS_DATA if (s[1], s[0]) not in existing_sponsor_keys]
    if sponsors_to_insert:
        c.executemany(
            'INSERT INTO title_sponsors (start_year, name, wealth) VALUES (?, ?, ?)',
            sponsors_to_insert,
        )
    c.executemany(
        'UPDATE title_sponsors SET wealth = ? WHERE name = ? AND start_year = ?',
        [(s[2], s[1], s[0]) for s in TITLE_SPONSORS_DATA],
    )
    c.executemany(
        'UPDATE teams SET title_sponsor_name = ?, title_sponsor_yearly = ?, title_sponsor_contract_length = ? WHERE name = ?',
        [
            (s[0], s[1], TEAM_TITLE_SPONSOR_CONTRACT_LENGTHS.get(team_name, 0), team_name)
            for team_name, s in TEAM_TITLE_SPONSORS.items()
        ]
    )
    c.executemany(
        'UPDATE teams SET other_sponsorship_yearly = ? WHERE name = ?',
        [(amount, name) for name, amount in TEAM_OTHER_SPONSORSHIP.items()]
    )
    c.executemany(
        'UPDATE teams SET engine_supplier_name = ?, engine_supplier_deal = ?, engine_supplier_yearly_cost = ?, engine_supplier_contract_length = ?, builds_own_engine = ? WHERE name = ?',
        [
            (s[0], s[1], s[2], TEAM_ENGINE_SUPPLIER_CONTRACT_LENGTHS.get(team_name, 0), TEAM_BUILDS_OWN_ENGINE.get(team_name, 0), team_name)
            for team_name, s in TEAM_ENGINE_SUPPLIERS.items()
        ]
    )
    c.executemany(
        'UPDATE teams SET tyre_supplier_name = ?, tyre_supplier_deal = ?, tyre_supplier_yearly_cost = ?, tyre_supplier_contract_length = ? WHERE name = ?',
        [
            (s[0], s[1], s[2], TEAM_TYRE_SUPPLIER_CONTRACT_LENGTHS.get(team_name, 0), team_name)
            for team_name, s in TEAM_TYRE_SUPPLIERS.items()
        ]
    )
    c.executemany(
        'UPDATE teams SET fuel_supplier_name = ?, fuel_supplier_deal = ?, fuel_supplier_yearly_cost = ? WHERE name = ?',
        [(s[0], s[1], s[2], team_name) for team_name, s in TEAM_FUEL_SUPPLIERS.items()]
    )
    c.execute('SELECT name, start_year FROM engine_suppliers')
    existing_engine_keys = {(row[0], row[1]) for row in c.fetchall()}
    engines_to_insert = [e for e in ENGINE_SUPPLIERS_DATA if (e[1], e[0]) not in existing_engine_keys]
    if engines_to_insert:
        c.executemany(
            'INSERT INTO engine_suppliers (start_year, name, country, resources, power) VALUES (?, ?, ?, ?, ?)',
            engines_to_insert,
        )
    c.executemany(
        'UPDATE engine_suppliers SET country = ?, resources = ?, power = ? WHERE name = ? AND start_year = ?',
        [(e[2], e[3], e[4], e[1], e[0]) for e in ENGINE_SUPPLIERS_DATA],
    )
    c.execute('SELECT name, start_year FROM tyre_suppliers')
    existing_tyre_keys = {(row[0], row[1]) for row in c.fetchall()}
    tyres_to_insert = [t for t in TYRE_SUPPLIERS_DATA if (t[1], t[0]) not in existing_tyre_keys]
    if tyres_to_insert:
        c.executemany(
            'INSERT INTO tyre_suppliers (start_year, name, country, wear, grip) VALUES (?, ?, ?, ?, ?)',
            tyres_to_insert,
        )
    c.executemany(
        'UPDATE tyre_suppliers SET country = ?, wear = ?, grip = ? WHERE name = ? AND start_year = ?',
        [(t[2], t[3], t[4], t[1], t[0]) for t in TYRE_SUPPLIERS_DATA],
    )
    c.execute('SELECT name, start_year FROM fuel_suppliers')
    existing_fuel_keys = {(row[0], row[1]) for row in c.fetchall()}
    fuels_to_insert = [f for f in FUEL_SUPPLIERS_DATA if (f[1], f[0]) not in existing_fuel_keys]
    if fuels_to_insert:
        c.executemany(
            'INSERT INTO fuel_suppliers (start_year, name, country, resources, r_and_d) VALUES (?, ?, ?, ?, ?)',
            fuels_to_insert,
        )
    c.executemany(
        'UPDATE fuel_suppliers SET country = ?, resources = ?, r_and_d = ? WHERE name = ? AND start_year = ?',
        [(f[2], f[3], f[4], f[1], f[0]) for f in FUEL_SUPPLIERS_DATA],
    )
    conn.commit()
        
    if drivers_exist:
        return

    drivers_data = DRIVERS_DATA

    drivers_data_with_attrs = [
        (*d, DRIVER_CONTRACT_LENGTHS.get(d[1], 0 if d[0] > 0 else 2), DRIVER_SPEEDS.get(d[1], 50), DRIVER_RACE_STARTS.get(d[1], 0), DRIVER_WINS.get(d[1], 0))
        for d in drivers_data
    ]
    c.executemany(
        'INSERT INTO drivers (start_year, name, age, country, wage, pay_driver, contract_length, speed, race_starts, wins) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        drivers_data_with_attrs
    )

    teams_data = TEAMS_DATA

    teams_data_with_attrs = [(*t, TEAM_SPEEDS.get(t[1], 50), TEAM_WORKFORCE.get(t[1], 0)) for t in teams_data]
    teams_data_with_attrs = [
        (
            *row,
            TEAM_TITLE_SPONSORS.get(row[1], (None, 0))[0],
            TEAM_TITLE_SPONSORS.get(row[1], (None, 0))[1],
            TEAM_TITLE_SPONSOR_CONTRACT_LENGTHS.get(row[1], 0),
            TEAM_OTHER_SPONSORSHIP.get(row[1], 0),
        )
        for row in teams_data_with_attrs
    ]
    c.executemany(
        'INSERT INTO teams (start_year, name, country, driver1_name, driver2_name, balance, facilities, car_speed, workforce, title_sponsor_name, title_sponsor_yearly, title_sponsor_contract_length, other_sponsorship_yearly) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        teams_data_with_attrs
    )
    c.executemany(
        'UPDATE teams SET engine_supplier_name = ?, engine_supplier_deal = ?, engine_supplier_yearly_cost = ?, engine_supplier_contract_length = ?, builds_own_engine = ? WHERE name = ?',
        [
            (s[0], s[1], s[2], TEAM_ENGINE_SUPPLIER_CONTRACT_LENGTHS.get(team_name, 0), TEAM_BUILDS_OWN_ENGINE.get(team_name, 0), team_name)
            for team_name, s in TEAM_ENGINE_SUPPLIERS.items()
        ]
    )
    c.executemany(
        'UPDATE teams SET tyre_supplier_name = ?, tyre_supplier_deal = ?, tyre_supplier_yearly_cost = ?, tyre_supplier_contract_length = ? WHERE name = ?',
        [
            (s[0], s[1], s[2], TEAM_TYRE_SUPPLIER_CONTRACT_LENGTHS.get(team_name, 0), team_name)
            for team_name, s in TEAM_TYRE_SUPPLIERS.items()
        ]
    )
    c.executemany(
        'UPDATE teams SET fuel_supplier_name = ?, fuel_supplier_deal = ?, fuel_supplier_yearly_cost = ? WHERE name = ?',
        [(s[0], s[1], s[2], team_name) for team_name, s in TEAM_FUEL_SUPPLIERS.items()]
    )
    
    # Metadata
    c.execute('INSERT OR IGNORE INTO metadata (key, value) VALUES (?, ?)', ('start_year', '1998'))

    conn.commit()
    print("Database seeded successfully.")

if __name__ == "__main__":
    conn = init_db(DB_PATH)
    seed_data(conn)
    conn.close()

