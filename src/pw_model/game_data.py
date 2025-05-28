'''
Facade class to allow acces to common variables that require object chaining to retrieve them
'''
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

class GameData:
	def __init__(self, model: Model):
		self.model = model

	def get_number_of_races(self) -> int:
		return int(self.model.season.calendar.number_of_races)
	
	def current_week(self) -> int:
		return int(self.model.season.calendar.current_week)
	
	def driver_salary(self, driver_name: str) -> int:
		driver_model = self.model.entity_manager.get_driver_model(driver_name)
		return int(driver_model.contract.salary)
	
	def current_track_country(self) -> str:
		return self.model.season.calendar.current_track_model.country