from __future__ import annotations
from typing import TYPE_CHECKING, Union

import pandas as pd

if TYPE_CHECKING:
	from pw_model.season.season_model import SeasonModel
	from pw_model.track.track_model import TrackModel

from pw_model.pw_model_enums import CalendarState

class Calendar:
	def __init__(self, season: SeasonModel, dataframe: pd.DataFrame):
		'''
		Expected dataframe columns: ["Week", "Track", "Country", "Location", "Winner", "SessionType"]
		'''
		self.model = season.model
		self.season = season
		self.dataframe = dataframe
		self.state = CalendarState.PRE_SEASON

	@property
	def number_of_races(self) -> int:
		return int(len(self.race_weeks))
	
	@property
	def race_weeks(self) -> list[int]:
		race_rows = self.dataframe[self.dataframe["SessionType"] == "Race"]
		return [int(w) for w in race_rows["Week"].values.tolist()]

	@property
	def testing_weeks(self) -> list[int]:
		testing_rows = self.dataframe[self.dataframe["SessionType"] == "Testing"]
		return [int(w) for w in testing_rows["Week"].values.tolist()]

	@property
	def in_testing_week(self) -> bool:
		return self.current_week in self.testing_weeks

	@property
	def session_type(self) -> str:
		if self.in_race_week:
			return "Race"
		elif self.in_testing_week:
			return "Testing"
		return "None"

	@property
	def in_race_week(self) -> bool:
		return self.current_week in self.race_weeks
		
	@property
	def current_track_model(self) -> TrackModel:
		current_track = None

		'''
		DETERMINE THE TRACK MODEL FOR THE NEXT UPCOMING RACE
		'''
		for idx, row in self.dataframe.iterrows():
			if row["Week"] >= self.current_week:
				current_track = self.model.entity_manager.get_track_model(row["Track"])
				assert current_track is not None, f"Failed to find track {row['Track']}"
				break

		return current_track

	@property	
	def next_race(self) -> str:
		if self.next_race_idx is None:
			return "Post Season"
		else:
			track_name = self.dataframe.iloc[self.next_race_idx]["Track"]
			return str(self.model.entity_manager.get_track_model(track_name).title)

	@property
	def next_race_week(self) -> str:
		if self.next_race_idx is None:
			return "-"
		else:
			week = self.dataframe.iloc[self.next_race_idx]["Week"]

			return str(week)
	
	@property
	def countries(self) -> list[str]:
		return [str(c) for c in self.dataframe["Country"].values.tolist()]
	

	def setup_new_season(self) -> None:
		# Note should be called in the season constructor
		self.current_week = 1
		self.next_race_idx: Union[None, int] = 0
		self.clear_winner_column()
		self.state = CalendarState.PRE_SEASON

	def clear_winner_column(self) -> None:
		self.dataframe["Winner"] = None

	def get_week_of_next_race(self) -> int:
		return int(self.dataframe.iloc[self.next_race_idx]["Week"])
	
	def advance_one_week(self) -> None:
		self.current_week += 1

		# Reset state after testing/race
		if self.state in [CalendarState.POST_TEST, CalendarState.POST_RACE]:
			if self.current_week <= self.race_weeks[0]:
				self.state = CalendarState.PRE_SEASON
			else:
				self.state = CalendarState.IN_SEASON

		# Check if we are in a testing week
		if self.current_week in self.testing_weeks:
			if self.state == CalendarState.PRE_SEASON:
				self.state = CalendarState.PRE_SEASON_TESTING
			else:
				self.state = CalendarState.IN_SEASON_TESTING

		# Check if we are in a race week
		if self.current_week in self.race_weeks:
			self.state = CalendarState.RACE_WEEK

		# Check for post season
		if self.current_week > self.race_weeks[-1]:
			self.state = CalendarState.POST_SEASON

	def update_next_race(self) -> None:
		'''
		This gets called in the grand_prix model, in post race actions
		'''
		if self.next_race_idx is not None:
			self.next_race_idx += 1

			if self.next_race_idx > self.dataframe.shape[0] - 1:
				self.next_race_idx = None
	
	def post_race_actions(self, winner: str) -> None:
		idx = self.dataframe[self.dataframe["Week"] == self.current_week].index
		if not idx.empty:
			self.dataframe.at[idx[0], "Winner"] = winner
		# self.dataframe.at[self.next_race_idx, "Winner"] = winner
		self.update_next_race()

		self.state = CalendarState.POST_RACE

	def post_test_actions(self) -> None:
		idx = self.dataframe[self.dataframe["Week"] == self.current_week].index
		if not idx.empty:
			self.dataframe.at[idx[0], "Winner"] = "-"
			
		self.state = CalendarState.POST_TEST
