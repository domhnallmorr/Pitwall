from tests import create_model
from pw_model import load_save


def test_add_new_managers():

	model = create_model.create_model(auto_save=False)

	model.year = 1999

	orig_number_tech_directors = len(model.technical_directors)
	model.add_new_managers()

	assert model.get_technical_director_model("Willy Rampf") is not None
	assert len(model.technical_directors) == orig_number_tech_directors + 1 

	save_file = load_save.save_game(model, mode="memory")

	load_save.load(model, save_file, mode="memory")
	model.year = 2000

	model.add_new_managers()
	# assert model.get_technical_director_model("Henri Durand") is not None
	assert len(model.technical_directors) == orig_number_tech_directors + 3