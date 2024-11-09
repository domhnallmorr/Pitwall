from tests import create_model
from pw_model.staff_market import staff_market

def test_update_team_drivers():
	'''
	Test that drivers are signed and allocated to AI teams correctly
	'''
	model = create_model.create_model(auto_save=False)

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

def test_top3_drivers_logic():
	'''
	Current logic is that top 3 drivers should be in one the top 4 teams.
	make the top 3 drivers available (MS, MH and JV). Also make the Benetton driver 1 seat available
	Test that the top 3 drivers end up in one of the 4 seats
	'''

	for i in range(50):
		model = create_model.create_model(mode="headless", auto_save=False)

		schumacher_model = model.get_driver_model("Michael Schumacher")
		hakkinen_model = model.get_driver_model("Mika Hakkinen")
		villeneuve_model = model.get_driver_model("Jacques Villeneuve")
		fisichella_model = model.get_driver_model("Giancarlo Fisichella")

		schumacher_model.contract.contract_length = 1
		hakkinen_model.contract.contract_length = 1
		villeneuve_model.contract.contract_length = 1
		fisichella_model.contract.contract_length = 1

		model.staff_market.setup_dataframes()

		model.staff_market.determine_driver_transfers()
		model.staff_market.update_team_drivers()

		top_4_teams_driver1 = []

		for team in ["Ferrari", "Williams", "McLaren", "Benetton"]:
			team_model = model.get_team_model(team)
			top_4_teams_driver1.append(team_model.driver1)

		assert "Michael Schumacher" in top_4_teams_driver1
		assert "Mika Hakkinen" in top_4_teams_driver1
		assert "Jacques Villeneuve" in top_4_teams_driver1

def test_week_to_announce_signing():
	'''
	Ensure that the week to annouce signing is between weeks 4 and 40
	'''

	model = create_model.create_model(mode="headless", auto_save=False)

	for i in range(20*52):
		weeks = model.staff_market.new_contracts_df["WeekToAnnounce"].values.tolist()
		if len(weeks) > 0:
			assert min(weeks) >= 4
			assert max(weeks) <= 40

		model.advance()