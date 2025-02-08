from __future__ import annotations
import glob
import os
from typing import TYPE_CHECKING, Tuple, List, Union
import sqlite3

import pandas as pd

from pw_model.car import car_model
from pw_model.driver import driver_model
from pw_model.team import team_model
from pw_model.track import track_model
from pw_model.senior_staff import commercial_manager, technical_director
from pw_model.load_save.sponsors_load_save import load_sponsors

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def load_roster(model: Model, roster: str) -> pd.DataFrame:

	conn = sqlite3.connect(f"{model.run_directory}\\{roster}\\roster.db")

	season_file, track_files = checks(model, roster)
	load_tracks(model, track_files)
	calendar_dataframe = load_season(model, season_file)
	
	model.drivers, model.future_drivers = load_drivers(model, conn)
	model.commercial_managers, model.technical_directors, model.future_managers = load_senior_staff(model, conn)
	model.teams = load_teams(model, conn)

	return calendar_dataframe
	

def load_drivers(
    model: Model, 
    conn: sqlite3.Connection
) -> Tuple[List[driver_model.DriverModel], List[List[Tuple[str, driver_model.DriverModel]]]]:
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
	consistency_idx = column_names.index("Consistency")
	contract_length_idx = column_names.index("ContractLength")
	salary_idx = column_names.index("Salary")

	cursor = conn.cursor()
	cursor.execute(f"SELECT * FROM {table_name}")
	drivers_table = cursor.fetchall()

	for row in drivers_table:
		name = row[name_idx]
		age = row[age_idx]
		country = row[country_idx]
		speed = row[speed_idx]
		consistency = row[consistency_idx]
		contract_length = row[contract_length_idx]
		salary = row[salary_idx]

		driver = driver_model.DriverModel(model, name, age, country, speed, consistency, contract_length, salary)
		
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
			future_drivers.append([row[0], driver]) # [year, driver]

	return drivers, future_drivers

def load_teams(model: Model, conn: sqlite3.Connection) -> list[team_model.TeamModel]:
	sponsors_df = load_sponsors(conn)

	teams = []

	table_name = "teams"

	cursor = conn.execute(f'PRAGMA table_info({table_name})')
	columns = cursor.fetchall()
	column_names = [column[1] for column in columns]

	name_idx = column_names.index("Name")
	country_idx = column_names.index("Country")
	driver1_idx = column_names.index("Driver1")
	driver2_idx = column_names.index("Driver2")
	car_speed_idx = column_names.index("CarSpeed")
	number_of_staff_idx = column_names.index("NumberofStaff")
	facilities_idx = column_names.index("Facilities")

	balance_idx = column_names.index("StartingBalance")

	commercial_manager_idx = column_names.index("CommercialManager")
	technical_director_idx = column_names.index("TechnicalDirector")

	cursor = conn.cursor()
	cursor.execute(f"SELECT * FROM {table_name}")
	teams_table = cursor.fetchall()

	for row in teams_table:
		if row[0].lower() == "default":
			name = row[name_idx]
			country = row[country_idx]
			driver1 = row[driver1_idx]
			driver2 = row[driver2_idx]
			car_speed = row[car_speed_idx]

			facilities = row[facilities_idx]
			number_of_staff = row[number_of_staff_idx]

			starting_balance = row[balance_idx]
			title_sponsor = str(sponsors_df.loc[sponsors_df["Team"] == name, "TitleSponsor"].iloc[0])
			title_sponsor_value = int(sponsors_df.loc[sponsors_df["Team"] == name, "TitleSponsorValue"].iloc[0])
			other_sponsorship = int(sponsors_df.loc[sponsors_df["Team"] == name, "OtherSponsorsValue"].iloc[0])

			if title_sponsor_value is not None:
				title_sponsor_value = int(title_sponsor_value)

			commercial_manager = row[commercial_manager_idx]
			technical_director = row[technical_director_idx]

			car = car_model.CarModel(car_speed)
			team = team_model.TeamModel(model, name, country, driver1, driver2, car, number_of_staff, facilities,
							   starting_balance, other_sponsorship, title_sponsor, title_sponsor_value,
							   commercial_manager, technical_director)
			
			# ensure drivers are correctly loaded
			assert team.driver1_model is not None
			assert team.driver2_model is not None

			teams.append(team)

	return teams

def load_senior_staff(model: Model, conn: sqlite3.Connection
					  )-> Tuple[List[commercial_manager.CommercialManager],
				 List[technical_director.TechnicalDirector],
				 List[List[Tuple[str, Union[commercial_manager.CommercialManager, technical_director.TechnicalDirector]]]]]:
	technical_directors = []
	commercial_managers = []
	future_managers = []

	for table_name in ["technical_directors", "commercial_managers"]:

		cursor = conn.execute(f'PRAGMA table_info({table_name})')
		columns = cursor.fetchall()
		column_names = [column[1] for column in columns]

		name_idx = column_names.index("Name")
		age_idx = column_names.index("Age")
		skill_idx = column_names.index("Skill")
		contract_length_idx = column_names.index("ContractLength")
		salary_idx = column_names.index("Salary")

		cursor = conn.cursor()
		cursor.execute(f"SELECT * FROM {table_name}")
		managers_table = cursor.fetchall()

		for row in managers_table:
			name = row[name_idx]
			age = row[age_idx]
			skill = row[skill_idx]
			contract_length = row[contract_length_idx]
			salary = row[salary_idx]

			
			if table_name == "technical_directors":
				manager = technical_director.TechnicalDirector(model, name, age, skill, salary, contract_length)
			elif table_name == "commercial_managers":
				manager = commercial_manager.CommercialManager(model, name, age, skill, salary, contract_length)

			if "RetiringAge" in column_names:
				retiring_age_idx = column_names.index("RetiringAge")
				retiring_age = row[retiring_age_idx]
				manager.retiring_age = retiring_age

				retiring_idx = column_names.index("Retiring")
				retiring = bool(row[retiring_idx])
				manager.retiring = retiring

				retired_idx = column_names.index("Retired")
				retired = bool(row[retired_idx])
				manager.retired = retired

			if row[0].lower() == "default":
				if table_name == "technical_directors":
					technical_directors.append(manager)
				elif table_name == "commercial_managers":
					commercial_managers.append(manager)
			else:
				future_managers.append([row[0], manager])

	return commercial_managers, technical_directors, future_managers


# def create_driver(line_data: str, model):
# 	name = line_data[1].lstrip().rstrip()
# 	age = int(line_data[2])
# 	country = line_data[3]
# 	speed = int(line_data[4])

# 	driver = driver_model.DriverModel(model, name, age, country, speed)
	
# 	return driver

def load_season(model: Model, season_file: str) -> pd.DataFrame:

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

	columns = ["Week", "Track", "Country", "Location", "Winner"]

	for line in calendar_data:
		race_data = line.rstrip().split(",")
		week = int(race_data[1])
		track = model.get_track_model(race_data[0].rstrip().lstrip())

		dataframe_data.append([week, track.name, track.country, track.location, None])
	
	calendar_dataframe = pd.DataFrame(columns=columns, data=dataframe_data)

	return calendar_dataframe
	
def load_tracks(model: Model, track_files: list[str]) -> None:
	for file in track_files:
		with open(file) as f:
			data = f.readlines()

		data = [l.rstrip() for l in data]
		track = track_model.TrackModel(model, data)
		model.tracks.append(track)

def checks(model: Model, roster: str) -> Tuple[str, List[str]]:

	season_file = os.path.join(model.run_directory, roster, "season.txt")
	assert os.path.isfile(season_file), f"Cannot Find {season_file}"

	tracks_folder = os.path.join(model.run_directory, roster, "tracks")
	assert os.path.isdir(tracks_folder), f"Cannot Find {tracks_folder}"

	track_files = glob.glob(os.path.join(tracks_folder, "*.txt"))

	return season_file, track_files


	

