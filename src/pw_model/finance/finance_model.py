from __future__ import annotations

import collections
from datetime import datetime, timedelta
from typing import Deque
from typing import TYPE_CHECKING, Union

from pw_model.finance.sponsors_model import SponsorModel
from pw_model.finance.transport_costs import TransportCostsModel
from pw_model.finance.damage_costs import DamageCosts
from pw_model.finance.car_development_costs import CarDevelopmentCosts

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model
	from pw_model.team.team_model import TeamModel

def calculate_prize_money(finishing_position: int) -> int:
	'''
	finishing position should be zero indexed
	'''

	prize_money =  [
		33_000_000,
		31_000_000,
		27_000_000,
		23_000_000,
		13_000_000,
		11_000_000,
		9_000_000,
		7_000_000,
		5_000_000,
		3_000_000,
		1_000_000,
	]
	
	return prize_money[finishing_position]

class FinanceModel:
	def __init__(self, model: Model, team_model: TeamModel, opening_balance: int, other_sponsorship: int,
			  title_sponsor: str, title_sponsor_value: int):
		
		self.model = model
		self.team_model = team_model
		self.balance = opening_balance

		self.staff_yearly_cost = 28_000

		self.prize_money = 13_000_000

		# self.car_cost = 7_000_000 # generic value to cover car production and development costs

		self.balance_history: Deque[int] = collections.deque(maxlen=130) # 130 weeks (2.5 years) in length
		self.balance_history_dates: Deque[datetime] = collections.deque(maxlen=130)

		self.consecutive_weeks_in_debt = 0
		self.sponsors_model = SponsorModel(model, self.team_model, other_sponsorship, title_sponsor, title_sponsor_value)
		self.transport_costs_model = TransportCostsModel(self.model)
		self.damage_costs_model = DamageCosts()
		self.car_development_costs_model = CarDevelopmentCosts()

		self.season_opening_balance = opening_balance

	@property
	def season_profit(self) -> int:
		return self.balance - self.season_opening_balance

	@property
	def total_staff_costs_per_year(self) -> int:
		return int(self.staff_yearly_cost * self.team_model.number_of_staff)
	
	@property
	def drivers_payments(self) -> int:
		payments = 0

		for driver_model in [self.team_model.driver1_model, self.team_model.driver2_model]:
			if driver_model.contract.salary < 0:
				payments += driver_model.contract.salary * -1
		
		return payments
	
	@property
	def drivers_salary(self) -> int:
		salary = 0

		for driver_model in [self.team_model.driver1_model, self.team_model.driver2_model]:
			if driver_model.contract.salary > 0:
				salary += driver_model.contract.salary
		
		return salary		

	@property
	def total_income(self) -> int:
		return int(self.prize_money + self.sponsors_model.total_sponsor_income + self.drivers_payments)
	
	@property
	def total_expenditure(self) -> int:
		#TODO remove hard coding of race costs
		return int(self.total_staff_costs_per_year + self.drivers_salary + self.team_model.technical_director_model.contract.salary
			 + self.team_model.commercial_manager_model.contract.salary
			 + self.transport_costs_model.estimated_season_costs + self.damage_costs_model.damage_costs_this_season
			 + self.car_development_costs_model.costs_this_season + self.team_model.supplier_model.engine_supplier_cost)
	
	def weekly_update(self) -> None:
		
		# add prize money
		self.balance += int(self.prize_money / 52)

		# staff cost
		self.balance -= int((self.staff_yearly_cost / 52) * self.team_model.number_of_staff)

		# Drivers cost
		self.balance -= int(self.team_model.driver1_model.contract.salary / 52)
		self.balance -= int(self.team_model.driver2_model.contract.salary / 52)

		# manager costs
		self.balance -= int(self.team_model.technical_director_model.contract.salary / 52)
		self.balance -= int(self.team_model.commercial_manager_model.contract.salary / 52)
		
		# Car development costs
		self.balance -= self.car_development_costs_model.process_weekly_payment() # apply weekly car development costs

		self.update_balance_history()

		if self.balance < 0:
			self.consecutive_weeks_in_debt += 1
		else:
			self.consecutive_weeks_in_debt = 0

	def post_race_actions(self, player_driver1_crashed: bool, player_driver2_crashed: bool) -> None:
		start_balance = self.balance
		transport_cost, damage_cost = self.apply_race_costs(player_driver1_crashed, player_driver2_crashed)
		title_sponsor_payment = self.process_race_income()
		engine_payment = self.team_model.supplier_model.engine_payments[-1]

		profit = self.balance - start_balance
		# self.race_profits.append(profit)

		self.model.inbox.new_race_finance_email(transport_cost, damage_cost, title_sponsor_payment, engine_payment, profit)
		
	def process_race_income(self) -> int:
		self.sponsors_model.process_sponsor_post_race_payments()
		
		other_sponsors_payments = self.sponsors_model.other_sponser_payments[-1]
		self.balance += other_sponsors_payments

		title_sponsor_payment = int(self.sponsors_model.title_sponser_payments[-1])
		self.balance += title_sponsor_payment

		return title_sponsor_payment
	
	def apply_race_costs(self, player_driver1_crashed: bool, player_driver2_crashed: bool) -> tuple[int, int]:
		# Transport
		self.transport_costs_model.gen_race_transport_cost()
		transport_cost = int(self.transport_costs_model.costs_by_race[-1])
		self.balance -= transport_cost

		# Crash Costs
		self.damage_costs_model.calculate_race_damage_costs(player_driver1_crashed, player_driver2_crashed)
		damage_cost = int(self.damage_costs_model.damage_costs[-1])
		self.balance -= damage_cost

		# Supplier Costs
		self.team_model.supplier_model.process_race_payments()
		engine_cost = int(self.team_model.supplier_model.engine_payments[-1])
		self.balance -= engine_cost

		return transport_cost, damage_cost

	def update_balance_history(self) -> None:
		self.balance_history.append(self.balance)
		self.balance_history_dates.append(datetime(self.model.year, 1, 1) + timedelta(weeks=self.model.season.calendar.current_week - 1))

	def update_prize_money(self, finishing_position: int) -> None:
		self.prize_money = calculate_prize_money(finishing_position)

		self.model.inbox.new_prize_money_email(self.prize_money)

	def update_facilities_cost(self, cost: int) -> None:
		self.balance -= cost

	def end_season(self) -> None:
		self.season_opening_balance = self.balance
		self.sponsors_model.setup_new_season()
		self.transport_costs_model.setup_new_season()
		self.car_development_costs_model.setup_new_season()

		self.race_profits : list[int] = []

