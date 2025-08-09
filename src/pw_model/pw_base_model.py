import logging
import os
import statistics
from typing import List, Union
import sqlite3

from pw_model.driver.driver_model import DriverModel
from pw_model.driver_negotiation.driver_offers import DriverOffers
from pw_model.email import email_model
from pw_model.season import season_model
from pw_model.sponsor_market.sponsor_market import SponsorMarket
from pw_model.staff_market import staff_market
from pw_model.pw_model_enums import StaffRoles
from pw_model.staff_market import manager_transfers
from pw_model.load_save import load_save 
from pw_model.game_data import GameData
from pw_model.track.track_model import TrackModel
from pw_model.load_save.roster_loader import LoadModes, RosterLoader

from pw_model.team.team_model import TeamModel
from pw_model.senior_staff.commercial_manager import CommercialManager
from pw_model.senior_staff.technical_director import TechnicalDirector
from pw_model.senior_staff.team_principal import TeamPrincipalModel
from pw_model.engine.engine_supplier_model import EngineSupplierModel
from pw_model.entity_manager import EntityManager
from pw_model.sponsors.sponsor_model import SponsorModel
from pw_model.tyre.tyre_supplier_model import TyreSupplierModel

from pw_model.player.player_model import PlayerModel

class Model:
	def __init__(self, roster: str, run_directory: str, mode: str="normal", auto_save: bool=True):
		
		assert mode in ["normal", "headless"]

		# logging.basicConfig(filename=f"{run_directory}\\log.txt", filemode="w", level=logging.DEBUG)
		logging.basicConfig(level=logging.DEBUG)

		self.player_model = PlayerModel(self)
		self.run_directory = run_directory
		self.auto_save = auto_save

		self.game_data = GameData(self)
		self.inbox = email_model.Inbox(self)
		self.tracks: List[TrackModel] = []
		self.retired_drivers: List[DriverModel] = []
		self.teams: List[TeamModel] = [] # gets populated in the load_roster function
		self.future_drivers: List[DriverModel] = []
		self.drivers: List[DriverModel] = []
		self.commercial_managers: List[CommercialManager] = []
		self.technical_directors: List[TechnicalDirector] = []
		self.future_managers: List[Union[CommercialManager, TechnicalDirector, TeamPrincipalModel]] = []
		self.team_principals: List[TeamPrincipalModel] = []
		self.engine_suppliers: List[EngineSupplierModel] = []
		self.tyre_suppliers: List[TyreSupplierModel] = []
		self.sponsors: List[SponsorModel] = []
		self.future_sponsors: List[tuple[str, SponsorModel]] = []

		self.entity_manager = EntityManager(self)	

		if roster is not None:
			roster_path = os.path.join(run_directory, roster)
			self.load_roster(roster)
			# roster_path = os.path.join(run_directory, roster)
			# self.roster_loader = RosterLoader(self, roster_path, load_mode=LoadModes.ROSTER)
			
			# self.tracks = self.roster_loader.loaded_data.tracks
			# self.calendar_dataframe = self.roster_loader.loaded_data.calendar_dataframe
			# self.drivers = self.roster_loader.loaded_data.drivers
			# self.future_drivers = self.roster_loader.loaded_data.future_drivers
			# self.commercial_managers = self.roster_loader.loaded_data.commercial_managers
			# self.technical_directors = self.roster_loader.loaded_data.technical_directors
			# self.team_principals = self.roster_loader.loaded_data.team_principals
			# self.future_managers = self.roster_loader.loaded_data.future_managers
			# self.sponsors = self.roster_loader.loaded_data.sponsors
			# self.future_sponsors = self.roster_loader.loaded_data.future_sponsors
			# self.teams = self.roster_loader.loaded_data.teams
			# self.engine_suppliers = self.roster_loader.loaded_data.engine_suppliers
			# self.tyre_suppliers = self.roster_loader.loaded_data.tyre_suppliers
		
		self.player_team = self.teams[0].name # set player team initally to first team in roster. This is so the view can setup all the pages on startup
		self.year = 1998
		self.FINAL_WEEK = 52
		self.season = season_model.SeasonModel(self, self.roster_loader.loaded_data.calendar_dataframe)

		self.staff_market = staff_market.StaffMarket(self)
		self.sponsor_market = SponsorMarket(self)
		self.driver_offers = DriverOffers(self)

		self.end_season(increase_year=False, start_career=True)
		
		if mode == "headless":
			self.player_team = None
			# this is called in start_career method, when player is  (mode=normal)
			self.staff_market.setup_dataframes() # 
			self.staff_market.compute_transfers()
			self.sponsor_market.compute_transfers()

		for team in self.teams:
			# call any functions that need the model fully initialised
			team.car_development_model.setup_new_season()
		assert self.entity_manager.get_team_principal_model("Craig Pollock") is not None

	@property
	def player_team_model(self) -> TeamModel:
		return self.entity_manager.get_team_model(self.player_team)
	
	def load_career(self) -> None:
		load_save.load(self)
	
	def save_career(self) -> None:
		load_save.save_game(self)

	def load_roster(self, roster_path: str, load_mode: LoadModes=LoadModes.ROSTER, conn: Union[None, sqlite3.Connection]=None) -> None:
		self.roster_loader = RosterLoader(self, roster_path, load_mode=load_mode, conn=conn)
		
		self.tracks = self.roster_loader.loaded_data.tracks
		self.calendar_dataframe = self.roster_loader.loaded_data.calendar_dataframe
		self.drivers = self.roster_loader.loaded_data.drivers
		self.future_drivers = self.roster_loader.loaded_data.future_drivers
		self.commercial_managers = self.roster_loader.loaded_data.commercial_managers
		self.technical_directors = self.roster_loader.loaded_data.technical_directors
		self.team_principals = self.roster_loader.loaded_data.team_principals
		self.future_managers = self.roster_loader.loaded_data.future_managers
		self.sponsors = self.roster_loader.loaded_data.sponsors
		self.future_sponsors = self.roster_loader.loaded_data.future_sponsors
		self.teams = self.roster_loader.loaded_data.teams
		self.engine_suppliers = self.roster_loader.loaded_data.engine_suppliers
		self.tyre_suppliers = self.roster_loader.loaded_data.tyre_suppliers

	def advance(self) -> None:
		self.inbox.reset_number_new_emails()

		if self.season.calendar.current_week == self.FINAL_WEEK - 1:
			self.staff_market.ensure_player_has_staff_for_next_season()
			
		self.season.advance_one_week()

		if self.player_team is not None:
			self.entity_manager.get_team_model(self.player_team).advance()

		# advance functions for AI teams
		for team in self.teams:
			if team.name != self.player_team:
				team.car_development_model.advance()

		self.staff_market.announce_signings()
		self.sponsor_market.announce_signings()

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

		for technical_director in self.technical_directors:
			technical_director.end_season(increase_age=increase_year)

		for team_principal in self.team_principals:
			team_principal.end_season(increase_age=increase_year)

		for sponsor in self.sponsors:
			sponsor.end_season(increase_year=increase_year)

		if increase_year is True:
			self.year += 1
			self.staff_market.update_team_drivers()
			self.sponsor_market.update_team_sponsors()
			logging.critical(f"Start Season {self.year}")
			self.entity_manager.setup_new_season() # add new drivers and managers
			self.driver_offers.setup_new_season()

		self.staff_market.setup_dataframes()
		self.sponsor_market.setup_dataframes()

		self.season.setup_new_season_variables()

		if start_career is False:
			self.staff_market.compute_transfers() # driver transfers at start of career are handled in the start_career method (once player_team is defined)
			self.sponsor_market.compute_transfers() # driver transfers at start of career are handled in the start_career method (once player_team is defined)


	def start_career(self, player_team: str) -> None:
		self.player_team = player_team

		if player_team is not None:
			self.player_team_model.finance_model.update_prize_money(self.season.standings_manager.player_team_position)

		self.staff_market.setup_dataframes() # to set player as team principal for relevant team
		self.staff_market.compute_transfers()
		self.sponsor_market.compute_transfers() # driver transfers at start of career are handled in the start_career method (once player_team is defined)

	#TODO Move this to a different file, possibly a stand alone file in the teams folder
	def gen_team_average_stats(self) -> dict[str, int]:
		
		team_average_stats = {
			"car_speed": int(statistics.fmean([t.car_model.speed for t in self.teams])),
			"driver_skill": int(statistics.fmean([t.average_driver_skill for t in self.teams])),
			"managers": int(statistics.fmean([t.average_manager_skill for t in self.teams])),
			"staff": int(statistics.fmean([t.number_of_staff for t in self.teams])),
			"max_staff": max([t.number_of_staff for t in self.teams]),
			"facilities": int(statistics.fmean([t.facilities_model.factory_rating for t in self.teams])),
			"max_sponsorship": max([t.finance_model.sponsorship_model.total_sponsor_income for t in self.teams]),
			"sponsorship": int(statistics.fmean([t.finance_model.sponsorship_model.total_sponsor_income for t in self.teams])),
		}

		return team_average_stats



