from tests import create_model
from race_weekend_model import race_weekend_model
from race_weekend_model.race_model_enums import SessionNames, SessionMode
from race_weekend_model.race_start_calculations import calculate_run_to_turn1
from pw_model.track import track_model

from tests.test_model.track import test_track_model

def test_participants_creation():
	model = create_model.create_model(mode="headless")
	
	# Make Jorg Muller the 2nd Ferrari driver, will do check to ensure he is in the participants and Irvine is not
	ferrari_model = model.entity_manager.get_team_model("Ferano")
	ferrari_model.driver2 = "Jorg Muller"

	track = test_track_model.create_dummy_track()
	_race_model = race_weekend_model.RaceWeekendModel("headless", model, track)

	assert len(_race_model.participants) == 22

	assert _race_model.get_particpant_model_by_name("Evan Irving") is None
	assert _race_model.get_particpant_model_by_name("Jorg Muller") is not None

	muller_model = _race_model.get_particpant_model_by_name("Jorg Muller")
	assert muller_model.driver.country == "Germany" # check the muller participant is picking up his model and not Irvine's
	assert muller_model.driver.speed == 48

	# Do some spot checks on participants speed to ensure they've picked up the correct driver model
	schumacher_model = _race_model.get_particpant_model_by_name("Marco Schneider")
	assert schumacher_model.driver.speed == 98

	diniz_model = _race_model.get_particpant_model_by_name("Pablo Dinez")
	assert diniz_model.driver.speed == 55

def test_run_to_turn_1():
	model = create_model.create_model(mode="headless")
	track = test_track_model.create_dummy_track()
	_race_model = race_weekend_model.RaceWeekendModel("headless", model, track)

	# Run qualy to establish a grid order
	_race_model.setup_qualifying(60*60, SessionNames.QUALIFYING)
	
	_race_model.setup_race()
	_race_model.current_session.mode = SessionMode.SIMULATE
	order_after_turn1 = calculate_run_to_turn1(_race_model)

	assert len(order_after_turn1) == 22
	names = [p[1] for p in order_after_turn1]
	assert len(list(set(names))) == 22
	times = [p[0] for p in order_after_turn1]
	assert max(times) < 50_000 # make sure theres no unusual large time to turn 1