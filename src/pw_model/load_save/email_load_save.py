from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

import pandas as pd

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def save_email(model: Model, save_file: sqlite3.Connection) -> None:
	df = model.inbox.generate_dataframe()
	df.to_sql("email", save_file, if_exists="replace", index=False)

def load_email(conn: sqlite3.Connection, model: Model) -> None:
	df = pd.read_sql('SELECT * FROM email', conn)
	model.inbox.load_dataframe(df)

