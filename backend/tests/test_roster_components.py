import sqlite3

from app.core.roster_components import load_drivers, load_teams, load_tyre_suppliers
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


def test_load_drivers_reads_consistency_and_qualifying_columns():
    conn = sqlite3.connect(":memory:")
    create_schema(conn)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO drivers (
            start_year, name, age, country, wage, pay_driver, contract_length, speed, consistency, qualifying
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (0, "Marco Schneider", 29, "Germany", 24_000_000, 0, 4, 98, 100, 5),
    )
    conn.commit()

    drivers, driver_map = load_drivers(cursor, 1998)

    assert len(drivers) == 1
    assert driver_map["Marco Schneider"].speed == 98
    assert driver_map["Marco Schneider"].consistency == 100
    assert driver_map["Marco Schneider"].qualifying == 5


def test_load_tyre_suppliers_reads_supplier_development_attributes():
    conn = sqlite3.connect(":memory:")
    create_schema(conn)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tyre_suppliers (
            start_year, name, country, wear, grip, resources, innovation, reliability
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (0, "Greatday", "USA", 60, 80, 88, 82, 90),
    )
    conn.commit()

    tyre_suppliers = load_tyre_suppliers(cursor, 1998, include=True)

    assert len(tyre_suppliers) == 1
    assert tyre_suppliers[0].resources == 88
    assert tyre_suppliers[0].innovation == 82
    assert tyre_suppliers[0].reliability == 90
