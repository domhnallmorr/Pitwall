from app.core.db import get_connection
from app.models.driver import Driver
from app.models.team import Team
from app.models.enums import DriverRole
from app.models.calendar import Event, EventType
from typing import List, Tuple
from app.models.circuit import Circuit

def load_roster(year: int = 0) -> Tuple[List[Team], List[Driver], int, List[Event], List[Circuit]]:
    """
    Loads teams, drivers, calendar, and circuits.
    Returns: (Teams, Drivers, StartYear, Events, Circuits)
    """
    conn = get_connection()
    c = conn.cursor()

    # 1. Start Year
    if year == 0:
        c.execute("SELECT value FROM metadata WHERE key='start_year'")
        result = c.fetchone()
        start_year = int(result[0]) if result else 1998
    else:
        start_year = year

    # 2. Drivers
    # Allow loading drivers assigned to specific year OR default (0)
    c.execute("PRAGMA table_info(drivers)")
    driver_columns = {row[1] for row in c.fetchall()}
    has_speed = "speed" in driver_columns
    has_race_starts = "race_starts" in driver_columns
    has_wins = "wins" in driver_columns

    speed_expr = "speed" if has_speed else "50"
    race_starts_expr = "race_starts" if has_race_starts else "0"
    wins_expr = "wins" if has_wins else "0"
    c.execute(
        f'SELECT id, name, age, country, wage, pay_driver, {speed_expr} AS speed, {race_starts_expr} AS race_starts, {wins_expr} AS wins '
        'FROM drivers WHERE start_year = ? OR start_year = 0 ORDER BY id ASC',
        (start_year,),
    )
    drivers = []
    driver_map = {} # Name -> ID mapping for assigning to teams
    for row in c.fetchall():
        speed = row[6] if row[6] is not None else 50
        race_starts = row[7] if row[7] is not None else 0
        wins = row[8] if row[8] is not None else 0
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
        )
        drivers.append(d)
        driver_map[d.name] = d

    # 3. Teams
    # Link drivers to teams using the map
    c.execute("PRAGMA table_info(teams)")
    team_columns = {row[1] for row in c.fetchall()}
    has_car_speed = "car_speed" in team_columns

    if has_car_speed:
        c.execute(
            'SELECT id, name, country, driver1_name, driver2_name, balance, facilities, car_speed FROM teams WHERE start_year = ? OR start_year = 0 ORDER BY id ASC',
            (start_year,),
        )
    else:
        c.execute(
            'SELECT id, name, country, driver1_name, driver2_name, balance, facilities FROM teams WHERE start_year = ? OR start_year = 0 ORDER BY id ASC',
            (start_year,),
        )
    teams = []
    for row in c.fetchall():
        car_speed = row[7] if has_car_speed and row[7] is not None else 50
        t = Team(id=row[0], name=row[1], country=row[2], balance=row[5], facilities=row[6], car_speed=car_speed)
        
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

    # 4. Load Calendar
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

    # 5. Load Circuits
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
    return teams, drivers, start_year, events, circuits
