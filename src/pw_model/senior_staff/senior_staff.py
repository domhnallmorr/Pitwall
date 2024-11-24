import random

from pw_model.senior_staff import staff_contract

def decide_when_retiring(age):
	retiring_age = random.randint(45, 65)
	if retiring_age < age:
		retiring_age = age

	return retiring_age

class SeniorStaff:
	def __init__(self,
			  model,
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
	def details(self) -> dict:
		return {
			"name": self.name,
			"age": self.age
		}
	
	def end_season(self, increase_age=True) -> None:
		
		if increase_age is True:
			self.age += 1

