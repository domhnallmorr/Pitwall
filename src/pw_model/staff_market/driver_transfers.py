import logging
import random

from pw_model.pw_model_enums import StaffRoles

def get_free_agents(model, for_player_team: bool =False) -> list:
		free_agents = []

		for driver in model.drivers:
			if driver.retired is False:
				if driver.retiring is False:

					if for_player_team is True:
						# When the player is hiring a new driver, any driver not announced for next season is considered a free agent
						if not model.staff_market.grid_next_year_announced_df.isin([driver.name]).any().any():
							free_agents.append(driver.name)
					else: # for AI teams, don;t consider if hiring is announced yet, this avoids the same driver being hired by multiple teams
						if not model.staff_market.grid_next_year_df.isin([driver.name]).any().any():
							free_agents.append(driver.name)
	
		return free_agents

def determine_driver_transfers(model) -> None:
	staff_market = model.staff_market
	transfers = []

	handle_top_3_drivers(model)

	teams_requiring_driver1 = staff_market.compile_teams_requiring_drivers(StaffRoles.DRIVER1)
	teams_requiring_driver2 = staff_market.compile_teams_requiring_drivers(StaffRoles.DRIVER2)

	for driver_idx in [StaffRoles.DRIVER1, StaffRoles.DRIVER2]:

		if driver_idx == StaffRoles.DRIVER1:
			teams_list = teams_requiring_driver1
		else:
			teams_list = teams_requiring_driver2

		for team in teams_list:
			if team != model.player_team:
				free_agents = get_free_agents(model)
				assert len(free_agents) > 0, "ran out of drivers"
				for driver in free_agents:
					assert driver not in model.staff_market.grid_next_year_df[StaffRoles.DRIVER1.value].values
					assert driver not in model.staff_market.grid_next_year_df[StaffRoles.DRIVER2.value].values
				team_hire_driver(model, team, driver_idx, free_agents)

def handle_top_3_drivers(model) -> None:
	'''
	ensure top 3 drivers are in the top 4 teams next season
	top 3 drivers should be over 25 years old
	
	example of model.season.drivers_by_rating
	[['Michael Schumacher', 98], ['Mika Hakkinen', 87], ['Jacques Villeneuve', 84], ['Damon Hill', 78], .......
	'''

	drivers_by_rating = [driver for driver in model.season.drivers_by_rating if model.get_driver_model(driver[0]).age > 25]
	
	drivers_by_rating = [d[0] for d in drivers_by_rating[:3]] # d[0] is drivers name
	teams_by_rating = [t[0] for t in model.season.teams_by_rating[:4]] # t[0] is teams name
	free_agents = get_free_agents(model)

	# remove player team if in top 4 teams
	if model.player_team in teams_by_rating:
		teams_by_rating.remove(model.player_team)

	top_available_drivers = [driver for driver in drivers_by_rating if driver in free_agents]
	teams_requiring_driver1 = model.staff_market.compile_teams_requiring_drivers(StaffRoles.DRIVER1)
	top_available_teams = [team for team in teams_by_rating if team in teams_requiring_driver1]
	
	if len(top_available_drivers) > 0: # if any of the top drivers are available
		for team in top_available_teams:
			team_hire_driver(model, team, StaffRoles.DRIVER1, top_available_drivers)
			
			# redefine top available drivers
			free_agents = get_free_agents(model)
			top_available_drivers = [driver for driver in drivers_by_rating if driver in free_agents]

			if len(top_available_drivers) == 0: # run out of drivers
				break

def team_hire_driver(model, team: str, driver_idx: str, free_agents: list) -> None:
	'''
	This method handles the AI controlled teams hiring a new driver
	'''
	logging.debug(f"{team} hiring {driver_idx}")
	logging.debug(f"Free Agents: {free_agents}")
	
	team_model = model.get_team_model(team)
	driver_hired = team_model.hire_driver(driver_idx, free_agents)

	# model.staff_market.grid_next_year_df.loc[model.staff_market.grid_next_year_df["team"] == team, driver_idx] = driver_hired

	# week_to_announce = max(random.randint(4, 40), model.season.current_week + 1) # ensure the week is not in the past
	# model.staff_market.new_contracts_df.loc[len(model.staff_market.new_contracts_df.index)] = [team, week_to_announce, driver_idx, driver_hired, 4_000_000, random.randint(2, 5)]

	# # self.model.inbox.generate_driver_hiring_email(team_model, self.model.get_driver_model(driver_hired))
	model.staff_market.handle_team_hiring_someone(team, driver_idx, driver_hired)