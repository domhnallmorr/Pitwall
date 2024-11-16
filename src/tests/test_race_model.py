from tests import create_model
from race_model import race_model
from race_model.race_model_enums import SessionNames
from pw_model.track import track_model

from tests import test_track_model

def test_participants_creation():
	model = create_model.create_model(mode="headless")
	
	# Make Jorg Muller the 2nd Ferrari driver, will do check to ensure he is in the participants and Irvine is not
	ferrari_model = model.get_team_model("Ferrari")
	ferrari_model.driver2 = "Jorg Muller"

	track = test_track_model.create_dummy_track()
	_race_model = race_model.RaceModel("headless", model, track)

	assert len(_race_model.participants) == 22

	assert _race_model.get_particpant_model_by_name("Eddie Irvine") is None
	assert _race_model.get_particpant_model_by_name("Jorg Muller") is not None

	muller_model = _race_model.get_particpant_model_by_name("Jorg Muller")
	assert muller_model.driver.country == "Germany" # check the muller participant is picking up his model and not Irvine's
	assert muller_model.driver.speed == 48

	# Do some spot checks on participants speed to ensure they've picked up the correct driver model
	schumacher_model = _race_model.get_particpant_model_by_name("Michael Schumacher")
	assert schumacher_model.driver.speed == 98

	diniz_model = _race_model.get_particpant_model_by_name("Pedro Diniz")
	assert diniz_model.driver.speed == 65

def test_session_setup():
	model = create_model.create_model(mode="headless")

	track = test_track_model.create_dummy_track()
	_race_model = race_model.RaceModel("headless", model, track)

	_race_model.setup_qualifying(60*60, SessionNames.QUALIFYING)

	assert _race_model.current_session.time_left == 3600

	# check particpants have qualy runs generated
	for participant in _race_model.participants:
		assert len(participant.practice_runs) == 4
		for run in participant.practice_runs:
			assert run[1] == 3
			assert run[2] == 3



