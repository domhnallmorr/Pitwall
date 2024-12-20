import random

from pw_model.driver.driver_model import DriverModel
from pw_model.car.car_model import CarModel
from pw_model.track.track_model import TrackModel

class ParticpantModel:
	def __init__(self, driver: DriverModel,
			  team_name: str, car: CarModel, circuit: TrackModel, starting_position: int):
		self.driver = driver
		self.team_name = team_name
		self.car_model = car
		self.circuit_model = circuit #TODO should probably rename this track model for consistancy
		self.position = starting_position


		self.calculate_base_laptime()
		self.calculate_pitstop_laps()
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

		self.laptimes: list[int] = []
		self.gaps_to_leader: list[int] = []
		self.total_time = 0 # total time to complete the laps run so far
		self.pitstop_times: list[int] = []
		self.pitstop_laps: list[int] = [] # lap on which pitstop occured, updated when participant pits
		self.positions_by_lap: list[int] = [] # not zero indexed
		self.tyre_wear_by_lap: list[int] = [] # not zero indexed
		self.number_of_pitstops = 0
		self.starting_position = None # not zero indexed

		self.status = "in_pit"
		self.attacking = False
		self.defending = False

		self.fastest_laptime = None
		# self.laptime = None

		# self.next_update_time = None # for updating practice session

	def calculate_base_laptime(self) -> None:
		self.base_laptime = self.circuit_model.base_laptime

		# add driver component
		'''
		driver with 0 speed rating is considered 3s slower than driver with 100 speed rating
		'''
		self.base_laptime += (100 - self.driver.speed) * 2_0 # 100 * 20 = 2000 (2s in ms)

		# add car component
		'''
		car with 0 speed rating is considered 5s slower than car with 100 speed rating
		'''
		self.base_laptime += (100 - self.car_model.speed) * 5_0

		# print(f"{self.name}: {self.base_laptime}")

	def calculate_laptime(self, gap_ahead: int) -> None:
		# reset status if we just made a pitstop
		if "pitting in" in self.status:
			self.status = "running"

		# CHECK IF RETIRES THIS LAP
		if self.retires is True and self.retire_lap == self.current_lap:
			self.status = "retired"

		# DON'T RETIRE, CALCULATE LAPTIME
		else:
			dirty_air_effect = 0
			if gap_ahead:
				if gap_ahead <= 1_500:
					dirty_air_effect = 500 # assume we lose half a second in dirty air (1.5s or less behind car in front)

			self.calculate_lap_time(700, dirty_air_effect)	

			if self.current_lap in [self.pit1_lap, self.pit2_lap, self.pit3_lap]:
				self.status = "pitting in"

			if "pitting in" in self.status:
				self.laptime += self.circuit_model.pit_stop_loss
				self.pitstop_times.append(random.randint(3_800, 6_000))
				self.laptime += self.pitstop_times[-1] 
				self.number_of_pitstops += 1
				self.pitstop_laps.append(self.current_lap)

	def calculate_lap_time(self, random_element: int, dirty_air_effect: int) -> None:
		self.laptime = self.base_laptime + random.randint(0, random_element) + self.car_model.fuel_effect + self.car_model.tyre_wear + dirty_air_effect

	def complete_lap(self) -> None:
		self.laptimes.append(self.laptime)
		self.total_time += self.laptime

		new_tyres = False
		if self.current_lap in [self.pit1_lap, self.pit2_lap, self.pit3_lap]: # handle change tyres and fuel during pitstop
			self.update_pitstop_tyres_fuel()
		else:		
			self.update_fuel_and_tyre_wear(new_tyres)

		self.current_lap += 1

	def update_fuel_and_tyre_wear(self, new_tyres: bool=False) -> None:
		self.car_model.update_fuel(self.circuit_model)
		self.car_model.update_tyre_wear(self.circuit_model, new_tyres)

		self.tyre_wear_by_lap.append(self.car_model.tyre_wear)

	def update_pitstop_tyres_fuel(self) -> None:
		self.car_model.tyre_wear = 0

		planned_laps = [self.pit1_lap, self.pit2_lap, self.pit3_lap, self.circuit_model.number_of_laps]
		planned_laps = [l for l in planned_laps if l is not None]# remove None if assigned to pit2/3 lap
		planned_laps = [l for l in planned_laps if l > self.current_lap]

		required_laps = min(planned_laps) - self.current_lap
		
		self.car_model.fuel_load = self.car_model.calculate_required_fuel(self.circuit_model, required_laps)

	def recalculate_laptime_when_passed(self, revised_laptime: int) -> None:
		self.total_time -= self.laptimes[-1]
		self.total_time += revised_laptime
		self.laptime = revised_laptime
		self.laptimes[-1] = revised_laptime
		
	def calculate_pitstop_laps(self) -> None:
		self.number_of_planned_stops = random.choice([1, 2, 3])

		# set default None values for pit stops 2 and 3
		self.pit2_lap = None
		self.pit3_lap = None

		half_distance = int(self.circuit_model.number_of_laps / 2)
		third_distance = int(self.circuit_model.number_of_laps / 3)
		two_thirds_distance = int(third_distance * 2)
		quarter_distance = int(self.circuit_model.number_of_laps / 4)
		three_quarters_distance = int(quarter_distance * 3)

		if self.number_of_planned_stops == 1:
			self.pit1_lap = random.randint(half_distance - 5, half_distance + 5)

		elif self.number_of_planned_stops == 2:
			self.pit1_lap = random.randint(third_distance - 3, third_distance + 3)
			self.pit2_lap = random.randint(two_thirds_distance - 3, two_thirds_distance + 3)

		elif self.number_of_planned_stops == 3:
			self.pit1_lap = random.randint(quarter_distance - 2, quarter_distance + 2)
			self.pit2_lap = random.randint(half_distance - 2, half_distance + 2)
			self.pit3_lap = random.randint(three_quarters_distance - 2, three_quarters_distance + 2)

	def calculate_if_retires(self) -> None:
		self.retires = False
		self.retire_lap = None

		if random.randint(0, 100) < 20:
			self.retires = True
			self.retire_lap = random.randint(3, self.circuit_model.number_of_laps)

	def update_fastest_lap(self) -> None:
		if self.fastest_laptime is None:
			self.fastest_laptime = self.laptime
		elif min(self.laptimes) == self.laptime:
			self.fastest_laptime = self.laptime

	def update_player_pitstop_laps(self, data: dict[str, int]) -> None:
		'''
		data is a dict optained from the view
		{
		"pit1_lap": 24,
		"pit2_lap": ... etc
		}
		'''
		self.pit1_lap = data["pit1_lap"]
		self.pit2_lap = data["pit2_lap"]
		self.pit3_lap = data["pit3_lap"]

	def setup_session(self) -> None:
		self.practice_laps_completed = 0
		self.practice_runs: list[list[int]] = [] # [[time_left, fuel, number_laps]]

	def setup_start_fuel_and_tyres(self) -> None:
		# for grand prix only (called in GrandPrix contructor)
		# setup the fuel and tyres for the start of the race
		self.car_model.setup_start_fuel_and_tyres(self.circuit_model, self.pit1_lap)

	def generate_practice_runs(self, session_time: int, session: str) -> None:
		assert session in ["FP"], f"Unsupported Session {session}"

		time_left = int(session_time)

		while time_left > 0:
			leave_time = random.randint(time_left - (20*60), time_left)
			number_laps = random.randint(3, 10)
			min_fuel_load = int(self.circuit_model.fuel_consumption * number_laps) + 1
			fuel_load = random.randint(min_fuel_load, 155)

			self.practice_runs.append([leave_time, fuel_load, number_laps])

			base_laptime_seconds = self.circuit_model.base_laptime / 1000
			time_left -= number_laps * (base_laptime_seconds + 10)
			
			time_in_pits = random.randint(15, 35) * 60
			time_left -= time_in_pits
			
			time_left = int(time_left) # ensure time left is an int (for randint)

	def generate_qualy_runs(self) -> None:
		# ASSUMES 1 HOUR QUALY, 12 laps (4 runs, 3 laps each)

		number_laps = 3
		fuel_load = 3

		# RUN 1
		leave_time = random.randint(3_000, 3_550)
		self.practice_runs.append([leave_time, fuel_load, number_laps])

		# RUN 2
		leave_time = random.randint(1_960, 2_760)
		self.practice_runs.append([leave_time, fuel_load, number_laps])

		# RUN 3
		leave_time = random.randint(1_060, 1_860)
		self.practice_runs.append([leave_time, fuel_load, number_laps])

		# RUN 4
		leave_time = random.randint(190, 900)
		self.practice_runs.append([leave_time, fuel_load, number_laps])

	def check_leaving_pit_lane(self, time_left: int) -> bool:
		leaving = False

		if len(self.practice_runs) > 0:
			for run in self.practice_runs:
				if run[0] >= time_left:
					leaving = True
					self.pit_in_lap = self.practice_laps_completed + run[2]
					break
		
		if leaving is True:
			self.car_model.tyre_wear = 0
			self.car_model.fuel_load = self.practice_runs[0][1]
			self.practice_runs.pop(0)

			self.update_next_update_time(time_left)
			self.status = "running"
			self.laptime = 120_000 # outlap time

		return leaving
	
	def update_practice(self, time_left: int) -> None:
		self.update_fuel_and_tyre_wear()
		
		if self.practice_laps_completed == self.pit_in_lap:
			self.status = "in_pit"
		else:
			self.practice_laps_completed += 1
			self.calculate_lap_time(700, 0)

			if self.practice_laps_completed == self.pit_in_lap:
				self.laptime += 6_000 # make in lap slow
				
			if self.fastest_laptime is None:
				self.fastest_laptime = self.laptime
			else:
				if self.laptime < self.fastest_laptime:
					self.fastest_laptime = self.laptime
				
			self.update_next_update_time(time_left)

	def update_next_update_time(self, time_left: int) -> None:
		self.next_update_time = time_left - 90

	def send_player_car_out(self, time_left: int, fuel_load_laps: int, number_laps_to_run: int) -> None:
		fuel_load_kg = self.car_model.calculate_required_fuel(fuel_load_laps)
		# TODO fix hard coding of -10 seconds below
		self.practice_runs.append([time_left-10, fuel_load_kg, number_laps_to_run])