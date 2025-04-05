from __future__ import annotations
from typing import TYPE_CHECKING

import pandas as pd

from race_weekend_model.race_model_enums import SessionNames, ParticipantStatus

if TYPE_CHECKING:
	from race_weekend_model.race_weekend_model import RaceWeekendModel
	from race_weekend_model.particpant_model import ParticpantModel

class StandingsModel:
	def __init__(self, race_weekend_model: RaceWeekendModel):
		self.race_weekend_model = race_weekend_model

		columns = ["Position", "Driver", "Team", "Lap",
			"Total Time", "Gap Ahead", "Gap to Leader", "Last Lap",
			"Status", "Lapped Status", "Pit", "Fastest Lap",
			"Grid", "Retirement Reason"]
	
		data = []

		for participant in self.race_weekend_model.participants: 
			data.append(
					[participant.position, participant.name, participant.team_name, 0,
					0.0, 0, 0, "-",
					"running", None, 0, None,
					0, None]
				)
		
		self.dataframe = pd.DataFrame(columns=columns, data=data)

	@property
	def current_session_type(self) -> SessionNames:
		return self.race_weekend_model.current_session.session_type
	
	@property
	def leader(self) -> str:
		return str(self.dataframe.iloc[0]["Driver"])
	
	@property
	def fastest_lap(self) -> int:
		fastest_lap_index = self.dataframe["Fastest Lap"].idxmin()
		fastest_lap_time = int(self.dataframe["Fastest Lap"][fastest_lap_index])

		return fastest_lap_time

	@property
	def fastest_lap_driver(self) -> str:
		fastest_lap_index = self.dataframe["Fastest Lap"].idxmin()
		fastest_lap_driver = str(self.dataframe["Driver"][fastest_lap_index])

		return fastest_lap_driver
	
	@property
	def current_order(self) -> list[str]:
		return self.dataframe["Driver"].values.tolist()

	def update(self) -> None:
		self.update_all_participants()
		self.update_order()
		self.update_gap_columns()

		if self.current_session_type == SessionNames.RACE:
			self.update_lapped_status()
			self.update_participant_race_data()

	def update_all_participants(self) -> None:
		for driver in self.dataframe["Driver"]:
			particpant_model = self.race_weekend_model.get_particpant_model_by_name(driver)
			self.update_participant(particpant_model)

	def update_participant(self, particpant_model: ParticpantModel) -> None:
		# particpant_model.update_fastest_lap()
		driver = particpant_model.name
		self.dataframe.loc[self.dataframe["Driver"] == driver, "Last Lap"] = particpant_model.laptime_manager.laptime
		self.dataframe.loc[self.dataframe["Driver"] == driver, "Fastest Lap"] = particpant_model.laptime_manager.fastest_lap

		if self.race_weekend_model.current_session.session_type == SessionNames.RACE:
			self.dataframe.loc[self.dataframe["Driver"] == driver, "Total Time"] = particpant_model.laptime_manager.total_time
			self.dataframe.loc[self.dataframe["Driver"] == driver, "Lap"] = particpant_model.current_lap
			self.dataframe.loc[self.dataframe["Driver"] == driver, "Status"] = particpant_model.status
			self.dataframe.loc[self.dataframe["Driver"] == driver, "Pit"] = particpant_model.number_of_pitstops
			self.dataframe.loc[self.dataframe["Driver"] == driver, "Retirement Reason"] = particpant_model.retirement_reason
			

	def update_order(self) -> None:
		if self.race_weekend_model.current_session.session_type == SessionNames.RACE:
			self.dataframe = self.dataframe.sort_values(by=["Lap", "Total Time"], ascending=[False, True])
		else:
			self.dataframe.sort_values("Fastest Lap", inplace=True)

		# RESET INDEX AND POSITION COLUMNS
		self.dataframe.reset_index(drop=True, inplace=True)
		self.dataframe["Position"] = self.dataframe.index + 1

	def update_gap_columns(self) -> None:
		if self.race_weekend_model.current_session.session_type == SessionNames.RACE:
			self.dataframe["Gap Ahead"] = self.dataframe["Total Time"].diff()

			leader_time = self.dataframe.loc[self.dataframe["Position"] == 1, "Total Time"].values[0]
			self.dataframe["Gap to Leader"] = (self.dataframe["Total Time"] - leader_time)
		else:
			self.dataframe["Gap to Leader"] = (self.dataframe["Fastest Lap"] - self.fastest_lap)

	def update_lapped_status(self) -> None:
		for idx, row in self.dataframe.iterrows():		
			if row["Gap to Leader"] > self.race_weekend_model.track_model.base_laptime:
				self.dataframe.at[idx, "Lapped Status"] = f"lapped {int(row['Gap to Leader']/self.race_weekend_model.track_model.base_laptime)}" # add number of laps down to status
	
	def update_participant_race_data(self) -> None:
		for idx, row in self.dataframe.iterrows():
			particpant_model = self.race_weekend_model.get_particpant_model_by_name(row["Driver"])	
			particpant_model.positions_by_lap.append(idx + 1)
			particpant_model.gaps_to_leader.append(row["Gap to Leader"])

	def setup_initial_timed_session_standings(self) -> None:
		self.dataframe["Status"] = ParticipantStatus.IN_PITS.value
		
	def update_all_participant_status(self) -> None:
		for participant in self.race_weekend_model.participants:
			self.dataframe.loc[self.dataframe["Driver"] == participant.name, "Status"] = participant.status

	def setup_grid_order(self) -> None:
		self.dataframe.set_index('Driver', inplace=True, drop=False)
		self.dataframe = self.dataframe.loc[self.race_weekend_model.starting_grid.grid_order]

		self.dataframe.reset_index(drop=True, inplace=True)
		self.dataframe["Position"] = self.dataframe.index + 1

		for idx, row in self.dataframe.iterrows():
			driver = row["Driver"]
			self.dataframe.loc[self.dataframe["Driver"] == driver, "Grid"] = idx + 1