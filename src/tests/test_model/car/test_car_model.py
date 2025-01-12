import pytest

from tests import create_model
from race_weekend_model import race_weekend_model
from tests.test_model.track import test_track_model

def test_update_car_speed():
	'''
	Test to ensure udpate car speed method is producing resonable values
	'''

	model = create_model.create_model()

	ferrari_model = model.get_team_model("Ferrari")
	minardi_model = model.get_team_model("Minardi")

	for i in range(100): # run 100 tests
		ferrari_model.update_car_speed()
		minardi_model.update_car_speed()

		# ensure speed is between 1 and 100
		assert ferrari_model.car_model.speed > 0 and ferrari_model.car_model.speed <= 100
		assert minardi_model.car_model.speed > 0 and minardi_model.car_model.speed <= 100

		# ensure ferrari's car is faster than mindardi
		assert ferrari_model.car_model.speed > minardi_model.car_model.speed

		# ensure car speeds are within reasonable range
		assert ferrari_model.car_model.speed > 50 # make sure ferrari's car is at least a decent midfield car
		assert minardi_model.car_model.speed < 70 # make sure mindardi can't build a reasonably quick car

def test_fuel_consumption():
	model = create_model.create_model(mode="headless")
	track = test_track_model.create_dummy_track()
	_race_model = race_weekend_model.RaceWeekendModel("headless", model, track)

	schumacher_model = _race_model.get_particpant_model_by_name("Michael Schumacher")

	# check the car model caluclates required fuel for a given number of laps correctly
	# dummy track is based on A1 ring, 71 lap race
	assert schumacher_model.car_model.calculate_required_fuel(track, 71) == 148
	assert schumacher_model.car_model.calculate_required_fuel(track, 36) == 75
	assert schumacher_model.car_model.calculate_required_fuel(track, 18) == 38

	# Test car model assigns correct fuel load at start of race

	schumacher_model.pit_strategy.number_of_planned_stops = 1
	schumacher_model.pit_strategy.pit1_lap = 36

	schumacher_model.setup_start_fuel_and_tyres()
	assert schumacher_model.car_model.fuel_load == 75

	schumacher_model.pit_strategy.number_of_planned_stops = 3
	schumacher_model.pit_strategy.pit1_lap = 10
	schumacher_model.setup_start_fuel_and_tyres()
	assert schumacher_model.car_model.fuel_load == 21

	# random test
	schumacher_model.pit_strategy.calculate_pitstop_laps()
	schumacher_model.setup_start_fuel_and_tyres()
	assert schumacher_model.car_model.fuel_load == int(2.08 * (schumacher_model.pit_strategy.pit1_lap + 0.5))

	