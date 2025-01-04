'''
A specific class to holds the starting grid positions for each driver.
It updates each participant model's starting_position variable
It is also responsible for applying the grid order to the GrandPrixModel's standings dataframe
'''
from __future__ import annotations
from typing import TYPE_CHECKING

import pandas as pd

from race_weekend_model.race_model_enums import SessionNames
if TYPE_CHECKING:
	from race_weekend_model.race_weekend_model import RaceWeekendModel

class StartingGrid:
	def __init__(self, race_weekend_model: RaceWeekendModel):
		self.race_weekend_model = race_weekend_model

		self.setup_grid_order()
		self.update_participants()

	def setup_grid_order(self) -> None:
		qualy_results = self.race_weekend_model.results[SessionNames.QUALIFYING.value]["results"]
		self.grid_order = qualy_results["Driver"]

	def update_participants(self) -> None:
		'''
		Update starting position variable in eeach participant
		'''
		for idx, driver in enumerate(self.grid_order):
			participant = self.race_weekend_model.get_particpant_model_by_name(driver)

			# update position in participant class
			participant.starting_position = idx + 1
	
	def apply_grid_order_to_standings(self, standings_df: pd.DataFrame) -> pd.DataFrame:
		standings_df.set_index('Driver', inplace=True, drop=False)
		standings_df = standings_df.loc[self.grid_order]

		standings_df.reset_index(drop=True, inplace=True)
		standings_df["Position"] = standings_df.index + 1

		for idx, row in standings_df.iterrows():
			driver = row["Driver"]
			standings_df.loc[standings_df["Driver"] == driver, "Grid"] = idx + 1

		return standings_df

