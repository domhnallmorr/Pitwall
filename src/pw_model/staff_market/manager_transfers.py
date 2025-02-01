
'''
A set of functions for determine transfer of managers between teams
'''
from __future__ import annotations
import random
from typing import TYPE_CHECKING, List

from pw_model import pw_base_model
from pw_model.pw_model_enums import StaffRoles

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def get_free_agents(model: Model, role: StaffRoles, for_player_team: bool=False) -> List[str]:
	staff_market = model.staff_market
	free_agents = []

	if role == StaffRoles.TECHNICAL_DIRECTOR:
		managers = model.technical_directors
	elif role == StaffRoles.COMMERCIAL_MANAGER:
		managers = model.commercial_managers

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

def determine_technical_director_transfers(model: Model) -> None:
	'''
	compute transfers for AI teams
	'''
	staff_market = model.staff_market

	handle_top_5_technical_directors(model)

	teams_requiring_tech_director = staff_market.compile_teams_requiring_manager(StaffRoles.TECHNICAL_DIRECTOR)

	for team in teams_requiring_tech_director:
		if team != model.player_team:
			free_agents = get_free_agents(model, StaffRoles.TECHNICAL_DIRECTOR)
			assert len(free_agents) > 0, "No more free agents available"
			team_hire_technical_director(model, team, free_agents)

def get_top_available_technical_directors(model: Model, number: int) -> list[str]:
	tech_directors_by_rating = [td for td in model.season.technical_directors_by_rating]
	tech_directors_by_rating = [td[0] for td in tech_directors_by_rating[:number]] # d[0] is name, filter to top 5
	free_agents = get_free_agents(model, StaffRoles.TECHNICAL_DIRECTOR)

	top_available_tech_directors = [td for td in tech_directors_by_rating if td in free_agents]

	return top_available_tech_directors

def handle_top_5_technical_directors(model: Model) -> None:
	'''
	Ensure that the top 5 technical directors are hired for next year (if not retiring)
	'''
	top_available_tech_directors = get_top_available_technical_directors(model, 5)
	teams_requiring_tech_director =model.staff_market.compile_teams_requiring_manager(StaffRoles.TECHNICAL_DIRECTOR)
	random.shuffle(teams_requiring_tech_director)

	if len(top_available_tech_directors) > 0: # if any of the technical directors are available
		for team in teams_requiring_tech_director:
			team_hire_technical_director(model, team, top_available_tech_directors)
			
			# redefine top available technical directors
			free_agents = get_free_agents(model, StaffRoles.TECHNICAL_DIRECTOR)
			top_available_tech_directors = [td for td in top_available_tech_directors if td in free_agents]

			if len(top_available_tech_directors) == 0: # run out of technical directors
				break
	
def team_hire_technical_director(model: Model, team: str, free_agents: List[str]) -> None:
	team_model = model.get_team_model(team)
	td_hired = random.choice(free_agents)
	week_to_announce = max(random.randint(4, 40), model.season.calendar.current_week + 1) 
	model.staff_market.technical_director_hired(team, td_hired, week_to_announce)

def determine_commercial_manager_transfers(model: Model) -> None:
	'''
	compute transfers for AI teams
	'''
	staff_market = model.staff_market
	teams_requiring_commercial_manager = staff_market.compile_teams_requiring_manager(StaffRoles.COMMERCIAL_MANAGER)

	for team in teams_requiring_commercial_manager:
		if team != model.player_team:
			free_agents = get_free_agents(model, StaffRoles.COMMERCIAL_MANAGER)
			assert len(free_agents) > 0, "No more free agents available"
			team_hire_commercial_manager(model, team, free_agents)

def team_hire_commercial_manager(model: Model, team: str, free_agents: List[str]) -> None:
	team_model = model.get_team_model(team)
	cm_hired = random.choice(free_agents)
	week_to_announce = max(random.randint(4, 40), model.season.calendar.current_week + 1) 
	model.staff_market.commercial_manager_hired(team, cm_hired, week_to_announce)