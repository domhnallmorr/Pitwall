from __future__ import annotations
from typing import TYPE_CHECKING

import sqlite3
import pandas as pd
import numpy as np
from io import StringIO

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model


def save_drivers_season_stats(model: Model, save_file: sqlite3.Connection) -> None:
	cursor = save_file.cursor()

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS "DriverSeasonStats" (
		"Name"	TEXT,
		"StartsThisSeason"	INTEGER,
		"PointsThisSeason"	INTEGER,
		"PolesThisSeason"	INTEGER,
		"WinsThisSeason"	INTEGER,
		"PodiumsThisSeason"	INTEGER,
		"DNFsThisSeason"	INTEGER,
		"BestResultThisSeason"	INTEGER,
		"BestResultRndThisSeason"	INTEGER,
		"Race_Results"	TEXT
		)'''
				)
	
	cursor.execute("DELETE FROM DriverSeasonStats") # clear existing data

	for driver in model.drivers:
		name = driver.name
		starts_this_season = driver.season_stats.starts_this_season
		points_this_season = driver.season_stats.points_this_season
		poles_this_season = driver.season_stats.poles_this_season
		wins_this_season = driver.season_stats.wins_this_season
		podiums_this_season = driver.season_stats.podiums_this_season
		dnfs_this_season = driver.season_stats.dnfs_this_season
		best_result_this_season = driver.season_stats.best_result_this_season
		rnd_best_result_scored = driver.season_stats.rnd_best_result_scored
		race_results_str = driver.season_stats.race_results_df.to_json()

		cursor.execute('''
				INSERT INTO DriverSeasonStats (name, startsthisseason, pointsthisseason, polesthisseason, winsthisseason, podiumsthisseason, dnfsthisseason,
				 bestresultthisseason, bestresultrndthisseason, race_results)
				VALUES (?, ?, ?, ?, ?, ?, ?,
				 ?, ?, ?)
		''', (
			name,
			starts_this_season,
			points_this_season,
			poles_this_season,
			wins_this_season,
			podiums_this_season,
			dnfs_this_season,
			best_result_this_season,
			rnd_best_result_scored,
			race_results_str,
		))

def load_drivers_season_stats(conn: sqlite3.Connection, model: Model) -> None:
	stats_df = pd.read_sql('SELECT * FROM DriverSeasonStats', conn)

	for idx, row in stats_df.iterrows():
		name = row["Name"]
		starts_this_season = row["StartsThisSeason"]
		points_this_season = row["PointsThisSeason"]
		poles_this_season = row["PolesThisSeason"]
		wins_this_season = row["WinsThisSeason"]
		podiums_this_season = row["PodiumsThisSeason"]
		dnfs_this_season = row["DNFsThisSeason"]
		race_results_str = row["Race_Results"]

		driver_model = model.entity_manager.get_driver_model(name)
		driver_model.setup_season_stats()
		driver_model.season_stats.starts_this_season = starts_this_season
		driver_model.season_stats.points_this_season = points_this_season
		driver_model.season_stats.poles_this_season = poles_this_season
		driver_model.season_stats.wins_this_season = wins_this_season
		driver_model.season_stats.podiums_this_season = podiums_this_season
		driver_model.season_stats.dnfs_this_season = dnfs_this_season
		df = pd.read_json(StringIO(race_results_str)) # load race results from string
		#replace nan with None
		df = df.replace({np.nan: None})
		driver_model.season_stats.race_results_df = df