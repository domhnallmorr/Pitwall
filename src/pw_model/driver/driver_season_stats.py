from __future__ import annotations
from typing import TYPE_CHECKING

import pandas

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model
	from pw_model.driver.driver_model import DriverModel

class DriverSeasonStats:
	def __init__(self, model: Model, driver_model: DriverModel):
		self.model = model
		self.driver_model = driver_model
		self.setup_new_season(model)

	def setup_new_season(self, model: Model) -> None:
		self.starts_this_season: int = 0
		self.points_this_season: int = 0
		self.poles_this_season: int = 0
		self.wins_this_season: int = 0
		self.podiums_this_season: int = 0
		self.dnfs_this_season: int = 0
		self.best_result_this_season: int = 0
		self.rnd_best_result_scored: int = 0 # the rnd at which the best result was scored

		number_of_races = model.season.calendar.number_of_races

		columns = [i for i in range(number_of_races)]
		data = [None for i in range(number_of_races)]
		self.race_results_df = pandas.DataFrame(columns=columns, data=[data])
		self.qualy_results_df = pandas.DataFrame(columns=columns, data=[data])

	def update_post_race(self, position: int) -> None:
		race_number = self.model.season.calendar.next_race_idx

		self.race_results_df[race_number] = position + 1
