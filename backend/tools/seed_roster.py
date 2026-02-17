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
            car_speed INTEGER DEFAULT 50
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

    teams_data_with_speed = [(*t, team_speeds.get(t[1], 50)) for t in teams_data]
    c.executemany(
        'INSERT INTO teams (start_year, name, country, driver1_name, driver2_name, balance, facilities, car_speed) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        teams_data_with_speed
    )
    
    # Metadata
    c.execute('INSERT OR IGNORE INTO metadata (key, value) VALUES (?, ?)', ('start_year', '1998'))

    conn.commit()
    print("Database seeded successfully.")

if __name__ == "__main__":
    conn = init_db()
    seed_data(conn)
    conn.close()
