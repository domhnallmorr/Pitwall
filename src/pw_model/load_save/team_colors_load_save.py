from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

from pw_model.team.team_model import TeamModel

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def save_team_colors(model: Model, save_file: sqlite3.Connection) -> None:
	cursor = save_file.cursor()
	cursor.execute('''
			CREATE TABLE IF NOT EXISTS "TeamColors" (
            "Team" TEXT,
			"PrimaryColour" TEXT
            )'''
        )
	cursor.execute("DELETE FROM TeamColors")  # Clear existing data

	for team in model.teams:
		cursor.execute('''
			INSERT INTO TeamColors (Team, PrimaryColour)
			VALUES (?, ?)
		''', (
			team.name,
			team.team_colors_manager.primary_colour
		))

def load_team_colors(teams: list[TeamModel], conn: sqlite3.Connection):
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM TeamColors")
	rows = cursor.fetchall()

	for row in rows:
		team_name = row[0]
		primary_colour = row[1]

		for team_model in teams:
			if team_model.name == team_name:
				team_model.team_colors_manager.primary_colour = primary_colour
				break

