from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3
from pw_model.team.team_model import TeamModel

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def save_team_descriptions(model: Model, save_file: sqlite3.Connection) -> None:
	cursor = save_file.cursor()
	cursor.execute('''
			CREATE TABLE IF NOT EXISTS "TeamSelectionText" (
            "Team" TEXT,
			"Description" TEXT
            )'''
        )
	cursor.execute("DELETE FROM TeamSelectionText")  # Clear existing data

	for team in model.teams:
		cursor.execute('''
			INSERT INTO TeamSelectionText (Team, Description)
			VALUES (?, ?)
		''', (
			team.name,
			team.team_description
		))

def load_team_descriptions(conn: sqlite3.Connection, teams: list[TeamModel]) -> None:

	table = "TeamSelectionText"
	cursor = conn.execute(f'PRAGMA table_info({table})')
	columns = cursor.fetchall()
	column_names = [column[1] for column in columns]

	name_idx = column_names.index("Team")
	description_idx = column_names.index("Description")

	cursor = conn.cursor()
	cursor.execute(f"SELECT * FROM {table}")

	for row in cursor.fetchall():
		team_name = row[name_idx]
		for team in teams:
			if team.name == team_name:
				team.team_description = row[description_idx]
				break
