import pytest
import sqlite3
from unittest.mock import patch
import app.main as app_main
from app.main import process_command
from app.core.roster import load_roster
from app.models.finance import TransactionCategory
from app.core.crash_damage import DamageTier
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
    assert app_main.CURRENT_STATE.finance.prize_money_entitlement == 33_000_000
    assert app_main.CURRENT_STATE.finance.prize_money_total_races > 0

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


@patch('app.core.roster.get_connection')
def test_simulate_race_pays_prize_money_installment(mock_get_conn, test_db):
    mock_get_conn.return_value = test_db
    app_main.CURRENT_STATE = None

    start_response = process_command({'type': 'start_career'})
    assert start_response['status'] == 'success'
    starting_balance = app_main.CURRENT_STATE.finance.balance
    app_main.CURRENT_STATE.calendar.current_week = 10  # Albert Park race week

    race_response = process_command({'type': 'simulate_race'})
    assert race_response['status'] == 'success'

    finance = app_main.CURRENT_STATE.finance
    assert finance.prize_money_races_paid == 1
    assert finance.prize_money_paid > 0
    assert finance.balance > starting_balance
    transport_txs = [t for t in finance.transactions if t.category == TransactionCategory.TRANSPORT]
    assert len(transport_txs) == 1
    assert transport_txs[0].amount < 0
    transport_emails = [e for e in app_main.CURRENT_STATE.emails if e.subject.startswith("Transport Confirmed:")]
    assert len(transport_emails) >= 1

    finance_response = process_command({'type': 'get_finance'})
    assert finance_response['status'] == 'success'
    assert 'summary' in finance_response['data']
    assert 'track_profit_loss' in finance_response['data']
    assert finance_response['data']['summary']['transport_total'] > 0

    driver_response = process_command({'type': 'get_driver', 'name': 'John Newhouse'})
    assert driver_response['status'] == 'success'
    assert 'season_results' in driver_response['data']
    assert len(driver_response['data']['season_results']) == 1


@patch('app.core.roster.get_connection')
@patch('app.race.race_manager.random.sample', side_effect=lambda seq, k: [seq[0]])
@patch('app.race.race_manager.RaceManager._pick_crash_count', return_value=1)
@patch(
    'app.core.crash_damage.CrashDamageManager.calculate_damage_cost',
    return_value=(DamageTier("minor", 50_000, 150_000, 0.5), 100_000),
)
def test_simulate_race_applies_crash_damage_cost_for_player_team(
    mock_damage_cost,
    mock_pick_crash_count,
    mock_sample,
    mock_get_conn,
    test_db,
):
    mock_get_conn.return_value = test_db
    app_main.CURRENT_STATE = None

    start_response = process_command({'type': 'start_career'})
    assert start_response['status'] == 'success'
    app_main.CURRENT_STATE.calendar.current_week = 10

    race_response = process_command({'type': 'simulate_race'})
    assert race_response['status'] == 'success'

    finance = app_main.CURRENT_STATE.finance
    damage_txs = [t for t in finance.transactions if t.category == TransactionCategory.CRASH_DAMAGE]
    assert len(damage_txs) == 1
    assert damage_txs[0].amount == -100_000

    damage_emails = [e for e in app_main.CURRENT_STATE.emails if e.subject.startswith("Crash Damage Report:")]
    assert len(damage_emails) == 1
