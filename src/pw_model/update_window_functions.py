
'''
SERIES OF FUNCTIONS TO GET DATA REQUIRED TO UPDATE WINDOWS IN THE VIEW
'''


def get_main_window_data(model):
	data = {}
	
	player_team_model = model.get_team_model(model.player_team)
	data["team"] = f"{model.player_team} - ${player_team_model.finance_model.balance:,}"
	data["date"] = f"Week {model.season.current_week} - {model.year}"
	data["in_race_week"] = model.season.in_race_week

	return data
