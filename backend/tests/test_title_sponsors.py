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
def test_load_roster_can_include_title_sponsors(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    result = load_roster(year=1998, include_title_sponsors=True)
    assert len(result) == 6
    teams, drivers, year, events, circuits, sponsors = result

    assert year == 1998
    assert len(sponsors) == 14
    marbano = next(s for s in sponsors if s.name == "Marbano")
    tonometal = next(s for s in sponsors if s.name == "Tonometal")
    bright_shot = next(s for s in sponsors if s.name == "Bright Shot")
    assert marbano.wealth == 99
    assert tonometal.wealth == 25
    assert bright_shot.wealth == 85


@patch("app.core.roster.get_connection")
def test_load_roster_future_year_includes_future_title_sponsors(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    result = load_roster(year=2001, include_title_sponsors=True)
    _, _, year, _, _, sponsors = result

    assert year == 2001
    sponsor_names = {s.name for s in sponsors}
    assert "FRL" in sponsor_names
    assert "Panatron" in sponsor_names
    assert "VL" not in sponsor_names


@patch("app.core.roster.get_connection")
def test_team_records_include_seeded_title_sponsor_deals(mock_get_conn):
    mock_get_conn.return_value = create_seeded_db()

    teams, *_ = load_roster(year=1998)
    warrick = next(t for t in teams if t.name == "Warrick")
    swords = next(t for t in teams if t.name == "Swords")

    assert warrick.title_sponsor_name == "Windale"
    assert warrick.title_sponsor_yearly == 32_500_000
    assert warrick.title_sponsor_contract_length == 2
    assert warrick.other_sponsorship_yearly == 9_500_000
    assert swords.title_sponsor_name == "Dasko"
    assert swords.title_sponsor_yearly == 5_200_000
    assert swords.title_sponsor_contract_length == 1
    assert swords.other_sponsorship_yearly == 18_000_000
