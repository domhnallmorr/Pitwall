from tests import create_model
from pw_model.load_save.load_save import save_game, load


def test_add_new_managers():

	model = create_model.create_model(auto_save=False)

	model.year = 1999

	orig_number_tech_directors = len(model.technical_directors)
	model.entity_manager.add_new_managers()

	assert model.entity_manager.get_technical_director_model("Willy Rampf") is not None
	assert len(model.technical_directors) == orig_number_tech_directors + 1 

	save_file = save_game(model, mode="memory")

	load(model, save_file, mode="memory")
	model.year = 2000

	model.entity_manager.add_new_managers()
	# assert model.entity_manager.get_technical_director_model("Henri Durand") is not None
	assert len(model.technical_directors) == orig_number_tech_directors + 3

	assert model.entity_manager.get_team_principal_model("Paul Stoddart") is not None