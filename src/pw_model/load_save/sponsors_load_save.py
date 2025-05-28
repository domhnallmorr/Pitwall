from __future__ import annotations
import sqlite3
from typing import TYPE_CHECKING

import pandas as pd

from pw_model.sponsors.sponsor_model import SponsorModel
from pw_model.pw_model_enums import SponsorTypes

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def save_sponsors(model: Model, save_file: sqlite3.Connection) -> None:
	cursor = save_file.cursor()

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS "Sponsors" (
		"Year"	TEXT,
		"Name"	TEXT,
		"Wealth"	INTEGER
		)'''
				)
	
	cursor.execute("DELETE FROM Sponsors") # clear existing data

	for idx, sponsor_type in enumerate([model.sponsors, model.future_sponsors]):
		for sponsor in sponsor_type:
			if idx == 0:
				year = "default"
			else:
				year = sponsor[0]
				sponsor = sponsor[1]

			cursor.execute('''
				INSERT INTO Sponsors (year, name, wealth) 
				VALUES (?, ?, ?)
			''', (
				year,
				sponsor.name, 
				sponsor.wealth
			))

def load_sponsors(conn: sqlite3.Connection) -> tuple[list[SponsorModel], list[tuple[str, SponsorModel]]]:
	sponsors : list[SponsorModel] = []
	future_sponsors : list[tuple[str, SponsorModel]] = []

	# First get the sponsor contract details from TeamSponsors
	sponsor_contracts: dict[str, tuple[int, int]] = {}  # Dict[sponsor_name, (payment, contract_length)]
	team_sponsors_df = pd.read_sql(
		"SELECT TitleSponsor, TitleSponsorValue, TitleSponsorContractLength FROM TeamSponsors", 
		conn
	)
	
	for _, row in team_sponsors_df.iterrows():
		if row["TitleSponsor"] and row["TitleSponsorValue"]:
			sponsor_contracts[row["TitleSponsor"]] = (
				row["TitleSponsorValue"],
				row["TitleSponsorContractLength"],
				SponsorTypes.TITLE
			)

	# Then load the sponsors
	table_name = "Sponsors"
	cursor = conn.execute(f"PRAGMA table_info({table_name})")
	columns = cursor.fetchall()
	column_names = [column[1] for column in columns]

	year_idx = column_names.index("Year")
	name_idx = column_names.index("Name")
	wealth_idx = column_names.index("Wealth")

	cursor = conn.cursor()
	cursor.execute(f"SELECT * FROM {table_name}")
	sponsors_table = cursor.fetchall()

	for row in sponsors_table:
		year = row[year_idx]
		name = row[name_idx]
		wealth = int(row[wealth_idx])
		
		# Get contract details if this sponsor is currently a title sponsor
		contract_details = sponsor_contracts.get(name)
		if contract_details:
			total_payment, contract_length, sponsor_type = contract_details
		else:
			total_payment, contract_length, sponsor_type = 0, 0, SponsorTypes.NONE
		
		sponsor = SponsorModel(name, wealth, sponsor_type, contract_length=contract_length, total_payment=total_payment)

		if year == "default":
			sponsors.append(sponsor)
		else:
			future_sponsors.append((year, sponsor))

	return sponsors, future_sponsors

