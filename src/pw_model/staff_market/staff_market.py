from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING
import random

import pandas as pd

from pw_model.pw_model_enums import StaffRoles
from pw_model.staff_market import driver_transfers, manager_transfers, contract_functions

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model
'''
Class for the following functionaility

compile list of drivers retiring
compile list of teams who need drivers
Finalise player driver hirings
call email model to generate an email announcing a driver hiring

grid_next_year_df is a dataframe that contains the staff for each team for next year. This gets computed at the start of each season, and recomputed if the player signs someone
grid_next_year_announced_df, gets populated as the season progresses and signings are announced. These are finalised signings that will carry over to next season
new_contracts_df is a dataframe that contains new contract information for any new signings
'''



class StaffMarket:
	def __init__(self, model: Model):
		self.model = model
		
	def setup_dataframes(self) -> None:
		columns = ["Team", "WeekToAnnounce", "DriverIdx", "Driver", "Salary", "ContractLength"]
		self.new_contracts_df = pd.DataFrame(columns=columns) # dataframe for tracking details of new contracts offered to new hires

		columns = ["team", StaffRoles.TEAM_PRINCIPAL.value, StaffRoles.DRIVER1.value, StaffRoles.DRIVER2.value,
			 StaffRoles.TECHNICAL_DIRECTOR.value, StaffRoles.COMMERCIAL_MANAGER.value]
		this_year_data = [] # grid for upcoming season
		next_year_data = [] # grid for next year

		for team in self.model.teams:
			this_year_data.append([team.name, team.team_principal])
			next_year_data.append([team.name, team.team_principal])

			for staff_model in [team.driver1_model, team.driver2_model, team.technical_director_model, team.commercial_manager_model]:
				this_year_data[-1].append(staff_model.name)

				if staff_model.retiring is True or staff_model.contract.contract_length < 2:
					next_year_data[-1].append(None)
				else:
					next_year_data[-1].append(staff_model.name)

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
	def player_requiring_driver1(self) -> bool:
		# if driver1 is an open seat in the player's team for next season
		# NB, for this to work, player hirings must be added to grid_next_year_announced_df straight away 

		if self.model.player_team in self.compile_teams_requiring_drivers(StaffRoles.DRIVER1):
			return True
		else:
			return False

	@property
	def player_requiring_driver2(self) -> bool:
		# if driver2 is an open seat in the player's team for next season
		if self.model.player_team in self.compile_teams_requiring_drivers(StaffRoles.DRIVER2):
			return True
		else:
			return False
				
	@property
	def player_requiring_technical_director(self) -> bool:
		if self.model.player_team in self.compile_teams_requiring_manager(StaffRoles.TECHNICAL_DIRECTOR):
			return True
		else:
			return False

	@property
	def player_requiring_commercial_manager(self) -> bool:
		if self.model.player_team in self.compile_teams_requiring_manager(StaffRoles.COMMERCIAL_MANAGER):
			return True
		else:
			return False
		
	def compile_teams_requiring_drivers(self, driver_idx: Enum) -> list[str]:
		assert driver_idx in [StaffRoles.DRIVER1, StaffRoles.DRIVER2], f"Unsupported driver_idx {driver_idx}"

		teams = []

		for idx, row in self.grid_next_year_df.iterrows():
			if row[driver_idx.value] is None:
				teams.append(row["team"])
		
		return teams

	def compile_teams_requiring_any_driver(self) -> list[str]:
		# this method is different from compile_teams_requiring_drivers in that in accounts for both Driver1 and Driver2
		teams1 = self.compile_teams_requiring_drivers(StaffRoles.DRIVER1)
		teams2 = self.compile_teams_requiring_drivers(StaffRoles.DRIVER2)

		return list(set(teams1 + teams2))

	#TODO can merge this with compile drivers method to create 1 single method
	def compile_teams_requiring_manager(self, role: Enum) -> list[str]:
		assert role in [StaffRoles.TECHNICAL_DIRECTOR, StaffRoles.COMMERCIAL_MANAGER], f"Unsupported manager role {role}"

		teams = []

		for idx, row in self.grid_next_year_df.iterrows():
			if row[role.value] is None:
				teams.append(row["team"])
		
		return teams

	def handle_team_hiring_someone(self, team:  str, role: Enum, person_hired: str) -> None:
		'''
		This is for AI only teams, for player team, complete_hiring is called
		'''
		assert role in [StaffRoles.DRIVER1, StaffRoles.DRIVER2, StaffRoles.TECHNICAL_DIRECTOR]
		self.grid_next_year_df.loc[self.grid_next_year_df["team"] == team, role.value] = person_hired
		
		week_to_announce = max(random.randint(4, 40), self.model.season.calendar.current_week + 1) # ensure the week is not in the past
		self.new_contracts_df.loc[len(self.new_contracts_df.index)] = [team, week_to_announce, role.value, person_hired, 4_000_000, random.randint(2, 5)]


	def update_team_drivers(self) -> None:
		assert None not in self.grid_next_year_df.values

		for idx, row in self.grid_next_year_df.iterrows():
			team_name = row["team"]
			team_model = self.model.get_team_model(team_name)

			# Get new contract details
			if row[StaffRoles.DRIVER1.value] in self.new_contracts_df["Driver"].values:
				driver1_contract = self.new_contracts_df.loc[self.new_contracts_df["Driver"] == row[StaffRoles.DRIVER1.value]].to_dict(orient="records")[0]
			else:
				driver1_contract = None # driver retained this year

			if row[StaffRoles.DRIVER2.value] in self.new_contracts_df["Driver"].values:
				driver2_contract = self.new_contracts_df.loc[self.new_contracts_df["Driver"] == row[StaffRoles.DRIVER2.value]].to_dict(orient="records")[0]
			else:
				driver2_contract = None

			if row[StaffRoles.TECHNICAL_DIRECTOR.value] in self.new_contracts_df["Driver"].values:
				tech_director_contract = self.new_contracts_df.loc[self.new_contracts_df["Driver"] == row[StaffRoles.TECHNICAL_DIRECTOR.value]].to_dict(orient="records")[0]
			else:
				tech_director_contract = None

			# Commercial Manager
			if row[StaffRoles.COMMERCIAL_MANAGER.value] in self.new_contracts_df["Driver"].values:
				commercial_manager_contract = self.new_contracts_df.loc[self.new_contracts_df["Driver"] == row[StaffRoles.COMMERCIAL_MANAGER.value]].to_dict(orient="records")[0]
			else:
				commercial_manager_contract = None

			team_model.update_drivers(row[StaffRoles.DRIVER1.value], row[StaffRoles.DRIVER2.value], driver1_contract, driver2_contract)
			team_model.update_managers(row[StaffRoles.TECHNICAL_DIRECTOR.value], tech_director_contract,
							  row[StaffRoles.COMMERCIAL_MANAGER.value], commercial_manager_contract)

	def complete_hiring(self, person_hired: str, team_name: str, role: StaffRoles) -> None:
		assert role in [StaffRoles.DRIVER1, StaffRoles.DRIVER2, StaffRoles.TECHNICAL_DIRECTOR, StaffRoles.COMMERCIAL_MANAGER]
		team_model = self.model.get_team_model(team_name)

		self.grid_next_year_df.loc[self.grid_next_year_df["team"] == team_name, role.value] = person_hired
		if team_name == self.model.player_team:
			salary = contract_functions.determine_final_salary(self.model, person_hired, role)
			contract_length = random.randint(2, 5)
			self.new_contracts_df.loc[len(self.new_contracts_df.index)] = [team_name, self.model.season.calendar.current_week, role.value, person_hired, salary, contract_length]
		
		# if team_name == self.model.player_team: # make this announced straight away for player hirings
		self.grid_next_year_announced_df.loc[self.grid_next_year_df["team"] == team_name, role.value] = person_hired

		if role in [StaffRoles.DRIVER1, StaffRoles.DRIVER2]:
			self.model.inbox.generate_driver_hiring_email(team_model, self.model.get_driver_model(person_hired))
		elif role in [StaffRoles.TECHNICAL_DIRECTOR, StaffRoles.COMMERCIAL_MANAGER]:
			self.model.inbox.new_manager_hired_email(team_name, person_hired, role.value)

		if team_name == self.model.player_team: # if the player signs a driver, we must recopute AI signings
			self.recompute_transfers_after_player_hiring()

	def ensure_player_has_staff_for_next_season(self) -> None:
		'''
		At the end of the season, if the player has failed to hire a driver(s)
		this method automically hires a random driver
		Will probably update this to end the game if player has failed to hire drivers
		'''
		if self.player_requiring_driver1 is True:
			driver_transfers.team_hire_driver(self.model, self.model.player_team, StaffRoles.DRIVER1, driver_transfers.get_free_agents(self.model))

		if self.player_requiring_driver2 is True:
			driver_transfers.team_hire_driver(self.model, self.model.player_team, StaffRoles.DRIVER2, driver_transfers.get_free_agents(self.model))
			
		if self.player_requiring_commercial_manager is True:
			manager_transfers.team_hire_commercial_manager(self.model, self.model.player_team,
												  manager_transfers.get_free_agents(self.model, StaffRoles.COMMERCIAL_MANAGER))

		if self.player_requiring_technical_director is True:
			manager_transfers.team_hire_technical_director(self.model, self.model.player_team,
												  manager_transfers.get_free_agents(self.model, StaffRoles.TECHNICAL_DIRECTOR))

	def announce_signings(self) -> None:
		for idx, row in self.new_contracts_df.iterrows():
			if row["WeekToAnnounce"] == self.model.season.calendar.current_week:
				person_hired = row["Driver"]
				team_name = row["Team"]
				role = StaffRoles(row["DriverIdx"]) # role is stored as an enum value (string) in the DF
				
				self.complete_hiring(person_hired, team_name, role)

	def recompute_transfers_after_player_hiring(self) -> None:
		# remove any contracts that have not been announced yet
		self.new_contracts_df = self.new_contracts_df[self.new_contracts_df["WeekToAnnounce"] <= self.model.season.calendar.current_week].reset_index(drop=True)

		# redo grid_next_year_df
		self.grid_next_year_df = self.grid_next_year_announced_df.copy(deep=True)

		# determine all transfers
		self.compute_transfers()

	def technical_director_hired(self, team: str, technical_director: str, week_to_announce: int) -> None:
		self.grid_next_year_df.loc[self.grid_next_year_df["team"] == team, StaffRoles.TECHNICAL_DIRECTOR.value] = technical_director
		self.new_contracts_df.loc[len(self.new_contracts_df.index)] = [team, week_to_announce, StaffRoles.TECHNICAL_DIRECTOR.value, technical_director, 4_000_000, random.randint(2, 5)]

	def commercial_manager_hired(self, team: str, commercial_manager: str, week_to_announce: int) -> None:
		self.grid_next_year_df.loc[self.grid_next_year_df["team"] == team, StaffRoles.COMMERCIAL_MANAGER.value] = commercial_manager
		self.new_contracts_df.loc[len(self.new_contracts_df.index)] = [team, week_to_announce, StaffRoles.COMMERCIAL_MANAGER.value, commercial_manager, 4_000_000, random.randint(2, 5)]

	def compute_transfers(self) -> None:
		driver_transfers.determine_driver_transfers(self.model)
		manager_transfers.determine_technical_director_transfers(self.model)
		manager_transfers.determine_commercial_manager_transfers(self.model)
