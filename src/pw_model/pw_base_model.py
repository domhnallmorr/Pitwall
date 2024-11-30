import logging
import statistics
from typing import List, Union


from pw_model import load_roster
from pw_model.season import season_model
from pw_model.email import email_model
from pw_model.staff_market import staff_market
from pw_model.pw_model_enums import StaffRoles
from pw_model.staff_market import manager_transfers
from pw_model import load_save
from pw_model.track.track_model import TrackModel
from pw_model.driver.driver_model import DriverModel
from pw_model.team.team_model import TeamModel
from pw_model.senior_staff.commercial_manager import CommercialManager
from pw_model.senior_staff.technical_director import TechnicalDirector

class Model:
	def __init__(self, roster: str, run_directory: str, mode: str="normal", auto_save: bool=True):
		
		assert mode in ["normal", "headless"]

		# logging.basicConfig(filename=f"{run_directory}\\log.txt", filemode="w", level=logging.DEBUG)
		logging.basicConfig(level=logging.DEBUG)

		self.run_directory = run_directory
		self.auto_save = auto_save

		self.inbox = email_model.Inbox(self)
		self.tracks: List[TrackModel] = []
		self.retired_drivers: List[DriverModel] = []
		self.teams: List[TeamModel] = [] # gets populated in the load_roster function
		self.future_drivers: List[DriverModel] = []
		self.drivers: List[DriverModel] = []
		self.commercial_managers: List[CommercialManager] = []
		self.technical_directors: List[TechnicalDirector] = []
		self.future_managers: List[Union[CommercialManager, TechnicalDirector]] = []

		if roster is not None:
			load_roster.load_roster(self, roster)
		
		self.player_team = self.teams[0].name # set player team initally to first team in roster. This is so the view can setup all the pages on startup
		self.year = 1998
		self.season = season_model.SeasonModel(self)

		self.staff_market = staff_market.StaffMarket(self)
		self.end_season(increase_year=False, start_career=True)

		if mode == "headless":
			self.player_team = None
			# this is called in start_career method, when player is  (mode=normal)
			self.staff_market.compute_transfers()

	@property
	def player_team_model(self) -> TeamModel:
		return self.get_team_model(self.player_team)
	
	def load_career(self) -> None:
		load_save.load(self)
	
	def save_career(self) -> None:
		load_save.save_game(self)

	def get_driver_model(self, driver_name: str) -> DriverModel:
		driver_model = None

		for d in self.drivers:
			if d.name == driver_name:
				driver_model = d
				break
			
		return driver_model
	
	def get_team_model(self, team_name: str) -> TeamModel:
		team_model = None

		for t in self.teams:
			if t.name == team_name:
				team_model = t
				break
			
		return team_model
	
	def get_commercial_manager_model(self, name: str) -> CommercialManager:
		commercial_manager_model = None

		for c in self.commercial_managers:
			if c.name == name:
				commercial_manager_model = c
				break
			
		return commercial_manager_model

	def get_technical_director_model(self, name: str) -> TechnicalDirector:
		technical_director_mdoel = None

		for t in self.technical_directors:
			if t.name == name:
				technical_director_mdoel = t
				break
			
		return technical_director_mdoel
	
	def get_track_model(self, track_name: str) -> TrackModel:
		track_model = None

		for track in self.tracks:
			if track.name == track_name:
				track_model = track

		assert track_model is not None, f"Failed to Find Track {track_name}"

		return track_model
	
	def advance(self) -> None:
		self.inbox.reset_number_new_emails()
		
		if self.season.current_week == 51:
			self.staff_market.ensure_player_has_drivers_for_next_season()
			
		self.season.advance_one_week()

		if self.player_team is not None:
			self.get_team_model(self.player_team).advance()
		self.staff_market.announce_signings()

		if self.auto_save is True:
			self.save_career()

	def end_season(self, increase_year: bool=True, start_career: bool=False) -> None:
		logging.critical("End Season")
		'''
		the order in which the below code is important
		team end_season must be called first
		this updates the drivers for upcoming season
		then the drivers end_season can assign the correct team to the driver
		'''
		# if increase_year is True:
			

		for team in self.teams:
			team.end_season(increase_year) # update drivers for next year

		for driver in self.drivers:
			driver.end_season(increase_age=increase_year)

		for commercial_manager in self.commercial_managers:
			commercial_manager.end_season(increase_age=increase_year)
			# TODO remove this
			commercial_manager.retiring = False

		for technical_director in self.technical_directors:
			technical_director.end_season(increase_age=increase_year)
		# # TODO move the below into a start new season method
		# for team in self.teams:
		# 	team.check_drivers_for_next_year()

		if increase_year is True:
			self.year += 1
			self.staff_market.update_team_drivers()
			logging.critical(f"Start Season {self.year}")
			self.add_new_drivers()
			self.add_new_managers()

		self.staff_market.setup_dataframes()

		self.season.setup_new_season_variables()

		if start_career is False:
			self.staff_market.compute_transfers() # driver transfers at start of career are handled in the start_career method (once player_team is defined)

	def add_new_drivers(self) -> None:
		new_drivers = [d for d in self.future_drivers if int(d[0]) == self.year]

		for new_driver in new_drivers:
			self.drivers.append(new_driver[1])

			self.future_drivers.remove(new_driver)

		# Check we don't have duplicate drivers
		drivers_names = [driver.name for driver in self.drivers]
		assert len(drivers_names) == len(set(drivers_names))
	
	def add_new_managers(self) -> None:
		new_managers = [m for m in self.future_managers if int(m[0]) == self.year]
		
		'''
		example of new_managers list
		[['1999', <pw_model.senior_staff.technical_director.TechnicalDirector object at 0x00000150339AA8A0>]]
		'''

		for new_manager in new_managers:
			if new_manager[1].role == StaffRoles.COMMERCIAL_MANAGER:
				self.commercial_managers.append(new_manager[1])
			elif new_manager[1].role == StaffRoles.TECHNICAL_DIRECTOR:
				self.technical_directors.append(new_manager[1])

			self.future_managers.remove(new_manager)

	def start_career(self, player_team: str) -> None:
		self.player_team = player_team

		if player_team is not None:
			self.player_team_model.finance_model.update_prize_money(self.season.standings_manager.player_team_position)

		self.staff_market.compute_transfers()

	#TODO Move this to a different file, possibly a stand alone file in the teams folder
	def gen_team_average_stats(self) -> dict:
		
		team_average_stats = {
			"car_speed": int(statistics.fmean([t.car_model.speed for t in self.teams])),
			"driver_skill": int(statistics.fmean([t.average_driver_skill for t in self.teams])),
			"managers": int(statistics.fmean([t.average_manager_skill for t in self.teams])),
			"staff": int(statistics.fmean([t.number_of_staff for t in self.teams])),
			"max_staff": max([t.number_of_staff for t in self.teams]),
			"facilities": int(statistics.fmean([t.facilities_model.factory_rating for t in self.teams])),
			"max_sponsorship": max([t.finance_model.total_sponsorship for t in self.teams]),
			"sponsorship": int(statistics.fmean([t.finance_model.total_sponsorship for t in self.teams])),
		}

		return team_average_stats

