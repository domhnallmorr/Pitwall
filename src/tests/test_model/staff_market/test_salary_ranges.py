from pw_model.staff_market import manager_transfers
from pw_model.pw_model_enums import StaffRoles
from tests import create_model


def test_salary_ranges():
	''' 
	Test that salaries are within expected ranges when player hired someone
	'''

	model = create_model.create_model(auto_save=False)
	model.player_team == "Williams"

	muller_model = model.get_driver_model("Jorg Muller")
	gene_model = model.get_driver_model("Marc Gene")
	gene_model.speed = 99

	oatley_model = model.get_technical_director_model("Neil Oatley")
	gallagher_model = model.get_commercial_manager_model("Mark Gallagher")

	model.staff_market.complete_hiring("Marc Gene", "Williams", StaffRoles.DRIVER1, 3_200_000)
	model.staff_market.complete_hiring("Jorg Muller", "Williams", StaffRoles.DRIVER2, 700_000)
	model.staff_market.complete_hiring("Neil Oatley", "Williams", StaffRoles.TECHNICAL_DIRECTOR)
	model.staff_market.complete_hiring("Mark Gallagher", "Williams", StaffRoles.COMMERCIAL_MANAGER)
	model.end_season()

	assert gene_model.contract.salary == 3_200_000
	assert muller_model.contract.salary == 700_000
	assert oatley_model.contract.salary >= 700_000 and oatley_model.contract.salary <= 1_200_000
	assert gallagher_model.contract.salary >= 180_000 and gallagher_model.contract.salary <= 220_000

