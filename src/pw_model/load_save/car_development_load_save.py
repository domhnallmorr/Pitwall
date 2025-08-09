from __future__ import annotations
from typing import TYPE_CHECKING
import json
import sqlite3

from pw_model.car_development.car_development_model import CarDevelopmentEnums, CarDevelopmentStatusEnums

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def save_car_development(model: Model, save_file: sqlite3.Connection) -> None:
		
	cursor = save_file.cursor()
	# Save current development status for player team
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS "CarDevelopment" (
		"Team"                  TEXT,
		"CurrentStatus"         TEXT,
		"TimeLeft"             INTEGER,
		"DevelopmentType"      TEXT,
		"CarSpeedHistory"      TEXT
		)'''
	)
	
	cursor.execute("DELETE FROM CarDevelopment")  # Clear existing data

	car_dev = model.player_team_model.car_development_model
	
	for team in model.teams:
		car_dev = team.car_development_model

		if team == model.player_team_model:
			current_status = car_dev.current_status.value
			time_left = car_dev.time_left
			development_type = car_dev.current_development_type.value
			car_speed_history = json.dumps(car_dev.car_speed_history)
		else:
			current_status = ""
			time_left = 0
			development_type = ""
			car_speed_history = json.dumps(car_dev.car_speed_history)

		cursor.execute('''
			INSERT INTO CarDevelopment (Team, CurrentStatus, TimeLeft, DevelopmentType, CarSpeedHistory)
			VALUES (?, ?, ?, ?, ?)
		''', (
			team.name,
			current_status,
			time_left,
			development_type,
			car_speed_history,
		))
	# cursor.execute('''
	#     INSERT INTO car_development (Team, CurrentStatus, TimeLeft, DevelopmentType, CarSpeedHistory)
	#     VALUES (?, ?, ?, ?, ?)
	# ''', (
	#     model.player_team,
	#     car_dev.current_status.value,
	#     car_dev.time_left,
	#     car_dev.current_development_type.value,
	#     json.dumps(car_dev.car_speed_history)
	# ))

	# Save planned updates for all teams
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS "CarDevelopmentPlannedUpdates" (
		"Team"              TEXT,
		"Week"             INTEGER,
		"DevelopmentType"  TEXT
		)'''
	)
	
	cursor.execute("DELETE FROM CarDevelopmentPlannedUpdates")  # Clear existing data
	
	# Save planned updates for all teams
	for team in model.teams:
		car_dev = team.car_development_model
		for update in car_dev.planned_updates:
			week = update[0]
			dev_type = update[1]            
			cursor.execute('''
				INSERT INTO CarDevelopmentPlannedUpdates (Team, Week, DevelopmentType)
				VALUES (?, ?, ?)
			''', (
				team.name,
				week,
				dev_type.value
			))

def load_car_development(conn: sqlite3.Connection, model: Model) -> None:
	if not model.player_team_model:
		return
		
	cursor = conn.cursor()

	# Get column indices
	table_name = "CarDevelopment"
	cursor = conn.execute(f'PRAGMA table_info({table_name})')
	columns = cursor.fetchall()
	column_names = [column[1] for column in columns]

	team_idx = column_names.index("Team")
	current_status_idx = column_names.index("CurrentStatus")
	time_left_idx = column_names.index("TimeLeft")
	development_type_idx = column_names.index("DevelopmentType")
	car_speed_history_idx = column_names.index("CarSpeedHistory")

	# Read data for all teams
	cursor.execute("SELECT * FROM CarDevelopment")
	rows = cursor.fetchall()
	
	for row in rows:
		team_name = row[team_idx] # Get the team name from the row data at the team_idx position
		team_model = model.entity_manager.get_team_model(team_name) # Get the team model from the entity manager
		car_dev = team_model.car_development_model # Get the car development model for the player team

		if team_name == model.player_team: # Check if the team name matches the player team name
			car_dev.current_status = CarDevelopmentStatusEnums(row[current_status_idx]) # Set the current status from the row data at the current_status_idx position
			car_dev.time_left = row[time_left_idx] # Set the time left from the row data at the time_left_idx position
			car_dev.current_development_type = CarDevelopmentEnums(row[development_type_idx]) # Set the current development type from the row data at the development_type_idx position
		
		car_dev.car_speed_history = json.loads(row[car_speed_history_idx]) if row[car_speed_history_idx] else [] # Set the car speed history from the row data at the car_speed_history_idx position

	# Load planned updates for all teams
	cursor.execute("SELECT Team, Week, DevelopmentType FROM CarDevelopmentPlannedUpdates")
	rows = cursor.fetchall()
	
	# Group updates by team
	for team in model.teams:
		team_updates = [(row[1], CarDevelopmentEnums(row[2])) 
					   for row in rows if row[0] == team.name]
		team.car_development_model.planned_updates = team_updates
