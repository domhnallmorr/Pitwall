import random
from typing import Optional

class PitStrategy:
	def __init__(self, number_of_laps: int):
		self.number_of_laps = number_of_laps
		self.determine_number_of_stops()
		self.calculate_pitstop_laps()

	@property
	def lap_ranges(self) -> list[Optional[int]]:
		'''
		List of laps to stop and the number of laps
		Used in pit stops to know how much fuel is required to be put in
		'''
		laps = self.pit_laps
		laps.append(self.number_of_laps)
              
		return laps 

	@property
	def pit_laps(self) -> list[Optional[int]]:
		return [self.pit1_lap, self.pit2_lap, self.pit3_lap]

	def calculate_pitstop_laps(self) -> None:
		"""
        Calculate the laps for pitstops based on the number of planned stops.
        Returns a dictionary with pitstop laps.
        """
		half_distance = self.number_of_laps // 2
		third_distance = self.number_of_laps // 3
		quarter_distance = self.number_of_laps // 4

		self.pit1_lap = None
		self.pit2_lap = None
		self.pit3_lap = None

		if self.planned_stops == 1:
			self.pit1_lap = random.randint(half_distance - 5, half_distance + 5)

		elif self.planned_stops == 2:
			self.pit1_lap = random.randint(third_distance - 3, third_distance + 3)
			self.pit2_lap = random.randint((third_distance * 2) - 3, (third_distance * 2) + 3)

		elif self.planned_stops == 3:
			self.pit1_lap = random.randint(quarter_distance - 2, quarter_distance + 2)
			self.pit2_lap = random.randint(half_distance - 2, half_distance + 2)
			self.pit3_lap = random.randint((quarter_distance * 3) - 2, (quarter_distance * 3) + 2)

	def determine_number_of_stops(self) -> None:
		"""
		Randomly determine the number of planned pitstops (1, 2, or 3).
        """
		self.planned_stops = random.choice([1, 2, 3])
