from __future__ import annotations

import collections
from datetime import datetime, timedelta
from typing import Deque
from typing import TYPE_CHECKING, Union

from pw_model.finance.transport_costs import TransportCostsModel

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
	def __init__(self, model: Model, team_model: TeamModel, opening_balance: int, total_sponsorship: int):
		self.model = model
		self.team_model = team_model
		self.balance = opening_balance

		self.staff_yearly_cost = 28_000

		self.prize_money = 13_000_000
		self.total_sponsorship = total_sponsorship

		self.car_cost = 7_000_000 # generic value to cover car production and development costs

		self.balance_history: Deque[int] = collections.deque(maxlen=130) # 130 weeks (2.5 years) in length
		self.balance_history_dates: Deque[datetime] = collections.deque(maxlen=130)

		self.consecutive_weeks_in_debt = 0
		self.transport_costs_model = TransportCostsModel(self.model)
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
		return self.prize_money + self.total_sponsorship + self.drivers_payments
	
	@property
	def total_expenditure(self) -> int:
		#TODO remove hard coding of race costs
		return int(self.total_staff_costs_per_year + self.drivers_salary + self.team_model.technical_director_model.contract.salary + self.team_model.commercial_manager_model.contract.salary + 8_000_000 + self.car_cost)
	
	def weekly_update(self) -> None:
		
		# add prize money
		self.balance += int(self.prize_money / 52)

		# add sponsorship
		self.balance += int(self.total_sponsorship / 52)

		# staff cost
		self.balance -= int((self.staff_yearly_cost / 52) * self.team_model.number_of_staff)

		# Drivers cost
		self.balance -= int(self.team_model.driver1_model.contract.salary / 52)
		self.balance -= int(self.team_model.driver2_model.contract.salary / 52)

		# manager costs
		self.balance -= int(self.team_model.technical_director_model.contract.salary / 52)
		self.balance -= int(self.team_model.commercial_manager_model.contract.salary / 52)
		
		self.update_balance_history()

		if self.balance < 0:
			self.consecutive_weeks_in_debt += 1
		else:
			self.consecutive_weeks_in_debt = 0
		
	def apply_race_costs(self) -> None:
		self.transport_costs_model.gen_race_transport_cost()
		self.balance -= self.transport_costs_model.costs_by_race[-1]
	
	def update_balance_history(self) -> None:
		self.balance_history.append(self.balance)
		self.balance_history_dates.append(datetime(self.model.year, 1, 1) + timedelta(weeks=self.model.season.current_week - 1))

	def update_prize_money(self, finishing_position: int) -> None:
		self.prize_money = calculate_prize_money(finishing_position)

		self.model.inbox.new_prize_money_email(self.prize_money)

	def update_facilities_cost(self, cost: int) -> None:
		self.balance -= cost

	def end_season(self) -> None:
		# determine sponsorship
		sponsorship = self.team_model.commercial_manager_model.determine_yearly_sponsorship()

		self.model.inbox.new_sponsor_income_email(sponsorship)
		self.total_sponsorship = sponsorship
		self.season_opening_balance = self.balance

	def to_dict(self) -> dict[str, Union[int, list[Union[int, str]]]]:
		return {
			"balance": self.balance,
			"staff_yearly_cost": self.staff_yearly_cost,
			"prize_money": self.prize_money,
			"total_sponsorship": self.total_sponsorship,
			"balance_history": list(self.balance_history),
			"balance_history_dates": [d.strftime("%Y-%m-%d") for d in self.balance_history_dates],
		}