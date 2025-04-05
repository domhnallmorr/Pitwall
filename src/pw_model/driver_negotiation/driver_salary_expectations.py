from __future__ import annotations
from typing import TYPE_CHECKING
from pw_model.driver_negotiation.driver_classification import classify_driver
from pw_model.driver_negotiation.driver_negotiation_enums import DriverCategory

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model


def determine_driver_salary_expectation(model: Model, driver: str) -> int:
	# Get driver's overall rating
	driver_model = model.get_driver_model(driver)
	driver_classification = classify_driver(driver, model)
	current_salary = driver_model.contract.salary
	age = driver_model.age

	if age < 25:
		salary_increase = 1.1 # younger drivers expect some salary increase
	elif age < 32:
		salary_increase = 1.20 # drivers in their prime expect higher salary increases
	else:
		salary_increase = 1.0 # older drivers expect no salary increase

	increased_salary = int(current_salary * salary_increase) # expect min 5% increase in salary

	# classification salary caps max possible salary for driver's ability
	if driver_classification == DriverCategory.ELITE:
		classification_salary = 29_000_000
	elif driver_classification == DriverCategory.TOP:
		classification_salary = 14_000_000
	elif driver_classification == DriverCategory.MID:
		classification_salary = 6_000_000
	else:
		classification_salary = 1_600_000


	if increased_salary > classification_salary:
		return classification_salary
	else:
		return increased_salary