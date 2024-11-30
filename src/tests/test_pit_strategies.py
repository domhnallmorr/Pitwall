import pytest

from tests import create_model
from race_model import race_model
from tests import test_track_model
from race_model.race_model_enums import SessionStatus

def test_pit_strategy_setup():
	# check planned pit stop laps are in expected range (based on a 71 lap race)

	model = create_model.create_model()
	track = test_track_model.create_dummy_track()
	_race_model = race_model.RaceModel("headless", model, track)

	schumacher_model = _race_model.get_particpant_model_by_name("Michael Schumacher")

	for i in range(100):
		assert schumacher_model.number_of_planned_stops in [1, 2, 3]

		if schumacher_model.number_of_planned_stops == 1:
			assert schumacher_model.pit1_lap >= 30
			assert schumacher_model.pit1_lap <= 40

			assert schumacher_model.pit2_lap is None
			assert schumacher_model.pit3_lap is None
		
		if schumacher_model.number_of_planned_stops == 2:
			assert schumacher_model.pit1_lap >= 20
			assert schumacher_model.pit1_lap <= 27

			assert schumacher_model.pit2_lap >= 43
			assert schumacher_model.pit2_lap <= 50

			assert schumacher_model.pit3_lap is None
		
		if schumacher_model.number_of_planned_stops == 3:
			assert schumacher_model.pit1_lap >= 15
			assert schumacher_model.pit1_lap <= 19

			assert schumacher_model.pit2_lap >= 33
			assert schumacher_model.pit2_lap <= 37

			assert schumacher_model.pit3_lap >= 49
			assert schumacher_model.pit3_lap <= 53

		schumacher_model.calculate_pitstop_laps()

def test_starting_fuel():
	# check that starting fuel matches the calculated pit strategy

	model = create_model.create_model()
	track = test_track_model.create_dummy_track()
	_race_model = race_model.RaceModel("headless", model, track)

	schumacher_model = _race_model.get_particpant_model_by_name("Michael Schumacher")
	schumacher_model.number_of_planned_stops = 1
	schumacher_model.pit1_lap = 10
	schumacher_model.pit2_lap = None
	schumacher_model.pit3_lap = None

	irvine_model = _race_model.get_particpant_model_by_name("Eddie Irvine")
	irvine_model.pit1_lap = 20

	_race_model.setup_race()
	assert schumacher_model.pit1_lap == 10
	assert schumacher_model.car_model.fuel_load == int(2.08 * (schumacher_model.pit1_lap + 0.5))

def test_pitstops():
	model = create_model.create_model()
	track = test_track_model.create_dummy_track()
	_race_model = race_model.RaceModel("headless", model, track)

	_race_model.setup_race()

	schumacher_model = _race_model.get_particpant_model_by_name("Michael Schumacher")
	schumacher_model.retires = False # make sure he does not retire
	
	schumacher_model.number_of_planned_stops = 3
	schumacher_model.pit1_lap = 10
	schumacher_model.pit2_lap = 20
	schumacher_model.pit3_lap = 30

	while _race_model.current_session.status != SessionStatus.POST_SESSION:
		_race_model.current_session.advance(mode="simulate")

		if _race_model.current_session.current_lap in [11, 21, 31]:
			assert schumacher_model.car_model.tyre_wear == 0 # check tyres were changed
		if _race_model.current_session.current_lap in [11, 21]:
			assert schumacher_model.car_model.fuel_load == 21 # check 10 laps of fuel was put in
		if _race_model.current_session.current_lap == 31:
			assert schumacher_model.car_model.fuel_load == 86 # check 41 laps of fuel was put in