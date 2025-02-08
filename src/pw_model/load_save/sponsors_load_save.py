from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

import pandas as pd

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def save_sponsor_model(model: Model, save_file: sqlite3.Connection) -> None:
	cursor = save_file.cursor()
	cursor.execute('''
			CREATE TABLE IF NOT EXISTS "team_sponsors" (
            "Team" INTEGER,
			"TitleSponsor" INTEGER,
            "TitleSponsorValue" TEXT,
			"OtherSponsorsValue" INTEGER
            )'''
        )
	cursor.execute("DELETE FROM team_sponsors")  # Clear existing data

	for team_model in model.teams:
		team_name = team_model.name
		sponsors_model = team_model.finance_model.sponsors_model

		title_sponsor = sponsors_model.title_sponsor
		# title_sponsor_value = None # default None for AI teams, don't track specifics like that for AI
		# other_sponsors_value = None # default None for AI teams, don't track specifics like that for AI

		title_sponsor_value = sponsors_model.title_sponsor_value
		other_sponsors_value = sponsors_model.other_sponsorship

		cursor.execute('''
				INSERT INTO team_sponsors (Team, TitleSponsor, TitleSponsorValue, OtherSponsorsValue)
				VALUES (?, ?, ?, ?)
			''', (
				team_name,
				title_sponsor,
				title_sponsor_value,
				other_sponsors_value
			))
		
def load_sponsors(conn: sqlite3.Connection) -> pd.DataFrame:
	return pd.read_sql('SELECT * FROM team_sponsors', conn)