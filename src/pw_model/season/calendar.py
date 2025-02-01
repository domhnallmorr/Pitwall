from __future__ import annotations
from typing import TYPE_CHECKING, Union

import pandas as pd

if TYPE_CHECKING:
	from pw_model.season.season_model import SeasonModel
	from pw_model.track.track_model import TrackModel

class Calendar:
	def __init__(self, season: SeasonModel, dataframe: pd.DataFrame):
		'''
		Expected dataframe columns: ["Week", "Track", "Country", "Location", "Winner"]
		'''
		self.model = season.model
		self.season = season
		self.dataframe = dataframe

	@property
	def race_weeks(self) -> list[int]:
		return [int(w) for w in self.dataframe["Week"].values.tolist()]

	@property
	def in_race_week(self) -> bool:
		is_race_week = False
		
		if self.current_week in self.race_weeks:
			if self.get_week_of_next_race() == self.current_week:
				is_race_week = True
				
		return is_race_week
	
	@property
	def current_track_model(self) -> TrackModel:
		current_track = None

		'''
		DETERMINE THE TRACK MODEL FOR THE NEXT UPCOMING RACE
		'''
		for idx, row in self.dataframe.iterrows():
			if row["Week"] >= self.current_week:
				current_track = self.model.get_track_model(row["Track"])
				assert current_track is not None, f"Failed to find track {row['Track']}"
				break

		return current_track

	@property	
	def next_race(self) -> str:
		if self.next_race_idx is None:
			return "Post Season"
		else:
			track_name = self.dataframe.iloc[self.next_race_idx]["Track"]
			return str(self.model.get_track_model(track_name).title)

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

	def clear_winner_column(self) -> None:
		self.dataframe["Winner"] = None

	def get_week_of_next_race(self) -> int:
		return int(self.dataframe.iloc[self.next_race_idx]["Week"])
	
	def advance_one_week(self) -> None:
		self.current_week += 1

	def update_next_race(self) -> None:
		'''
		This gets called in the grand_prix model, in post race actions
		'''
		if self.next_race_idx is not None:
			self.next_race_idx += 1

			if self.next_race_idx > self.dataframe.shape[0] - 1:
				self.next_race_idx = None
	
	def post_race_actions(self, winner: str) -> None:
		self.dataframe.at[self.next_race_idx, "Winner"] = winner
		self.update_next_race()