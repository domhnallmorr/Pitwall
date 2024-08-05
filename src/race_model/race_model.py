import random

# from race_engine_model import race_engine_circuit_model, race_engine_particpant_model, race_engine_car_model, race_engine_driver_model
from race_model import practice_model, qualy_model, grand_prix_model
from race_model import particpant_model

class RaceModel:
	def __init__(self, mode, model, track_model):
		assert mode in ["UI", "headless"], f"Unsupported Mode {mode}" # headless is model only, UI means were using the GUI

		self.mode = mode
		self.model = model
		self.track_model = track_model
		self.setup_participants(model)

		self.results = {}
	
	def setup_participants(self, model):
		self.participants = []

		driver_count = 0
		for team in model.teams:
			for driver in [team.driver1_model, team.driver2_model]:
				driver_count += 1
				self.participants.append(particpant_model.ParticpantModel(driver, team.car_model, self.track_model, driver_count))

	def get_particpant_model_by_name(self, name):
		for p in self.participants:
			if p.name == name:
				return p
			
	def setup_practice(self, session_time, session_name):
		self.current_session_name = session_name
		self.current_session = practice_model.PracticeModel(self, session_time)
		self.setup_session()

	def setup_qualfying(self, session_time, session_name):
		self.current_session_name = session_name
		self.current_session = qualy_model.QualyModel(self, session_time)
		self.setup_session()

	def setup_race(self):
		self.current_session_name = "Race"
		self.current_session = grand_prix_model.GrandPrixModel(self)
		self.setup_session()

	def setup_session(self):
		for p in self.participants:
			p.setup_variables_for_session()

	def update_player_drivers_strategy(self, driver1_data, driver2_data):
		self.player_driver1.update_player_pitstop_laps(driver1_data)
		self.player_driver2.update_player_pitstop_laps(driver2_data)

	def simulate_session(self):
		while self.current_session.status not in ["post_session", "post_race"]:
			self.current_session.advance("simulate")

