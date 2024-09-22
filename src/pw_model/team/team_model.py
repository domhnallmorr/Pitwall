import copy
import logging
import random
from pw_model.season import season_stats
from pw_model.finance import finance_model
from pw_model.driver import driver_model

class TeamModel:
	def __init__(self, model, name, driver1, driver2, car_model,
			  number_of_staff : int, 
			  starting_balance, starting_sponsorship):
		self.model = model
		self.name = name
		self.driver1 = driver1 # name of driver1/2
		self.driver2 = driver2
		self.car_model = car_model


		self.number_of_staff = number_of_staff
				
		self.finance_model = finance_model.FinanceModel(model, self, starting_balance, starting_sponsorship)

	def __repr__(self):
		return f"TeamModel <{self.name}>"
	
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
	
	def advance(self):
		self.finance_model.weekly_update()
		
	def end_season(self, increase_year: bool):
		self.setup_season_stats()

		if increase_year is True:
			self.update_car_speed()

	def setup_season_stats(self):
		self.season_stats = season_stats.SeasonStats()

	def hire_driver(self, driver_type, free_agents):
		'''
		free_agents is a list of driver_names
		'''
		assert driver_type in ["driver1", "driver2"]

		driver_choosen = random.choice(free_agents)

		logging.debug(f"{self.name} hired {driver_choosen}")

		# Generate Email
		# self.model.inbox.generate_driver_hiring_email(self, driver_choosen)

		return driver_choosen
	
	def update_drivers(self, driver1, driver2):
		self.driver1 = driver1
		self.driver2 = driver2

	def update_car_speed(self):
		'''
		Recalculate the car speed at the end of the year for the next season
		'''

		staff_ceoff = 0.4
		random_element = random.randint(-30, 20)
		
		speed = (self.number_of_staff * staff_ceoff) + random_element

		speed = max(1, min(100, speed)) # make sure speed is between 1 and 100

		self.car_model.update_speed(speed)

		if self.is_player_team is True:
			self.model.inbox.new_car_update_email()
