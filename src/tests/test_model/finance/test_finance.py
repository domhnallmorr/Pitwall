import pytest
from unittest.mock import MagicMock

from pw_model.finance.finance_model import FinanceModel, calculate_prize_money
from race_weekend_model.race_model_enums import SessionNames
# from FinanceModel import FinanceModel, calculate_prize_money
from tests import create_model
from tests.test_model.track import test_track_model
from race_weekend_model import race_weekend_model

@pytest.fixture
def mock_model():
    # A minimal mock for the overall Model
    model = MagicMock()
    model.year = 1998
    # create a mock season with a mock calendar
    model.season.calendar.current_week = 1
    return model

@pytest.fixture
def mock_driver_model_positive():
    # Basic driver model stub
    driver = MagicMock()
    driver.contract.salary = 1_000_000
    return driver

@pytest.fixture
def mock_driver_model_negative():
    # Basic driver model stub for negative salary (driver paying the team)
    driver = MagicMock()
    driver.contract.salary = -500_000
    return driver

@pytest.fixture
def mock_director_model():
    # Stub technical director
    director = MagicMock()
    director.contract.salary = 750_000
    return director

@pytest.fixture
def mock_manager_model():
    # Stub commercial manager
    manager = MagicMock()
    manager.contract.salary = 600_000
    return manager

@pytest.fixture
def mock_team_model(mock_driver_model_positive, mock_driver_model_negative,
                    mock_director_model, mock_manager_model):
    # Team model with required attributes
    team_model = MagicMock()
    team_model.number_of_staff = 100
    team_model.driver1_model = mock_driver_model_positive
    team_model.driver2_model = mock_driver_model_negative
    team_model.technical_director_model = mock_director_model
    team_model.commercial_manager_model = mock_manager_model
    return team_model

@pytest.fixture
def finance_model(mock_model, mock_team_model):
    # Create a FinanceModel instance with some baseline test data
    fm = FinanceModel(
        model=mock_model,
        team_model=mock_team_model,
        opening_balance=10_000_000,
        other_sponsorship=2_000_000,
        title_sponsor="MyTitleSponsor",
        title_sponsor_value=5_000_000
    )
    fm.transport_costs_model.setup_new_season()
    return fm

def test_finance_model_initial_balance(finance_model):
    assert finance_model.balance == 10_000_000 #"Initial balance should match the opening balance"

def test_calculate_prize_money():
    # check known positions
    assert calculate_prize_money(0) == 33000000 # \"P1 expected to have 33,000,000 prize money\"
    assert calculate_prize_money(1) == 31000000 # \"P2 expected to have 31,000,000 prize money\"
    assert calculate_prize_money(10) == 1000000 # \"P11 expected to have 1,000,000 prize money\"

def test_season_profit(finance_model):
    # Initially, season_opening_balance = 10,000,000 and current balance = 10,000,000
    assert finance_model.season_profit == 0 #"No profit/loss at season start\"

def test_weekly_update(finance_model, mock_team_model):
    # We track the balance before calling weekly_update
    before_balance = finance_model.balance

    finance_model.weekly_update()

    after_balance = finance_model.balance
    # Some cost/income changes are applied weekly
    # The difference should not be zero but negative or positive depending on staff, drivers, etc.
    assert after_balance != before_balance #"Balance should change after weekly_update\"
    assert len(finance_model.balance_history) == 1 #\"Balance history should record a new entry\"

def test_post_race_actions(finance_model, mock_model):
    # Test scenario 1: No crashes
    starting_balance = finance_model.balance
    finance_model.post_race_actions(player_driver1_crashed=False, player_driver2_crashed=False)
    balance_no_crashes = finance_model.balance
    
    # We expect some changes in the balance after transport costs and sponsor payments
    assert balance_no_crashes != starting_balance #"Balance should change after post_race_actions"
    
    # Test scenario 2: Driver 1 crashes
    starting_balance = finance_model.balance
    finance_model.post_race_actions(player_driver1_crashed=True, player_driver2_crashed=False)
    balance_with_crash = finance_model.balance
    
    # Balance should be lower due to crash damage
    assert balance_with_crash < starting_balance #"Balance should decrease more when driver crashes"
    
    # Test scenario 3: Both drivers crash
    starting_balance = finance_model.balance
    finance_model.post_race_actions(player_driver1_crashed=True, player_driver2_crashed=True)
    balance_both_crash = finance_model.balance
    
    # Balance should be even lower with both drivers crashing
    assert balance_both_crash < starting_balance #"Balance should decrease more when both drivers crash"
    assert finance_model.damage_costs_model.damage_costs[-1] > 0 #"Damage costs should be positive when crashes occur"

def test_update_prize_money(finance_model):
    # Let's pick finishing position 0 = 1st place
    finance_model.update_prize_money(0)
    assert finance_model.prize_money == 33000000 #\"Prize money should match first place\"

def test_consecutive_weeks_in_debt(finance_model):
    # Force a negative balance scenario
    finance_model.consecutive_weeks_in_debt = 0
    finance_model.balance = -10000000000 #make balance a large negative number, so after weekly update it will still be negative
    # Now call weekly_update
    finance_model.weekly_update()

    assert finance_model.consecutive_weeks_in_debt == 1 #\"Should have incremented weeks in debt\"
    
    finance_model.balance = 10000000000
    finance_model.weekly_update()

    assert finance_model.consecutive_weeks_in_debt == 0

def test_end_season(finance_model):
    # Just verify that end_season resets the season opening balance, sets up new season
    # The actual logic for sponsor_model.setup_new_season etc. is tested externally
    finance_model.end_season()
    assert finance_model.season_opening_balance == finance_model.balance #\\\n        \"At season end, opening_balance should match current balance\"

def test_race_crash_damage_flow():
    """Test that driver crashes in race properly flow through to damage costs"""
    # Create basic model setup
    model = create_model.create_model(mode="headless")
    model.player_team = "Williams"
    model.player_team_model.finance_model.prize_money = 0
    model.player_team_model.finance_model.sponsors_model.other_sponsorship = 0
    model.player_team_model.finance_model.sponsors_model.title_sponsor_value = 0

    track = test_track_model.create_dummy_track()
    race_model = race_weekend_model.RaceWeekendModel("headless", model, track)
    #TODO add function in race_model to setup and run a race
    race_model.setup_qualifying(60*60, SessionNames.QUALIFYING)
    race_model.setup_race()
    
    # Get initial balance to compare later
    initial_balance = model.player_team_model.finance_model.balance
    
    # Simulate different crash scenarios
    crash_scenarios = [
        (False, False),  # No crashes
        (True, False),   # Only driver 1 crashes
        (False, True),   # Only driver 2 crashes
        (True, True)     # Both drivers crash
    ]
    
    for driver1_crashed, driver2_crashed in crash_scenarios:
        # Reset balance
        model.player_team_model.finance_model.balance = initial_balance
        
        # Simulate race with crashes
        race_model.current_session.player_driver1_crashed = driver1_crashed
        race_model.current_session.player_driver2_crashed = driver2_crashed
        
        # Process post-race actions
        model.season.post_race_actions(
            winner="Test Driver",
            player_driver1_crashed=driver1_crashed,
            player_driver2_crashed=driver2_crashed
        )
        
        # Get the latest damage costs
        latest_damage = model.player_team_model.finance_model.damage_costs_model.damage_costs[-1]
        
        if not driver1_crashed and not driver2_crashed:
            assert latest_damage == 0, "No damage costs should be applied when no crashes occur"
        else:
            assert latest_damage > 0, "Damage costs should be applied when crashes occur"
            assert model.player_team_model.finance_model.balance < initial_balance, "Balance should decrease after crash damage"
            
            # Verify individual driver crash costs
            if driver1_crashed:
                assert model.player_team_model.finance_model.damage_costs_model.driver1_latest_crash_cost > 0
            else:
                assert model.player_team_model.finance_model.damage_costs_model.driver1_latest_crash_cost == 0
                
            if driver2_crashed:
                assert model.player_team_model.finance_model.damage_costs_model.driver2_latest_crash_cost > 0
            else:
                assert model.player_team_model.finance_model.damage_costs_model.driver2_latest_crash_cost == 0
