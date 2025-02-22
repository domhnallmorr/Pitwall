from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

import pandas as pd

from pw_model.team.team_facade import get_season_opening_balance, get_weeks_in_debt

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def save_finance_model(model: Model, save_file: sqlite3.Connection) -> None:
	
	cursor = save_file.cursor()
	cursor.execute('''
			CREATE TABLE IF NOT EXISTS "finance" (
            "SeasonOpeningBalance" INTEGER,
			"WeeksInDebt" INTEGER
            )'''
        )
	cursor.execute("DELETE FROM finance")  # Clear existing data


	cursor.execute('''
			INSERT INTO finance (SeasonOpeningBalance, WeeksInDebt)
			VALUES (?, ?)
		''', (
			get_season_opening_balance(model.player_team_model),
			get_weeks_in_debt(model.player_team_model)
		))

def load_finance_model(model: Model, conn: sqlite3.Connection) -> None:
	finance_df = pd.read_sql('SELECT * FROM finance', conn)

	for idx, row in finance_df.iterrows():
		model.player_team_model.finance_model.season_opening_balance = row["SeasonOpeningBalance"]
		model.player_team_model.finance_model.consecutive_weeks_in_debt = row["WeeksInDebt"]
		