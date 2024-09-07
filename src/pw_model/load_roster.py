import glob
import os
import re

import pandas as pd

from pw_model.car import car_model
from pw_model.driver import driver_model
from pw_model.team import team_model
from pw_model.track import track_model

def load_roster(model, roster):

	drivers_file, teams_file, season_file, track_files = checks(model, roster)

	model.drivers, model.future_drivers = load_drivers(model, drivers_file)
	model.teams = load_teams(model, teams_file)

	load_tracks(model, track_files)
	model.calendar = load_season(model, season_file)
	

def load_drivers(model, drivers_file):
	drivers = []
	future_drivers = []

	with open(drivers_file) as f:
		data = f.readlines()

	for idx, line in enumerate(data[1:]):
		line = line.split(",")

		if line[0].lower() == "default":
			name = line[1].lstrip().rstrip()
			age = int(line[2])
			country = line[3]
			speed = int(line[4])

			driver = driver_model.DriverModel(model, name, age, country, speed)
			drivers.append(driver)
		else:
			future_drivers.append(line)
	
	return drivers, future_drivers

def load_teams(model, teams_file):
	teams = []
	with open(teams_file) as f:
		data = f.readlines()

	for idx, line in enumerate(data[1:]):
		line = line.split(",")

		if line[0].lower() == "default":
			name = line[1].lstrip().rstrip()
			driver1 = line[2].lstrip().rstrip()
			driver2 = line[3].lstrip().rstrip()
			car_speed = int(line[4].lstrip().rstrip())
			
			car = car_model.CarModel(car_speed)
			team = team_model.TeamModel(model, name, driver1, driver2, car)
			
			# ensure drivers are correctly loaded
			assert team.driver1_model is not None
			assert team.driver2_model is not None

			teams.append(team)

	return teams

def create_driver(line_data, model):
	name = line_data[1].lstrip().rstrip()
	age = int(line_data[2])
	country = line_data[3]
	speed = int(line_data[4])

	driver = driver_model.DriverModel(model, name, age, country, speed)
	
	return driver

def load_season(model, season_file):

	with open(season_file) as f:
		data = f.readlines()

	# PROCESS CALENDAR
	for idx, line in enumerate(data):
		if line.lower().startswith("calendar<"):
			start_idx = idx
		elif line.lower().startswith("calendar>"):
			end_idx = idx

	assert end_idx - start_idx + 1 > 2

	calendar_data = data[start_idx + 1: end_idx]
	dataframe_data = []

	columns = ["Week", "Track", "Country", "Location"]

	for line in calendar_data:
		race_data = line.rstrip().split(",")
		week = int(race_data[1])
		track = model.get_track_model(race_data[0].rstrip().lstrip())

		dataframe_data.append([week, track.name, track.country, track.location])
	
	calendar = pd.DataFrame(columns=columns, data=dataframe_data)

	return calendar
	
def load_tracks(model, track_files):
	for file in track_files:
		with open(file) as f:
			data = f.readlines()

		data = [l.rstrip() for l in data]
		track = track_model.TrackModel(model, data)
		model.tracks.append(track)

def checks(model, roster):

	# check files present
	drivers_file = os.path.join(model.run_directory, roster, "drivers.txt")
	assert os.path.isfile(drivers_file), f"Cannot Find {drivers_file}"

	teams_file = os.path.join(model.run_directory, roster, "teams.txt")
	assert os.path.isfile(drivers_file), f"Cannot Find {teams_file}"

	season_file = os.path.join(model.run_directory, roster, "season.txt")
	assert os.path.isfile(season_file), f"Cannot Find {season_file}"

	drivers_names = check_drivers_file_format(drivers_file)
	#TODO finish teams file checks
	check_teams_file_format(teams_file, drivers_names)

	tracks_folder = os.path.join(model.run_directory, roster, "tracks")
	assert os.path.isdir(tracks_folder), f"Cannot Find {tracks_folder}"

	track_files = glob.glob(os.path.join(tracks_folder, "*.txt"))

	return drivers_file, teams_file, season_file, track_files

def check_drivers_file_format(drivers_file):
	drivers_names = []

	with open(drivers_file) as f:
		data = f.readlines()
	
	# Check we have at least 1 driver
	assert len(data) > 1, "Insufficient Data in drivers.txt File"
	headers = "Year,Name,Age,Country,Speed"

	# check headers are correct
	assert data[0] == headers + "\n", "Incorrect Headers in drivers.txt File"

	for idx, line in enumerate(data[1:]):
		line = line.rstrip().split(",")
		# check number of fields correct (comma delimited)
		assert len(line) == len(headers.split(",")), f"drivers.txt file, Line {idx + 2}, Expected {len(headers)} Fields, Found {len(line)}"

		# check first field is default or a year
		if line[0].lower() != "default":
			pattern = r'^\d{4}$'
			assert re.match(pattern, line[0]) is not None, f"drivers.txt file, Line {idx + 2}, Year Field Must be 'default' or Year in Format YYYY. Found '{line[0]}'"

		# ensure drivers name field is populated
		assert line[1].strip() != "", f"drivers.txt file, Line {idx + 2}, Driver Name Field Not Populated"
		drivers_names.append(line[1].strip())

		# check age is in correct format
		pattern = r'^\d{2}$'
		assert re.match(pattern, line[2]) is not None, f"drivers.txt file, Line {idx + 2}, Driver Age Field Must be Numeric in the Format 'XY', Found '{line[2]}'"

		#TODO check country, speed
		return drivers_names
	
def check_teams_file_format(teams_file, drivers_names):
	with open(teams_file) as f:
		data = f.readlines()
	
	# Check we have at least 1 driver
	assert len(data) > 1, "Insufficient Data in teams.txt File"
	headers = "Year,Name,Driver1,Driver2,Car Speed"

	# check headers are correct
	assert data[0] == headers + "\n", "Incorrect Headers in teams.txt File"

	for idx, line in enumerate(data[1:]):
		line = line.rstrip().split(",")

# def check_season_file_format(season_file):
