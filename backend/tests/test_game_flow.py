import pytest
import sqlite3
from unittest.mock import patch
import app.main as app_main
from app.main import process_command
from app.core.roster import load_roster
from tools.seed_roster import create_schema, seed_data

@pytest.fixture
def test_db():
    # Setup in-memory DB
    conn = sqlite3.connect(':memory:')
    create_schema(conn)
    seed_data(conn)
    return conn

@patch('app.core.roster.get_connection')
def test_load_roster_signature(mock_get_conn, test_db):
    """
    Ensure load_roster returns exactly 4 values (Teams, Drivers, Year, Events).
    """
    mock_get_conn.return_value = test_db
    
    result = load_roster(year=1998)
    
    assert len(result) == 5
    teams, drivers, year, events, circuits = result
    
    assert year == 1998
    assert len(drivers) > 0
    assert len(teams) > 0
    assert len(events) > 0
    assert len(circuits) > 0

@patch('app.core.roster.get_connection')
def test_start_career_flow(mock_get_conn, test_db):
    """
    Integration test for 'start_career' command.
    """
    mock_get_conn.return_value = test_db
    app_main.CURRENT_STATE = None
    
    # 1. Start Career Command
    cmd = {'type': 'start_career'}
    
    # We need to ensure we don't carry over global state from other tests/runs if we run in same process
    # But for this test, we assume fresh process or we can reset CURRENT_STATE if exposed.
    # main.py CURRENT_STATE is global, so in a real test runner we might need to reset it.
    # For now, just running it.
    
    response = process_command(cmd)
    
    assert response['status'] == 'success'
    assert response['type'] == 'game_started'
    assert response['data']['team_name'] == 'Warrick'
    assert "Week 1" in response['data']['week_display']
    assert response['data']['year'] == 1998

@patch('app.core.retirement.random.random', return_value=0.0)
@patch('app.core.roster.get_connection')
def test_start_career_can_announce_donovan_final_season(mock_get_conn, mock_random, test_db):
    mock_get_conn.return_value = test_db
    app_main.CURRENT_STATE = None

    response = process_command({'type': 'start_career'})

    assert response['status'] == 'success'
    state = app_main.CURRENT_STATE
    retirement_watch_emails = [e for e in state.emails if "Retirement Watch:" in e.subject]

    assert len(retirement_watch_emails) == 1
    assert "Donovan Upland" in retirement_watch_emails[0].body
