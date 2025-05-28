from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

import pandas as pd

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def save_sponsors_this_year(model: Model, save_file: sqlite3.Connection) -> None:
	model.sponsor_market.sponsors_this_year_df.to_sql("SponsorsThisYear_df", save_file, if_exists="replace", index=False)

def save_sponsors_next_year(model: Model, save_file: sqlite3.Connection) -> None:
	model.sponsor_market.sponsors_next_year_df.to_sql("SponsorsNextYear_df", save_file, if_exists="replace", index=False)	
	model.sponsor_market.sponsors_next_year_announced_df.to_sql("SponsorsNextYearAnnounced_df", save_file, if_exists="replace", index=False)

def save_sponsor_new_contracts_df(model: Model, save_file: sqlite3.Connection) -> None:
	model.sponsor_market.new_contracts_df.to_sql("NewSponsorContracts_df", save_file, if_exists="replace", index=False)

def load_sponsors_this_year(conn: sqlite3.Connection, model: Model) -> None:
	model.sponsor_market.sponsors_this_year_df = pd.read_sql('SELECT * FROM SponsorsThisYear_df', conn)

def load_sponsors_next_year(conn: sqlite3.Connection, model: Model) -> None:
	model.sponsor_market.sponsors_next_year_df = pd.read_sql('SELECT * FROM SponsorsNextYear_df', conn)
	model.sponsor_market.sponsors_next_year_announced_df = pd.read_sql('SELECT * FROM SponsorsNextYearAnnounced_df', conn)
	model.sponsor_market.new_contracts_df = pd.read_sql('SELECT * FROM NewSponsorContracts_df', conn)