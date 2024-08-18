import random
import pytest

from pw_model.team import team_model 

def gen_dummy_team(model=None, name="Williams", driver1="Jacques Villeneuve", driver2="Heinz-Harald Frentzen"):
	model = model
	name = name
	driver1 = driver1
	driver2 = driver2
	car_model = None

	return team_model.TeamModel(model, name, driver1, driver2, car_model)

def test_repr_method(capfd):
	dummy_team = gen_dummy_team()
	print(dummy_team)
	out, err = capfd.readouterr()
	assert out == "TeamModel <Williams>\n"

def test_end_season_method():

	dummy_team = gen_dummy_team()

	for i in range(100):
		# assign random points
		dummy_team.points_this_season = random.randint(0, 100)
		dummy_team.end_season()

		assert dummy_team.season_stats.starts_this_season == 0
		assert dummy_team.season_stats.points_this_season == 0
		assert dummy_team.season_stats.poles_this_season == 0
		assert dummy_team.season_stats.wins_this_season == 0
		assert dummy_team.season_stats.podiums_this_season == 0
		assert dummy_team.season_stats.starts_this_season == 0
		assert dummy_team.season_stats.dnfs_this_season == 0