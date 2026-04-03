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
def test_load_roster_can_include_fuel_suppliers(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    result = load_roster(year=1998, include_fuel_suppliers=True)
    assert len(result) == 6
    teams, drivers, year, events, circuits, fuel_suppliers = result

    assert year == 1998
    assert len(fuel_suppliers) == 8

    shale = next(f for f in fuel_suppliers if f.name == "Shale")
    imp = next(f for f in fuel_suppliers if f.name == "Imp")

    assert shale.country == "United Kingdom"
    assert shale.resources == 5
    assert shale.r_and_d == 4
    assert imp.country == "France"
    assert imp.resources == 1
    assert imp.r_and_d == 5


@patch("app.core.roster.get_connection")
def test_load_roster_can_include_all_sets_including_fuel(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    result = load_roster(
        year=1998,
        include_technical_directors=True,
        include_commercial_managers=True,
        include_title_sponsors=True,
        include_engine_suppliers=True,
        include_tyre_suppliers=True,
        include_fuel_suppliers=True,
    )

    assert len(result) == 11
    (
        teams,
        drivers,
        year,
        events,
        circuits,
        technical_directors,
        commercial_managers,
        title_sponsors,
        engine_suppliers,
        tyre_suppliers,
        fuel_suppliers,
    ) = result
    assert len(technical_directors) == 20
    assert len(commercial_managers) == 18
    assert len(title_sponsors) == 14
    assert len(engine_suppliers) == 7
    assert len(tyre_suppliers) == 2
    assert len(fuel_suppliers) == 8


@patch("app.core.roster.get_connection")
def test_team_records_include_seeded_fuel_supplier_deals(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    teams, *_ = load_roster(year=1998)
    warrick = next(t for t in teams if t.name == "Warrick")
    ferano = next(t for t in teams if t.name == "Ferano")
    schweizer = next(t for t in teams if t.name == "Schweizer")

    assert warrick.fuel_supplier_name == "Brasoil"
    assert warrick.fuel_supplier_deal == "partner"
    assert warrick.fuel_supplier_yearly_cost == 150_000

    assert ferano.fuel_supplier_name == "Shale"
    assert ferano.fuel_supplier_deal == "works"
    assert ferano.fuel_supplier_yearly_cost == -3_000_000

    assert schweizer.fuel_supplier_name == "Shale"
    assert schweizer.fuel_supplier_deal == "customer"
    assert schweizer.fuel_supplier_yearly_cost == 350_000
