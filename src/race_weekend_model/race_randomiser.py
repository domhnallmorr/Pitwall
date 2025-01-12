import random

class RaceRandomiser:
	@staticmethod
	def run_to_turn1_random_factor(driver_name: str) -> float:
		return random.uniform(-2.0, 2.0)