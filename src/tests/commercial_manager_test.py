import matplotlib.pyplot as plt

from tests import create_model

def test_sponsorship_update():

	model = create_model.create_model()

	for idx, team in enumerate(["Ferrari", "Prost", "Minardi"]):
		team_model = model.get_team_model(team)

		sponsorhip_values = []
		indices = []
		for i in range(150):
			team_model.end_season(increase_year=True)
			model.player_team = team
			sponsorhip_values.append(team_model.finance_model.total_sponsorship)
			indices.append(i)

		assert max(sponsorhip_values) <= 50_000_000
		plt.scatter(indices, sponsorhip_values, label=team)

	plt.ylim(0, 55_000_000)
	plt.grid()
	plt.legend()

	plt.savefig("sponsorship_values.png")

def test_end_season():
	model = create_model.create_model()

	team_model = model.get_team_model("Ferrari")

	commercial_manager_age = team_model.commercial_manager_model.age

	team_model.commercial_manager_model.end_season()

	assert team_model.commercial_manager_model.age == commercial_manager_age + 1

	'''
	Test that model end season method updates commercial manager as expected
	'''
	model.end_season()

	assert team_model.commercial_manager_model.age == commercial_manager_age + 2