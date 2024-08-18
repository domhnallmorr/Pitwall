import random
from pw_model.season import season_stats

def decide_when_retiring(age):
	retiring_age = random.randint(35, 42)
	if retiring_age < age:
		retiring_age = age + 1

	return retiring_age

class DriverModel:
	def __init__(self, model, name, age, country, speed):
		self.model = model
		self.name = name
		self.age = age
		self.country = country
		self.speed = speed

		self.setup_season_stats()
		self.retiring_age = decide_when_retiring(self.age)

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
	
	def end_season(self):
		self.age += 1
		self.setup_season_stats()

	def setup_season_stats(self):
		self.season_stats = season_stats.SeasonStats()
