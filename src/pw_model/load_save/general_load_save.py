from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

from pw_model.season.calendar import CalendarState

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model


def save_general(model: Model, save_file: sqlite3.Connection) -> None:
	cursor = save_file.cursor()

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS "general" (
		"Year"	INTEGER,		
		"Week"	INTEGER,
		"PlayerTeam"	TEXT,
		"NextRaceIdx"	INTEGER,
		"CalendarState"	TEXT
		)'''
				)				

	cursor.execute("DELETE FROM general") # clear existing data

	cursor.execute('''
		INSERT INTO general (year, week, playerteam, nextraceidx, calendarstate) 
		VALUES (?, ?, ?, ?, ?)
	''', (
		model.year,
		model.season.calendar.current_week, 
		model.player_team, 
		model.season.calendar.next_race_idx,
		model.season.calendar.state.value
	))


def load_general(conn: sqlite3.Connection, model: Model) -> None:
	table_name = "general"
	cursor = conn.execute(f'PRAGMA table_info({table_name})')

	columns = cursor.fetchall()
	column_names = [column[1] for column in columns]

	year_idx = column_names.index("Year")
	week_idx = column_names.index("Week")
	player_team_idx = column_names.index("PlayerTeam")
	next_race_idx = column_names.index("NextRaceIdx")
	calendar_state_idx = column_names.index("CalendarState")

	cursor = conn.cursor()
	cursor.execute(f"SELECT * FROM {table_name}")

	data = cursor.fetchall()[0]

	model.season.calendar.current_week = data[week_idx]
	model.year = data[year_idx]
	model.player_team = data[player_team_idx]
	model.season.calendar.next_race_idx = data[next_race_idx]
	model.season.calendar.state = CalendarState(data[calendar_state_idx])