import sqlite3
from unittest.mock import patch

from app.core.roster import load_roster
from tools.seed_roster import create_schema, seed_data


def create_seeded_db():
    conn = sqlite3.connect(":memory:")
    create_schema(conn)
    seed_data(conn)
    return conn


@patch("app.core.roster.get_connection")
def test_load_roster_can_include_engine_suppliers(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    result = load_roster(year=1998, include_engine_suppliers=True)
    assert len(result) == 6
    teams, drivers, year, events, circuits, engine_suppliers = result

    assert year == 1998
    assert len(engine_suppliers) == 7

    marcado = next(e for e in engine_suppliers if e.name == "Marcado")
    frost = next(e for e in engine_suppliers if e.name == "Frost")
    assert marcado.country == "Germany"
    assert marcado.resources == 92
    assert marcado.power == 80
    assert frost.country == "USA"
    assert frost.resources == 65
    assert frost.power == 38


@patch("app.core.roster.get_connection")
def test_team_records_include_seeded_engine_supplier_deals(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    teams, *_ = load_roster(year=1998)
    warrick = next(t for t in teams if t.name == "Warrick")
    schweizer = next(t for t in teams if t.name == "Schweizer")

    assert warrick.engine_supplier_name == "Mechatron"
    assert warrick.engine_supplier_deal == "customer"
    assert warrick.engine_supplier_yearly_cost == 4_500_000
    assert schweizer.engine_supplier_name == "Ferano"
    assert schweizer.engine_supplier_deal == "customer"
    assert schweizer.engine_supplier_yearly_cost == 9_500_000


@patch("app.core.roster.get_connection")
def test_load_roster_can_include_all_staff_sponsor_and_engine_sets(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    result = load_roster(
        year=1998,
        include_technical_directors=True,
        include_commercial_managers=True,
        include_title_sponsors=True,
        include_engine_suppliers=True,
    )

    assert len(result) == 9
    teams, drivers, year, events, circuits, technical_directors, commercial_managers, title_sponsors, engine_suppliers = result
    assert len(technical_directors) == 20
    assert len(commercial_managers) == 18
    assert len(title_sponsors) == 11
    assert len(engine_suppliers) == 7
