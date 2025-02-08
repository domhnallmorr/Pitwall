import pandas as pd

from tests import create_model
from pw_model.load_save.load_save import save_game, load

def test_load_standings():
	model = create_model.create_model()

	columns = ["Position", "Driver", "Team"]
	data = []
	count = 0
	for team in model.teams:
		data.append([count, team.driver1, team.name])
		count += 1

		data.append([count, team.driver2, team.name])
		count += 1


	result1 = pd.DataFrame(columns=columns, data=data)
	model.season.standings_manager.update_standings(result1)

	model.season.standings_manager.update_standings(result1)

	driver_row1 = model.season.standings_manager.drivers_standings_df.values.tolist()[0]
	teams_row1 = model.season.standings_manager.constructors_standings_df.values.tolist()[0]

	assert driver_row1[2] == 20 # check leader (winner of both races) as 20 points
	assert teams_row1[1] == 32 # check points for leading team (1-2 in both races)

	# SAVE THE MODEL
	save_file = save_game(model, mode="memory")

	model = create_model.create_model() #recreate model (simulate start new game)

	load(model, save_file, mode="memory")

	driver_row1 = model.season.standings_manager.drivers_standings_df.values.tolist()[0]
	teams_row1 = model.season.standings_manager.constructors_standings_df.values.tolist()[0]

	assert driver_row1[2] == 20 # check standings were loaded ok
	assert teams_row1[1] == 32 # check standings were loaded ok

	model.season.standings_manager.update_standings(result1)

	driver_row1 = model.season.standings_manager.drivers_standings_df.values.tolist()[0]
	teams_row1 = model.season.standings_manager.constructors_standings_df.values.tolist()[0]

	assert driver_row1[2] == 30 # leader should now have 30 points having won all races
	assert teams_row1[1] == 48
