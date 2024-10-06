import glob
import os
import re
import sqlite3

import pandas as pd

from pw_model.car import car_model
from pw_model.driver import driver_model
from pw_model.team import team_model
from pw_model.track import track_model

def load_roster(model, roster):

	conn = sqlite3.connect(f"{model.run_directory}\\{roster}\\roster.db")

	season_file, track_files = checks(model, roster)

	model.drivers, model.future_drivers = load_drivers(model, conn)
	model.teams = load_teams(model, conn)

	load_tracks(model, track_files)
	model.calendar = load_season(model, season_file)
	

def load_drivers(model, conn):
	drivers = []
	future_drivers = []

	table_name = "drivers"
	cursor = conn.execute(f'PRAGMA table_info({table_name})')
	columns = cursor.fetchall()
	column_names = [column[1] for column in columns]

	name_idx = column_names.index("Name")
	age_idx = column_names.index("Age")
	country_idx = column_names.index("Country")
	speed_idx = column_names.index("Speed")

	cursor = conn.cursor()
	cursor.execute(f"SELECT * FROM {table_name}")
	drivers_table = cursor.fetchall()

	for row in drivers_table:
		name = row[name_idx]
		age = row[age_idx]
		country = row[country_idx]
		speed = row[speed_idx]

		driver = driver_model.DriverModel(model, name, age, country, speed)
		
		if "RetiringAge" in column_names:
			retiring_age_idx = column_names.index("RetiringAge")
			retiring_age = row[retiring_age_idx]
			driver.retiring_age = retiring_age

			retiring_idx = column_names.index("Retiring")
			retiring = bool(row[retiring_idx])
			driver.retiring = retiring

			retired_idx = column_names.index("Retired")
			retired = bool(row[retired_idx])
			driver.retired = retired

		if row[0].lower() == "default":
			drivers.append(driver)
		else:
			future_drivers.append([row[0], driver])

	return drivers, future_drivers

def load_teams(model, conn):
	teams = []

	table_name = "teams"

	cursor = conn.execute(f'PRAGMA table_info({table_name})')
	columns = cursor.fetchall()
	column_names = [column[1] for column in columns]

	name_idx = column_names.index("Name")
	driver1_idx = column_names.index("Driver1")
	driver2_idx = column_names.index("Driver2")
	car_speed_idx = column_names.index("CarSpeed")
	number_of_staff_idx = column_names.index("NumberofStaff")
	facilities_idx = column_names.index("Facilities")
	balance_idx = column_names.index("StartingBalance")
	starting_sponsorship_idx = column_names.index("StartingSponsorship")

	cursor = conn.cursor()
	cursor.execute(f"SELECT * FROM {table_name}")
	teams_table = cursor.fetchall()

	for row in teams_table:
		if row[0].lower() == "default":
			name = row[name_idx]
			driver1 = row[driver1_idx]
			driver2 = row[driver2_idx]
			car_speed = row[car_speed_idx]

			facilities = row[facilities_idx]
			number_of_staff = row[number_of_staff_idx]

			starting_balance = row[balance_idx]
			starting_sponsorship = row[starting_sponsorship_idx]

			car = car_model.CarModel(car_speed)
			team = team_model.TeamModel(model, name, driver1, driver2, car, number_of_staff, facilities, starting_balance, starting_sponsorship)
			
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

	season_file = os.path.join(model.run_directory, roster, "season.txt")
	assert os.path.isfile(season_file), f"Cannot Find {season_file}"

	tracks_folder = os.path.join(model.run_directory, roster, "tracks")
	assert os.path.isdir(tracks_folder), f"Cannot Find {tracks_folder}"

	track_files = glob.glob(os.path.join(tracks_folder, "*.txt"))

	return season_file, track_files


	

