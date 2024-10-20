from pw_model.senior_staff import senior_staff

import random

class TechnicalDirector(senior_staff.SeniorStaff):
	def __init__(self,
			  model,
			  name : str,
			  age : int,
			  skill : int,
			  salary : float):
		
		super().__init__(model, name, age, skill, salary)

	@property
	def team_model(self):
		current_team = None

		for team in self.model.teams:
			if self.name == team.commercial_manager:
				current_team = team
				break

		return current_team
	
