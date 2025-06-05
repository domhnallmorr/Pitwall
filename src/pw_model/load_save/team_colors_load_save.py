from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model


def load_team_colors(model: Model, conn: sqlite3.Connection):
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM TeamColors")
	rows = cursor.fetchall()

	for row in rows:
		team_name = row[0]
		primary_colour = row[1]

		team_model = model.entity_manager.get_team_model(team_name)
		if team_model is None:
			continue

		team_model.team_colors_manager.primary_colour = primary_colour
