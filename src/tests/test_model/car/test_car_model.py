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

	