'''
A class for tracking any offers made to drivers
'''
from __future__ import annotations
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

class DriverOffers:
	def __init__(self, model: Model):
		self.model = model
		self.game_data = self.model.game_data
		self.setup_dataframe()

	def setup_dataframe(self) -> None:
		columns = ["Week", "Driver"]

		self.dataframe = pd.DataFrame(columns=columns)

	def add_offer(self, driver: str) -> None:
		self.dataframe.loc[len(self.dataframe)] = [self.game_data.current_week(), driver]
	
	def setup_new_season(self) -> None:
		self.dataframe.drop(self.dataframe.index, inplace=True)

	def drivers_who_have_been_approached(self) -> list[str]:
		return [str(d) for d in self.dataframe["Driver"].values.tolist()]
