from pw_model.season import season_stats

class TeamModel:
	def __init__(self, model, name, driver1, driver2, car_model):
		self.model = model
		self.name = name
		self.driver1 = driver1 # name of driver1/2
		self.driver2 = driver2
		self.car_model = car_model

		self.setup_season_stats()
	
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
	