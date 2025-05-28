import matplotlib.pyplot as plt

from tests import create_model

def test_sponsorship_update():

	model = create_model.create_model(mode="headless")

	for idx, team in enumerate(["Ferano", "Pascal", "Marchetti"]):
		team_model = model.entity_manager.get_team_model(team)

		sponsorship_values = []
		indices = []
		for i in range(150):
			team_model.end_season(increase_year=True)
			model.player_team = team
			sponsorship_values.append(team_model.finance_model.sponsorship_model.other_sponsorship)
			indices.append(i)

		assert max(sponsorship_values) <= 20_000_000
		plt.scatter(indices, sponsorship_values, label=team)

	plt.ylim(0, 55_000_000)
	plt.grid()
	plt.legend()

	plt.savefig("sponsorship_values.png")

def test_end_season():
	model = create_model.create_model(mode="headless")

	team_model = model.entity_manager.get_team_model("Ferano")

	commercial_manager_age = team_model.commercial_manager_model.age

	team_model.commercial_manager_model.end_season()

	assert team_model.commercial_manager_model.age == commercial_manager_age + 1

	'''
	Test that model end season method updates commercial manager as expected
	'''
	model.end_season()

	assert team_model.commercial_manager_model.age == commercial_manager_age + 2