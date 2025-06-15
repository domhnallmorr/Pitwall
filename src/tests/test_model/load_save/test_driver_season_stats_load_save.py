import sqlite3
import pandas as pd
import numpy as np
import pytest

from pw_model.load_save.driver_season_stats_load_save import save_drivers_season_stats, load_drivers_season_stats


class FakeEntityManager:
	def __init__(self, drivers):
		self._drivers = {d.name: d for d in drivers}

	def get_driver_model(self, name):
		return self._drivers[name]


class FakeSeasonStats:
	def __init__(self, df: pd.DataFrame):
		# Initialize all stat attributes
		self.starts_this_season = None
		self.points_this_season = None
		self.poles_this_season = None
		self.wins_this_season = None
		self.podiums_this_season = None
		self.dnfs_this_season = None
		# Attach the DataFrame of race results
		self.race_results_df = df
		self.best_result_this_season = None
		self.rnd_best_result_scored = None


class FakeDriverModel:
	def __init__(self, name: str, season_stats: FakeSeasonStats):
		self.name = name
		self.season_stats = season_stats

	def setup_season_stats(self):
		# No-op for our test double
		return


class FakeModel:
	def __init__(self, drivers):
		self.drivers = drivers
		self.entity_manager = FakeEntityManager(drivers)


def _normalize_nulls(df: pd.DataFrame) -> pd.DataFrame:
	"""Convert Python ``None`` values to ``np.nan`` in a DataFrame **without**
	triggering pandas FutureWarnings about down‑casting.
	"""
	out = df.replace({None: np.nan})
	# ``infer_objects`` is the path recommended by the warning message.
	return out.infer_objects(copy=False)


@pytest.mark.parametrize("stat_values", [
	{
		'starts': 3,
		'points': 15,
		'poles': 2,
		'wins': 1,
		'podiums': 2,
		'dnfs': 0,
		'df': pd.DataFrame({'race_number': [1, 2, 3], 'position': [1, 3, 5]})
	},
	{
		'starts': 2,
		'points': 10,
		'poles': 0,
		'wins': 0,
		'podiums': 1,
		'dnfs': 1,
		'df': pd.DataFrame({'race_number': [1, 2], 'position': [None, 2]})
	}
])
def test_save_load_roundtrip(stat_values):
	# Setup initial season stats
	original_df = stat_values['df']
	season_stats = FakeSeasonStats(original_df.copy())
	season_stats.starts_this_season = stat_values['starts']
	season_stats.points_this_season = stat_values['points']
	season_stats.poles_this_season = stat_values['poles']
	season_stats.wins_this_season = stat_values['wins']
	season_stats.podiums_this_season = stat_values['podiums']
	season_stats.dnfs_this_season = stat_values['dnfs']

	# Create driver and model
	driver = FakeDriverModel("TestDriver", season_stats)
	model = FakeModel([driver])

	# Use in-memory SQLite database
	conn = sqlite3.connect(':memory:')

	# Save to DB
	save_drivers_season_stats(model, conn)

	# Mutate stats to different values to ensure load overwrites
	season_stats.starts_this_season = None
	season_stats.points_this_season = None
	season_stats.poles_this_season = None
	season_stats.wins_this_season = None
	season_stats.podiums_this_season = None
	season_stats.dnfs_this_season = None
	season_stats.race_results_df = pd.DataFrame()

	# Load from DB
	load_drivers_season_stats(conn, model)

	# Assert that loaded values match the originals
	assert driver.season_stats.starts_this_season == stat_values['starts']
	assert driver.season_stats.points_this_season == stat_values['points']
	assert driver.season_stats.poles_this_season == stat_values['poles']
	assert driver.season_stats.wins_this_season == stat_values['wins']
	assert driver.season_stats.podiums_this_season == stat_values['podiums']
	assert driver.season_stats.dnfs_this_season == stat_values['dnfs']


