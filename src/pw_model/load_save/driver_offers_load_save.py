from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

import pandas as pd

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def save_driver_offers(model: Model, save_file: sqlite3.Connection) -> None:
	model.driver_offers.dataframe.to_sql("driver_offers", save_file, if_exists="replace", index=False)

def load_driver_offers(conn: sqlite3.Connection, model: Model) -> None:
	model.driver_offers.dataframe = pd.read_sql('SELECT * FROM driver_offers', conn)