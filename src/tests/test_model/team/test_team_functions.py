import random
from unittest.mock import patch

import matplotlib.pyplot as plt
import pytest

from pw_model.team import team_model 
from tests import create_model



def test_end_season_method():

	model = create_model.create_model()
	test_team = model.entity_manager.get_team_model("Warrick")

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
	team_model = model.entity_manager.get_team_model("Warrick")

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

def test_rating():
	model = create_model.create_model(mode="headless")

	Warrick_model = model.entity_manager.get_team_model("Warrick")
	expected_rating = int( (100 + 75 + 75) / 3 )

	assert Warrick_model.overall_rating == expected_rating

def test_team_principal_influence():
	"""Test that team principal skill influences car speed for AI teams only"""
	model = create_model.create_model(mode="headless")
	
	# Test AI team (Ferrari)
	ferrari_model = model.entity_manager.get_team_model("Ferano")
	# Make Ferrari non-player team by setting a different team as player team
	model.player_team = "Warrick"
	
	# Store original speed calculation components
	base_staff_speed = ferrari_model.number_of_staff * 0.4
	base_facilities = ferrari_model.facilities_model.factory_rating
	base_tech_director = ferrari_model.technical_director_model.skill
	
	with patch('random.randint', return_value=0):
	
		# Test with high skill principal (75)
		ferrari_model.team_principal_model.skill = 75
		ferrari_model.update_car_speed()
		speed_with_good_principal = ferrari_model.car_model.speed
		
		# Test with low skill principal (25)
		ferrari_model.team_principal_model.skill = 25
		ferrari_model.update_car_speed()
		speed_with_poor_principal = ferrari_model.car_model.speed
		
		# High skill principal should result in higher speed
		assert speed_with_good_principal > speed_with_poor_principal
	
	# Test player team
	Warrick_model = model.entity_manager.get_team_model("Warrick")
	# Make Warrick the player team
	model.player_team = "Warrick"
	
	# Test with high skill principal
	Warrick_model.team_principal_model.skill = 75
	Warrick_model.update_car_speed()
	player_speed_good_principal = Warrick_model.car_model.speed
	
	# Test with low skill principal
	Warrick_model.team_principal_model.skill = 25
	Warrick_model.update_car_speed()
	player_speed_poor_principal = Warrick_model.car_model.speed
	
	# Principal skill should not affect player team speed
	# Note: Due to random elements, we can't check for exact equality
	# Instead, verify the difference is minimal (only due to random factor)
	speed_difference = abs(player_speed_good_principal - player_speed_poor_principal)
	assert speed_difference <= 30  # Maximum random variation is -30 to 20
