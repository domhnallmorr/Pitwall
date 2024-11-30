
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

class TrackModel:
	def __init__(self, model: Model, data: list[str]):
		self.model = model
		self.parse_data(data)

		'''
		Assume 155kg required to run race, round down a little for conservatism
		'''
		self.fuel_consumption = round((155/self.number_of_laps) - 0.1, 2)

		'''
		base tyre wear, 20 laps equates to 1 second loss in performance
		'''
		self.tyre_wear = int(1_000 / 20)

		self.pit_stop_loss = 20_000 #20s loss coming through pits

		self.dist_to_turn1 = 615 # distance from pole to turn 1 in meters
		
	def parse_data(self, data: list[str]) -> None:
		self.name = ""
		self.country = ""
		self.location = ""
		self.title: str = ""
		self.number_of_laps = 0
		self.base_laptime = 0

		for line in data:
			if line.startswith("Name:"):
				self.name = line.split(":")[1].lstrip()
			if line.startswith("Country:"):
				self.country = line.split(":")[1].lstrip()
			if line.startswith("Location:"):
				self.location = line.split(":")[1].lstrip()
			if line.startswith("Title:"):
				self.title = line.split(":")[1].lstrip()
			if line.startswith("Laps:"):
				self.number_of_laps = int(line.split(":")[1].lstrip())
			if line.startswith("Base Laptime:"):
				self.base_laptime = int(line.split(":")[1].lstrip())


		assert self.name != ""
		assert self.country != ""
		assert self.location != ""
		assert self.title != ""
		assert self.number_of_laps > 0
		assert self.base_laptime > 0
	