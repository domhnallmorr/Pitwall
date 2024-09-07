
'''
SERIES OF FUNCTIONS TO GET DATA REQUIRED TO UPDATE WINDOWS IN THE VIEW
'''


def get_main_window_data(model):
	data = {}
	
	data["team"] = f"{model.player_team} - $1000000"
	data["date"] = f"Week {model.season.current_week} - {model.year}"
	data["in_race_week"] = model.season.in_race_week

	return data
