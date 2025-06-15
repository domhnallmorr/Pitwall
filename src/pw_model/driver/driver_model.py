from __future__ import annotations
import random
from typing import TypedDict, TYPE_CHECKING, Optional

from pw_model.driver import driver_contract
from pw_model.driver.driver_career_stats import DriverCareerStats
from pw_model.driver import driver_season_stats
from pw_model.team import team_model

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def decide_when_retiring(age: int) -> int:
	retiring_age = random.randint(35, 42)
	if retiring_age < age:
		retiring_age = age

	return retiring_age

class DriverDetails(TypedDict):
	name: str
	age: int

class DriverModel:
	def __init__(self,
			  model : Model,
			  name : str,
			  age : int,
			  country : str,
			  speed : int,
			  consistency : int,
			  qualifying : int,
			  contract_length : int,
			  salary : int,
			  starts : int,
			  pay_driver : bool,
			  budget : int,
			  championships : int = 0,
			  wins : int = 0):
		
		self.model = model
		self.name = name
		self.age = age
		self.country = country
		self.speed = speed
		self.consistency = consistency
		self.qualifying = qualifying
		
		self.pay_driver = pay_driver
		self.budget = budget

		self.retiring = False
		self.retired = False

		self.team_next_year = None

		self.contract = driver_contract.DriverContract(contract_length=contract_length, salary=salary)

		self.retiring_age = decide_when_retiring(self.age)

		self.career_stats = DriverCareerStats(starts=starts, championships=championships, wins=wins)

		# self.setup_season_stats()

	@property
	def team_model(self) -> team_model.TeamModel:
		current_team = None

		for team in self.model.teams:
			if self in [team.driver1_model, team.driver2_model]:
				current_team = team
				break

		return current_team
	
	@property
	def overall_rating(self) -> int:
		rating = (self.speed + self.consistency + (self.qualifying * 20)) / 3
		return int(rating)

	@property
	def current_standings_position(self) -> Optional[int]: #0 indexed, None if driver is not in race
		return int(self.model.season.standings_manager.driver_position(self.name)) if self.model.season.standings_manager.driver_position(self.name) is not None else None
	
	@property
	def details(self) -> DriverDetails:
		return {
			"name": self.name,
			"age": self.age
		}
	
	def __repr__(self) -> str:
		return f"DriverModel <{self.name}>"
	
	def end_season(self, increase_age: bool=True) -> None:
		if increase_age is True: # this method is run when driver is initialised, don't increase age or contract in that case
			self.age += 1
			self.career_stats.update_after_season(self.current_standings_position)

		if self.retired is False:
			if self.retiring is True:
				self.retired = True
				
			else:
				if increase_age is True:
					# Update contract
					self.contract.end_season()

			self.setup_season_stats()

			if self.retiring_age == self.age:
				self.handle_start_of_retiring_season()
			
		
	def handle_start_of_retiring_season(self) -> None:
		self.retiring = True
		self.model.inbox.generate_driver_retirement_email(self)

	def setup_season_stats(self) -> None:
		self.season_stats = driver_season_stats.DriverSeasonStats(self.model, self)

