from __future__ import annotations
import logging
import random
from typing import TypedDict, TYPE_CHECKING

from pw_model.senior_staff import staff_contract
from pw_model.pw_model_enums import StaffRoles

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def decide_when_retiring(age: int) -> int:
	retiring_age = random.randint(55, 65)
	if retiring_age < age:
		retiring_age = age

	return retiring_age

class StaffPersonDetails(TypedDict):
    name: str
    age: int

class SeniorStaff:
	def __init__(self,
			  model: Model,
			  name: str,
			  age: int,
			  skill: int,
			  salary: int,
			  contract_length: int):
	
		self.model = model
		self.name = name
		self.age = age
		self.skill = skill

		self.retiring = False
		self.retired = False
		self.retiring_age = decide_when_retiring(age)

		self.contract = staff_contract.StaffContract(salary=salary, contract_length=contract_length)

	@property
	def average_skill(self) -> int:
		return self.skill
	
	@property
	def details(self) -> StaffPersonDetails:
		return {
			"name": self.name,
			"age": self.age
		}
	
	def end_season(self, increase_age: bool=True) -> None:
		
		if increase_age is True:
			self.age += 1

		if self.retired is False:
			if self.retiring is True:
				self.retired = True
				logging.debug(f"{self.name} retiring")

			else:
				if increase_age is True:
					# Update contract
					self.contract.end_season()

			if self.retiring_age == self.age:
				self.handle_start_of_retiring_season()
			
		
	def handle_start_of_retiring_season(self) -> None:
		logging.debug(f"{self.name} starting retiring season")
		# check we won't run out of active managers
		delay_retirement = False

		if self.role == StaffRoles.TEAM_PRINCIPAL:
			if self.model.entity_manager.no_of_active_team_principals == len(self.model.teams):
				delay_retirement = True
				self.delay_retirement()
		
		if delay_retirement is False:
			self.retiring = True
			self.model.inbox.generate_driver_retirement_email(self)

	def delay_retirement(self) -> None:
		logging.debug(f"{self.name} delaying retirement")
		self.retiring_age += 1