'''
This is the baseline class for all session (practice, qualy, race)
It's main function is to hold methods/variables that are common across all session types
Most importantly it holds a pandas dataframe called self.standings_df that contains the current standings of the session
'''
from __future__ import annotations
import copy
from typing import Optional, TYPE_CHECKING
import pandas as pd

from race_model.race_model_enums import SessionStatus

if TYPE_CHECKING:
	from race_model.race_model import RaceModel

class SessionModel:
	def __init__(self, race_model: RaceModel):
		self.race_model = race_model
		self.setup_standings()

		self.status = SessionStatus.PRE_SESSION
		self.time_left = None

		self.commentary_messages: list[str] = []
		self.commentary_to_process: list[str] = []
		self.retirements: list[str] = []

		self.current_lap = None
		self.fastest_laptime = None
		self.fastest_laptime_driver = None

	@property
	def fastest_lap_time(self) -> int:
		fastest_lap_index = self.standings_df["Fastest Lap"].idxmin()
		fastest_lap_time = int(self.standings_df["Fastest Lap"][fastest_lap_index])

		return fastest_lap_time
	
	@property
	def fastest_lap_driver(self) -> str:
		fastest_lap_index = self.standings_df["Fastest Lap"].idxmin()
		fastest_lap_driver = str(self.standings_df["Driver"][fastest_lap_index])

		return fastest_lap_driver
	
	@property
	def leader(self) -> str:
		leader = str(self.standings_df.iloc[0]["Driver"])

		return leader
	
	def setup_standings(self) -> None:
		'''
		setup pandas dataframe to track standings, assumes participants have been supplied in starting grid order!
		'''
		columns = ["Position", "Driver", "Team", "Lap", "Total Time", "Gap Ahead", "Gap to Leader", "Last Lap", "Status", "Lapped Status", "Pit", "Fastest Lap", "Grid"] # all times in milliseconds

		data = []
		for participant in self.race_model.participants: 
			data.append([participant.position, participant.name, participant.team_name, 0, 0.0, 0, 0, "-", "running", None, 0, None, 0])

		self.standings_df = pd.DataFrame(columns=columns, data=data)
		
		''' example;
		    Position              Driver Team  Lap  Total Time  Gap Ahead  Gap to Leader Last Lap   Status Lapped Status  Pit Fastest Lap
		0          1    Sebastian Vettel         0           0          0              0        -  running          None    0        None
		1          2         Mark Webber         0           0          0              0        -  running          None    0        None
		2          3     Fernando Alonso         0           0          0              0        -  running          None    0        None
		'''

	def calculate_lap_time(self) -> None:
		pass


	def refresh_standings_column(self) -> None:
		self.standings_df.reset_index(drop=True, inplace=True)
		self.standings_df["Position"] = self.standings_df.index + 1

	def process_lastest_commentary(self) -> Optional[list[str]]:
		latest_commentary = None

		if len(self.commentary_to_process) > 0:
			latest_commentary = self.commentary_to_process.pop(0)

			if self.race_model.mode == "headless":
				print(latest_commentary)

		return latest_commentary
	
	def process_headless_commentary(self) -> None:
		assert self.race_model.mode == "headless", f"This method is not supported for mode {self.race_model.mode}"

		while len(self.commentary_to_process) > 0:
			self.process_lastest_commentary()

	def get_data_for_view(self):
		data = {}

		data["status"] = self.status.value
		data["current_lap"] = self.current_lap
		data["total_laps"] = self.race_model.circuit_model.number_of_laps
		data["time_left"] = self.time_left
		data["standings"] = self.standings_df.copy(deep=True)
		
		data["fastest_lap_times"] = [p.name for p in self.race_model.participants if p.fastest_laptime == p.laptime]
		data["fastest_laptime"] = self.fastest_laptime
		data["fastest_laptime_driver"] = self.fastest_laptime_driver

		data["retirements"] = self.retirements

		if len(self.commentary_to_process) > 0:
			data["commentary"] = self.commentary_to_process.pop(0)
		else:
			data["commentary"] = ""

		# HACK FOR NOW
		driver1 = self.race_model.get_particpant_model_by_name("Nico Rosberg")
		data["driver1_fuel"] = driver1.car_model.fuel_load

		# LAP TIMES DATA
		data["laptimes"] = {}
		for p in self.race_model.participants:
			data["laptimes"][p.name] = copy.deepcopy(p.laptimes)

		return data
	
	def update_fastest_lap(self):
		for driver in self.standings_df["Driver"]:
			particpant_model = self.race_model.get_particpant_model_by_name(driver)
			if particpant_model.laptime < self.fastest_laptime:
				self.fastest_laptime = particpant_model.laptime
				self.fastest_laptime_driver = driver
				self.fastest_laptime_lap = self.current_lap

		