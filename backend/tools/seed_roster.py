import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'roster.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create Tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            country TEXT,
            start_year INTEGER DEFAULT 0 -- 0 represents 'default'
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
    
    conn.commit()
    return conn

def seed_data(conn):
    c = conn.cursor()
    
    # Check if data exists
    c.execute('SELECT count(*) FROM drivers')
    if c.fetchone()[0] > 0:
        print("Data already exists, skipping seed.")
        return

    drivers_data = [
        (0, "John Newhouse", 27, "Canada"),
        (0, "Henrik Friedrich", 31, "Germany"),
        (0, "Marco Schneider", 29, "Germany"),
        (0, "Evan Irving", 33, "United Kingdom"),
        (0, "Fabrizio Giorgetti", 25, "Italy"),
        (0, "Andreas Wurst", 24, "Austria"),
        (0, "Daniel Caldwell", 27, "United Kingdom"),
        (0, "Mikko Hanninen", 30, "Finland"),
        (0, "Donovan Upland", 38, "United Kingdom"),
        (0, "Roland Schneider", 23, "Germany"),
        (0, "Alexis Perrin", 32, "France"),
        (0, "Luca Treno", 24, "Italy"),
        (0, "Julien Alesso", 34, "France"),
        (0, "Jimmy Hobart", 34, "United Kingdom"),
        (0, "Pablo Dinez", 28, "Brazil"),
        (0, "Mikko Salmi", 32, "Finland"),
        (0, "Rodrigo Barros", 26, "Brazil"),
        (0, "Lars Nielsen", 25, "Denmark"),
        (0, "Roberto Rossi", 26, "Brazil"),
        (0, "Toshiro Tanaka", 24, "Japan"),
        (0, "Kazuki Nakamura", 27, "Japan"),
        (0, "Eduardo Torres", 20, "Argentina"),
    ]

    c.executemany('INSERT INTO drivers (start_year, name, age, country) VALUES (?, ?, ?, ?)', drivers_data)

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

    conn.commit()
    print("Database seeded successfully.")

if __name__ == "__main__":
    conn = init_db()
    seed_data(conn)
    conn.close()
