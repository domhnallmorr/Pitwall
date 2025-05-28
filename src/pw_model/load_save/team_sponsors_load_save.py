from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

import pandas as pd

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def save_team_sponsors(model: Model, save_file: sqlite3.Connection) -> None:
	cursor = save_file.cursor()
	cursor.execute('''
			CREATE TABLE IF NOT EXISTS "TeamSponsors" (
            "Team" TEXT,
			"TitleSponsor" TEXT,
            "TitleSponsorValue" INTEGER,
			"TitleSponsorContractLength" INTEGER,
			"OtherSponsorsValue" INTEGER
            )'''
        )
	cursor.execute("DELETE FROM TeamSponsors")  # Clear existing data

	for team_model in model.teams:
		team_name = team_model.name
		sponsorship_model = team_model.finance_model.sponsorship_model

		title_sponsor = sponsorship_model.title_sponsor
		# title_sponsor_value = None # default None for AI teams, don't track specifics like that for AI
		# other_sponsors_value = None # default None for AI teams, don't track specifics like that for AI

		title_sponsor_value = sponsorship_model.title_sponsor_value
		title_sponsor_contract_length = sponsorship_model.title_sponsor_contract_length
		other_sponsors_value = sponsorship_model.other_sponsorship

		cursor.execute('''
				INSERT INTO TeamSponsors (Team, TitleSponsor, TitleSponsorValue, TitleSponsorContractLength, OtherSponsorsValue)
				VALUES (?, ?, ?, ?, ?)
			''', (
				team_name,
				title_sponsor,
				title_sponsor_value,
				title_sponsor_contract_length,
				other_sponsors_value
			))
		
def load_team_sponsors(conn: sqlite3.Connection) -> pd.DataFrame:
	return pd.read_sql('SELECT * FROM TeamSponsors', conn)