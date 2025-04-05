import random

class RaceRandomiser:
	@staticmethod
	def run_to_turn1_random_factor(driver_name: str) -> float:
		return random.uniform(-2.0, 2.0)
	
	@staticmethod
	def turn1_incident_occurred() -> int:
		return random.randint(0, 100)
	
	@staticmethod
	def spin_victim_idx(number_of_participants: int) -> int:
		return random.randint(0, number_of_participants - 1)
	
	@staticmethod
	def turn1_spin_time_loss() -> float:
		return random.randint(5_000, 20_000) # 5-20s time loss