
from tests import create_model
from race_weekend_model.race_model_enums import ParticipantStatus

def test_base_laptime():
	model = create_model.create_model()

	race_model = create_model.create_race_model(model)

	schumacher_model = race_model.get_particpant_model_by_name("Michael Schumacher")
	irvine_model = race_model.get_particpant_model_by_name("Eddie Irvine")

	nakano_model = race_model.get_particpant_model_by_name("Shinji Nakano")

	assert schumacher_model.laptime_manager.base_laptime < irvine_model.laptime_manager.base_laptime
	assert nakano_model.laptime_manager.base_laptime - schumacher_model.laptime_manager.base_laptime < 6_000
 
