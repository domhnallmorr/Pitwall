import sqlite3
from unittest.mock import patch

from app.core.roster import load_roster, load_commercial_managers
from app.main import process_command
import app.main as app_main
from tools.seed_roster import create_schema, seed_data


def create_seeded_db():
    conn = sqlite3.connect(":memory:")
    create_schema(conn)
    seed_data(conn)
    return conn


@patch("app.core.roster.get_connection")
def test_load_commercial_managers_assigns_team_ids(mock_get_conn):
    mock_get_conn.side_effect = [create_seeded_db(), create_seeded_db()]

    teams, _, year, _, _ = load_roster(year=1998)
    commercial_managers = load_commercial_managers(year=year, teams=teams)

    assert len(commercial_managers) == 18
    jace = next(cm for cm in commercial_managers if cm.name == "Jace Whitman")
    gaston = next(cm for cm in commercial_managers if cm.name == "Gaston Seville")
    warrick = next(t for t in teams if t.name == "Warrick")
    assert jace.team_id == warrick.id
    assert warrick.commercial_manager_id == jace.id
    assert gaston.team_id is None


@patch("app.core.roster.get_connection")
def test_start_career_loads_commercial_managers(mock_get_conn):
    conn = create_seeded_db()
    mock_get_conn.return_value = conn
    app_main.CURRENT_STATE = None

    started = process_command({"type": "start_career"})
    assert started["status"] == "success"
    assert len(app_main.CURRENT_STATE.commercial_managers) == 18
    team = next(t for t in app_main.CURRENT_STATE.teams if t.name == "Warrick")
    assert team.commercial_manager_id is not None


@patch("app.core.roster.get_connection")
def test_get_staff_includes_team_commercial_manager(mock_get_conn):
    conn = create_seeded_db()
    mock_get_conn.return_value = conn
    app_main.CURRENT_STATE = None

    started = process_command({"type": "start_career"})
    assert started["status"] == "success"

    staff = process_command({"type": "get_staff"})
    assert staff["status"] == "success"
    assert staff["data"]["commercial_manager"] is not None
    assert staff["data"]["commercial_manager"]["name"] == "Jace Whitman"
