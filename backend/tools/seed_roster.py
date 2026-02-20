import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'roster.db')

def create_schema(conn):
    c = conn.cursor()
    
    # Create Tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            country TEXT,
            start_year INTEGER DEFAULT 0,
            wage INTEGER DEFAULT 0,
            pay_driver INTEGER DEFAULT 0,
            speed INTEGER DEFAULT 50,
            race_starts INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0
        )
    ''')
    
    c.execute('''
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
            title_sponsor_yearly INTEGER DEFAULT 0
        )
    ''')

    c.execute('''
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
    ''')

    c.execute('''
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
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS title_sponsors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            wealth INTEGER DEFAULT 0,
            start_year INTEGER DEFAULT 0
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            week INTEGER,
            name TEXT,
            type TEXT
        )
    ''')

    c.execute('''
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
    ''')

    # Backwards-compatible migration for existing DBs.
    c.execute("PRAGMA table_info(drivers)")
    driver_columns = {row[1] for row in c.fetchall()}
    if "speed" not in driver_columns:
        c.execute("ALTER TABLE drivers ADD COLUMN speed INTEGER DEFAULT 50")
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
    
    conn.commit()

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    create_schema(conn)
    return conn

def seed_data(conn):
    c = conn.cursor()
    driver_speeds = {
        "John Newhouse": 84,
        "Henrik Friedrich": 72,
        "Marco Schneider": 98,
        "Evan Irving": 75,
        "Fabrizio Giorgetti": 70,
        "Andreas Wurst": 71,
        "Daniel Caldwell": 77,
        "Mikko Hanninen": 87,
        "Donovan Upland": 78,
        "Roland Schneider": 70,
        "Alexis Perrin": 59,
        "Luca Treno": 76,
        "Julien Alesso": 75,
        "Jimmy Hobart": 69,
        "Pablo Dinez": 55,
        "Mikko Salmi": 68,
        "Rodrigo Barros": 77,
        "Lars Nielsen": 45,
        "Roberto Rossi": 21,
        "Toshiro Tanaka": 55,
        "Kazuki Nakamura": 39,
        "Eduardo Torres": 29,
        "Javier Perez Mendoza": 79,
        "Leonardo Badei": 59,
        "Jan van der Veen": 66,
        "Pablo del Rosario": 65,
        "Stefan Sarrien": 64,
        "Jorn Maller": 48,
        "Luisano Burci": 61,
        "Jean-Claude Boulain": 54,
        "Alex Zanetto": 55,
        "Marco Genoa": 64,
        "Rico Zanda": 66,
        "Jamie Brenton": 80,
        "Nico Heidmann": 74,
        "Gustav Mazzane": 52,
    }
    driver_race_starts = {
        "John Newhouse": 33,
        "Henrik Friedrich": 65,
        "Marco Schneider": 101,
        "Evan Irving": 65,
        "Fabrizio Giorgetti": 25,
        "Andreas Wurst": 3,
        "Daniel Caldwell": 58,
        "Mikko Hanninen": 96,
        "Donovan Upland": 83,
        "Roland Schneider": 17,
        "Alexis Perrin": 59,
        "Luca Treno": 13,
        "Julien Alesso": 167,
        "Jimmy Hobart": 112,
        "Pablo Dinez": 50,
        "Mikko Salmi": 52,
        "Rodrigo Barros": 81,
        "Lars Nielsen": 17,
        "Roberto Rossi": 16,
        "Toshiro Tanaka": 0,
        "Kazuki Nakamura": 0,
        "Eduardo Torres": 0,
        "Javier Perez Mendoza": 0,
        "Leonardo Badei": 34,
        "Jan van der Veen": 48,
        "Pablo del Rosario": 0,
        "Stefan Sarrien": 0,
        "Jorn Maller": 0,
        "Luisano Burci": 0,
        "Jean-Claude Boulain": 0,
        "Alex Zanetto": 25,
        "Marco Genoa": 0,
        "Rico Zanda": 0,
        "Jamie Brenton": 0,
        "Nico Heidmann": 0,
        "Gustav Mazzane": 0,
    }
    driver_wins = {
        "John Newhouse": 11,
        "Henrik Friedrich": 1,
        "Marco Schneider": 28,
        "Evan Irving": 0,
        "Fabrizio Giorgetti": 0,
        "Andreas Wurst": 0,
        "Daniel Caldwell": 3,
        "Mikko Hanninen": 1,
        "Donovan Upland": 21,
        "Roland Schneider": 0,
        "Alexis Perrin": 1,
        "Luca Treno": 0,
        "Julien Alesso": 1,
        "Jimmy Hobart": 2,
        "Pablo Dinez": 0,
        "Mikko Salmi": 0,
        "Rodrigo Barros": 0,
        "Lars Nielsen": 0,
        "Roberto Rossi": 0,
        "Toshiro Tanaka": 0,
        "Kazuki Nakamura": 0,
        "Eduardo Torres": 0,
        "Javier Perez Mendoza": 0,
        "Leonardo Badei": 0,
        "Jan van der Veen": 0,
        "Pablo del Rosario": 0,
        "Stefan Sarrien": 0,
        "Jorn Maller": 0,
        "Luisano Burci": 0,
        "Jean-Claude Boulain": 0,
        "Alex Zanetto": 0,
        "Marco Genoa": 0,
        "Rico Zanda": 0,
        "Jamie Brenton": 0,
        "Nico Heidmann": 0,
        "Gustav Mazzane": 0,
    }
    team_speeds = {
        "Warrick": 80,
        "Ferano": 84,
        "Benedetti": 74,
        "McAlister": 90,
        "Joyce": 70,
        "Pascal": 60,
        "Schweizer": 70,
        "Swords": 45,
        "Strathmore": 50,
        "Tarnwell": 40,
        "Marchetti": 35,
    }
    team_workforce = {
        "Warrick": 250,
        "Ferano": 230,
        "Benedetti": 190,
        "McAlister": 240,
        "Joyce": 138,
        "Pascal": 110,
        "Schweizer": 180,
        "Swords": 97,
        "Strathmore": 130,
        "Tarnwell": 105,
        "Marchetti": 90,
    }
    team_title_sponsors = {
        "Warrick": ("Windale", 32_500_000),
        "Ferano": ("Marbano", 31_500_000),
        "Benedetti": ("Soft Eight", 26_500_000),
        "McAlister": ("East", 32_000_000),
        "Joyce": ("Barlow & Hunt", 23_500_000),
        "Pascal": ("Gavalon", 25_000_000),
        "Schweizer": ("Yellow Cow", 21_500_000),
        "Swords": ("Dasko", 5_200_000),
        "Strathmore": ("HBRC", 3_800_000),
        "Tarnwell": ("PIKA", 4_000_000),
        "Marchetti": ("Tonometal", 4_400_000),
    }
    technical_directors_data = [
        (0, "Peter Heed", "United Kingdom", 52, 75, 5, 4_800_000, "Warrick"),
        (0, "Rob Brann", "United Kingdom", 48, 90, 3, 2_800_000, "Ferano"),
        (0, "Paddy Simons", "United Kingdom", 45, 80, 3, 2_400_000, "Benedetti"),
        (0, "Aidan Newson", "United Kingdom", 40, 95, 5, 3_200_000, "McAlister"),
        (0, "Gerry Mandarin", "United Kingdom", 47, 62, 1, 800_000, "Joyce"),
        (0, "Bertrand Duvet", "France", 59, 50, 1, 720_000, "Pascal"),
        (0, "Leon Ressner", "Germany", 47, 55, 3, 640_000, "Schweizer"),
        (0, "James Barnwood", "United Kingdom", 52, 78, 1, 2_000_000, "Swords"),
        (0, "Adrian Jenson", "United Kingdom", 51, 35, 1, 560_000, "Strathmore"),
        (0, "Henry Pendleton", "United Kingdom", 54, 45, 1, 480_000, "Tarnwell"),
        (0, "Ginter Brumer", "Austria", 48, 50, 3, 400_000, "Marchetti"),
        (0, "Francis Durney", None, 48, 30, 0, 0, None),
        (0, "Louis Bigoire", None, 38, 32, 0, 0, None),
        (0, "Gianni Tredoni", None, 41, 29, 0, 0, None),
        (0, "Andrew Rennard", None, 47, 42, 0, 0, None),
        (0, "Mike Coughlan", None, 39, 45, 0, 0, None),
        (0, "Mike Gascoyne", None, 35, 70, 0, 0, None),
        (0, "Neil Oatley", None, 44, 60, 0, 0, None),
        (0, "Sergio Rinland", None, 46, 34, 0, 0, None),
        (0, "Aldo Costa", None, 37, 66, 0, 0, None),
    ]
    commercial_managers_data = [
        (0, "Jace Whitman", 29, 70, 5, 360_000, "Warrick"),
        (0, "Silvano Domencari", 33, 90, 5, 560_000, "Ferano"),
        (0, "Dylan Warden", 29, 66, 1, 416_000, "Benedetti"),
        (0, "Emre Sadi", 29, 82, 4, 512_000, "McAlister"),
        (0, "Iain Philbrook", 47, 92, 4, 464_000, "Joyce"),
        (0, "Yann Lamberti", 44, 55, 2, 320_000, "Pascal"),
        (0, "Felix Kessler", 43, 52, 3, 272_000, "Schweizer"),
        (0, "Jodie Olivetti", 56, 40, 1, 176_000, "Swords"),
        (0, "Rory Armstead", 29, 61, 3, 304_000, "Strathmore"),
        (0, "Rufus Marlowing", 42, 42, 1, 80_000, "Tarnwell"),
        (0, "Gianluca Rumiere", 58, 39, 1, 128_000, "Marchetti"),
        (0, "Gaston Seville", 50, 35, 0, 0, None),
        (0, "Miles Galloway", 38, 66, 0, 0, None),
        (0, "Matteo Cusano", 39, 31, 0, 0, None),
        (0, "Ronan Wexton", 41, 46, 0, 0, None),
        (0, "Lars Olsson", 43, 59, 0, 0, None),
        (0, "Hugo Bourdain", 52, 28, 0, 0, None),
        (0, "Matteo Fessari", 45, 60, 0, 0, None),
    ]
    title_sponsors_data = [
        (0, "Windale", 80),
        (0, "Marbano", 99),
        (0, "Soft Eight", 75),
        (0, "East", 90),
        (0, "Barlow & Hunt", 70),
        (0, "Gavalon", 60),
        (0, "Yellow Cow", 99),
        (0, "Dasko", 45),
        (0, "HBRC", 58),
        (0, "PIKA", 28),
        (0, "Tonometal", 25),
    ]
    
    # ... (Drivers/Teams logic omitted for brevity, keeping existing structure via tool)    
    # Ensure required circuits exist (safe for existing DBs).
    required_circuits = [
        ("Albert Park", "Australia", "Melbourne", 58, 84000, 5.303, 1200, 6, None),
        ("Interlagos", "Brazil", "Sao Paulo", 72, 72000, 4.292, 900, 7, None),
        ("Autodromo Oscar Alfredo Galvez", "Argentina", "Buenos Aries", 72, 80000, 4.259, 1300, 3, None),
        ("Autodromo Enzo e Dino Ferrari", "San Marino", "Imola", 62, 81000, 4.933, 1800, 3, None),
        ("Circuit de Barcelona-Catalunya", "Spain", "Barcelona", 66, 75000, 4.728, 1800, 5, None),
        ("Circuit de Monaco", "Monaco", "Monte Carlo", 78, 75000, 3.367, 2000, 1, None),
        ("Circuit Gilles Villeneuve", "Canada", "Montreal", 70, 73000, 4.421, 700, 8, None),
        ("Circuit de Nevers Magny-Cours", "France", "Magny-Cours", 72, 70000, 4.250, 1500, 5, None),
        ("Silverstone Circuit", "United Kingdom", "Silverstone", 60, 79000, 5.140, 900, 7, None),
        ("A1 Ring", "Austria", "Spielberg", 71, 68000, 4.319, 800, 7, None),
        ("Hockenheimring", "Germany", "Hockenheim", 45, 97000, 6.823, 600, 10, None),
        ("Hungaroring", "Hungary", "Budapest", 77, 73000, 3.972, 1900, 2, None),
        ("Circuit de Spa-Francorchamps", "Belgium", "Stavelot", 44, 104000, 6.968, 700, 9, None),
        ("Autodromo Nazionale di Monza", "Italy", "Monza", 53, 80000, 5.770, 700, 10, None),
        ("Nurburgring", "Luxembourg", "Nurburg", 67, 74000, 4.556, 1100, 7, None),
        ("Suzuka Circuit", "Japan", "Suzuka", 53, 90000, 5.860, 1400, 6, None),
    ]
    c.execute('SELECT name FROM circuits')
    existing_circuit_names = {row[0] for row in c.fetchall()}
    circuits_to_insert = [row for row in required_circuits if row[0] not in existing_circuit_names]

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
        future_drivers_data = [
            (1999, "Jamie Brenton", 19, "United Kingdom", 0, 0),
            (1999, "Nico Heidmann", 22, "Germany", 0, 0),
            (1999, "Gustav Mazzane", 24, "Argentina", 0, 1),
        ]
        c.execute('SELECT name, start_year FROM drivers')
        existing_driver_keys = {(row[0], row[1]) for row in c.fetchall()}
        drivers_to_insert = [d for d in future_drivers_data if (d[1], d[0]) not in existing_driver_keys]
        if drivers_to_insert:
            print(f"Seeding {len(drivers_to_insert)} future driver(s)...")
            drivers_to_insert_with_attrs = [
                (*d, driver_speeds.get(d[1], 50), driver_race_starts.get(d[1], 0), driver_wins.get(d[1], 0))
                for d in drivers_to_insert
            ]
            c.executemany(
                'INSERT INTO drivers (start_year, name, age, country, wage, pay_driver, speed, race_starts, wins) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                drivers_to_insert_with_attrs
            )
            conn.commit()

        # Always refresh speed values for known names in existing DBs.
        c.executemany(
            'UPDATE drivers SET speed = ? WHERE name = ?',
            [(speed, name) for name, speed in driver_speeds.items()]
        )
        c.executemany(
            'UPDATE drivers SET race_starts = ? WHERE name = ?',
            [(starts, name) for name, starts in driver_race_starts.items()]
        )
        c.executemany(
            'UPDATE drivers SET wins = ? WHERE name = ?',
            [(wins, name) for name, wins in driver_wins.items()]
        )
        c.executemany(
            'UPDATE teams SET car_speed = ? WHERE name = ?',
            [(speed, name) for name, speed in team_speeds.items()]
        )
        c.executemany(
            'UPDATE teams SET workforce = ? WHERE name = ?',
            [(workforce, name) for name, workforce in team_workforce.items()]
        )
        c.executemany(
            'UPDATE teams SET title_sponsor_name = ?, title_sponsor_yearly = ? WHERE name = ?',
            [(s[0], s[1], team_name) for team_name, s in team_title_sponsors.items()]
        )

        c.execute('SELECT name, start_year FROM technical_directors')
        existing_td_keys = {(row[0], row[1]) for row in c.fetchall()}
        tds_to_insert = [td for td in technical_directors_data if (td[1], td[0]) not in existing_td_keys]
        if tds_to_insert:
            c.executemany(
                'INSERT INTO technical_directors (start_year, name, country, age, skill, contract_length, salary, team_name) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                tds_to_insert,
            )

        c.executemany(
            'UPDATE technical_directors SET country = ?, age = ?, skill = ?, contract_length = ?, salary = ?, team_name = ? WHERE name = ? AND start_year = ?',
            [(td[2], td[3], td[4], td[5], td[6], td[7], td[1], td[0]) for td in technical_directors_data],
        )

        c.execute('SELECT name, start_year FROM commercial_managers')
        existing_cm_keys = {(row[0], row[1]) for row in c.fetchall()}
        cms_to_insert = [cm for cm in commercial_managers_data if (cm[1], cm[0]) not in existing_cm_keys]
        if cms_to_insert:
            c.executemany(
                'INSERT INTO commercial_managers (start_year, name, age, skill, contract_length, salary, team_name) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                cms_to_insert,
            )

        c.executemany(
            'UPDATE commercial_managers SET age = ?, skill = ?, contract_length = ?, salary = ?, team_name = ? WHERE name = ? AND start_year = ?',
            [(cm[2], cm[3], cm[4], cm[5], cm[6], cm[1], cm[0]) for cm in commercial_managers_data],
        )

        c.execute('SELECT name, start_year FROM title_sponsors')
        existing_sponsor_keys = {(row[0], row[1]) for row in c.fetchall()}
        sponsors_to_insert = [s for s in title_sponsors_data if (s[1], s[0]) not in existing_sponsor_keys]
        if sponsors_to_insert:
            c.executemany(
                'INSERT INTO title_sponsors (start_year, name, wealth) VALUES (?, ?, ?)',
                sponsors_to_insert,
            )
        c.executemany(
            'DELETE FROM title_sponsors WHERE start_year = ? AND name = ?',
            [(0, name) for name in ("Bright Shot", "Technonica", "x-plus")],
        )
        c.executemany(
            'UPDATE title_sponsors SET wealth = ? WHERE name = ? AND start_year = ?',
            [(s[2], s[1], s[0]) for s in title_sponsors_data],
        )
        conn.commit()
        
    # Check if Calendar exists
    c.execute('SELECT count(*) FROM calendar')
    calendar_exists = c.fetchone()[0] > 0
    
    if not calendar_exists:
        print("Seeding Calendar...")
        calendar_events = [
            (1998, 5, "Circuit de Barcelona-Catalunya", "TEST"),
            (1998, 7, "Circuit de Barcelona-Catalunya", "TEST"),
            (1998, 10, "Albert Park", "RACE"),
            (1998, 13, "Interlagos", "RACE"),
            (1998, 15, "Autodromo Oscar Alfredo Galvez", "RACE"),
            (1998, 17, "Autodromo Enzo e Dino Ferrari", "RACE"),
            (1998, 19, "Circuit de Barcelona-Catalunya", "RACE"),
            (1998, 21, "Circuit de Monaco", "RACE"),
            (1998, 23, "Circuit Gilles Villeneuve", "RACE"),
            (1998, 26, "Circuit de Nevers Magny-Cours", "RACE"),
            (1998, 28, "Silverstone Circuit", "RACE"),
            (1998, 30, "A1 Ring", "RACE"),
            (1998, 31, "Hockenheimring", "RACE"),
            (1998, 33, "Hungaroring", "RACE"),
            (1998, 35, "Circuit de Spa-Francorchamps", "RACE"),
            (1998, 37, "Autodromo Nazionale di Monza", "RACE"),
            (1998, 39, "Nurburgring", "RACE"),
            (1998, 44, "Suzuka Circuit", "RACE")
            # Testing sessions from user list
            # (1998, 5, "Circuit de Barcelona-Catalunya", "TEST"), # Added above
            # (1998, 7, "Circuit de Barcelona-Catalunya", "TEST"), # Added above
            # (1998, 16, "Circuit de Barcelona-Catalunya", "TEST")
            # ... (truncated for brevity, adding full user list if needed, but starting with requested subset)
        ]
        # Adding the rest of user requested testing sessions for completeness if simple
        more_tests = [
            (1998, 16, "Circuit de Barcelona-Catalunya", "TEST"),
            (1998, 20, "Silverstone Circuit", "TEST"),
            (1998, 25, "Circuit de Nevers Magny-Cours", "TEST"),
            (1998, 29, "Circuit de Barcelona-Catalunya", "TEST"),
            (1998, 34, "Silverstone Circuit", "TEST"),
            (1998, 38, "Circuit de Barcelona-Catalunya", "TEST"),
            (1998, 41, "Circuit de Barcelona-Catalunya", "TEST")
        ]
        calendar_events.extend(more_tests)
        
        c.executemany('INSERT INTO calendar (year, week, name, type) VALUES (?, ?, ?, ?)', calendar_events)
        conn.commit()
        print("Calendar seeded.")

    # Always ensure technical directors are seeded and up to date.
    c.execute('SELECT name, start_year FROM technical_directors')
    existing_td_keys = {(row[0], row[1]) for row in c.fetchall()}
    tds_to_insert = [td for td in technical_directors_data if (td[1], td[0]) not in existing_td_keys]
    if tds_to_insert:
        c.executemany(
            'INSERT INTO technical_directors (start_year, name, country, age, skill, contract_length, salary, team_name) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            tds_to_insert,
        )
    c.executemany(
        'UPDATE technical_directors SET country = ?, age = ?, skill = ?, contract_length = ?, salary = ?, team_name = ? WHERE name = ? AND start_year = ?',
        [(td[2], td[3], td[4], td[5], td[6], td[7], td[1], td[0]) for td in technical_directors_data],
    )
    c.execute('SELECT name, start_year FROM commercial_managers')
    existing_cm_keys = {(row[0], row[1]) for row in c.fetchall()}
    cms_to_insert = [cm for cm in commercial_managers_data if (cm[1], cm[0]) not in existing_cm_keys]
    if cms_to_insert:
        c.executemany(
            'INSERT INTO commercial_managers (start_year, name, age, skill, contract_length, salary, team_name) VALUES (?, ?, ?, ?, ?, ?, ?)',
            cms_to_insert,
        )
    c.executemany(
        'UPDATE commercial_managers SET age = ?, skill = ?, contract_length = ?, salary = ?, team_name = ? WHERE name = ? AND start_year = ?',
        [(cm[2], cm[3], cm[4], cm[5], cm[6], cm[1], cm[0]) for cm in commercial_managers_data],
    )
    c.execute('SELECT name, start_year FROM title_sponsors')
    existing_sponsor_keys = {(row[0], row[1]) for row in c.fetchall()}
    sponsors_to_insert = [s for s in title_sponsors_data if (s[1], s[0]) not in existing_sponsor_keys]
    if sponsors_to_insert:
        c.executemany(
            'INSERT INTO title_sponsors (start_year, name, wealth) VALUES (?, ?, ?)',
            sponsors_to_insert,
        )
    c.executemany(
        'UPDATE title_sponsors SET wealth = ? WHERE name = ? AND start_year = ?',
        [(s[2], s[1], s[0]) for s in title_sponsors_data],
    )
    conn.commit()
        
    if drivers_exist:
        return

    drivers_data = [
        (0, "John Newhouse", 27, "Canada", 9600000, 0),
        (0, "Henrik Friedrich", 31, "Germany", 3200000, 0),
        (0, "Marco Schneider", 29, "Germany", 24000000, 0),
        (0, "Evan Irving", 33, "United Kingdom", 5280000, 0),
        (0, "Fabrizio Giorgetti", 25, "Italy", 2080000, 0),
        (0, "Andreas Wurst", 24, "Austria", 1600000, 0),
        (0, "Daniel Caldwell", 27, "United Kingdom", 3680000, 0),
        (0, "Mikko Hanninen", 30, "Finland", 7200000, 0),
        (0, "Donovan Upland", 38, "United Kingdom", 8000000, 0),
        (0, "Roland Schneider", 23, "Germany", 3200000, 0),
        (0, "Alexis Perrin", 32, "France", 2080000, 0),
        (0, "Luca Treno", 24, "Italy", 1440000, 0),
        (0, "Julien Alesso", 34, "France", 6400000, 0),
        (0, "Jimmy Hobart", 34, "United Kingdom", 3040000, 0),
        (0, "Pablo Dinez", 28, "Brazil", -9600000, 1),
        (0, "Mikko Salmi", 32, "Finland", 1920000, 0),
        (0, "Rodrigo Barros", 26, "Brazil", 4160000, 0),
        (0, "Lars Nielsen", 25, "Denmark", 1280000, 0),
        (0, "Roberto Rossi", 26, "Brazil", -4300000, 1),
        (0, "Toshiro Tanaka", 24, "Japan", -6400000, 1),
        (0, "Kazuki Nakamura", 27, "Japan", -2900000, 1),
        (0, "Eduardo Torres", 20, "Argentina", -3700000, 1),
        (1999, "Jamie Brenton", 19, "United Kingdom", 0, 0),
        (1999, "Nico Heidmann", 22, "Germany", 0, 0),
        (1999, "Gustav Mazzane", 24, "Argentina", 0, 1),
    ]

    drivers_data_with_attrs = [
        (*d, driver_speeds.get(d[1], 50), driver_race_starts.get(d[1], 0), driver_wins.get(d[1], 0))
        for d in drivers_data
    ]
    c.executemany(
        'INSERT INTO drivers (start_year, name, age, country, wage, pay_driver, speed, race_starts, wins) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        drivers_data_with_attrs
    )

    teams_data = [
        (0, "Warrick", "United Kingdom", "John Newhouse", "Henrik Friedrich", 47000000, 75),
        (0, "Ferano", "Italy", "Marco Schneider", "Evan Irving", 56000000, 70),
        (0, "Benedetti", "Italy", "Fabrizio Giorgetti", "Andreas Wurst", 38000000, 70),
        (0, "McAlister", "United Kingdom", "Mikko Hanninen", "Daniel Caldwell", 53000000, 85),
        (0, "Joyce", "Ireland", "Donovan Upland", "Roland Schneider", 28775000, 60),
        (0, "Pascal", "France", "Alexis Perrin", "Luca Treno", 32000000, 55),
        (0, "Schweizer", "Switzerland", "Julien Alesso", "Jimmy Hobart", 26000000, 75),
        (0, "Swords", "United Kingdom", "Pablo Dinez", "Mikko Salmi", 16000000, 40),
        (0, "Strathmore", "United Kingdom", "Rodrigo Barros", "Lars Nielsen", 17000000, 60),
        (0, "Tarnwell", "United Kingdom", "Roberto Rossi", "Toshiro Tanaka", 6600000, 35),
        (0, "Marchetti", "Italy", "Kazuki Nakamura", "Eduardo Torres", 8900000, 18),
    ]

    teams_data_with_attrs = [(*t, team_speeds.get(t[1], 50), team_workforce.get(t[1], 0)) for t in teams_data]
    teams_data_with_attrs = [
        (*row, team_title_sponsors.get(row[1], (None, 0))[0], team_title_sponsors.get(row[1], (None, 0))[1])
        for row in teams_data_with_attrs
    ]
    c.executemany(
        'INSERT INTO teams (start_year, name, country, driver1_name, driver2_name, balance, facilities, car_speed, workforce, title_sponsor_name, title_sponsor_yearly) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        teams_data_with_attrs
    )
    
    # Metadata
    c.execute('INSERT OR IGNORE INTO metadata (key, value) VALUES (?, ?)', ('start_year', '1998'))

    conn.commit()
    print("Database seeded successfully.")

if __name__ == "__main__":
    conn = init_db()
    seed_data(conn)
    conn.close()
