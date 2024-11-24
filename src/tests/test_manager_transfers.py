
from pw_model.staff_market import manager_transfers
from pw_model.pw_model_enums import StaffRoles
from tests import create_model

def test_free_agents():
	model = create_model.create_model(mode="headless", auto_save=False)

	free_agents = manager_transfers.get_free_agents(model, role=StaffRoles.TECHNICAL_DIRECTOR, for_player_team=True)

	assert len(free_agents) == 14
	
	assert free_agents == ["Gary Anderson", "Bernard Dudot", "John Barnard", "Alan Jenkins", "Harvey Postlethwaite",
						"Frank Dernie", "Loïc Bigois",
						"Gabriele Tredozi",
						"Adrian Reynard",
						"Mike Coughlan",
						"Mike Gascoyne",
						"Neil Oatley",
						"Sergio Rinland",
						"Aldo Costa",]
	
	# repeat test just not for player team
	free_agents = manager_transfers.get_free_agents(model, role=StaffRoles.TECHNICAL_DIRECTOR, for_player_team=False)

	# the model should have computed the transfers for the 5 teams looking for a tech director
	# this should reduce free agents to 14 - 5 = 9
	assert len(free_agents) == 9