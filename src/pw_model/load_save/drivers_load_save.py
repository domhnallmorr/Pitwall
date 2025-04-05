
from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3
from pw_model import load_roster

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model


def save_drivers(model: Model, save_file: sqlite3.Connection) -> None:

	cursor = save_file.cursor()

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS "drivers" (
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
		"PayDriver"	INTEGER,
		"Budget"	INTEGER
		)'''
				)
	
	cursor.execute("DELETE FROM drivers") # clear existing data

	for idx, driver_type in enumerate([model.drivers, model.future_drivers]):
		for driver in driver_type:
			if idx == 0:
				year = "default"
			else:
				year = driver[0]
				driver = driver[1]


			cursor.execute('''
				INSERT INTO drivers (year, name, age, country,
				  speed, consistency, qualifying, contractlength,
				  retiringage, retiring, retired, salary,
				  starts, paydriver, budget) 
				VALUES (?, ?, ?, ?,
				  ?, ?, ?, ?,
				  ?, ?, ?, ?,
				  ?, ?, ?)
				  
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
				int(driver.pay_driver), # convert bool to int for sqlite3 compatibility
				driver.budget,
			))

def load_drivers(conn: sqlite3.Connection, model: Model) -> None:
	drivers, future_drivers = load_roster.load_drivers(model, conn)
	model.drivers = drivers
	model.future_drivers = future_drivers