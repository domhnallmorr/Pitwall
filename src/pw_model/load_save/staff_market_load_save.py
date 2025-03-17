from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

import pandas as pd

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model


def save_grid_this_year(model: Model, save_file: sqlite3.Connection) -> None:
	model.staff_market.grid_this_year_df.to_sql("grid_this_year_df", save_file, if_exists="replace", index=False)

def save_grid_next_year(model: Model, save_file: sqlite3.Connection) -> None:
	model.staff_market.grid_next_year_df.to_sql("grid_next_year_df", save_file, if_exists="replace", index=False)
	model.staff_market.grid_next_year_announced_df.to_sql("grid_next_year_announced", save_file, if_exists="replace", index=False)

def save_new_contracts_df(model: Model, save_file: sqlite3.Connection) -> None:
	model.staff_market.new_contracts_df.to_sql("new_contracts_df", save_file, if_exists="replace", index=False)


def load_grid_this_year(conn: sqlite3.Connection, model: Model) -> None:
	model.staff_market.grid_this_year_df = pd.read_sql('SELECT * FROM grid_this_year_df', conn)

def load_grid_next_year(conn: sqlite3.Connection, model: Model) -> None:
	model.staff_market.grid_next_year_df = pd.read_sql('SELECT * FROM grid_next_year_df', conn)
	model.staff_market.grid_next_year_announced_df = pd.read_sql('SELECT * FROM grid_next_year_announced', conn)
	model.staff_market.new_contracts_df = pd.read_sql('SELECT * FROM new_contracts_df', conn)