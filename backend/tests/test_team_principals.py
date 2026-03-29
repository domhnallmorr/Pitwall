import sqlite3
from unittest.mock import patch

from app.core.roster import load_roster, load_team_principals
from tools.seed_roster import create_schema, seed_data


def create_seeded_db():
    conn = sqlite3.connect(":memory:")
    create_schema(conn)
    seed_data(conn)
    return conn


@patch("app.core.roster.get_connection")
def test_load_team_principals_assigns_team_ids_and_owner_flags(mock_get_conn):
    mock_get_conn.side_effect = [create_seeded_db(), create_seeded_db()]

    teams, _, year, _, _ = load_roster(year=1998)
    team_principals = load_team_principals(year=year, teams=teams)

    assert len(team_principals) == 13
    franklin = next(tp for tp in team_principals if tp.name == "Franklin Warrick")
    julien = next(tp for tp in team_principals if tp.name == "Julien Tissot")
    cedric = next(tp for tp in team_principals if tp.name == "Cedric Palling")
    warrick = next(t for t in teams if t.name == "Warrick")

    assert franklin.team_id == warrick.id
    assert franklin.owns_team is True
    assert warrick.team_principal_id == franklin.id
    assert julien.owns_team is False
    assert cedric.team_id is None
