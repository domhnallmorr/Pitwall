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
from pw_model.senior_staff.commercial_manager import CommercialManager
from pw_model.senior_staff.technical_director import TechnicalDirector
from pw_model.senior_staff.team_principal import TeamPrincipalModel
from pw_model.load_save.team_sponsors_load_save import load_team_sponsors
from pw_model.load_save.engine_suppliers_load_save import load_engine_suppliers
from pw_model.load_save.tyres_load_save import load_tyre_suppliers
from pw_model.load_save.sponsors_load_save import load_sponsors
from pw_model.load_save.team_colors_load_save import load_team_colors
from pw_model.team.suppliers_model import SupplierDeals

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def load_roster(model: Model, roster: str) -> pd.DataFrame:

	conn = sqlite3.connect(f"{model.run_directory}\\{roster}\\roster.db")

	season_file, track_files = checks(model, roster)
	load_tracks(model, track_files)
	calendar_dataframe = load_season(model, season_file)
	
	model.drivers, model.future_drivers = load_drivers(model, conn)
	model.commercial_managers, model.technical_directors, model.team_principals, model.future_managers = load_senior_staff(model, conn)
	model.teams = load_teams(model, conn)
	load_team_descriptions(conn, model)
	model.engine_suppliers = load_engine_suppliers(model, conn)
	model.tyre_suppliers = load_tyre_suppliers(model, conn)
	load_sponsors(conn, model)
	load_team_colors(model, conn)

	return calendar_dataframe
	

def load_drivers(
	model: Model, 
	conn: sqlite3.Connection
) -> Tuple[List[driver_model.DriverModel], List[List[Tuple[str, driver_model.DriverModel]]]]:
	drivers = []
	future_drivers = []

	table_name = "Drivers"
	cursor = conn.execute(f'PRAGMA table_info({table_name})')
	columns = cursor.fetchall()
	column_names = [column[1] for column in columns]

	name_idx = column_names.index("Name")
	age_idx = column_names.index("Age")
	country_idx = column_names.index("Country")
	speed_idx = column_names.index("Speed")
	consistency_idx = column_names.index("Consistency")
	qualifying_idx = column_names.index("Qualifying")
	contract_length_idx = column_names.index("ContractLength")
	salary_idx = column_names.index("Salary")
	pay_driver_idx = column_names.index("PayDriver")
	budget_idx = column_names.index("Budget")

	# stats
	starts_idx = column_names.index("Starts")
	championships_idx = column_names.index("Championships")
	wins_idx = column_names.index("Wins")

	cursor = conn.cursor()
	cursor.execute(f"SELECT * FROM {table_name}")
	drivers_table = cursor.fetchall()

	for row in drivers_table:
		name = row[name_idx]
		age = row[age_idx]
		country = row[country_idx]
		speed = row[speed_idx]
		consistency = row[consistency_idx]
		qualifying = row[qualifying_idx]
		contract_length = row[contract_length_idx]
		salary = row[salary_idx]
		pay_driver = bool(int(row[pay_driver_idx]))
		budget = row[budget_idx]

		# stats
		starts = row[starts_idx]
		championships = row[championships_idx]
		wins = row[wins_idx]

		driver = driver_model.DriverModel(model, name, age, country, speed, consistency, qualifying, contract_length, salary,
									starts, pay_driver, budget, championships, wins)
		
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
	sponsors_df = load_team_sponsors(conn)

	teams = []

	table_name = "Teams"

	cursor = conn.execute(f'PRAGMA table_info({table_name})')
	columns = cursor.fetchall()
	column_names = [column[1] for column in columns]

	name_idx = column_names.index("Name")
	country_idx = column_names.index("Country")
	team_principal_idx = column_names.index("TeamPrincipal")
	driver1_idx = column_names.index("Driver1")
	driver2_idx = column_names.index("Driver2")
	car_speed_idx = column_names.index("CarSpeed")
	number_of_staff_idx = column_names.index("NumberofStaff")
	facilities_idx = column_names.index("Facilities")

	# Engine Supplier
	engine_supplier_idx = column_names.index("EngineSupplier")
	engine_supplier_deal_idx = column_names.index("EngineSupplierDeal")
	engine_supplier_cost_idx = column_names.index("EngineSupplierCosts")

	# Tyre Suuplier
	tyre_supplier_idx = column_names.index("TyreSupplier")
	tyre_supplier_deal_idx = column_names.index("TyreSupplierDeal")
	tyre_supplier_cost_idx = column_names.index("TyreSupplierCosts")
	
	balance_idx = column_names.index("StartingBalance")

	commercial_manager_idx = column_names.index("CommercialManager")
	technical_director_idx = column_names.index("TechnicalDirector")

	cursor = conn.cursor()
	cursor.execute(f"SELECT * FROM {table_name}")
	teams_table = cursor.fetchall()

	for idx, row in enumerate(teams_table):
		if row[0].lower() == "default":
			name = row[name_idx]
			country = row[country_idx]
			team_principal = row[team_principal_idx]
			driver1 = row[driver1_idx]
			driver2 = row[driver2_idx]
			car_speed = row[car_speed_idx]

			facilities = row[facilities_idx]
			number_of_staff = row[number_of_staff_idx]

			engine_supplier = row[engine_supplier_idx]
			engine_supplier_deal = SupplierDeals(row[engine_supplier_deal_idx])
			engine_supplier_cost = row[engine_supplier_cost_idx]

			tyre_supplier = row[tyre_supplier_idx]
			tyre_supplier_deal = SupplierDeals(row[tyre_supplier_deal_idx])
			tyre_supplier_cost = row[tyre_supplier_cost_idx]

			starting_balance = row[balance_idx]
			title_sponsor = str(sponsors_df.loc[sponsors_df["Team"] == name, "TitleSponsor"].iloc[0])
			other_sponsorship = int(sponsors_df.loc[sponsors_df["Team"] == name, "OtherSponsorsValue"].iloc[0])

			commercial_manager = row[commercial_manager_idx]
			technical_director = row[technical_director_idx]

			car = car_model.CarModel(car_speed)
			team = team_model.TeamModel(model, name, country, team_principal, driver1, driver2, car, number_of_staff, facilities,
							   starting_balance, other_sponsorship, title_sponsor,
							   commercial_manager, technical_director,
							   engine_supplier, engine_supplier_deal, engine_supplier_cost,
							   tyre_supplier, tyre_supplier_deal, tyre_supplier_cost,
							   idx)
			
			# ensure drivers are correctly loaded
			assert team.driver1_model is not None
			assert team.driver2_model is not None

			teams.append(team)

	return teams

def load_team_descriptions(conn: sqlite3.Connection, model: Model) -> None:

	table = "TeamSelectionText"
	cursor = conn.execute(f'PRAGMA table_info({table})')
	columns = cursor.fetchall()
	column_names = [column[1] for column in columns]

	name_idx = column_names.index("Team")
	description_idx = column_names.index("Description")

	cursor = conn.cursor()
	cursor.execute(f"SELECT * FROM {table}")

	for row in cursor.fetchall():
		team = model.entity_manager.get_team_model(row[name_idx])
		if team is None:
			continue
		team.team_description = row[description_idx]


def load_senior_staff(model: Model, conn: sqlite3.Connection) -> Tuple[List[CommercialManager], List[TechnicalDirector], List[TeamPrincipalModel], List[Union[CommercialManager, TechnicalDirector, TeamPrincipalModel]]]:
	technical_directors = []
	commercial_managers = []
	future_managers = []
	team_principals = []

	for table_name in ["TechnicalDirectors", "CommercialManagers", "TeamPrincipals"]:
		cursor = conn.execute(f'PRAGMA table_info({table_name})')
		columns = cursor.fetchall()
		column_names = [column[1] for column in columns]

		name_idx = column_names.index("Name")
		age_idx = column_names.index("Age")
		skill_idx = column_names.index("Skill")
		contract_length_idx = column_names.index("ContractLength")
		
		if "Salary" in column_names: # salary is not in team principals table
			salary_idx = column_names.index("Salary")

		cursor = conn.cursor()
		cursor.execute(f"SELECT * FROM {table_name}")
		managers_table = cursor.fetchall()

		for row in managers_table:
			name = row[name_idx]
			age = row[age_idx]
			skill = row[skill_idx]
			contract_length = row[contract_length_idx]
			
			if "Salary" in column_names: # salary is not in team principals table:
				salary = row[salary_idx]

			if table_name == "TechnicalDirectors":
				manager = TechnicalDirector(model, name, age, skill, salary, contract_length)
			elif table_name == "CommercialManagers":
				manager = CommercialManager(model, name, age, skill, salary, contract_length)
			elif table_name == "TeamPrincipals":
				manager = TeamPrincipalModel(model, name, age, skill, contract_length)

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
				if table_name == "TechnicalDirectors":
					technical_directors.append(manager)
				elif table_name == "CommercialManagers":
					commercial_managers.append(manager)
				elif table_name == "TeamPrincipals":
					team_principals.append(manager)
			else:
				future_managers.append([row[0], manager])

	return commercial_managers, technical_directors, team_principals, future_managers


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
	# calendar_start_idx = None
	# calendar_end_idx = None
	# testing_start_idx = None
	# testing_end_idx = None

	for idx, line in enumerate(data):
		if line.lower().startswith("calendar<"):
			calendar_start_idx: int = idx
		elif line.lower().startswith("calendar>"):
			calendar_end_idx = idx
		elif line.lower().startswith("testing<"):
			testing_start_idx = idx
		elif line.lower().startswith("testing>"):
			testing_end_idx = idx

	# Process race calendar
	calendar_data = data[calendar_start_idx + 1: calendar_end_idx]
	grand_prix_data = []
	columns = ["Week", "Track", "Country", "Location", "Winner", "SessionType"]

	for line in calendar_data:
		race_data = line.rstrip().split(",")
		week = int(race_data[1])
		track = model.entity_manager.get_track_model(race_data[0].rstrip().lstrip())
		grand_prix_data.append([week, track.name, track.country, track.location, None, "Race"])

	# Process testing sessions
	testing_data = []

	if testing_start_idx and testing_end_idx:
		testing_sessions = data[testing_start_idx + 1: testing_end_idx]
		for line in testing_sessions:
			test_data = line.rstrip().split(",")
			week = int(test_data[1])
			track = model.entity_manager.get_track_model(test_data[0].rstrip().lstrip())
			testing_data.append([week, track.name, track.country, track.location, None, "Testing"])

	# Combine race and testing data
	all_data = grand_prix_data + testing_data
	
	# Sort by week number
	all_data.sort(key=lambda x: x[0])
	calendar_dataframe = pd.DataFrame(columns=columns, data=all_data)
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


