from __future__ import annotations
from typing import TYPE_CHECKING, Union
import random

from pw_model.senior_staff import senior_staff
from pw_model.pw_model_enums import StaffRoles

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model
	from pw_model.team.team_model import TeamModel

class TechnicalDirector(senior_staff.SeniorStaff): # type: ignore
	def __init__(self,
			  model: Model,
			  name : str,
			  age : int,
			  skill : int,
			  salary : int,
			  contract_length : int):
		
		super().__init__(model, name, age, skill, salary, contract_length)
		self.role = StaffRoles.TECHNICAL_DIRECTOR
		
	@property
	def team_model(self) -> Union[None, TeamModel]:
		current_team = None

		for team in self.model.teams:
			if self.name == team.commercial_manager:
				current_team = team
				break

		return current_team
	
