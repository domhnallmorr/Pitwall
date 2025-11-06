from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

from pw_model.pw_model_enums import StaffRoles

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

'''
Load technical directors is handled in the load_senior_staff function of the load_roster module
'''

def save_technical_directors(model : Model, save_file: sqlite3.Connection) -> None:
	cursor = save_file.cursor()

	cursor.execute('''
	CREATE TABLE IF NOT EXISTS "TechnicalDirectors" (
	"Year"	TEXT,
	"Name"	TEXT,
	"Age"	INTEGER,
	"Skill"	INTEGER,
	"Salary"	INTEGER,
	"ContractLength"	INTEGER,
	"RetiringAge"	INTEGER,
	"Retiring"	INTEGER,
	"Retired"	INTEGER
			)'''
				)
	
	cursor.execute("DELETE FROM TechnicalDirectors") # clear existing data

	for idx, list_type in enumerate([model.technical_directors, model.future_managers]):
		for technical_director in list_type:
			process = False
			if idx == 0:
				year = "default"
				process = True
			elif idx == 1:
				if technical_director[1].role == StaffRoles.TECHNICAL_DIRECTOR:
					year = technical_director[0]
					technical_director = technical_director[1]
					process = True

			if process is True:
				
				cursor.execute('''
					INSERT INTO TechnicalDirectors (year, name, age, skill, salary, contractlength, retiringage, retiring, retired) 
					VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
				''', (
					year,
					technical_director.name, 
					technical_director.age,
					technical_director.skill,
					technical_director.contract.salary,
					technical_director.contract.contract_length,
					technical_director.retiring_age,
					technical_director.retiring,
					technical_director.retired,
				))

