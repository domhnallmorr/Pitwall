from __future__ import annotations
import copy
import logging
import random
from typing import TYPE_CHECKING

from pw_model.season import season_stats
from pw_model.finance import finance_model

from pw_model.senior_staff import commercial_manager, technical_director
from pw_model.team import facilities_model
from pw_model.pw_model_enums import StaffRoles

if TYPE_CHECKING:
	from pw_model.driver import driver_model

class TeamModel:
	def __init__(self, model, name, driver1, driver2, car_model,
			  number_of_staff : int, 
			  facilities : int, 
			  starting_balance : int,
			  starting_sponsorship : int,
			  commercial_manager : str,
			  technical_director : str):
		
		self.model = model
		self.name = name
		self.driver1 = driver1 # name of driver1/2
		self.driver2 = driver2
		self.car_model = car_model

		self.number_of_staff = number_of_staff
		self.facilities_model = facilities_model.FacilityModel(self, facilities)
				
		self.finance_model = finance_model.FinanceModel(model, self, starting_balance, starting_sponsorship)

		self.commercial_manager = commercial_manager
		self.technical_director = technical_director

		self.setup_season_stats()

	def __repr__(self):
		return f"TeamModel <{self.name}>"
	
	@property
	def overall_rating(self) -> int:
		return int( (self.technical_director_model.skill + self.facilities_model.factory_rating + self.staff_rating) / 3 )
	
	@property
	def staff_rating(self) -> int:
		# Measure between 1 and 100 of the number of staff a team has
		max_staff = max([t.number_of_staff for t in self.model.teams])

		return int( (self.number_of_staff / max_staff) * 100 )
	
	@property
	def is_player_team(self) -> bool:
		if self.name == self.model.player_team:
			return True
		else:
			return False
	
	@property
	def driver1_model(self) -> driver_model.DriverModel:
		return self.model.get_driver_model(self.driver1)

	@property
	def driver2_model(self):
		return self.model.get_driver_model(self.driver2)
	
	@property
	def commercial_manager_model(self) -> commercial_manager.CommercialManager:
		return self.model.get_commercial_manager_model(self.commercial_manager)

	@property
	def technical_director_model(self) -> technical_director.TechnicalDirector:
		return self.model.get_technical_director_model(self.technical_director)
	
	#TODO make a property in driver model to calculate average skill
	@property
	def average_driver_skill(self) -> int:
		return int((self.driver1_model.speed + self.driver2_model.speed) / 2)
	
	@property
	def average_manager_skill(self):
		skill = 0
		for idx, manager in enumerate([self.commercial_manager_model, self.technical_director_model]):
			skill += manager.average_skill

		return int(skill / (idx + 1)) # return average skill of all managers

	@property
	def current_position(self) -> int: #in constructors championship, 0 indexed
		return self.model.season.standings_manager.team_position(self.name)
	
	def advance(self):
		self.finance_model.weekly_update()
		
	def end_season(self, increase_year: bool):
		self.setup_season_stats()

		if increase_year is True:
			self.facilities_model.end_season()

			if self.is_player_team:
				self.finance_model.end_season()
				self.finance_model.update_prize_money(self.current_position)
			else: # AI only functions
				self.update_workforce()

			self.update_car_speed()

	def setup_season_stats(self):
		self.season_stats = season_stats.SeasonStats()

	def hire_driver(self, driver_type: str, free_agents: list):
		'''
		free_agents is a list of driver_names
		'''
		assert driver_type in [StaffRoles.DRIVER1, StaffRoles.DRIVER2]

		driver_choosen = random.choice(free_agents)

		logging.debug(f"{self.name} hired {driver_choosen}")

		return driver_choosen
	
	def update_drivers(self, driver1 : str, driver2 : str, driver1_contract : dict, driver2_contract : dict) -> None:
		self.driver1 = driver1
		self.driver2 = driver2

		if driver1_contract is not None:
			self.driver1_model.contract.contract_length = driver1_contract["ContractLength"]

		if driver2_contract is not None:
			self.driver2_model.contract.contract_length = driver2_contract["ContractLength"]

	def update_managers(self, technical_director: str, technical_director_contract: dict) -> None:
		self.technical_director = technical_director

		if technical_director_contract is not None:
			self.technical_director_model.contract.contract_length = technical_director_contract["ContractLength"]
			
	def update_car_speed(self):
		'''
		Recalculate the car speed at the end of the year for the next season
		'''

		staff_ceoff = 0.4
		random_element = random.randint(-30, 20)
		
		staff_speed = (self.number_of_staff * staff_ceoff)

		facilities_speed = self.facilities_model.factory_rating

		speed = (staff_speed + facilities_speed + self.technical_director_model.skill + random_element) / 3

		speed = max(1, min(100, speed)) # make sure speed is between 1 and 100

		self.car_model.update_speed(speed)

		if self.is_player_team is True:
			self.model.inbox.new_car_update_email()

	def update_workforce(self):
		# randomly update number of staff, should trend upwards over the seasons
		self.number_of_staff += random.randint(-15, 20)
		if self.number_of_staff > 250:
			self.number_of_staff = 250
		elif self.number_of_staff < 90:
			self.number_of_staff = 90


	def to_dict(self):
		data =  {
			"name": self.name,
			"driver1": self.driver1,
			"driver2": self.driver2,
			"number_of_staff": self.number_of_staff,
			"facilities_model": self.facilities_model.to_dict(),
		}

		if self.is_player_team is True:
			data["finance_model"] = self.finance_model.to_dict()

		return data
	