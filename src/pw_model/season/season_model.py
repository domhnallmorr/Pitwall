from __future__ import annotations
import pandas as pd
from typing import List, Union, TYPE_CHECKING

from pw_model.season import standings_manager
from pw_model.season.calendar import Calendar

if TYPE_CHECKING:
	import pandas as pd
	from pw_model.track.track_model import TrackModel
	from pw_model.pw_base_model import Model
	from pw_model.driver.driver_model import DriverModel
	from pw_model.team.team_model import TeamModel
	from pw_model.senior_staff.technical_director import TechnicalDirector

class SeasonModel:
	def __init__(self, model: Model, calendar_dataframe: pd.DataFrame):
		self.model = model
		self.calendar = Calendar(self, calendar_dataframe)
		self.setup_new_season_variables()

	# @property
	# def race_weeks(self) -> List[int]:
	# 	return [int(w) for w in self.model.calendar["Week"].values.tolist()]
	
	# @property
	# def in_race_week(self) -> bool:
	# 	is_race_week = False
		
	# 	if self.current_week in self.calendar.race_weeks:
	# 		if self.calendar.get_week_of_next_race() == self.current_week:
	# 			is_race_week = True
				
	# 	return is_race_week

		
	# @property
	# def current_track_model(self) -> TrackModel:
	# 	current_track = None

	# 	'''
	# 	DETERMINE THE TRACK MODEL FOR THE NEXT UPCOMING RACE
	# 	'''
	# 	for idx, row in self.model.calendar.iterrows():
	# 		if row["Week"] >= self.current_week:
	# 			current_track = self.model.get_track_model(row["Track"])
	# 			assert current_track is not None, f"Failed to find track {row['Track']}"
	# 			break

	# 	return current_track

	# @property	
	# def next_race(self) -> str:
	# 	if self.next_race_idx is None:
	# 		return "Post Season"
	# 	else:
	# 		track_name = self.model.calendar.iloc[self.next_race_idx]["Track"]
	# 		return str(self.model.get_track_model(track_name).title)

	# @property
	# def next_race_week(self) -> str:
	# 	if self.next_race_idx is None:
	# 		return "-"
	# 	else:
	# 		week = self.model.calendar.iloc[self.next_race_idx]["Week"]

	# 		return str(week)

	@property
	def drivers_by_rating(self) -> list[list[Union[str, int]]]:
		'''
		compile all drivers on the grid and arrange by their overall rating
		'''
		drivers = []
		for team in self.model.teams:
			drivers.append([team.driver1, team.driver1_model.overall_rating])
			drivers.append([team.driver2, team.driver2_model.overall_rating])

		# sort by rating
		drivers = sorted(drivers, key=lambda x: x[1], reverse=True)

		''' 
		example ouput
		[['Michael Schumacher', 98], ['Mika Hakkinen', 87], ['Jacques Villeneuve', 84], ['Damon Hill', 78], ....
		'''
		return drivers
	
	@property
	def teams_by_rating(self) -> list[list[Union[str, int]]]:
		'''
		compile all teams on the grid and arrange by their overall rating
		Example output;
		[['McLaren', 90], ['Ferrari', 84], ['Williams', 80], ['Benetton', 74], .......
		'''
		teams = []

		for team in self.model.teams:
			teams.append([team.name, team.overall_rating])

		teams = sorted(teams, key=lambda x: x[1], reverse=True)

		return teams
	
	@property
	def technical_directors_by_rating(self) -> list[list[Union[str, int]]]:
		'''
		compile all technical directors on the grid and arrange by their overall rating
		example output;
		[['Adrian Newey', 95], ['Ross Brawn', 90], ['Pat Symonds', 80], ....
		'''
		technical_directors = []

		for team in self.model.teams:
			technical_directors.append([team.technical_director, team.technical_director_model.skill])

		technical_directors = sorted(technical_directors, key=lambda x: x[1], reverse=True)

		return technical_directors

	def setup_new_season_variables(self) -> None:
		# self.next_race_idx: Union[None, int] = 0

		self.standings_manager = standings_manager.StandingsManager(self.model)
		self.calendar.setup_new_season()

	def advance_one_week(self) -> None:
		self.calendar.advance_one_week()

		if self.calendar.current_week == 53:
			self.model.end_season()

	# def update_next_race(self) -> None:
	# 	'''
	# 	This gets called in the grand_prix model, in post race actions
	# 	'''
	# 	if self.next_race_idx is not None:
	# 		self.next_race_idx += 1

	# 		if self.next_race_idx > self.model.calendar.shape[0] - 1:
	# 			self.next_race_idx = None

	def post_race_actions(self, winner: str) -> None:
		# Update winner 
		self.calendar.post_race_actions(winner)
		# Update finances with race costs
		self.model.player_team_model.finance_model.apply_race_costs()
		# self.update_next_race()
