'''
This is base model for all on track elements of the game
It's purpose is to
	setup the paricipants in the event
	setup the individual sesssion
	Hold results from each session
	It also has an instance variable of the track_model for the event
'''
import copy
import random
from enum import Enum

from pw_model import pw_base_model
from pw_model.track import track_model
from race_weekend_model import qualy_model, grand_prix_model
from race_weekend_model import particpant_model
from race_weekend_model.starting_grid import StartingGrid
from race_weekend_model.race_model_enums import SessionNames, SessionStatus, SessionMode
from race_weekend_model.race_randomiser import RaceRandomiser
from race_weekend_model.particpant_model import ParticpantModel

class RaceWeekendModel:
	def __init__(self, mode: str, model: pw_base_model.Model, track_model: track_model.TrackModel):
		assert mode in ["UI", "headless"], f"Unsupported Mode {mode}" # headless is model only, UI means were using the GUI

		self.mode = mode
		self.model = model
		self.track_model = track_model
		self.randomiser = RaceRandomiser()
		self.setup_participants(model)

		self.results = {}

		# Initialize these as None by default
		self.player_driver1_participant = None
		self.player_driver2_participant = None

		# Only try to set player participants if we have a player team
		if self.model.player_team_model is not None:
			for particpant in self.participants:
				if particpant.driver.name == self.model.player_team_model.driver1:
					self.player_driver1_participant = particpant
				elif particpant.driver.name == self.model.player_team_model.driver2:
					self.player_driver2_participant = particpant

	def setup_participants(self, model: pw_base_model.Model) -> None:
		# Setup an Paricipant class instance for each competitor
		# A participant is the combination of a car and a driver
		self.participants: ParticpantModel = []

		driver_count = 0
		for team in model.teams:
			for driver in [team.driver1_model, team.driver2_model]:
				driver_count += 1
				self.participants.append(particpant_model.ParticpantModel(driver, team.name, copy.deepcopy(team.car_model), self.track_model, driver_count))

	def get_particpant_model_by_name(self, name: str) -> ParticpantModel:
		for p in self.participants:
			if p.name == name:
				return p
			
	def setup_practice(self, session_time: int, session_name: str) -> None:
		self.current_session_name = session_name
		self.current_session = practice_model.PracticeModel(self, session_time)
		self.setup_session()

	def setup_qualifying(self,
					  session_time: int,# in seconds e.g. 60*60 for 1 hr
					  session_type: Enum) -> None:
		assert session_type == SessionNames.QUALIFYING # session is a variable for future development of Q1, Q2, Q3, for the 1998 1hr qualfy
		
		self.current_session_name = session_type.value	
		self.current_session = qualy_model.QualyModel(self, session_time)
		self.setup_session()
		self.current_session.generate_results()

	def setup_race(self) -> None:
		self.starting_grid = StartingGrid(self)
		self.current_session_name = SessionNames.RACE.value
		self.current_session = grand_prix_model.GrandPrixModel(self)
		self.setup_session()

	def setup_session(self) -> None:
		for p in self.participants:
			p.setup_variables_for_session()

	def update_player_drivers_strategy(self, driver1_data, driver2_data) -> None:
		self.player_driver1.update_player_pitstop_laps(driver1_data)
		self.player_driver2.update_player_pitstop_laps(driver2_data)

	def simulate_session(self) -> None:
		while self.current_session.status != SessionStatus.POST_SESSION:
			self.current_session.advance(SessionMode.SIMULATE)

