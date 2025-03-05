from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

import pandas as pd

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model


def save_calendar(model: Model, save_file: sqlite3.Connection) -> None:
	model.season.calendar.dataframe.to_sql("calendar", save_file, if_exists="replace", index=False)


def load_calendar(conn: sqlite3.Connection, model: Model) -> None:
	model.season.calendar.dataframe = pd.read_sql('SELECT * FROM calendar', conn)