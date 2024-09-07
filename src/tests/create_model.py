import os
from pw_model import pw_model


def create_model():

	run_directory = os.path.dirname(os.path.join(os.path.abspath(__file__)))
	run_directory = os.path.dirname(run_directory) # go one level up to src folder

	roster = "1998_Roster"

	return pw_model.Model(roster, run_directory)

