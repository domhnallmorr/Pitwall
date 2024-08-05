

class DriverModel:
	def __init__(self, model, name, age, country, speed):
		self.model = model
		self.name = name
		self.age = age
		self.country = country
		self.speed = speed

		self.setup_season_stats()

	@property
	def team_model(self):
		current_team = None

		for team in self.model.teams:
			if self in [team.driver1_model, team.driver2_model]:
				current_team = team
				break

		return current_team
			
	def __repr__(self):
		return f"DriverModel <{self.name}>"
	

	def setup_season_stats(self):
		self.starts = 0
		self.points_this_season = 0
		self.poles = 0
		self.wins_this_season = 0
		self.podiums_this_season = 0
		self.starts_this_season = 0
		self.dnfs_this_season = 0

