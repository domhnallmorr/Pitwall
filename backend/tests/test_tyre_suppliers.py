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
def test_load_roster_can_include_tyre_suppliers(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    result = load_roster(year=1998, include_tyre_suppliers=True)
    assert len(result) == 6
    teams, drivers, year, events, circuits, tyre_suppliers = result

    assert year == 1998
    assert len(tyre_suppliers) == 2

    greatday = next(t for t in tyre_suppliers if t.name == "Greatday")
    spanrock = next(t for t in tyre_suppliers if t.name == "Spanrock")

    assert greatday.country == "USA"
    assert greatday.wear == 60
    assert greatday.grip == 80
    assert spanrock.country == "Japan"
    assert spanrock.wear == 80
    assert spanrock.grip == 70


@patch("app.core.roster.get_connection")
def test_load_roster_can_include_all_sets_including_tyres(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    result = load_roster(
        year=1998,
        include_technical_directors=True,
        include_commercial_managers=True,
        include_title_sponsors=True,
        include_engine_suppliers=True,
        include_tyre_suppliers=True,
    )

    assert len(result) == 10
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
    ) = result
    assert len(technical_directors) == 20
    assert len(commercial_managers) == 18
    assert len(title_sponsors) == 14
    assert len(engine_suppliers) == 7
    assert len(tyre_suppliers) == 2


@patch("app.core.roster.get_connection")
def test_team_records_include_seeded_tyre_supplier_deals(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    teams, *_ = load_roster(year=1998)
    warrick = next(t for t in teams if t.name == "Warrick")
    benedetti = next(t for t in teams if t.name == "Benedetti")
    tarnwell = next(t for t in teams if t.name == "Tarnwell")

    assert warrick.tyre_supplier_name == "Greatday"
    assert warrick.tyre_supplier_deal == "partner"
    assert warrick.tyre_supplier_yearly_cost == 0

    assert benedetti.tyre_supplier_name == "Spanrock"
    assert benedetti.tyre_supplier_deal == "partner"
    assert benedetti.tyre_supplier_yearly_cost == 0

    assert tarnwell.tyre_supplier_name == "Greatday"
    assert tarnwell.tyre_supplier_deal == "customer"
    assert tarnwell.tyre_supplier_yearly_cost == 450_000
