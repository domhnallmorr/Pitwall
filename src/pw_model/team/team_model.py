import copy
import logging
import random
from pw_model.season import season_stats

class TeamModel:
	def __init__(self, model, name, driver1, driver2, car_model):
		self.model = model
		self.name = name
		self.driver1 = driver1 # name of driver1/2
		self.driver2 = driver2
		self.car_model = car_model
		
		# self.drivers_next_year = [None, None]

	def __repr__(self):
		return f"TeamModel <{self.name}>"
	
	@property
	def driver1_model(self):
		return self.model.get_driver_model(self.driver1)

	@property
	def driver2_model(self):
		return self.model.get_driver_model(self.driver2)
	
	def end_season(self):
		self.setup_season_stats()

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