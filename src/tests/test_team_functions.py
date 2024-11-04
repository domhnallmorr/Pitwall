import random

import matplotlib.pyplot as plt
import pytest

from pw_model.team import team_model 
from tests import create_model



def test_end_season_method():

	model = create_model.create_model()
	test_team = model.get_team_model("Williams")

	for i in range(100):
		# assign random points
		test_team.points_this_season = random.randint(0, 100)
		test_team.end_season(increase_year=True)

		assert test_team.season_stats.starts_this_season == 0
		assert test_team.season_stats.points_this_season == 0
		assert test_team.season_stats.poles_this_season == 0
		assert test_team.season_stats.wins_this_season == 0
		assert test_team.season_stats.podiums_this_season == 0
		assert test_team.season_stats.starts_this_season == 0
		assert test_team.season_stats.dnfs_this_season == 0

def test_get_driver_models():
	model = create_model.create_model()
	team_model = model.get_team_model("Williams")

	assert team_model.driver1_model.name == "Jacques Villeneuve"
	assert team_model.driver2_model.name == "Heinz-Harald Frentzen"

def test_workplace_update():
	# test the update to workforce over 20 seasons
	model = create_model.create_model(mode="headless")

	plot_data = {t.name: [] for t in model.teams}

	for i in range(20):
		for team in model.teams:
			team.update_workforce()
			plot_data[team.name].append(team.number_of_staff)

			assert team.number_of_staff >= 90
			assert team.number_of_staff <= 250

	for team in plot_data.keys():
		plt.plot([i for i in range(20)], plot_data[team], label=team)

	plt.grid()
	plt.legend()
	plt.savefig("workforce.png")
