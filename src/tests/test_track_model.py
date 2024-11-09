from pw_model.track import track_model

def create_dummy_track():
	data = [
		"Name: A1 Ring",
		"Country: Austria",
		"Location: Spielberg",
		"Title: Austrian Grand Prix",
		"Laps: 71",
		"Base Laptime: 84_000",
	]

	return track_model.TrackModel(None, data)

	
def test_track_fuel_consumption():
	track_model = create_dummy_track()

	# fuel consumption should be 155kg / 71 == 2.18 - 0.1 = 2.08
	# the -0.1 is an attempt to avoid cars running out of fuel
	assert track_model.fuel_consumption == 2.08