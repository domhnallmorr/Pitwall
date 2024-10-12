from tests import create_model
from pw_model.finance import finance_model

import random

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

		team_model.commercial_manager_model.contract.salary = random.randint(1, 10_000_000)

		team_model.finance_model.staff_yearly_cost = 28_000

		assert team_model.finance_model.total_staff_costs_per_year == 3_108_000 #number staff * yearly wage

		team_model.finance_model.weekly_update()

		expected_income = team_model.finance_model.prize_money + team_model.finance_model.total_sponsorship
		expected_costs = team_model.driver1_model.contract.salary + team_model.driver2_model.contract.salary + team_model.finance_model.total_staff_costs_per_year + team_model.commercial_manager_model.contract.salary

		expected_balance = expected_income - expected_costs
		weekly_change = int(expected_balance / 52)

		assert abs(team_model.finance_model.balance - weekly_change) < 10 # allow a little leaway for conversion to integer errors
		assert team_model.finance_model.balance_history[-1] == team_model.finance_model.balance

		last_balance = team_model.finance_model.balance
		race_cost = random.randint(80, 2_000_000)
		team_model.finance_model.apply_race_costs(race_cost)

		assert team_model.finance_model.balance == last_balance - race_cost
		

