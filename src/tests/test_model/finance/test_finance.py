# from tests import create_model
# from pw_model.finance import finance_model

# import random

# import pandas as pd
# import pytest


# def test_balance_update():
# 	for i in range(50):
# 		model = create_model.create_model()

# 		team_model = model.get_team_model("Jordan")

# 		# set some dummy values
# 		team_model.finance_model.balance = 0
# 		team_model.number_of_staff = 111
# 		team_model.finance_model.prize_money = random.randint(1, 25_000_000)
# 		team_model.finance_model.total_sponsorship = random.randint(1, 50_000_000)

# 		team_model.driver1_model.contract.salary = random.randint(1, 10_000_000)
# 		team_model.driver2_model.contract.salary = random.randint(1, 10_000_000)

# 		team_model.technical_director_model.contract.salary = random.randint(1, 10_000_000)
# 		team_model.commercial_manager_model.contract.salary = random.randint(1, 10_000_000)

# 		team_model.finance_model.staff_yearly_cost = 28_000

# 		assert team_model.finance_model.total_staff_costs_per_year == 3_108_000 #number staff * yearly wage

# 		team_model.finance_model.weekly_update()

# 		expected_income = team_model.finance_model.prize_money + team_model.finance_model.total_sponsorship
# 		expected_costs = team_model.driver1_model.contract.salary + team_model.driver2_model.contract.salary
# 		expected_costs += team_model.finance_model.total_staff_costs_per_year
# 		expected_costs += team_model.technical_director_model.contract.salary
# 		expected_costs += team_model.commercial_manager_model.contract.salary

# 		expected_balance = expected_income - expected_costs
# 		weekly_change = int(expected_balance / 52)

# 		assert abs(team_model.finance_model.balance - weekly_change) < 10 # allow a little leaway for conversion to integer errors
# 		assert team_model.finance_model.balance_history[-1] == team_model.finance_model.balance

# 		last_balance = team_model.finance_model.balance
# 		team_model.finance_model.apply_race_costs()

# 		assert team_model.finance_model.balance == last_balance - team_model.finance_model.transport_costs_model.costs_by_race[-1]
		
# def test_prize_money_update():
# 	'''
# 	Do a spot check on ending the season and check if prize money is updated
# 	set player_team to Williams, create a dummy dataframe for contructors championship and test if prize money gets updated
# 	'''
# 	model = create_model.create_model(mode="headless")

# 	# Redfine constructors standings
# 	data = [
# 		"Ferrari",
# 		"Benetton",
# 		"Jordan",
# 		"Stewart",
# 		"Williams",
# 		"Prost"
# 	]

# 	model.season.standings_manager.constructors_standings_df = pd.DataFrame(data=data, columns=["Team"])

# 	# model.staff_market.ensure_player_has_drivers_for_next_season()
# 	model.player_team = "Williams"
# 	model.player_team_model.finance_model.prize_money = 0 # set to zero and check if it gets updated
# 	model.end_season()
# 	assert model.player_team_model.finance_model.prize_money == 13_000_000


import pytest
from unittest.mock import MagicMock

from pw_model.finance.finance_model import FinanceModel, calculate_prize_money
# from FinanceModel import FinanceModel, calculate_prize_money

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
    # The post_race_actions might call transport costs and sponsor payments
    starting_balance = finance_model.balance

    finance_model.post_race_actions()

    # We expect some changes in the balance after transport, sponsor payments, etc.
    assert finance_model.balance != starting_balance #\"Balance should change after post_race_actions\"

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
