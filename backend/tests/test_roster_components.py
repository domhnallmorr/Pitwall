import sqlite3

from app.core.roster_components import load_teams
from tools.seed_schema import create_schema


def test_load_teams_reads_factory_size_department_and_commercial_staff_columns():
    conn = sqlite3.connect(":memory:")
    create_schema(conn)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO teams (
            start_year, name, country, driver1_name, driver2_name, balance, facilities,
            factory_size, car_speed, design_staff, engineering_staff, mechanics_staff, workforce, commercial_staff
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (0, "Warrick", "United Kingdom", None, None, 4_700_000, 90, 4, 80, 63, 61, 58, 182, 60),
    )
    conn.commit()

    teams = load_teams(cursor, 1998, {})

    assert len(teams) == 1
    assert teams[0].name == "Warrick"
    assert teams[0].factory_size == 4
    assert teams[0].design_staff == 63
    assert teams[0].engineering_staff == 61
    assert teams[0].mechanics_staff == 58
    assert teams[0].workforce == 182
    assert teams[0].commercial_staff == 60
