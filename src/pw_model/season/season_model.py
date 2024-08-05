import pandas as pd


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
				break

		return current_track

	@property	
	def next_race(self):
		if self.next_race_idx is None:
			return "Post Season"
		else:
			track_name = self.model.calendar.iloc[self.next_race_idx]["Track"]
			return self.model.get_track_model(track_name).title

	def setup_new_season_variables(self):

		self.current_week = 1
		self.next_race_idx = 0
		self.points_system = [10, 6, 4, 3, 2, 1]
		
		# SETUP DRIVER STANDINGS
		columns = ["Driver", "Team", "Points", "Wins", "Podiums", "Fastest Laps", "DNFs", "Starts"]
		data = []
		for team in self.model.teams:
			for driver in [team.driver1_model, team.driver2_model]:
				data.append([driver.name, team.name, 0, 0, 0, 0, 0, 0])

		self.drivers_standings_df = pd.DataFrame(columns=columns, data=data)

		# SETUP CONSTRUCTORS STANDINGS
		columns = ["Team", "Points", "Wins", "Podiums", "Fastest Laps", "DNFs"]
		data = []
		for team in self.model.teams:
			data.append([team.name, 0, 0, 0, 0, 0])

		self.constructors_standings_df = pd.DataFrame(columns=columns, data=data)

	def advance_one_week(self):

		self.current_week += 1

		if self.current_week == 53:
			self.model.end_season()

	def update_standings(self, result_df):
		# update points
		for idx, points in enumerate(self.points_system):
			driver_name = result_df.iloc[idx]["Driver"]
			driver_model = self.model.get_driver_model(driver_name)

			mask = self.drivers_standings_df["Driver"] == driver_name
			
			driver_model.points_this_season += points
			driver_model.team_model.points_this_season += points

			self.drivers_standings_df.loc[mask, "Points"] = driver_model.points_this_season

		self.drivers_standings_df.sort_values("Points", inplace=True, ascending=False)

		# update driver stats
		for idx, row in self.drivers_standings_df.iterrows():
			driver_name = row["Driver"]
			driver_model = self.model.get_driver_model(driver_name)
			mask = self.drivers_standings_df["Driver"] == driver_name

			self.drivers_standings_df.loc[mask, "Wins"] = driver_model.wins_this_season
			self.drivers_standings_df.loc[mask, "Podiums"] = driver_model.podiums_this_season
			self.drivers_standings_df.loc[mask, "DNFs"] = driver_model.dnfs_this_season
			self.drivers_standings_df.loc[mask, "Starts"] = driver_model.starts_this_season


		# update constructors standings
		for idx, row in self.constructors_standings_df.iterrows():
			team_name = row["Team"]
			team_model = self.model.get_team_model(team_name)
			mask = self.constructors_standings_df["Team"] == team_name		

			self.constructors_standings_df.loc[mask, "Points"] = team_model.points_this_season
			self.constructors_standings_df.loc[mask, "Wins"] = team_model.wins_this_season
			self.constructors_standings_df.loc[mask, "Podiums"] = team_model.podiums_this_season
			self.constructors_standings_df.loc[mask, "DNFs"] = team_model.dnfs_this_season

		self.constructors_standings_df.sort_values("Points", inplace=True, ascending=False)

	def update_next_race(self):
		'''
		This gets called in the grand_prix model, in post race actions
		'''
		self.next_race_idx += 1

		if self.next_race_idx > self.model.calendar.shape[0] - 1:
			self.next_race_idx = None