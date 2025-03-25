from __future__ import annotations
import copy
import logging
import random
from typing import TYPE_CHECKING, Dict, Any

from pw_model.season import season_stats
from pw_model.finance import finance_model

from pw_model.senior_staff import commercial_manager, technical_director, team_principal
from pw_model.team.facilities_model import FacilityModel
from pw_model.finance.sponsors_model import SponsorModel
from pw_model.pw_model_enums import StaffRoles
from pw_model.team.suppliers_model import SupplierModel
from pw_model.car_development.car_development_model import CarDevelopmentModel
from pw_model.engine.engine_supplier_model import EngineSupplierModel
from pw_model.tyre.tyre_supplier_model import TyreSupplierModel

if TYPE_CHECKING:
	from pw_model.driver import driver_model
	from pw_model.pw_base_model import Model
	from pw_model.car.car_model import CarModel

class TeamModel:
	def __init__(self, model: Model, name: str,
			  country: str,
			  team_principal: str,
			  driver1: str, driver2: str,
			  car_model: CarModel,
			  number_of_staff : int, 
			  facilities : int, 
			  starting_balance : int,
			  other_sponsorship : int,
			  title_sponsor : str,
			  title_sponsor_value : int,
			  commercial_manager : str,
			  technical_director : str,
			  engine_supplier : str,
			  engine_supplier_deal : str,
			  engine_supplier_cost : int,
			  tyre_supplier : str,
			  tyre_supplier_deal : str,
			  tyre_supplier_cost : int,
			  finishing_position : int = None # last season finishing position
			  ):
		
		self.model = model
		self.name = name
		self.country = country
		self.team_principal = team_principal
		self.driver1 = driver1 # name of driver1/2
		self.driver2 = driver2
		self.car_model = car_model
		self.car_development_model = CarDevelopmentModel(self.model, self)

		self.number_of_staff = number_of_staff
		self.facilities_model = FacilityModel(self, facilities)
				
		self.finance_model = finance_model.FinanceModel(model, self, starting_balance, other_sponsorship, title_sponsor, title_sponsor_value, finishing_position)

		self.commercial_manager = commercial_manager
		self.technical_director = technical_director
		self.supplier_model = SupplierModel(self.model, engine_supplier, engine_supplier_deal, engine_supplier_cost,
									  tyre_supplier, tyre_supplier_deal, tyre_supplier_cost)

		self.setup_season_stats()

	def __repr__(self) -> str:
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
	def driver2_model(self) -> driver_model.DriverModel:
		return self.model.get_driver_model(self.driver2)
	
	@property
	def commercial_manager_model(self) -> commercial_manager.CommercialManager:
		return self.model.get_commercial_manager_model(self.commercial_manager)

	@property
	def technical_director_model(self) -> technical_director.TechnicalDirector:
		return self.model.get_technical_director_model(self.technical_director)

	@property
	def team_principal_model(self) -> team_principal.TeamPrincipalModel:
		return self.model.get_team_principal_model(self.team_principal)
	
	@property
	def engine_supplier_model(self) -> EngineSupplierModel:
		return self.model.get_engine_supplier_model(self.supplier_model.engine_supplier)

	@property
	def tyre_supplier_model(self) -> TyreSupplierModel:
		return self.model.get_tyre_supplier_model(self.supplier_model.tyre_supplier)

	#TODO make a property in driver model to calculate average skill
	@property
	def average_driver_skill(self) -> int:
		return int((self.driver1_model.speed + self.driver2_model.speed) / 2)
	
	@property
	def average_manager_skill(self) -> int:
		skill = 0
		for idx, manager in enumerate([
			self.commercial_manager_model,
			self.technical_director_model,
			self.team_principal_model
		]):
			skill += manager.average_skill

		return int(skill / (idx + 1))  # return average skill of all managers

	@property
	def current_position(self) -> int: #in constructors championship, 0 indexed
		return int(self.model.season.standings_manager.team_position(self.name))
	
	def advance(self) -> None:
		'''
		Advance the team by one week
		'''
		self.finance_model.weekly_update()
		self.car_development_model.advance()
		
	def end_season(self, increase_year: bool) -> None:
		self.setup_season_stats()

		if increase_year is True:
			self.facilities_model.end_season()
			self.car_development_model.setup_new_season()

			if self.is_player_team:
				self.finance_model.end_season()
				self.finance_model.update_prize_money(self.current_position)
			else: # AI only functions
				self.update_workforce()

			self.update_car_speed()
		else:
			# This gets called when the game starts
			# The transport model needs the season to fully initialised to compute transport costs
			self.finance_model.transport_costs_model.setup_new_season()

	def setup_season_stats(self) -> None:
		self.season_stats = season_stats.SeasonStats()

	def hire_driver(self, driver_type: str, free_agents: list[str]) -> str:
		'''
		free_agents is a list of driver_names
		'''
		assert driver_type in [StaffRoles.DRIVER1, StaffRoles.DRIVER2]

		driver_choosen = random.choice(free_agents)

		logging.debug(f"{self.name} hired {driver_choosen}")

		return driver_choosen
	
	def update_drivers(self, driver1 : str, driver2 : str, driver1_contract : Dict[str, Any], driver2_contract : Dict[str, Any]) -> None:
		self.driver1 = driver1
		self.driver2 = driver2

		if driver1_contract is not None:
			self.driver1_model.contract.contract_length = driver1_contract["ContractLength"]
			self.driver1_model.contract.salary = driver1_contract["Salary"]

		if driver2_contract is not None:
			self.driver2_model.contract.contract_length = driver2_contract["ContractLength"]
			self.driver2_model.contract.salary = driver2_contract["Salary"]

	def update_managers(self, technical_director: str, technical_director_contract: Dict[str, Any],
					 commercial_manager: str, commercial_manager_contract: Dict[str, Any]) -> None:
		self.technical_director = technical_director
		self.commercial_manager = commercial_manager

		#TODO need to improve means of updating contract
		if technical_director_contract is not None:
			self.technical_director_model.contract.contract_length = technical_director_contract["ContractLength"]
			self.technical_director_model.contract.salary = technical_director_contract["Salary"]
			
		if commercial_manager_contract is not None:
			self.commercial_manager_model.contract.contract_length = commercial_manager_contract["ContractLength"]
			self.commercial_manager_model.contract.salary = commercial_manager_contract["Salary"]

	def update_car_speed(self) -> None:
		'''
		Recalculate the car speed at the end of the year for the next season
		'''
		staff_coeff = 0.4
		random_element = random.randint(-30, 20)
		
		staff_speed = (self.number_of_staff * staff_coeff)
		facilities_speed = self.facilities_model.factory_rating
		
		# Calculate base speed first
		base_speed = (staff_speed + facilities_speed + self.technical_director_model.skill + random_element) / 3
		
		# Apply modest team principal influence for AI teams only
		if not self.is_player_team:
			# Apply a small boost/penalty based on team principal skill
			# Skill of 50 = no effect, above 50 = small boost, below 50 = small penalty
			principal_modifier = (self.team_principal_model.skill - 50) * 0.0025  # 0.5% influence per skill point from baseline
			base_speed *= (1 + principal_modifier)
		
		speed = max(1, min(100, base_speed))  # make sure speed is between 1 and 100
		
		self.car_model.update_speed(speed)
		
		if self.is_player_team is True:
			self.model.inbox.new_car_update_email()

	def update_workforce(self) -> None:
		# randomly update number of staff, should trend upwards over the seasons
		self.number_of_staff += random.randint(-15, 20)
		if self.number_of_staff > 250:
			self.number_of_staff = 250
		elif self.number_of_staff < 90:
			self.number_of_staff = 90


	
