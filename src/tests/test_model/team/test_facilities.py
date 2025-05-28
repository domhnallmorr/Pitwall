import random
import pytest
from tests import create_model

def test_opponent_facility_update():

	'''
	Check if factory rating drops below 10, that factory is updated
	'''
	model = create_model.create_model()
	ferrari_model = model.entity_manager.get_team_model("Ferano")

	for i in range(100):
		ferrari_model.facilities_model.factory_rating = 9

		ferrari_model.end_season(increase_year=True)
		assert ferrari_model.facilities_model.factory_rating >= 25 # factory degrades by 4 at end of season

	'''
	Check that factory rating is always between 1 and 100
	'''
	model = create_model.create_model()
	ferrari_model = model.entity_manager.get_team_model("Ferano")
	minardi_model = model.entity_manager.get_team_model("Marchetti")

	for i in range(200):
		ferrari_model.end_season(increase_year=True)
		minardi_model.end_season(increase_year=True)

		assert ferrari_model.facilities_model.factory_rating >= 1 and ferrari_model.facilities_model.factory_rating <= 100
		assert minardi_model.facilities_model.factory_rating >= 1 and minardi_model.facilities_model.factory_rating <= 100

def test_update_player_facilities():
	model = create_model.create_model()

	model.player_team = "Marchetti"

	'''
	Make sure player's facilities never go below 1 and never increase (without user input)
	'''

	for i in range(50):
		rating_before = model.player_team_model.facilities_model.factory_rating
		model.player_team_model.end_season(increase_year=True)
		rating_after = model.player_team_model.facilities_model.factory_rating

		assert rating_after <= rating_before
		assert rating_after >= 1

	'''
	Test updating facilities gives expected rating
	'''
	model.player_team_model.facilities_model.update_facilties(45)

	assert model.player_team_model.facilities_model.factory_rating == 46 # rating will have degraded to 1 before update applied, 1 + 45 = 46

	'''
	Ensure factory rating can't go above 100
	'''
	model.player_team_model.facilities_model.update_facilties(110)
	assert model.player_team_model.facilities_model.factory_rating == 100