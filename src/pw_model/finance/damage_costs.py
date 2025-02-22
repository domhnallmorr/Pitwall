import random

class DamageCosts:
	def __init__(self) -> None:
		self.randomiser = DamageRandomiser()
		self.setup_new_season()


	def setup_new_season(self) -> None:
		self.damage_costs :list[int] = []
		self.damage_costs_this_season = 0

	def calculate_race_damage_costs(self, player_driver1_crashed: bool, player_driver2_crashed: bool) -> None:
		self.driver1_latest_crash_cost = 0
		self.driver2_latest_crash_cost = 0

		if player_driver1_crashed is True:
			self.driver1_latest_crash_cost = self.calculate_crash_cost()
		
		if player_driver2_crashed is True:
			self.driver2_latest_crash_cost = self.calculate_crash_cost()

		self.damage_costs.append(self.driver1_latest_crash_cost + self.driver2_latest_crash_cost)
		self.damage_costs_this_season += self.damage_costs[-1]

	def calculate_crash_cost(self) -> int:
		"""Determines the crash repair cost based on predefined probability bins."""
		ranges = [
			(50_000, 150_000, 0.5),  # 50% chance of minor damage
			(150_000, 300_000, 0.3), # 30% chance of moderate damage
			(300_000, 450_000, 0.15),# 15% chance of severe damage
			(450_000, 500_000, 0.05) # 5% chance of very severe damage
		]

		cost = self.randomiser.calculate_random_cost(ranges)

		return cost

class DamageRandomiser:
	def __init__(self) -> None:
		pass

	def calculate_random_cost(self, ranges: list[tuple[int, int, float]]) -> int:
		selected_range = random.choices(ranges, weights=[r[2] for r in ranges])[0]

		return random.randint(selected_range[0], selected_range[1])
