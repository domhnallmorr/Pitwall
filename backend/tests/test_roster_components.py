import sqlite3

from app.core.roster_components import load_teams
from tools.seed_schema import create_schema


def test_load_teams_reads_commercial_staff_column():
    conn = sqlite3.connect(":memory:")
    create_schema(conn)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO teams (
            start_year, name, country, driver1_name, driver2_name, balance, facilities,
            car_speed, workforce, commercial_staff
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (0, "Warrick", "United Kingdom", None, None, 4_700_000, 90, 80, 190, 60),
    )
    conn.commit()

    teams = load_teams(cursor, 1998, {})

    assert len(teams) == 1
    assert teams[0].name == "Warrick"
    assert teams[0].workforce == 190
    assert teams[0].commercial_staff == 60
