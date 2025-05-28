from tests import create_model

def test_player_requring_staff():
	'''
	Added this test when a bug was found where the UI replace button 
	was disabled for Gary Anderson occasionaly on career start when player choose to play as Jordan
	Was determined that in the handle_top_5_technical_directors function in manager transfers
	was incorrectly including the players_team in the process.
	Keeping this test to ensure Jordan always need a tech director on game start up
	'''

	for i in range(100):
		model = create_model.create_model(auto_save=False)
		model.start_career("Joyce")

		assert model.staff_market.player_requiring_technical_director is True
		assert model.staff_market.player_requiring_driver2 is True # Ralf Schumachers contract runs out in 1998

	for i in range(100):
		model = create_model.create_model(auto_save=False)
		model.start_career("Warrick")
		assert model.staff_market.player_requiring_driver1 is True

	for i in range(100):
		model = create_model.create_model(auto_save=False)
		model.start_career("Marchetti")
		assert model.staff_market.player_requiring_commercial_manager is True