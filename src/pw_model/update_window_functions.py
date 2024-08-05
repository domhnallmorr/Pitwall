
'''
SERIES OF FUNCTIONS TO GET DATA REQUIRED TO UPDATE WINDOWS IN THE VIEW
'''


def get_main_window_data(model):
	data = {}
	
	data["date"] = f"Week {model.season.current_week} - {model.year}"
	data["in_race_week"] = model.season.in_race_week

	return data
