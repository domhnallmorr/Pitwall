import random

import pytest

from pw_model.driver import driver_model 
from tests import create_model

def gen_dummy_driver(model=None, name="Jacques Villeneuve"):
	model = model
	name = name
	age = 27
	country = "Canada"
	speed = 84
	consistency = 30
	contact_length = 4
	salary = 1_000_000

	return driver_model.DriverModel(model, name, age, country, speed, consistency, contact_length, salary)

def test_determine_retiring_age():
	age = 20

	# check that retiring age returned is between 35 and 42 (inclusive)
	for i in range(200):
		assert driver_model.decide_when_retiring(age) >= 35
		assert driver_model.decide_when_retiring(age) <= 42

	# check that if driver is over 42, they retiring at their current age
	assert driver_model.decide_when_retiring(44) >= 44

def test_end_season_method():

	dummy_driver = gen_dummy_driver(model=create_model.create_model())

	age = dummy_driver.age
	contract_length = dummy_driver.contract.contract_length

	for i in range(100):
		# assign random points
		dummy_driver.points_this_season = random.randint(0, 100)
		dummy_driver.end_season()

		assert dummy_driver.age == age + i + 1
		if i < 4:
			assert dummy_driver.contract.contract_length == contract_length - i - 1
		else:
			assert dummy_driver.contract.contract_length == 0 # contract length should not go into negative numbers
		assert dummy_driver.season_stats.starts_this_season == 0
		assert dummy_driver.season_stats.points_this_season == 0
		assert dummy_driver.season_stats.poles_this_season == 0
		assert dummy_driver.season_stats.wins_this_season == 0
		assert dummy_driver.season_stats.podiums_this_season == 0
		assert dummy_driver.season_stats.starts_this_season == 0
		assert dummy_driver.season_stats.dnfs_this_season == 0

def test_repr_method(capfd):
	dummy_driver = gen_dummy_driver()
	print(dummy_driver)
	out, err = capfd.readouterr()
	assert out == "DriverModel <Jacques Villeneuve>\n"

#TODO test team property in DriverModel class
	