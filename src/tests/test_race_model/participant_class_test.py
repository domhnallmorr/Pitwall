
from tests import create_model


def test_base_laptime():
	model = create_model.create_model()

	race_model = create_model.create_race_model(model)

	schumacher_model = race_model.get_particpant_model_by_name("Michael Schumacher")
	irvine_model = race_model.get_particpant_model_by_name("Eddie Irvine")

	nakano_model = race_model.get_particpant_model_by_name("Shinji Nakano")

	assert schumacher_model.base_laptime < irvine_model.base_laptime
	assert nakano_model.base_laptime - schumacher_model.base_laptime < 6_000

def test_laptimes():
	model = create_model.create_model()

	race_model = create_model.create_race_model(model)

	schumacher_model = race_model.get_particpant_model_by_name("Michael Schumacher")

	schumacher_model.car_model.fuel_load = 0

	laptimes = []
	gap_ahead = 10_000 # avoid dirty air
	schumacher_model.status = "running" # let model now driver is on track
	schumacher_model.current_lap = 2
	
	for i in range(50):
		schumacher_model.calculate_laptime(gap_ahead)
		laptimes.append(schumacher_model.laptime)

	assert max(laptimes) != min(laptimes)
	assert max(laptimes) - min(laptimes) <= 700 # check that 7 tenths is max diff in laptimes

def test_dirty_air():
	model = create_model.create_model()
	race_model = create_model.create_race_model(model)
	schumacher_model = race_model.get_particpant_model_by_name("Michael Schumacher")

	schumacher_model.car_model.fuel_load = 0

	schumacher_model.calculate_lap_time(0, 0)

	assert schumacher_model.laptime == schumacher_model.base_laptime

	schumacher_model.calculate_lap_time(0, 500)
	assert schumacher_model.laptime == schumacher_model.base_laptime + 500
 
