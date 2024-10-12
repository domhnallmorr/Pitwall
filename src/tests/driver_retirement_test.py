from tests import create_model
from pw_model.staff_market import staff_market

import pytest


def test_driver_retirement_team_end_season():
	'''
	test that when a driver is retiring, that drivers next season gets updated appropriately
	'''

	model = create_model.create_model()

	team_model = model.get_team_model("Ferrari")

	# RETIRE SCHUMACHER and IRVINE
	schumacher_model = model.get_driver_model("Michael Schumacher")
	schumacher_model.retiring = True

	irvine_model = model.get_driver_model("Eddie Irvine")
	irvine_model.retiring = True

	model.staff_market.team_hire_driver("Ferrari", "driver1", ["Jos Verstappen"])
	model.staff_market.team_hire_driver("Ferrari", "driver2", ["Marc Gene"])

	# Make sure hired drivers no longer available for hire
	assert "Jos Verstappen" not in model.staff_market.get_free_agents()
	assert "Marc Gene" not in model.staff_market.get_free_agents()

	# complete all other driver transfers and end the season in the model
	model.staff_market.ensure_player_has_drivers_for_next_season()
	model.staff_market.determine_driver_transfers()
	model.end_season()

	# ensure ferrari's drivers have refreshed
	assert team_model.driver1 == "Jos Verstappen"
	assert "Jos Verstappen" in model.season.standings_manager.drivers_standings_df["Driver"].values

	assert team_model.driver2 == "Marc Gene"
	assert "Marc Gene" in model.season.standings_manager.drivers_standings_df["Driver"].values

	# Ensure schumacher and irvine not in standings
	assert "Michael Schumacher" not in model.season.standings_manager.drivers_standings_df["Driver"].values
	assert "Eddie Irvine" not in model.season.standings_manager.drivers_standings_df["Driver"].values

def test_driver_retirements_over_several_seasons():
	'''
	Run multiple seaosn, retire select drivers each season, ensure that the grid remains populated
	'''
	for i in range(50):
		model = create_model.create_model()
		for year in range(10):
			if year == 0:
				model.get_driver_model("Damon Hill").retiring = True
			if year == 1:
				model.get_driver_model("Esteban Tuero").retiring = True
			if year == 2:
				model.get_driver_model("Alexander Wurz").retiring = True
			if year == 3:
				model.get_driver_model("Jacques Villeneuve").retiring = True
			if year == 4:
				model.get_driver_model("Giancarlo Fisichella").retiring = True
			if year == 5:
				model.get_driver_model("Tora Takagi").retiring = True


			model.staff_market.ensure_player_has_drivers_for_next_season()
			model.staff_market.determine_driver_transfers()
			model.end_season()