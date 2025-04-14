from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def save_testing_model(model: Model, save_file: sqlite3.Connection) -> None:
	cursor = save_file.cursor()
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS "TestingModel" (
		"progress" INTEGER
		)'''
	)
	
	cursor.execute("DELETE FROM TestingModel")  # Clear existing data

	if model.player_team_model and model.player_team_model.testing_model:
		cursor.execute('''
			INSERT INTO TestingModel (progress)
			VALUES (?)
		''', (
			model.player_team_model.testing_model.testing_progress,
		))

def load_testing(conn: sqlite3.Connection, model: Model) -> None:
	if not model.player_team_model:
		return
		
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM TestingModel')
	row = cursor.fetchone()
	
	column_names = [column[0] for column in cursor.description]
	progress_idx = column_names.index("progress")

	if row:
		model.player_team_model.testing_model.testing_progress = row[progress_idx]
		