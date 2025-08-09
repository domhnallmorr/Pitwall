from tests import create_model
from pw_model.staff_market import staff_market
from pw_model.staff_market import driver_transfers
from pw_model.pw_model_enums import StaffRoles
import pytest


def test_driver_retirement_team_end_season():
	'''
	test that when a driver is retiring, that drivers next season gets updated appropriately
	'''

	model = create_model.create_model(mode="headless")

	team_model = model.entity_manager.get_team_model("Ferano")

	# RETIRE SCHUMACHER and IRVINE
	schumacher_model = model.entity_manager.get_driver_model("Marco Schneider")
	schumacher_model.retiring = True

	irvine_model = model.entity_manager.get_driver_model("Evan Irving")
	irvine_model.retiring = True

	driver_transfers.team_hire_driver(model, "Ferano", StaffRoles.DRIVER1, ["Jan van der Veen"])
	driver_transfers.team_hire_driver(model, "Ferano", StaffRoles.DRIVER2, ["Marc Gene"])

	# Make sure hired drivers no longer available for hire
	assert "Jan van der Veen" not in driver_transfers.get_free_agents(model)
	assert "Marc Gene" not in driver_transfers.get_free_agents(model)

	# complete all other driver transfers and end the season in the model
	model.staff_market.ensure_player_has_staff_for_next_season()
	model.staff_market.compute_transfers()
	model.end_season()

	# ensure ferrari's drivers have refreshed
	assert team_model.driver1 == "Jan van der Veen"
	assert "Jan van der Veen" in model.season.standings_manager.drivers_standings_df["Driver"].values

	assert team_model.driver2 == "Marc Gene"
	assert "Marc Gene" in model.season.standings_manager.drivers_standings_df["Driver"].values

	# Ensure schumacher and irvine not in standings
	assert "Marco Schneider" not in model.season.standings_manager.drivers_standings_df["Driver"].values
	assert "Evan Irving" not in model.season.standings_manager.drivers_standings_df["Driver"].values

def test_driver_retirements_over_several_seasons():
	'''
	Run multiple seaosn, retire select drivers each season, ensure that the grid remains populated
	'''
	for i in range(50):
		model = create_model.create_model(mode="headless", auto_save=False)
		for year in range(10):
			if year == 0:
				model.entity_manager.get_driver_model("Donovan Upland").retiring = True
			if year == 1:
				model.entity_manager.get_driver_model("Eduardo Torres").retiring = True
			if year == 2:
				model.entity_manager.get_driver_model("Andreas Wurst").retiring = True
			if year == 3:
				model.entity_manager.get_driver_model("John Newhouse").retiring = True
			if year == 4:
				model.entity_manager.get_driver_model("Fabrizio Giorgetti").retiring = True
			if year == 5:
				model.entity_manager.get_driver_model("Toshiro Tanaka").retiring = True


			model.staff_market.ensure_player_has_staff_for_next_season()
			model.staff_market.compute_transfers()
			model.end_season()