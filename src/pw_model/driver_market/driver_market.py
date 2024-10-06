
import logging

import pandas as pd

'''
Class for the following functionaility

compile list of drivers retiring
compile list of teams who need drivers
compile list of free agents

'''



class DriverMarket:
	def __init__(self, model):
		self.model = model
		
	def setup_dataframes(self):
		columns = ["team", "driver1", "driver2"]
		this_year_data = [] # grid for upcoming season
		next_year_data = [] # grid for next year

		for team in self.model.teams:
			this_year_data.append([team.name])
			next_year_data.append([team.name])

			for driver_model in [team.driver1_model, team.driver2_model]:
				this_year_data[-1].append(driver_model.name)

				if driver_model.retiring is True:
					next_year_data[-1].append(None)
				else:
					next_year_data[-1].append(driver_model.name)

		self.grid_this_year_df = pd.DataFrame(columns=columns, data=this_year_data)

		self.grid_next_year_df = pd.DataFrame(columns=columns, data=next_year_data)
		self.grid_next_year_announced_df = self.grid_next_year_df.copy(deep=True)
			
		'''
		        team               driver1                driver2
		0   Williams    Jacques Villeneuve  Heinz-Harald Frentzen
		1    Ferrari    Michael Schumacher           Eddie Irvine
		2   Benetton  Giancarlo Fisichella         Alexander Wurz
		3    McLaren       David Coulthard          Mika Hakkinen
		4     Jordan                  None        Ralf Schumacher
		'''

	@property
	def player_requiring_driver1(self):
		# if driver1 is an open seat in the player's team for next season
		# NB, for this to work, player hirings must be added to grid_next_year_announced_df straight away 

		if self.model.player_team in self.compile_teams_requiring_drivers("driver1"):
			return True
		else:
			return False

	@property
	def player_requiring_driver2(self):
		# if driver2 is an open seat in the player's team for next season
		if self.model.player_team in self.compile_teams_requiring_drivers("driver2"):
			return True
		else:
			return False
				

	def compile_teams_requiring_drivers(self, driver_idx):
		assert driver_idx in ["driver1", "driver2"], f"Unsupported driver_idx {driver_idx}"

		teams = []

		for idx, row in self.grid_next_year_announced_df.iterrows():
			if row[driver_idx] is None:
				teams.append(row["team"])
		
		return teams
	
	def get_free_agents(self):
		free_agents = []

		for driver in self.model.drivers:
			if driver.retired is False:
				if driver.retiring is False:
					if not self.grid_next_year_df.isin([driver.name]).any().any():
						free_agents.append(driver.name)
	
		return free_agents
	
	def determine_driver_transfers(self):
		self.transfers = []

		teams_requiring_driver1 = self.compile_teams_requiring_drivers("driver1")
		teams_requiring_driver2 = self.compile_teams_requiring_drivers("driver2")

		for driver_idx in ["driver1", "driver2"]:

			if driver_idx == "driver1":
				teams_list = teams_requiring_driver1
			else:
				teams_list = teams_requiring_driver2

			for team in teams_list:
				if team != self.model.player_team:
					free_agents = self.get_free_agents()
					self.team_hire_driver(team, driver_idx, free_agents)

	def team_hire_driver(self, team, driver_idx, free_agents):
		
		logging.debug(f"{team} hiring {driver_idx}")
		logging.debug(f"Free Agents: {free_agents}")
		
		#TODO move this to self.complete_driver_hiring
		team_model = self.model.get_team_model(team)
		driver_hired = team_model.hire_driver(driver_idx, free_agents)

		self.grid_next_year_df.loc[self.grid_next_year_df["team"] == team, driver_idx] = driver_hired

		self.model.inbox.generate_driver_hiring_email(team_model, self.model.get_driver_model(driver_hired))

	def update_team_drivers(self):

		assert None not in self.grid_next_year_df.values

		for idx, row in self.grid_next_year_df.iterrows():
			team_name = row["team"]
			team_model = self.model.get_team_model(team_name)
			
			team_model.update_drivers(row["driver1"], row["driver2"])

	def complete_driver_hiring(self, driver_hired, team_name, driver_idx):
		team_model = self.model.get_team_model(team_name)

		self.grid_next_year_df.loc[self.grid_next_year_df["team"] == team_name, driver_idx] = driver_hired

		if team_name == self.model.player_team: # make this announced straight away for player hirings
			self.grid_next_year_announced_df.loc[self.grid_next_year_df["team"] == team_name, driver_idx] = driver_hired

		self.model.inbox.generate_driver_hiring_email(team_model, self.model.get_driver_model(driver_hired))

	def ensure_player_has_drivers_for_next_season(self):
		if self.player_requiring_driver1 is True:
			self.team_hire_driver(self.model.player_team, "driver1", self.get_free_agents())

		if self.player_requiring_driver2 is True:
			self.team_hire_driver(self.model.player_team, "driver2", self.get_free_agents())
			