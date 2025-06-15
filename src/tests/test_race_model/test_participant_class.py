
from tests import create_model
from race_weekend_model.race_model_enums import ParticipantStatus

def test_base_laptime():
	model = create_model.create_model()

	race_model = create_model.create_race_model(model)

	schumacher_model = race_model.get_particpant_model_by_name("Marco Schneider")
	irvine_model = race_model.get_particpant_model_by_name("Evan Irving")

	nakano_model = race_model.get_particpant_model_by_name("Kazuki Nakamura")

	assert schumacher_model.laptime_manager.base_laptime < irvine_model.laptime_manager.base_laptime
	assert nakano_model.laptime_manager.base_laptime - schumacher_model.laptime_manager.base_laptime < 6_000
 
