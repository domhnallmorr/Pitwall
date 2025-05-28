from __future__ import annotations

import random
from typing import TYPE_CHECKING
from pw_model.pw_model_enums import StaffRoles

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def determine_driver_salary_range(driver_rating: int) -> list[int]:
	'''
	function for determining a reasonable salary range for a driver
	based on their ability
	'''
	if driver_rating >= 90:
		return [20_000_000, 26_000_000]
	elif driver_rating >= 80:
		return [9_000_000, 14_000_000]
	elif driver_rating >= 70:
		return [3_000_000, 6_000_000]
	elif driver_rating >= 50:
		return [900_000, 1_500_000]
	else:
		return [500_000, 900_000]

def determine_technical_director_salary_range(tech_director_rating: int) -> list[int]:
	if tech_director_rating >= 90:
		return [3_000_000, 6_000_000]
	elif tech_director_rating >= 80:
		return [1_500_000, 2_800_000]
	elif tech_director_rating >= 60:
		return [700_000, 1_200_000]
	else:
		return [200_000, 500_000]

def determine_commercial_manager_salary_range(tech_director_rating: int) -> list[int]:
	if tech_director_rating >= 90:
		return [400_000, 700_000]
	elif tech_director_rating >= 80:
		return [260_000, 370_000]
	elif tech_director_rating >= 60:
		return [180_000, 220_000]
	else:
		return [80_000, 150_000]
	
def determine_final_salary(model: Model, person_hired: str, role: StaffRoles) -> int:

	if role in [StaffRoles.DRIVER1, StaffRoles.DRIVER2]:
		driver_model = model.entity_manager.get_driver_model(person_hired)
		salary_range = determine_driver_salary_range(driver_model.overall_rating)
	
	elif role == StaffRoles.TECHNICAL_DIRECTOR:
		tech_director_model = model.entity_manager.get_technical_director_model(person_hired)
		salary_range = determine_technical_director_salary_range(tech_director_model.average_skill)

	elif role == StaffRoles.COMMERCIAL_MANAGER:
		commercial_manager_model = model.entity_manager.get_commercial_manager_model(person_hired)
		salary_range = determine_commercial_manager_salary_range(commercial_manager_model.average_skill)

	return random.randint(salary_range[0], salary_range[1])