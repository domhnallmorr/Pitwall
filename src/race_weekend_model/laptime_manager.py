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
	LAP1_TIME_LOSS_PER_POSITION,
	MAX_SPEED,
	DRIVER_SPEED_FACTOR,
	LAP1_TIME_LOSS,
	LAP_TIME_VARIATION_BASE,
	LAP_TIME_VARIATION,
	POWER_SENSITIVITY,
)

if TYPE_CHECKING:
	from race_weekend_model.particpant_model import ParticpantModel

class LapTimeManager:
	def __init__(self, participant: ParticpantModel):
		self.participant = participant
		self.randomiser = LapManagerRandomiser(self.participant)
		self.driver = participant.driver
		self.car_model = participant.car_model
		self.car_state = participant.car_state
		self.track_model = participant.track_model
		self.calculate_base_laptime()
		additonal_laptime_variaton = int((1 - (self.driver.consistency / 100)) * LAP_TIME_VARIATION)
		self.laptime_variation = LAP_TIME_VARIATION_BASE + additonal_laptime_variaton

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
		'''
		Fastest potential laptime a driver/car combination can achieve
		'''
		self.base_laptime = self.track_model.base_laptime

		# add driver component
		'''
		driver with 0 speed rating is considered 2s slower than driver with 100 speed rating
		'''
		self.base_laptime += (MAX_SPEED - self.driver.speed) * DRIVER_SPEED_FACTOR # 100 * 20 = 2000 (2s in ms)

		# determine power effect
		power_effect = self.calculate_engine_power_effect()
		self.base_laptime += power_effect # add power effect to base laptime

		# add car component
		'''
		car with 0 speed rating is considered 5s slower than car with 100 speed rating
		'''
		self.base_laptime += (MAX_SPEED - self.car_model.speed) * CAR_SPEED_FACTOR

	def calculate_engine_power_effect(self) -> int:
		"""Calculate time loss/gain due to engine power and track sensitivity"""
		# Get engine power (0-100 scale) from engine supplier
		engine_power = self.participant.team_model.engine_supplier_model.power
		
		# Track power sensitivity (1-10) affects how much engine power matters
		track_power_sensitivity = self.participant.track_model.power
		
		# Calculate power effect
		# POWER_SENSITIVITY (2000ms = 2s) is the maximum possible effect at power sensitivity 10
		# At sensitivity 1, effect is reduced to 10% of maximum
		power_effect = (POWER_SENSITIVITY * track_power_sensitivity / 10)
		
		# A power rating of 50 is neutral (no gain/loss)
		# Below 50 loses time, above 50 gains time
		return int(power_effect * (50 - engine_power) / 100)

	def setup_variables_for_session(self) -> None:
		self.laptime = None
		self.laptimes: list[int] = []

	def calculate_laptime(self, dirty_air_effect: int) -> None:
		'''
		Calculate the laptime for a given lap
		if pitting, the time loss in the pits is accounted for
		'''
		random_time_loss = self.randomiser.random_laptime_loss()
		self.laptime = self.base_laptime + random_time_loss + self.car_state.fuel_effect + self.car_state.tyre_wear + dirty_air_effect

		# ADD PIT STOP LOSS IF APPLICABLE
		if self.participant.status is ParticipantStatus.PITTING_IN:
			self.laptime += self.track_model.pit_stop_loss
			self.laptime += self.participant.pitstop_times[-1] 

	def complete_lap(self) -> None:
		if self.laptime is not None:
			self.laptimes.append(self.laptime)

	def calculate_qualfying_laptime(self) -> None:
		'''
		Basic method for calculating a laptime in qualfying
		'''
		self.calculate_laptime(0) # zero for no dirty air effect
		self.complete_lap()

	def calculate_first_lap_laptime(self, idx: int) -> None:
		'''
		calculate lap time for first lap based on position after turn 1
		idx is the position (zero indexed) of the participant after turn 1
		'''
		random_time_loss = self.randomiser.random_lap1_time_loss()
		self.laptime = self.track_model.base_laptime + LAP1_TIME_LOSS + (idx * LAP1_TIME_LOSS_PER_POSITION) + random_time_loss

	def recalculate_laptime_when_passed(self, revised_laptime: int) -> None:
		'''
		When a car is passed, laptime needs to be increased to account for time lost
		The laptime calculated already is void
		The new laptime is calculated in the grand prix model
		This ensures the passed car's total time is greater than the overtaking car
		'''
		if self.laptime is not None:
			self.laptime = revised_laptime
			self.laptimes[-1] = revised_laptime

class LapManagerRandomiser:
	def __init__(self, participant: ParticpantModel):
		self.participant = participant

	def random_lap1_time_loss(self) -> float:
		# random amount of time lost on lap 1, given in ms
		return random.uniform(100, 800)
	
	def random_laptime_loss(self) -> float:
		return random.uniform(0, self.participant.laptime_manager.laptime_variation)