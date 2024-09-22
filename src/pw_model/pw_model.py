import logging

from pw_model import load_roster
from pw_model.season import season_model
from pw_model.email import email_model
from pw_model.driver_market import driver_market



class Model:
	def __init__(self, roster, run_directory):

		self.player_team = "Jordan"

		# logging.basicConfig(filename=f"{run_directory}\\log.txt", filemode="w", level=logging.DEBUG)
		logging.basicConfig(level=logging.DEBUG)

		self.run_directory = run_directory

		self.inbox = email_model.Inbox(self)
		self.tracks = []
		self.retired_drivers = []

		if roster is not None:
			load_roster.load_roster(self, roster)

		self.year = 1998
		self.season = season_model.SeasonModel(self)

		self.driver_market = driver_market.DriverMarket(self)
		self.end_season(increase_year=False)

	@property
	def player_team_model(self):
		return self.get_team_model(self.player_team)
	
	def get_driver_model(self, driver_name):
		driver_model = None

		for d in self.drivers:
			if d.name == driver_name:
				driver_model = d
				break
			
		return driver_model
	
	def get_team_model(self, team_name):
		team_model = None

		for t in self.teams:
			if t.name == team_name:
				team_model = t
				break
			
		return team_model
	
	def get_track_model(self, track_name):
		track_model = None

		for track in self.tracks:
			if track.name == track_name:
				track_model = track

		assert track_model is not None, f"Failed to Find Track {track_name}"

		return track_model
	
	def advance(self):
		if self.season.current_week == 51:
			self.driver_market.ensure_player_has_drivers_for_next_season()
			
		self.season.advance_one_week()
		self.get_team_model(self.player_team).advance()

	def end_season(self, increase_year=True):
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

		self.player_team_model.finance_model.update_prize_money(self.season.standings_manager.player_team_position)
		# # TODO move the below into a start new season method
		# for team in self.teams:
		# 	team.check_drivers_for_next_year()

		if increase_year is True:
			self.year += 1
			self.driver_market.update_team_drivers()
			logging.critical(f"Start Season {self.year}")
			self.add_new_drivers()

		self.driver_market.setup_dataframes()
		self.driver_market.determine_driver_transfers()

		self.season.setup_new_season_variables()
		
	def add_new_drivers(self):
		new_drivers = [d for d in self.future_drivers if int(d[0]) == self.year]

		for line_data in new_drivers:
			new_driver = load_roster.create_driver(line_data, self)

			self.drivers.append(new_driver)
