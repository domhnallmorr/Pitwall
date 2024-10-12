
import pytest

from tests import create_model
from pw_model import load_save

def test_retirements():

	model = create_model.create_model()

	# Test Schumacher retirement
	schumacher_model = model.get_driver_model("Michael Schumacher")
	schumacher_model.retiring_age = schumacher_model.age
	schumacher_model.handle_start_of_retiring_season()
	
	model.staff_market.setup_dataframes()
	model.staff_market.determine_driver_transfers()

	save_file = load_save.save_game(model, mode="memory")

	model = create_model.create_model() # reset the model
	load_save.load(model, save_file, mode="memory") # load data

	schumacher_model = model.get_driver_model("Michael Schumacher")
	assert schumacher_model.retiring is True

	model.end_season()
	ferrari_model = model.get_team_model("Ferrari")
	assert ferrari_model.driver1 != "Michael Schumacher"

def test_retirment_age():
	model = create_model.create_model()

	# Test Schumacher retirement
	schumacher_model = model.get_driver_model("Michael Schumacher")
	schumacher_model.retiring_age = 55
	
	model.staff_market.setup_dataframes()
	model.staff_market.determine_driver_transfers()

	save_file = load_save.save_game(model, mode="memory")

	model = create_model.create_model() # reset the model
	load_save.load(model, save_file, mode="memory") # load data

	schumacher_model = model.get_driver_model("Michael Schumacher")
	assert schumacher_model.retiring_age == 55

def test_year_week():
	model = create_model.create_model()

	model.year = 1900
	model.season.current_week = 10

	save_file = load_save.save_game(model, mode="memory")

	model = create_model.create_model() # reset the model
	load_save.load(model, save_file, mode="memory") # load data

	assert model.year == 1900
	assert model.season.current_week == 10