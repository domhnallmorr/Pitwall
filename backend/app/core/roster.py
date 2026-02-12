from app.core.db import get_connection
from app.models.driver import Driver
from app.models.team import Team
from app.models.enums import DriverRole
from typing import List, Tuple

def load_roster(year: int = 0) -> Tuple[List[Team], List[Driver]]:
    """
    Loads teams and drivers for a specific start year (0 for default).
    Returns a tuple of (List[Team], List[Driver]).
    """
    conn = get_connection()
    c = conn.cursor()

    # Load Drivers
    c.execute('SELECT id, name, age, country FROM drivers WHERE start_year = ?', (year,))
    drivers = []
    driver_map = {} # Name -> ID mapping for assigning to teams
    for row in c.fetchall():
        d = Driver(id=row[0], name=row[1], age=row[2], country=row[3])
        drivers.append(d)
        driver_map[d.name] = d

    # Load Teams
    c.execute('SELECT id, name, country, driver1_name, driver2_name FROM teams WHERE start_year = ?', (year,))
    teams = []
    for row in c.fetchall():
        t = Team(id=row[0], name=row[1], country=row[2])
        
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

    conn.close()
    return teams, drivers
