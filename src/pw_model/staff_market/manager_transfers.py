
'''
A set of functions for determine transfer of managers between teams
'''
import random

from pw_model import pw_model
from pw_model.pw_model_enums import StaffRoles

def get_free_agents(model, role: StaffRoles, for_player_team: bool=False):
	staff_market = model.staff_market
	free_agents = []

	if role == StaffRoles.TECHNICAL_DIRECTOR:
		managers = model.technical_directors

	for manager in managers:
		if manager.retired is False:
				if manager.retiring is False:
					#TODO move the below to a dedicated method in the staff market
					if for_player_team is True:
						# When the player is hiring a new driver, any driver not announced for next season is considered a free agent
						if not staff_market.grid_next_year_announced_df.isin([manager.name]).any().any():
							free_agents.append(manager.name)
					else: # for AI teams, don;t consider if hiring is announced yet, this avoids the same driver being hired by multiple teams
						if not staff_market.grid_next_year_df.isin([manager.name]).any().any():
							free_agents.append(manager.name)

	return free_agents

def determine_technical_director_transfers(model):
	'''
	compute transfers for AI teams
	'''
	staff_market = model.staff_market
	transfers = []

	teams_requiring_tech_director = staff_market.compile_teams_requiring_manager(StaffRoles.TECHNICAL_DIRECTOR)

	for team in teams_requiring_tech_director:
		if team != model.player_team:
			free_agents = get_free_agents(model, StaffRoles.TECHNICAL_DIRECTOR)
			team_hire_technical_director(model, team, free_agents)

def team_hire_technical_director(model, team, free_agents: list):

	team_model = model.get_team_model(team)

	td_hired = random.choice(free_agents)

	week_to_announce = max(random.randint(4, 40), model.season.current_week + 1) 
	
	model.staff_market.technical_director_hired(team, td_hired, week_to_announce)