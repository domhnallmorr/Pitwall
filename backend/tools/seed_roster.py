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
            pay_driver INTEGER DEFAULT 0
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT,
            driver1_name TEXT, 
            driver2_name TEXT,
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
    
    conn.commit()

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    create_schema(conn)
    return conn

def seed_data(conn):
    c = conn.cursor()
    
    # ... (Drivers/Teams logic omitted for brevity, keeping existing structure via tool)    
    # Double check if circuits exist
    c.execute('SELECT count(*) FROM circuits')
    circuits_exist = c.fetchone()[0] > 0
    
    if not circuits_exist:
        print("Seeding Circuits...")
        circuits_data = [
            ("Albert Park", "Australia", "Melbourne", 58, 84000, 5.303, 1200, 6, None),
            ("Interlagos", "Brazil", "Sao Paulo", 72, 72000, 4.292, 900, 7, None),
            ("Autodromo Oscar Alfredo Galvez", "Argentina", "Buenos Aries", 72, 80000, 4.259, 1300, 3, None),
            ("Autodromo Enzo e Dino Ferrari", "San Marino", "Imola", 62, 81000, 4.933, 1800, 3, None),
            ("Circuit de Barcelona-Catalunya", "Spain", "Barcelona", 66, 75000, 4.728, 1800, 5, None)
        ]
        
        c.executemany('''
            INSERT INTO circuits (name, country, location, laps, base_laptime_ms, length_km, overtaking_delta, power_factor, track_map_path) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', circuits_data)
        conn.commit()
        print("Circuits seeded.")

    # Check if data exists
    c.execute('SELECT count(*) FROM drivers')

    drivers_exist = c.fetchone()[0] > 0
    
    if drivers_exist:
        print("Driver data already exists. Checking metadata...")
        # Ensure metadata exists even if drivers do
        c.execute('INSERT OR IGNORE INTO metadata (key, value) VALUES (?, ?)', ('start_year', '1998'))
        
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
    ]

    c.executemany('INSERT INTO drivers (start_year, name, age, country, wage, pay_driver) VALUES (?, ?, ?, ?, ?, ?)', drivers_data)

    teams_data = [
        (0, "Warrick", "United Kingdom", "John Newhouse", "Henrik Friedrich"),
        (0, "Ferano", "Italy", "Marco Schneider", "Evan Irving"),
        (0, "Benedetti", "Italy", "Fabrizio Giorgetti", "Andreas Wurst"),
        (0, "McAlister", "United Kingdom", "Mikko Hanninen", "Daniel Caldwell"),
        (0, "Joyce", "Ireland", "Donovan Upland", "Roland Schneider"),
        (0, "Pascal", "France", "Alexis Perrin", "Luca Treno"),
        (0, "Schweizer", "Switzerland", "Julien Alesso", "Jimmy Hobart"),
        (0, "Swords", "United Kingdom", "Pablo Dinez", "Mikko Salmi"),
        (0, "Strathmore", "United Kingdom", "Rodrigo Barros", "Lars Nielsen"),
        (0, "Tarnwell", "United Kingdom", "Roberto Rossi", "Toshiro Tanaka"),
        (0, "Marchetti", "Italy", "Kazuki Nakamura", "Eduardo Torres"),
    ]

    c.executemany('INSERT INTO teams (start_year, name, country, driver1_name, driver2_name) VALUES (?, ?, ?, ?, ?)', teams_data)
    
    # Metadata
    c.execute('INSERT OR IGNORE INTO metadata (key, value) VALUES (?, ?)', ('start_year', '1998'))

    conn.commit()
    print("Database seeded successfully.")

if __name__ == "__main__":
    conn = init_db()
    seed_data(conn)
    conn.close()
