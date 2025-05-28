
'''
Collection of facade functions to gather data for a team that is not stored within the TeamModel class
'''
from pw_model.team.team_model import TeamModel


# FACILITIES DATA
def get_facilities_rating(team_model: TeamModel) -> int:
	return int(team_model.facilities_model.factory_rating)

# FINANCIAL DATA
def get_team_title_sponsor(team_model: TeamModel) -> str:
	return str(team_model.finance_model.sponsorship_model.title_sponsor)

def get_team_title_sponsor_value(team_model: TeamModel) -> int:
	return int(team_model.finance_model.sponsorship_model.title_sponsor_value)

def get_team_income(team_model: TeamModel) -> int:
	return int(team_model.finance_model.total_income)

def get_team_expenditure(team_model: TeamModel) -> int:
	return int(team_model.finance_model.total_expenditure)

def get_team_balance(team_model: TeamModel) -> int:
	return int(team_model.finance_model.balance)

def get_season_opening_balance(team_model: TeamModel) -> int:
	return int(team_model.finance_model.season_opening_balance)

def get_weeks_in_debt(team_model: TeamModel) -> int:
	return int(team_model.finance_model.consecutive_weeks_in_debt)