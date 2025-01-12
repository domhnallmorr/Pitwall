'''
A class for computing laptimes
and storing pervious laptimes
'''
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import random

from race_weekend_model.race_model_enums import ParticipantStatus
from race_weekend_model.on_track_constants import (
	CAR_SPEED_FACTOR,
	DIRTY_AIR_THRESHOLD,
	DIRTY_AIR_EFFECT,
	DRIVER_SPEED_FACTOR,
	RETIREMENT_CHANCE,
	LAP_TIME_VARIATION,
	PIT_STOP_LOSS_RANGE,
)

if TYPE_CHECKING:
	from race_weekend_model.particpant_model import ParticpantModel

class LapTimeManager:
	def __init__(self, participant: ParticpantModel):
		self.participant = participant
		self.driver = participant.driver
		self.car_model = participant.car_model
		self.track_model = participant.track_model
		self.calculate_base_laptime()

	@property
	def total_time(self) -> int:
		return sum(self.laptimes)
	
	@property
	def fastest_lap(self) -> Optional[int]:
		if len(self.laptimes) == 0:
			return None
		else:
			return min(self.laptimes)
		
	def calculate_base_laptime(self) -> None:
		self.base_laptime = self.track_model.base_laptime

		# add driver component
		'''
		driver with 0 speed rating is considered 2s slower than driver with 100 speed rating
		'''
		self.base_laptime += (100 - self.driver.speed) * DRIVER_SPEED_FACTOR # 100 * 20 = 2000 (2s in ms)

		# add car component
		'''
		car with 0 speed rating is considered 5s slower than car with 100 speed rating
		'''
		self.base_laptime += (100 - self.car_model.speed) * CAR_SPEED_FACTOR

	def setup_variables_for_session(self) -> None:
		self.laptime = None
		self.laptimes: list[int] = []

	def calculate_lap_time(self, random_element: int, dirty_air_effect: int) -> None:
		self.laptime = self.base_laptime + random.randint(0, random_element) + self.car_model.fuel_effect + self.car_model.tyre_wear + dirty_air_effect

		# ADD PIT STOP LOSS IF APPLICABLE
		if self.participant.status is ParticipantStatus.PITTING_IN:
			self.laptime += self.track_model.pit_stop_loss
			self.laptime += self.participant.pitstop_times[-1] 

	def complete_lap(self) -> None:
		if self.laptime is not None:
			self.laptimes.append(self.laptime)

	def calculate_qualfying_laptime(self) -> None:
		self.calculate_lap_time(700, 0)
		self.complete_lap()

	def calculate_first_lap_laptime(self, idx: int) -> None:
		'''
		calculate lap time for first lap based on position after turn 1
		'''
		self.laptime = self.track_model.base_laptime + 6_000 + (idx * 1_000) + random.randint(100, 800)

	def recalculate_laptime_when_passed(self, revised_laptime: int) -> None:
		if self.laptime is not None:
			self.laptime = revised_laptime
			self.laptimes[-1] = revised_laptime

