from tests import create_model
from pw_model.finance import finance_model

import random

import pandas as pd
import pytest


def test_balance_update():
	for i in range(50):
		model = create_model.create_model()

		team_model = model.get_team_model("Jordan")

		# set some dummy values
		team_model.finance_model.balance = 0
		team_model.number_of_staff = 111
		team_model.finance_model.prize_money = random.randint(1, 25_000_000)
		team_model.finance_model.total_sponsorship = random.randint(1, 50_000_000)

		team_model.driver1_model.contract.salary = random.randint(1, 10_000_000)
		team_model.driver2_model.contract.salary = random.randint(1, 10_000_000)

		team_model.technical_director_model.contract.salary = random.randint(1, 10_000_000)
		team_model.commercial_manager_model.contract.salary = random.randint(1, 10_000_000)

		team_model.finance_model.staff_yearly_cost = 28_000

		assert team_model.finance_model.total_staff_costs_per_year == 3_108_000 #number staff * yearly wage

		team_model.finance_model.weekly_update()

		expected_income = team_model.finance_model.prize_money + team_model.finance_model.total_sponsorship
		expected_costs = team_model.driver1_model.contract.salary + team_model.driver2_model.contract.salary
		expected_costs += team_model.finance_model.total_staff_costs_per_year
		expected_costs += team_model.technical_director_model.contract.salary
		expected_costs += team_model.commercial_manager_model.contract.salary

		expected_balance = expected_income - expected_costs
		weekly_change = int(expected_balance / 52)

		assert abs(team_model.finance_model.balance - weekly_change) < 10 # allow a little leaway for conversion to integer errors
		assert team_model.finance_model.balance_history[-1] == team_model.finance_model.balance

		last_balance = team_model.finance_model.balance
		team_model.finance_model.apply_race_costs()

		assert team_model.finance_model.balance == last_balance - team_model.finance_model.transport_costs_model.costs_by_race[-1]
		
def test_prize_money_update():
	'''
	Do a spot check on ending the season and check if prize money is updated
	set player_team to Williams, create a dummy dataframe for contructors championship and test if prize money gets updated
	'''
	model = create_model.create_model(mode="headless")

	# Redfine constructors standings
	data = [
		"Ferrari",
		"Benetton",
		"Jordan",
		"Stewart",
		"Williams",
		"Prost"
	]

	model.season.standings_manager.constructors_standings_df = pd.DataFrame(data=data, columns=["Team"])

	# model.staff_market.ensure_player_has_drivers_for_next_season()
	model.player_team = "Williams"
	model.player_team_model.finance_model.prize_money = 0 # set to zero and check if it gets updated
	model.end_season()
	assert model.player_team_model.finance_model.prize_money == 13_000_000
