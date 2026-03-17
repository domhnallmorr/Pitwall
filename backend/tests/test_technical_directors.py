import sqlite3
from unittest.mock import patch

from app.core.roster import load_roster, load_technical_directors
from app.main import process_command
import app.main as app_main
from tools.seed_roster import create_schema, seed_data


def create_seeded_db():
    conn = sqlite3.connect(":memory:")
    create_schema(conn)
    seed_data(conn)
    return conn


@patch("app.core.roster.get_connection")
def test_load_technical_directors_assigns_team_ids(mock_get_conn):
    mock_get_conn.side_effect = [create_seeded_db(), create_seeded_db()]

    teams, _, year, _, _ = load_roster(year=1998)
    technical_directors = load_technical_directors(year=year, teams=teams)

    assert len(technical_directors) == 20
    peter = next(td for td in technical_directors if td.name == "Peter Heed")
    francis = next(td for td in technical_directors if td.name == "Francis Durney")
    aldo = next(td for td in technical_directors if td.name == "Aldo Conti")
    warrick = next(t for t in teams if t.name == "Warrick")
    assert peter.team_id == warrick.id
    assert warrick.technical_director_id == peter.id
    assert francis.team_id is None
    assert francis.country == "United Kingdom"
    assert aldo.country == "Italy"


@patch("app.core.roster.get_connection")
def test_get_staff_includes_team_technical_director(mock_get_conn):
    conn = create_seeded_db()
    mock_get_conn.return_value = conn
    app_main.CURRENT_STATE = None

    started = process_command({"type": "start_career"})
    assert started["status"] == "success"

    staff = process_command({"type": "get_staff"})
    assert staff["status"] == "success"
    assert staff["data"]["technical_director"] is not None
    assert staff["data"]["technical_director"]["name"] == "Peter Heed"
