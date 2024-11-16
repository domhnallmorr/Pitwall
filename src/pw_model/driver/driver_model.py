import random
from pw_model.season import season_stats
from pw_model.driver import driver_contract

def decide_when_retiring(age):
	retiring_age = random.randint(35, 42)
	if retiring_age < age:
		retiring_age = age

	return retiring_age

class DriverModel:
	def __init__(self, model,
			  name : str,
			  age : int,
			  country : str,
			  speed : int,
			  contract_length : int,
			  salary: int):
		
		self.model = model
		self.name = name
		self.age = age
		self.country = country
		self.speed = speed

		self.retiring = False
		self.retired = False

		self.team_next_year = None

		self.contract = driver_contract.DriverContract(contract_length=contract_length, salary=salary)

		self.retiring_age = decide_when_retiring(self.age)

		self.setup_season_stats()

	@property
	def team_model(self):
		current_team = None

		for team in self.model.teams:
			if self in [team.driver1_model, team.driver2_model]:
				current_team = team
				break

		return current_team
	
	@property
	def overall_rating(self) -> int:
		return self.speed

	@property
	def details(self) -> dict:
		return {
			"name": self.name,
			"age": self.age
		}
	
	def __repr__(self):
		return f"DriverModel <{self.name}>"
	
	def end_season(self, increase_age: bool=True) -> None:
		if increase_age is True: # this method is run when driver is initialised, don't increase age or contract in that case
			self.age += 1

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
		self.season_stats = season_stats.SeasonStats()

	def hired_by_team(self, team) -> None:
		assert team is not None

		self.team_next_year = team
		self.contract = driver_contract.DriverContract()
