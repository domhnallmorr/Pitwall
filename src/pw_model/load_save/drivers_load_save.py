
from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

from pw_model import load_roster
from pw_model.driver.driver_model import DriverModel

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model


def save_drivers(model: Model, save_file: sqlite3.Connection) -> None:

	cursor = save_file.cursor()

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS "Drivers" (
		"Year"	TEXT,
		"Name"	TEXT,
		"Age"	INTEGER,
		"Country"	TEXT,
		"Speed"	INTEGER,
		"Consistency"	INTEGER,
		"Qualifying"	INTEGER,
		"ContractLength"	INTEGER,
		"RetiringAge"	INTEGER,
		"Retiring"	INTEGER,
		"Retired"	INTEGER,
		"Salary"	INTEGER,
		"Starts"	INTEGER,
		"Championships"	INTEGER,
		"Wins"	INTEGER,
		"PayDriver"	INTEGER,
		"Budget"	INTEGER
		)'''
				)
	
	cursor.execute("DELETE FROM Drivers") # clear existing data

	for idx, driver_type in enumerate([model.drivers, model.future_drivers]):
		for driver in driver_type:
			if idx == 0:
				year = "default"
			else:
				year = driver[0]
				driver = driver[1]


			cursor.execute('''
				INSERT INTO Drivers (year, name, age, country,
				  speed, consistency, qualifying, contractlength,
				  retiringage, retiring, retired, salary,
				  starts, championships, wins,
				  paydriver, budget) 
				VALUES (?, ?, ?, ?,
				  ?, ?, ?, ?,
				  ?, ?, ?, ?,
				  ?, ?, ?,
				  ?, ?)
				  
			''', (
				year,
				driver.name, 
				driver.age, 
				driver.country, 
				driver.speed, 
				driver.consistency, 
				driver.qualifying,
				driver.contract.contract_length, 
				driver.retiring_age, 
				driver.retiring,
				driver.retired,
				driver.contract.salary,
				driver.career_stats.starts,
				driver.career_stats.championships,
				driver.career_stats.wins, # add wins to save file
				int(driver.pay_driver), # convert bool to int for sqlite3 compatibility
				driver.budget,
			))

def load_drivers(conn: sqlite3.Connection, model: Model) -> None:
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

		driver = DriverModel(model, name, age, country, speed, consistency, qualifying, contract_length, salary,
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