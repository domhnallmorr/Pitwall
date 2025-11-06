
from pw_model.staff_market import manager_transfers
from pw_model.pw_model_enums import StaffRoles
from tests import create_model

def test_free_agents():
	model = create_model.create_model(mode="headless", auto_save=False)
	free_agents = manager_transfers.get_free_agents(model, role=StaffRoles.TECHNICAL_DIRECTOR, for_player_team=True)

	expected_len = 0
	for td_model in model.technical_directors:
		if td_model.retiring is False and td_model.contract.contract_length < 2:
			expected_len += 1

	assert len(free_agents) == expected_len
		
	# repeat test just not for player team
	free_agents = manager_transfers.get_free_agents(model, role=StaffRoles.TECHNICAL_DIRECTOR, for_player_team=False)

	# the model should have computed the transfers for the 5 teams looking for a tech director
	assert len(free_agents) == expected_len - 5

def test_get_top_technical_directors():
	model = create_model.create_model(mode="headless", auto_save=False)
	model.staff_market.setup_dataframes() # reset any transfers the staff market implemented

	top_technical_directors = manager_transfers.get_top_available_technical_directors(model, 5)
	# Only John Barnard should be available by default
	assert top_technical_directors == ["James Barnwood"]

	# Make newey available and check he get's picked up
	newey_model = model.entity_manager.get_technical_director_model("Aidan Newson")
	newey_model.contract.contract_length = 1
	newey_model.retiring = False
	model.staff_market.setup_dataframes()

	top_technical_directors = manager_transfers.get_top_available_technical_directors(model, 5)
	assert len(top_technical_directors) == 2
	assert "Aidan Newson" in top_technical_directors
	assert "James Barnwood" in top_technical_directors

def test_top_5_technical_directors():
	model = create_model.create_model(mode="headless", auto_save=False)

	for i in range(50):
		assert "James Barnwood" not in manager_transfers.get_free_agents(model, StaffRoles.TECHNICAL_DIRECTOR)
		model.staff_market.setup_dataframes()
		model.staff_market.compute_transfers()

def test_teams_requiring_commercial_manager():
	model = create_model.create_model(mode="headless", auto_save=False)
	model.staff_market.setup_dataframes()

	teams_requiring_commercial_manager = model.staff_market.compile_teams_requiring_manager(StaffRoles.COMMERCIAL_MANAGER)

	assert len(teams_requiring_commercial_manager) == 4

def test_manager_transfer_at_season_end():
	model = create_model.create_model(mode="headless", auto_save=False)

	for i in range(10): # test for 10 seasons
		computed_transfers = model.staff_market.grid_next_year_df.copy(deep=True)
		model.end_season()

		for idx, row in computed_transfers.iterrows():
			team = row["team"]
			team_model = model.entity_manager.get_team_model(team)

			assert team_model.technical_director == row[StaffRoles.TECHNICAL_DIRECTOR.value]
			assert team_model.commercial_manager == row[StaffRoles.COMMERCIAL_MANAGER.value]

def test_player_hire_commercial_manager():
	'''
	Test when the player signs a commercial manager, that manger is not signed by any other team
	'''
	model = create_model.create_model(mode="headless", auto_save=False)
	model.player_team = "Benedetti"

	for i in range(50):
		model.staff_market.complete_hiring("Les Olsen", "Benedetti", StaffRoles.COMMERCIAL_MANAGER)

		assert model.staff_market.grid_next_year_df[StaffRoles.COMMERCIAL_MANAGER.value].values.tolist().count("Les Olsen") == 1

	'''
	Test that the player team's commercial manager is Les Oslen at start of next season (ai teams are tested in test_manager_transfer_at_season_end)
	'''
	model.end_season()
	assert model.player_team_model.commercial_manager == "Les Olsen"