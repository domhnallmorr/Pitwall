import pandas as pd

def create_standings_dataframe(teams: dict)-> pd.DataFrame: 
	'''
	teams format
	{"team1": ["Driver1", "Driver2"], "team2": ["Driver3", "Driver4"]}
	'''

	driver_columns = ["Driver", "Team", "Points", "Wins", "Podiums", "Fastest Laps", "DNFs", "Starts"]
	constructor_columns = ["Team", "Points", "Wins", "Podiums", "Fastest Laps", "DNFs"]

	team_data = []
	constructor_data = []

	for team in teams.keys():
		team_data.append([teams[team][0], team, 0, 0, 0, 0, 0, 0])
		team_data.append([teams[team][1], team, 0, 0, 0, 0, 0, 0])
		constructor_data.append([team, 0, 0, 0, 0, 0])

	drivers_standings_df = pd.DataFrame(columns=driver_columns, data=team_data)
	constructors_standings_df = pd.DataFrame(columns=constructor_columns, data=constructor_data)

	return drivers_standings_df, constructors_standings_df

class StandingsManager:
	def __init__(self, model):
		self.model = model
		self._points_system = [10, 6, 4, 3, 2, 1]
		self.setup_dataframes()

	@property
	def player_team_position(self):
		index = self.constructors_standings_df[self.constructors_standings_df["Team"] == self.model.player_team].index.values[0]

		return index

	def setup_dataframes(self):
		teams = {}

		for team in self.model.teams:
			teams[team.name] = [team.driver1, team.driver2]

		self.drivers_standings_df, self.constructors_standings_df = create_standings_dataframe(teams)
	
	def update_standings(self, result_df):
		# update points
		for idx, points in enumerate(self._points_system):
			driver_name = result_df.iloc[idx]["Driver"]
			driver_model = self.model.get_driver_model(driver_name)

			mask = self.drivers_standings_df["Driver"] == driver_name
			
			driver_model.season_stats.points_this_season += points
			driver_model.team_model.season_stats.points_this_season += points

			self.drivers_standings_df.loc[mask, "Points"] = driver_model.season_stats.points_this_season

		self.drivers_standings_df.sort_values("Points", inplace=True, ascending=False)

		# update driver stats
		for idx, row in self.drivers_standings_df.iterrows():
			driver_name = row["Driver"]
			driver_model = self.model.get_driver_model(driver_name)
			mask = self.drivers_standings_df["Driver"] == driver_name

			self.drivers_standings_df.loc[mask, "Wins"] = driver_model.season_stats.wins_this_season
			self.drivers_standings_df.loc[mask, "Podiums"] = driver_model.season_stats.podiums_this_season
			self.drivers_standings_df.loc[mask, "DNFs"] = driver_model.season_stats.dnfs_this_season
			self.drivers_standings_df.loc[mask, "Starts"] = driver_model.season_stats.starts_this_season


		# update constructors standings
		for idx, row in self.constructors_standings_df.iterrows():
			team_name = row["Team"]
			team_model = self.model.get_team_model(team_name)
			mask = self.constructors_standings_df["Team"] == team_name		

			self.constructors_standings_df.loc[mask, "Points"] = team_model.season_stats.points_this_season
			self.constructors_standings_df.loc[mask, "Wins"] = team_model.season_stats.wins_this_season
			self.constructors_standings_df.loc[mask, "Podiums"] = team_model.season_stats.podiums_this_season
			self.constructors_standings_df.loc[mask, "DNFs"] = team_model.season_stats.dnfs_this_season

		self.constructors_standings_df.sort_values("Points", inplace=True, ascending=False)
		
		
		self.drivers_standings_df.reset_index(drop=True, inplace=True)
		self.constructors_standings_df.reset_index(drop=True, inplace=True)

	def to_dict(self):
		return {
			"drivers_standings_df": self.drivers_standings_df.to_dict(),
			"constructors_standings_df": self.constructors_standings_df.to_dict(),
		}
	
	def team_position(self, team: str) -> int: #0 indexed
		index = self.constructors_standings_df[self.constructors_standings_df["Team"] == team].index.values[0]
		
		return index