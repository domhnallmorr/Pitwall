from enum import Enum

class CarDevelopmentCostsEnums(Enum):
	MINOR = 100_000    
	MEDIUM = 750_000 
	MAJOR = 1_500_000  

class CarDevelopmentCosts:
	def __init__(self) -> None:
		self.setup_new_season()

	def setup_new_season(self) -> None:
		self.development_costs = 0
		self.weekly_payment = 0
		self.weeks_remaining = 0
		self.costs_this_season = 0

	def start_development(self, total_cost: int, weeks: int) -> None:
		"""
		Calculate weekly payments for a new development project
		"""
		self.weekly_payment = int(total_cost / weeks)
		self.weeks_remaining = weeks

	def process_weekly_payment(self) -> int:
		"""
		Returns the weekly payment amount if development is ongoing, 0 otherwise
		"""
		if self.weeks_remaining > 0:
			self.development_costs += self.weekly_payment
			self.costs_this_season += self.weekly_payment
			self.weeks_remaining -= 1
			return self.weekly_payment
		return 0

	def development_in_progress(self) -> bool:
		return self.weeks_remaining > 0

