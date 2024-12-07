from tests import create_model

from pw_model.staff_market import manager_transfers
from pw_model.pw_model_enums import StaffRoles

def test_driver_retirement_team_end_season():
	'''
	check that at the end of the season, a retiring manager is not longer listed under free agents
	'''

	model = create_model.create_model(mode="headless")
	team_model = model.get_team_model("Ferrari")

	# RETIRE BRAWN
	brawn_model = model.get_technical_director_model("Ross Brawn")
	brawn_model.contract.contract_length = 1
	brawn_model.retiring = True
	
	# reset the staff market to account for Brawn retiring
	model.staff_market.setup_dataframes()
	assert "Ferrari" in model.staff_market.compile_teams_requiring_manager(StaffRoles.TECHNICAL_DIRECTOR)

	model.staff_market.compute_transfers()
	print(model.staff_market.grid_next_year_df)
	model.end_season()

	assert "Ross Brawn" not in manager_transfers.get_free_agents(model, StaffRoles.TECHNICAL_DIRECTOR)
	assert "Ross Brawn" not in model.staff_market.grid_this_year_df[StaffRoles.TECHNICAL_DIRECTOR.value].values
