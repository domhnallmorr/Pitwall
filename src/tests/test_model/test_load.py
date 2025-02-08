
import pytest

from tests import create_model
from pw_model.load_save.load_save import save_game, load

def test_retirements():

	model = create_model.create_model(mode="headless")

	# Test Schumacher retirement
	schumacher_model = model.get_driver_model("Michael Schumacher")
	schumacher_model.retiring_age = schumacher_model.age
	schumacher_model.handle_start_of_retiring_season()
	
	model.staff_market.setup_dataframes()
	model.staff_market.compute_transfers()

	save_file = save_game(model, mode="memory")

	model = create_model.create_model() # reset the model
	load(model, save_file, mode="memory") # load data

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
	model.staff_market.compute_transfers()

	save_file = save_game(model, mode="memory")

	model = create_model.create_model() # reset the model
	load(model, save_file, mode="memory") # load data

	schumacher_model = model.get_driver_model("Michael Schumacher")
	assert schumacher_model.retiring_age == 55

def test_year_week():
	model = create_model.create_model()

	model.year = 1900
	model.season.calendar.current_week = 10

	save_file = save_game(model, mode="memory")

	model = create_model.create_model() # reset the model
	load(model, save_file, mode="memory") # load data

	assert model.year == 1900
	assert model.season.calendar.current_week == 10

def test_retirement_age_senior_manager():
	model = create_model.create_model()

	brawn_model = model.get_technical_director_model("Ross Brawn")
	brawn_model.retiring_age = 45
	brawn_model.retired = True
	brawn_model.retiring = True

	save_file = save_game(model, mode="memory")
	model = create_model.create_model() # reset the model
	load(model, save_file, mode="memory") # load data

	brawn_model = model.get_technical_director_model("Ross Brawn")

	assert brawn_model.retired is True
	assert brawn_model.retiring_age == 45
	assert brawn_model.retiring is True
