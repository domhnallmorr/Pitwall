from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

import pandas as pd

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def save_standings(model: Model, save_file: sqlite3.Connection) -> None:
	model.season.standings_manager.drivers_standings_df.to_sql("drivers_standings_df", save_file, if_exists="replace", index=False)
	model.season.standings_manager.constructors_standings_df.to_sql("constructors_standings_df", save_file, if_exists="replace", index=False)

def load_standings(conn: sqlite3.Connection, model: Model) -> None:
	model.season.standings_manager.drivers_standings_df = pd.read_sql('SELECT * FROM drivers_standings_df', conn)
	model.season.standings_manager.constructors_standings_df = pd.read_sql('SELECT * FROM constructors_standings_df', conn)