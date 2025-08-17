import random

import pandas as pd

from tests import create_model
from race_weekend_model import race_weekend_model
from race_weekend_model.race_model_enums import SessionNames
from tests.test_model.track import test_track_model

def test_grid_order():
	model = create_model.create_model(mode="headless")
	
	# Make Jorg Muller the 2nd Ferrari driver, will do check to ensure he is in the participants and Irvine is not
	ferrari_model = model.entity_manager.get_team_model("Ferano")
	ferrari_model.driver2 = "Jorn Maller"

	track = test_track_model.create_dummy_track()
	_race_model = race_weekend_model.RaceWeekendModel("headless", model, track)

	# SETUP DUMMY GRID ORDER
	grid_order = random.shuffle([p.name for p in _race_model.participants])

	_race_model.results[SessionNames.QUALIFYING.value]= {}
	_race_model.results[SessionNames.QUALIFYING.value]["results"] = pd.DataFrame(columns=["Driver"], data=grid_order)

	_race_model.setup_race()
	_race_model.current_session.standings_model.setup_grid_order()

	for idx, row in _race_model.current_session.standings_model.dataframe.iterrows():
		assert row["Driver"] == grid_order[idx - 1]
		participant_model = _race_model.get_particpant_model_by_name(row["Driver"])
		assert participant_model.starting_position == idx