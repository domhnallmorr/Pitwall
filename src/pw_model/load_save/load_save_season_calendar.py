from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

import pandas as pd

from pw_model.track.track_model import TrackModel

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def get_track_model(track_models: list[TrackModel], track_name: str) -> TrackModel:
	for track in track_models:
		if track.name == track_name:
			return track
	raise ValueError(f"Failed to find track {track_name}")

def load_season_calendar(conn: sqlite3.Connection, track_models: list[TrackModel]) -> pd.DataFrame:
	raw_calendar_df = pd.read_sql(
		"SELECT Track, Week, SessionType FROM SeasonCalendar", 
		conn
	)
	data = []
	columns = ["Week", "Track", "Country", "Location", "Winner", "SessionType"]

	for idx, row in raw_calendar_df.iterrows():
		week = int(row["Week"])
		event_type = row["SessionType"]
		track = get_track_model(track_models, row["Track"])
		data.append([week, track.name, track.country, track.location, None, event_type.capitalize()])

	# Sort by week number
	data.sort(key=lambda x: x[0])
	calendar_dataframe = pd.DataFrame(columns=columns, data=data)

	return calendar_dataframe