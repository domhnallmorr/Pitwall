from __future__ import annotations
from typing import TYPE_CHECKING, List, Union
import sqlite3

from pw_model.senior_staff.commercial_manager import CommercialManager
from pw_model.senior_staff.technical_director import TechnicalDirector
from pw_model.senior_staff.team_principal import TeamPrincipalModel

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model
	
def load_senior_staff(conn: sqlite3.Connection, model: Model) -> tuple[List[CommercialManager], List[TechnicalDirector], List[TeamPrincipalModel], List[Union[CommercialManager, TechnicalDirector, TeamPrincipalModel]]]:
	technical_directors = []
	commercial_managers = []
	future_managers = []
	team_principals = []

	for table_name in ["technical_directors", "commercial_managers", "team_principals"]:
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

			if table_name == "technical_directors":
				manager = TechnicalDirector(model, name, age, skill, salary, contract_length)
			elif table_name == "commercial_managers":
				manager = CommercialManager(model, name, age, skill, salary, contract_length)
			elif table_name == "team_principals":
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
				if table_name == "technical_directors":
					technical_directors.append(manager)
				elif table_name == "commercial_managers":
					commercial_managers.append(manager)
				elif table_name == "team_principals":
					team_principals.append(manager)
			else:
				future_managers.append([row[0], manager])

	return commercial_managers, technical_directors, team_principals, future_managers