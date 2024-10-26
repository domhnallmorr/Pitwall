import pandas as pd

from pw_model.season import standings_manager

class SeasonModel:
	def __init__(self, model):
		self.model = model
		self.setup_new_season_variables()

	@property
	def race_weeks(self):
		return self.model.calendar["Week"].values.tolist()
	
	@property
	def in_race_week(self):
		if self.current_week in self.model.calendar["Week"].values:
			return True
		else:
			return False
		
	@property
	def current_track_model(self):
		current_track = None

		'''
		DETERMINE THE TRACK MODEL FOR THE NEXT UPCOMING RACE
		'''
		for idx, row in self.model.calendar.iterrows():
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
			track_name = self.model.calendar.iloc[self.next_race_idx]["Track"]
			return self.model.get_track_model(track_name).title

	@property
	def drivers_by_rating(self) -> list:
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
	def teams_by_rating(self) -> list:
		'''
		compile all teams on the grid and arrange by their overall rating
		'''
		teams = []

		for team in self.model.teams:
			teams.append([team.name, team.overall_rating])

		teams = sorted(teams, key=lambda x: x[1], reverse=True)

		'''
		[['McLaren', 90], ['Ferrari', 84], ['Williams', 80], ['Benetton', 74], .......
		'''
		return teams
	
	def setup_new_season_variables(self):

		self.current_week = 1
		self.next_race_idx = 0

		
		self.standings_manager = standings_manager.StandingsManager(self.model)

	def advance_one_week(self):

		self.current_week += 1

		if self.current_week == 53:
			self.model.end_season()

	def update_next_race(self):
		'''
		This gets called in the grand_prix model, in post race actions
		'''
		self.next_race_idx += 1

		if self.next_race_idx > self.model.calendar.shape[0] - 1:
			self.next_race_idx = None

	def post_race_actions(self):

		self.update_next_race()
		# Update finances with race costs
		self.model.player_team_model.finance_model.apply_race_costs()