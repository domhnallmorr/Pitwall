from pw_model.senior_staff import senior_staff
from pw_model.pw_model_enums import StaffRoles
import random

class TechnicalDirector(senior_staff.SeniorStaff):
	def __init__(self,
			  model,
			  name : str,
			  age : int,
			  skill : int,
			  salary : int,
			  contract_length : int):
		
		super().__init__(model, name, age, skill, salary, contract_length)
		self.role = StaffRoles.TECHNICAL_DIRECTOR
		
	@property
	def team_model(self):
		current_team = None

		for team in self.model.teams:
			if self.name == team.commercial_manager:
				current_team = team
				break

		return current_team
	
