import random

from pw_model.driver.driver_model import DriverModel
from pw_model.car.car_model import CarModel
from pw_model.track.track_model import TrackModel
from race_weekend_model.pit_strategy import PitStrategy
from race_weekend_model.laptime_manager import LapTimeManager
from race_weekend_model.race_model_enums import ParticipantStatus
from race_weekend_model.on_track_constants import (
	DIRTY_AIR_THRESHOLD,
	DIRTY_AIR_EFFECT,
	RETIREMENT_CHANCE,
	LAP_TIME_VARIATION,
	PIT_STOP_LOSS_RANGE,
)

class ParticpantModel:
	def __init__(self, driver: DriverModel,
			  team_name: str, car: CarModel, track_model: TrackModel, starting_position: int):
		self.driver = driver
		self.team_name = team_name
		self.car_model = car
		self.track_model = track_model
		self.position = starting_position

		self.laptime_manager = LapTimeManager(self)
		self.pit_strategy = PitStrategy(self.track_model.number_of_laps)
		self.calculate_if_retires()

	def __repr__(self) -> str:
		return f"<RaceEngineParticpantModel {self.driver.name}>"

	@property
	def linestyle(self) -> str:
		if self.driver.driver_status == 2:
			return "--"
		else:
			return "-"

	@property
	def name(self) -> str:
		return str(self.driver.name)

	def setup_variables_for_session(self) -> None:
		# the core variables associated with a participant for a given session, laptimes, current_lap, etc
		self.current_lap = 1

		self.gaps_to_leader: list[int] = []
		self.total_time = 0 # total time to complete the laps run so far
		self.pitstop_times: list[int] = []
		self.pitstop_laps: list[int] = [] # lap on which pitstop occured, updated when participant pits
		self.positions_by_lap: list[int] = [] # not zero indexed
		self.tyre_wear_by_lap: list[int] = [] # not zero indexed

		self.practice_laps_completed = 0
		
		self.number_of_pitstops = 0
		self.starting_position = None # not zero indexed, set in StartingGrid class

		self.status = ParticipantStatus.IN_PITS
		self.attacking = False
		self.defending = False

		self.laptime_manager.setup_variables_for_session()
		# self.laptime = None

		# self.next_update_time = None # for updating practice session


	def calculate_laptime(self, gap_ahead: int) -> None:
		# reset status if we just made a pitstop
		if self.status is ParticipantStatus.PITTING_IN:
			self.status = ParticipantStatus.RUNNING

		# CHECK IF RETIRES THIS LAP
		if self.retires is True and self.retire_lap == self.current_lap:
			self.status = ParticipantStatus.RETIRED

		# DON'T RETIRE, CALCULATE LAPTIME
		else:
			dirty_air_effect = 0
			if gap_ahead:
				if gap_ahead <= DIRTY_AIR_THRESHOLD:
					dirty_air_effect = DIRTY_AIR_EFFECT # assume we lose half a second in dirty air (1.5s or less behind car in front)

			if self.current_lap in self.pit_strategy.pit_laps:
				self.status = ParticipantStatus.PITTING_IN

			if self.status is ParticipantStatus.PITTING_IN:
				# self.laptime += self.track_model.pit_stop_loss
				self.pitstop_times.append(random.randint(PIT_STOP_LOSS_RANGE[0], PIT_STOP_LOSS_RANGE[1]))
				# self.laptime += self.pitstop_times[-1] 
				self.number_of_pitstops += 1
				self.pitstop_laps.append(self.current_lap)
			
			self.laptime_manager.calculate_lap_time(LAP_TIME_VARIATION, dirty_air_effect)	

	def complete_lap(self) -> None:
		self.laptime_manager.complete_lap()
		# self.total_time += self.laptime_manager.laptime

		new_tyres = False
		if self.current_lap in self.pit_strategy.pit_laps: # handle change tyres and fuel during pitstop
			self.update_pitstop_tyres_fuel()
		else:		
			self.update_fuel_and_tyre_wear(new_tyres)

		self.current_lap += 1

	def update_fuel_and_tyre_wear(self, new_tyres: bool=False) -> None:
		self.car_model.update_fuel(self.track_model)
		self.car_model.update_tyre_wear(self.track_model, new_tyres)

		self.tyre_wear_by_lap.append(self.car_model.tyre_wear)

	def update_pitstop_tyres_fuel(self) -> None:
		self.car_model.tyre_wear = 0

		planned_laps = self.pit_strategy.lap_ranges
		planned_laps = [l for l in planned_laps if l is not None]# remove None if assigned to pit2/3 lap
		planned_laps = [l for l in planned_laps if l > self.current_lap]

		required_laps = min(planned_laps) - self.current_lap
		
		self.car_model.fuel_load = self.car_model.calculate_required_fuel(self.track_model, required_laps)
		
	def calculate_if_retires(self) -> None:
		self.retires = False
		self.retire_lap = None

		if random.randint(0, 100) < RETIREMENT_CHANCE:
			self.retires = True
			self.retire_lap = random.randint(3, self.track_model.number_of_laps)

	def setup_start_fuel_and_tyres(self) -> None:
		# for grand prix only (called in GrandPrix contructor)
		# setup the fuel and tyres for the start of the race
		self.car_model.setup_start_fuel_and_tyres(self.track_model, self.pit_strategy.pit1_lap)

