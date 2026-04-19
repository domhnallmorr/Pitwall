import pytest
import sqlite3
from unittest.mock import patch
import app.main as app_main
from app.main import process_command
from app.core.roster import load_roster
from app.core.rollover import SeasonRolloverManager
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


@patch('app.core.roster.get_connection')
def test_start_career_flow_can_select_team(mock_get_conn, test_db):
    mock_get_conn.return_value = test_db
    app_main.CURRENT_STATE = None

    response = process_command({'type': 'start_career', 'team_name': 'Ferano'})

    assert response['status'] == 'success'
    assert response['type'] == 'game_started'
    assert response['data']['team_name'] == 'Ferano'

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
    assert finance.balance != starting_balance
    sponsorship_txs = [t for t in finance.transactions if t.category == TransactionCategory.SPONSORSHIP]
    assert len(sponsorship_txs) == 2
    assert all(t.amount > 0 for t in sponsorship_txs)
    transport_txs = [t for t in finance.transactions if t.category == TransactionCategory.TRANSPORT]
    assert len(transport_txs) == 1
    assert transport_txs[0].amount < 0
    driver_wage_txs = [t for t in finance.transactions if t.category == TransactionCategory.DRIVER_WAGES]
    assert len(driver_wage_txs) == 2
    assert all(t.amount != 0 for t in driver_wage_txs)
    design_staff_txs = [t for t in finance.transactions if t.category == TransactionCategory.DESIGN_STAFF_WAGES]
    engineering_staff_txs = [t for t in finance.transactions if t.category == TransactionCategory.ENGINEERING_STAFF_WAGES]
    mechanics_staff_txs = [t for t in finance.transactions if t.category == TransactionCategory.MECHANICS_STAFF_WAGES]
    assert len(design_staff_txs) == 1
    assert len(engineering_staff_txs) == 1
    assert len(mechanics_staff_txs) == 1
    assert design_staff_txs[0].amount < 0
    assert engineering_staff_txs[0].amount < 0
    assert mechanics_staff_txs[0].amount < 0
    engine_supplier_txs = [t for t in finance.transactions if t.category == TransactionCategory.ENGINE_SUPPLIER]
    assert len(engine_supplier_txs) == 1
    assert engine_supplier_txs[0].amount < 0
    tyre_supplier_txs = [t for t in finance.transactions if t.category == TransactionCategory.TYRE_SUPPLIER]
    assert len(tyre_supplier_txs) == 0  # Warrick has partner tyre deal in default data
    fuel_supplier_txs = [t for t in finance.transactions if t.category == TransactionCategory.FUEL_SUPPLIER]
    assert len(fuel_supplier_txs) == 1
    assert fuel_supplier_txs[0].amount < 0
    transport_emails = [e for e in app_main.CURRENT_STATE.emails if e.subject.startswith("Transport Confirmed:")]
    assert len(transport_emails) >= 1
    sponsorship_emails = [e for e in app_main.CURRENT_STATE.emails if e.subject.startswith("Sponsorship Payment Received:")]
    assert len(sponsorship_emails) >= 1
    payroll_emails = [e for e in app_main.CURRENT_STATE.emails if e.subject.startswith("Operational Staff Payroll Processed:")]
    assert len(payroll_emails) >= 1
    engine_supplier_emails = [e for e in app_main.CURRENT_STATE.emails if e.subject.startswith("Engine Supplier Settlement:")]
    assert len(engine_supplier_emails) >= 1
    fuel_supplier_emails = [e for e in app_main.CURRENT_STATE.emails if e.subject.startswith("Fuel Supplier Settlement:")]
    assert len(fuel_supplier_emails) >= 1
    finance_summary_emails = [e for e in app_main.CURRENT_STATE.emails if e.subject.startswith("Race Finance Summary:")]
    assert len(finance_summary_emails) >= 1
    assert "Engine supplier:" in finance_summary_emails[-1].body
    assert "Tyre supplier:" in finance_summary_emails[-1].body
    assert "Fuel supplier:" in finance_summary_emails[-1].body

    finance_response = process_command({'type': 'get_finance'})
    assert finance_response['status'] == 'success'
    assert 'summary' in finance_response['data']
    assert 'track_profit_loss' in finance_response['data']
    assert finance_response['data']['summary']['transport_total'] > 0
    assert finance_response['data']['summary']['design_staff_total'] > 0
    assert finance_response['data']['summary']['engineering_staff_total'] > 0
    assert finance_response['data']['summary']['mechanics_staff_total'] > 0
    assert finance_response['data']['summary']['workforce_total'] > 0
    assert finance_response['data']['summary']['engine_supplier_total'] < 0
    assert 'tyre_supplier_total' in finance_response['data']['summary']
    assert 'fuel_supplier_total' in finance_response['data']['summary']
    assert finance_response['data']['summary']['sponsorship_total'] > 0
    assert finance_response['data']['engine_supplier']['name'] == 'Mechatron'
    assert finance_response['data']['tyre_supplier']['name'] == 'Greatday'
    assert finance_response['data']['fuel_supplier']['name'] == 'Brasoil'

    driver_response = process_command({'type': 'get_driver', 'name': 'John Newhouse'})
    assert driver_response['status'] == 'success'
    assert 'season_results' in driver_response['data']
    assert len(driver_response['data']['season_results']) == 1


@patch('app.core.roster.get_connection')
def test_simulate_race_posts_expected_finance_categories_and_summary(mock_get_conn, test_db):
    mock_get_conn.return_value = test_db
    app_main.CURRENT_STATE = None

    start_response = process_command({'type': 'start_career', 'team_name': 'Schweizer'})
    assert start_response['status'] == 'success'
    app_main.CURRENT_STATE.calendar.current_week = 10

    race_response = process_command({'type': 'simulate_race'})
    assert race_response['status'] == 'success'

    finance = app_main.CURRENT_STATE.finance
    race_transactions = [
        t for t in finance.transactions
        if t.year == app_main.CURRENT_STATE.year
        and t.event_name == 'Albert Park'
        and t.event_type == 'RACE'
    ]
    categories = {t.category for t in race_transactions}

    assert TransactionCategory.PRIZE_MONEY in categories
    assert TransactionCategory.SPONSORSHIP in categories
    assert TransactionCategory.DRIVER_WAGES in categories
    assert TransactionCategory.MANAGEMENT_SALARIES in categories
    assert TransactionCategory.DESIGN_STAFF_WAGES in categories
    assert TransactionCategory.ENGINEERING_STAFF_WAGES in categories
    assert TransactionCategory.MECHANICS_STAFF_WAGES in categories
    assert TransactionCategory.COMMERCIAL_STAFF_WAGES in categories
    assert TransactionCategory.FACTORY_OVERHEAD in categories
    assert TransactionCategory.ENGINE_SUPPLIER in categories
    assert TransactionCategory.TYRE_SUPPLIER in categories
    assert TransactionCategory.FUEL_SUPPLIER in categories
    assert TransactionCategory.TRANSPORT in categories

    commercial_staff_txs = [t for t in race_transactions if t.category == TransactionCategory.COMMERCIAL_STAFF_WAGES]
    assert len(commercial_staff_txs) == 1
    assert commercial_staff_txs[0].amount < 0

    finance_summary_emails = [e for e in app_main.CURRENT_STATE.emails if e.subject.startswith("Race Finance Summary:")]
    assert len(finance_summary_emails) >= 1
    assert "Commercial staff payroll:" in finance_summary_emails[-1].body

    finance_response = process_command({'type': 'get_finance'})
    assert finance_response['status'] == 'success'
    summary = finance_response['data']['summary']
    assert summary['prize_money_total'] > 0
    assert summary['sponsorship_total'] > 0
    assert summary['driver_wage_expense_total'] > 0
    assert summary['management_salary_total'] > 0
    assert summary['design_staff_total'] > 0
    assert summary['engineering_staff_total'] > 0
    assert summary['mechanics_staff_total'] > 0
    assert summary['workforce_total'] > 0
    assert summary['commercial_staff_total'] > 0
    assert summary['factory_overhead_total'] > 0
    assert summary['engine_supplier_total'] < 0
    assert summary['transport_total'] > 0


@patch('app.core.player_engine_negotiations.random.uniform', return_value=0.0)
@patch('app.core.roster.get_connection')
def test_engine_negotiation_progresses_only_after_race_and_keeps_assigned_staff(
    mock_get_conn,
    mock_uniform,
    test_db,
):
    mock_get_conn.return_value = test_db
    app_main.CURRENT_STATE = None

    start_response = process_command({'type': 'start_career', 'team_name': 'Schweizer'})
    assert start_response['status'] == 'success'
    app_main.CURRENT_STATE.calendar.current_week = 10

    market_response = process_command({'type': 'get_engine_negotiation_market'})
    assert market_response['status'] == 'success'
    suppliers = market_response['data']['suppliers']
    assert suppliers

    supplier_id = suppliers[0]['id']
    start_negotiation_response = process_command({'type': 'start_engine_negotiation', 'supplier_id': supplier_id})
    assert start_negotiation_response['status'] == 'success'
    assert start_negotiation_response['type'] == 'engine_negotiation_updated'

    update_staff_response = process_command({'type': 'update_engine_negotiation_staff', 'assigned_staff': 20})
    assert update_staff_response['status'] == 'success'
    assert update_staff_response['data']['active_negotiation']['assigned_staff'] == 20

    app_main.CURRENT_STATE.calendar.current_week = 10
    starting_progress = app_main.CURRENT_STATE.player_engine_negotiation['progress']
    starting_boxes = app_main.CURRENT_STATE.player_engine_negotiation['progress_boxes']

    qualifying_response = process_command({'type': 'simulate_qualifying'})
    assert qualifying_response['status'] == 'success'
    assert app_main.CURRENT_STATE.player_engine_negotiation['progress'] == starting_progress
    assert app_main.CURRENT_STATE.player_engine_negotiation['progress_boxes'] == starting_boxes
    assert app_main.CURRENT_STATE.player_engine_negotiation['assigned_staff'] == 20

    race_response = process_command({'type': 'simulate_race'})
    assert race_response['status'] == 'success'
    assert app_main.CURRENT_STATE.player_engine_negotiation['progress'] > starting_progress
    assert app_main.CURRENT_STATE.player_engine_negotiation['progress_boxes'] >= starting_boxes
    assert app_main.CURRENT_STATE.player_engine_negotiation['assigned_staff'] == 20

    finance_response = process_command({'type': 'get_finance'})
    assert finance_response['status'] == 'success'
    active_negotiation = finance_response['data']['engine_negotiation']['active_negotiation']
    assert active_negotiation is not None
    assert active_negotiation['assigned_staff'] == 20
    assert active_negotiation['progress'] > starting_progress


@patch('app.core.player_engine_negotiations.random.uniform', return_value=0.0)
@patch('app.core.roster.get_connection')
def test_engine_hospitality_books_finance_cost_and_applies_post_race_bonus(
    mock_get_conn,
    mock_uniform,
    test_db,
):
    mock_get_conn.return_value = test_db
    app_main.CURRENT_STATE = None

    start_response = process_command({'type': 'start_career', 'team_name': 'Schweizer'})
    assert start_response['status'] == 'success'
    app_main.CURRENT_STATE.calendar.current_week = 10

    market_response = process_command({'type': 'get_engine_negotiation_market'})
    supplier_id = market_response['data']['suppliers'][0]['id']
    process_command({'type': 'start_engine_negotiation', 'supplier_id': supplier_id})

    book_response = process_command({'type': 'book_engine_negotiation_hospitality'})
    assert book_response['status'] == 'success'
    assert book_response['type'] == 'engine_negotiation_updated'
    assert book_response['data']['hospitality']['booked'] is True

    hospitality_txs = [t for t in app_main.CURRENT_STATE.finance.transactions if t.category == TransactionCategory.HOSPITALITY]
    assert len(hospitality_txs) == 1
    assert hospitality_txs[0].amount == -100_000
    assert app_main.CURRENT_STATE.pending_hospitality_event is not None

    app_main.CURRENT_STATE.calendar.current_week = 10
    race_response = process_command({'type': 'simulate_race'})
    assert race_response['status'] == 'success'

    assert app_main.CURRENT_STATE.pending_hospitality_event is None
    assert app_main.CURRENT_STATE.player_engine_negotiation['progress'] > 1.0
    hospitality_reports = [e for e in app_main.CURRENT_STATE.emails if e.subject.startswith("Hospitality Report:")]
    assert len(hospitality_reports) == 1


@patch('app.core.player_engine_negotiations.random.uniform', return_value=0.0)
@patch('app.core.roster.get_connection')
def test_engine_hospitality_can_be_booked_for_next_race_from_non_race_week(
    mock_get_conn,
    mock_uniform,
    test_db,
):
    mock_get_conn.return_value = test_db
    app_main.CURRENT_STATE = None

    start_response = process_command({'type': 'start_career', 'team_name': 'Schweizer'})
    assert start_response['status'] == 'success'
    app_main.CURRENT_STATE.calendar.current_week = 1

    market_response = process_command({'type': 'get_engine_negotiation_market'})
    supplier_id = market_response['data']['suppliers'][0]['id']
    process_command({'type': 'start_engine_negotiation', 'supplier_id': supplier_id})

    book_response = process_command({'type': 'book_engine_negotiation_hospitality'})
    assert book_response['status'] == 'success'
    assert book_response['data']['hospitality']['booked'] is True
    assert book_response['data']['hospitality']['event_name'] == 'Albert Park'
    assert book_response['data']['hospitality']['event_week'] == 10

    pending = app_main.CURRENT_STATE.pending_hospitality_event
    assert pending is not None
    assert pending['event_name'] == 'Albert Park'
    assert pending['week'] == 10


@patch('app.core.rollover.load_roster', return_value=([], [], 1999, [], []))
@patch('app.core.roster.get_connection')
def test_signed_engine_negotiation_applies_agreed_terms_at_rollover(mock_get_conn, mock_load_roster, test_db):
    mock_get_conn.return_value = test_db
    app_main.CURRENT_STATE = None

    start_response = process_command({'type': 'start_career', 'team_name': 'Schweizer'})
    assert start_response['status'] == 'success'

    market_response = process_command({'type': 'get_engine_negotiation_market'})
    assert market_response['status'] == 'success'
    supplier = market_response['data']['suppliers'][0]

    start_negotiation_response = process_command({'type': 'start_engine_negotiation', 'supplier_id': supplier['id']})
    assert start_negotiation_response['status'] == 'success'

    negotiation = app_main.CURRENT_STATE.player_engine_negotiation
    customer_threshold = negotiation['customer_threshold']
    negotiated_cost = negotiation['annual_values']['customer']
    negotiated_length = negotiation['contract_length']

    app_main.CURRENT_STATE.player_engine_negotiation['progress'] = float(customer_threshold)
    app_main.CURRENT_STATE.player_engine_negotiation['progress_boxes'] = customer_threshold

    sign_response = process_command({'type': 'sign_engine_negotiated_deal', 'tier': 'customer'})
    assert sign_response['status'] == 'success'
    assert sign_response['type'] == 'engine_negotiation_signed'
    assert sign_response['data']['supplier_name'] == supplier['name']
    assert sign_response['data']['deal_type'] == 'customer'
    assert sign_response['data']['yearly_cost'] == negotiated_cost
    assert sign_response['data']['contract_length'] == negotiated_length

    rollover_result = SeasonRolloverManager().process_rollover(app_main.CURRENT_STATE)

    assert rollover_result['new_year'] == 1999
    assert app_main.CURRENT_STATE.year == 1999
    assert app_main.CURRENT_STATE.player_team.engine_supplier_name == supplier['name']
    assert app_main.CURRENT_STATE.player_team.engine_supplier_deal == 'customer'
    assert app_main.CURRENT_STATE.player_team.engine_supplier_yearly_cost == negotiated_cost
    assert app_main.CURRENT_STATE.player_team.engine_supplier_contract_length == negotiated_length


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
