from tests import create_model

from pw_model.staff_market import manager_transfers
from pw_model.pw_model_enums import StaffRoles

def test_driver_retirement_team_end_season():
	'''
	check that at the end of the season, a retiring manager is not longer listed under free agents
	'''

	model = create_model.create_model(mode="headless")
	team_model = model.entity_manager.get_team_model("Ferano")

	# RETIRE BRAWN
	brawn_model = model.entity_manager.get_technical_director_model("Rob Brann")
	brawn_model.contract.contract_length = 1
	brawn_model.retiring = True

	# RETIRE Tyrrell
	tyrrell_model = model.entity_manager.get_team_principal_model("Ken Tyrrell")
	tyrrell_model.contract.contract_length = 1
	tyrrell_model.retiring = True
	
	# reset the staff market to account for Brawn retiring
	model.staff_market.setup_dataframes()
	assert "Ferano" in model.staff_market.compile_teams_requiring_manager(StaffRoles.TECHNICAL_DIRECTOR)
	assert "Tarnwell" in model.staff_market.compile_teams_requiring_manager(StaffRoles.TEAM_PRINCIPAL)

	model.staff_market.compute_transfers()
	model.end_season()

	assert "Rob Brann" not in manager_transfers.get_free_agents(model, StaffRoles.TECHNICAL_DIRECTOR)
	assert "Rob Brann" not in model.staff_market.grid_this_year_df[StaffRoles.TECHNICAL_DIRECTOR.value].values

	assert "Ken Tyrrell" not in manager_transfers.get_free_agents(model, StaffRoles.TEAM_PRINCIPAL)
	assert "Ken Tyrrell" not in model.staff_market.grid_this_year_df[StaffRoles.TEAM_PRINCIPAL.value].values
