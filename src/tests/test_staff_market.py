from tests import create_model
from pw_model.staff_market import staff_market

def test_update_team_drivers():
	'''
	Test that drivers are signed and allocated to AI teams correctly
	'''
	model = create_model.create_model()

	model.player_team = None

	# reset the staff market
	model.staff_market = staff_market.StaffMarket(model)


	for year in [1998, 1999, 2000, 2001]: # run test for a couple of seasons
		if year > 1998:
			model.year += 1
			model.add_new_drivers()

			for driver in model.drivers:
				driver.end_season(increase_age=True)

		model.staff_market.setup_dataframes()
		model.staff_market.determine_driver_transfers()
		model.staff_market.update_team_drivers()

		for idx, row in model.staff_market.grid_next_year_df.iterrows():
			team = row["team"]

			team_model = model.get_team_model(team)

			#ensure driver transfers applied correctly
			assert team_model.driver1 == row["driver1"]
			assert team_model.driver2 == row["driver2"]

			# ensure no driver has a contract length of 0 or less
			assert team_model.driver1_model.contract.contract_length > 0	
			assert team_model.driver2_model.contract.contract_length > 0

