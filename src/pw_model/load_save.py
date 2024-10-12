import json
import sqlite3

import pandas as pd

from pw_model import load_save
from pw_model import load_roster

def save_game(model, mode="file"):
	assert mode in ["file", "memory"]
	
	if mode == "file":
		save_file = sqlite3.connect(rf"{model.run_directory}\save_game.db")
	elif mode == "memory":
		save_file = sqlite3.connect(":memory:")
	
	save_general(model, save_file)
	save_drivers(model, save_file)
	save_commercial_managers(model, save_file)
	save_teams(model, save_file)
	save_grid_this_year(model, save_file)
	save_grid_next_year(model, save_file)
	save_standings(model, save_file)

	save_file.commit()

	if mode == "file":
		save_file.close() # only close if we are saving to file, if in memory, keep the connection open

	return save_file

def save_general(model, save_file):
	cursor = save_file.cursor()

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS "general" (
		"Year"	INTEGER,		
		"Week"	INTEGER,
		"PlayerTeam"	TEXT
		)'''
				)				

	cursor.execute("DELETE FROM general") # clear existing data

	cursor.execute('''
		INSERT INTO general (year, week, playerteam) 
		VALUES (?, ?, ?)
	''', (
		model.year,
		model.season.current_week, 
		model.player_team, 
	))


def save_drivers(model, save_file):

	cursor = save_file.cursor()

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS "drivers" (
		"Year"	TEXT,
		"Name"	TEXT,
		"Age"	INTEGER,
		"Country"	TEXT,
		"Speed"	INTEGER,
		"RetiringAge"	INTEGER,
		"Retiring"	INTEGER,
		"Retired"	INTEGER
		)'''
				)
	
	cursor.execute("DELETE FROM drivers") # clear existing data

	# for driver_type in [model.drivers, model.]

	for idx, driver_type in enumerate([model.drivers, model.future_drivers]):
		for driver in driver_type:
			if idx == 0:
				year = "default"
			else:
				year = driver[0]
				driver = driver[1]


			cursor.execute('''
				INSERT INTO drivers (year, name, age, country, speed, retiringage, retiring, retired) 
				VALUES (?, ?, ?, ?, ?, ?, ?, ?)
			''', (
				year,
				driver.name, 
				driver.age, 
				driver.country, 
				driver.speed, 
				driver.retiring_age, 
				driver.retiring,
				driver.retired
			))

def save_commercial_managers(model, save_file):
	cursor = save_file.cursor()

	cursor.execute('''
	CREATE TABLE IF NOT EXISTS "commercial_managers" (
	"Year"	TEXT,
	"Name"	TEXT,
	"Age"	INTEGER,
	"Skill"	INTEGER,
	"Salary"	INTEGER
			)'''
				)
	
	cursor.execute("DELETE FROM commercial_managers") # clear existing data

	for commercial_manager in model.commercial_managers:
		cursor.execute('''
			INSERT INTO commercial_managers (year, name, age, skill, salary) 
			VALUES (?, ?, ?, ?, ?)
		''', (
			"default",
			commercial_manager.name, 
			commercial_manager.age,
			commercial_manager.skill,
			commercial_manager.contract.salary,
		))

def save_teams(model, save_file):

	cursor = save_file.cursor()

	cursor.execute('''
	CREATE TABLE IF NOT EXISTS "teams" (
	"Year"	TEXT,
	"Name"	TEXT,
	"Driver1"	TEXT,
	"Driver2"	TEXT,
	"CarSpeed"	INTEGER,
	"NumberofStaff"	INTEGER,
	"Facilities"	INTEGER,
	"StartingBalance"	INTEGER,
	"StartingSponsorship"	INTEGER,
	"CommercialManager"	TEXT
	)'''
				)
	
	cursor.execute("DELETE FROM teams") # clear existing data

	for team in model.teams:

		cursor.execute('''
			INSERT INTO teams (year, name, Driver1, Driver2, CarSpeed, NumberofStaff, Facilities, StartingBalance, StartingSponsorship,
				 CommercialManager) 
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,
				 ?)
		''', (
			"default",
			team.name, 
			team.driver1,
			team.driver2, 
			team.car_model.speed, 
			team.number_of_staff, 
			team.facilities_model.factory_rating, 
			team.finance_model.balance, 
			team.finance_model.total_sponsorship, 
			team.commercial_manager,
		))

def save_grid_this_year(model, save_file):
	model.staff_market.grid_this_year_df.to_sql("grid_this_year_df", save_file, if_exists="replace", index=False)

def save_grid_next_year(model, save_file):
	model.staff_market.grid_next_year_df.to_sql("grid_next_year_df", save_file, if_exists="replace", index=False)
	model.staff_market.grid_next_year_announced_df.to_sql("grid_next_year_announced", save_file, if_exists="replace", index=False)

def save_standings(model, save_file):
	model.season.standings_manager.drivers_standings_df.to_sql("drivers_standings_df", save_file, if_exists="replace", index=False)
	model.season.standings_manager.constructors_standings_df.to_sql("constructors_standings_df", save_file, if_exists="replace", index=False)

def load(model, save_file=None, mode="file"):
	assert mode in ["file", "memory"]

	if mode == "file":
		if save_file is None:
			conn = sqlite3.connect(f"{model.run_directory}\\save_game.db")
		else:
			conn = sqlite3.connect(save_file)

	else:
		conn = save_file # db provided in memory

	load_drivers(conn, model)
	load_senior_staff(conn, model)
	load_teams(conn, model)
	load_general(conn, model)
	load_standings(conn, model)
	load_grid_this_year(conn, model)
	load_grid_next_year(conn, model)

def load_general(conn, model):
	table_name = "general"
	cursor = conn.execute(f'PRAGMA table_info({table_name})')

	columns = cursor.fetchall()
	column_names = [column[1] for column in columns]

	year_idx = column_names.index("Year")
	week_idx = column_names.index("Week")
	player_team_idx = column_names.index("PlayerTeam")

	cursor = conn.cursor()
	cursor.execute(f"SELECT * FROM {table_name}")

	data = cursor.fetchall()[0]

	model.season.current_week = data[week_idx]
	model.year = data[year_idx]
	model.player_team = data[player_team_idx]

def load_drivers(conn, model):
	drivers, future_drivers = load_roster.load_drivers(model, conn)
	model.drivers = drivers
	model.future_drivers = future_drivers

def load_senior_staff(conn, model):
	commercial_managers = load_roster.load_senior_staff(model, conn)
	model.commercial_managers = commercial_managers

def load_teams(conn, model):
	teams = load_roster.load_teams(model, conn)
	model.teams = teams

def load_standings(conn, model):
	model.season.standings_manager.drivers_standings_df = pd.read_sql('SELECT * FROM drivers_standings_df', conn)
	model.season.standings_manager.constructors_standings_df = pd.read_sql('SELECT * FROM constructors_standings_df', conn)

def load_grid_this_year(conn, model):
	model.staff_market.grid_this_year_df = pd.read_sql('SELECT * FROM grid_this_year_df', conn)

def load_grid_next_year(conn, model):
	model.staff_market.grid_next_year_df = pd.read_sql('SELECT * FROM grid_next_year_df', conn)
	model.staff_market.grid_next_year_announced_df = pd.read_sql('SELECT * FROM grid_next_year_announced', conn)
