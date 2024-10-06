
import pytest

from tests import create_model


def test_new_driver_creation():
	'''
	Test to ensure that new drivers are added correctly to the model
	at the start of each season
	'''
	model = create_model.create_model()
	model.start_career(player_team=None)

	# check that future driver data is stored in the model
	assert len(model.future_drivers) > 0

	# 

	# end season which calls the function to create the new drivers
	model.driver_market.ensure_player_has_drivers_for_next_season() # avoid assertion error None in grid_next_year_df.values
	model.end_season()

	# Button gets added at the start of 1999, so check that he is now in the game
	assert model.get_driver_model("Jenson Button") is not None

	# Check Button has been removed from future drivers
	for driver in model.future_drivers:
		assert driver[1].name != "Jenson Button"
