import matplotlib.pyplot as plt

from tests import create_model

def test_tyre_wear():
	model = create_model.create_model()

	race_model = create_model.create_race_model(model)

	schumacher_model = race_model.get_particpant_model_by_name("Michael Schumacher")

	race_model.setup_qualfying(60*60, "Qualy")
	race_model.simulate_session()

	tyre_wear = schumacher_model.tyre_wear_by_lap
	
	laps = [i for i in range(len(tyre_wear))]

	plt.plot(laps, tyre_wear, label="qualy")

	assert min(tyre_wear) < max(tyre_wear)

	race_model.setup_race()
	race_model.simulate_session()

	tyre_wear = schumacher_model.tyre_wear_by_lap

	assert min(tyre_wear) < max(tyre_wear)	

	laps = [i for i in range(len(tyre_wear))]

	plt.plot(laps, tyre_wear, label="race")
	plt.grid()
	plt.legend()
	plt.savefig(f"{model.run_directory }\\tests\\race_tyre_wear.png")
