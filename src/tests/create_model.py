import os
from pw_model import pw_model
from race_model import race_model


def create_model(mode="normal", auto_save=True):
	run_directory = os.path.dirname(os.path.join(os.path.abspath(__file__)))
	run_directory = os.path.dirname(run_directory) # go one level up to src folder

	roster = "1998_Roster"

	return pw_model.Model(roster, run_directory, mode=mode, auto_save=auto_save)

def create_race_model(model):
	return race_model.RaceModel("headless", model, model.tracks[0])
