from pw_model.track import track_model

class CarModel:
	def __init__(self, speed: int):
		self.speed = speed

		self.fuel_load = 155 # kg
		self.tyre_wear = 0 # time lost (in ms) due to tyre wear

	def update_speed(self, speed: int) -> None:
		assert speed > 0 and speed <= 100, f"Invalid speed: {speed}"
		
		self.speed = speed

	def update_fuel(self, circuit_model: track_model.TrackModel) -> None:
		self.fuel_load -= circuit_model.fuel_consumption
		self.fuel_load = round(self.fuel_load, 2)

	def update_tyre_wear(self, circuit_model: track_model.TrackModel, new_tyres: bool=False) -> None:
		if new_tyres is False:
			self.tyre_wear += circuit_model.tyre_wear
		else: # made a pitstop, new tyres fitted
			self.tyre_wear = 0

	@property
	def fuel_effect(self) -> int:
		'''
		effect of fuel on lap time
		assume 1kg adds 0.03s to laptime
		'''
		return int(self.fuel_load * 30)

	def calculate_required_fuel(self, circuit_model: track_model.TrackModel, number_of_laps: int) -> int:
		number_of_laps_conservative = float(number_of_laps) + 0.5 # ensure half a lap of fuel is added for conservatism
		
		return int(number_of_laps_conservative * circuit_model.fuel_consumption)

	def setup_start_fuel_and_tyres(self, circuit_model: track_model.TrackModel, first_stop_lap: int) -> None:
		self.fuel_load = self.calculate_required_fuel(circuit_model, first_stop_lap)
		self.tyre_wear = 0 # fit new tyres
		
	def implement_car_development(self, speed_increase: int) -> None:
		self.speed += speed_increase
		