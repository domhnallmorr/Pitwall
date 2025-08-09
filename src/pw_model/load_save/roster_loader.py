
from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING, List, Union
import glob
import os
import sqlite3
import pandas as pd
from dataclasses import dataclass

# import load functions
from pw_model.load_save.tracks_load import load_tracks
from pw_model.load_save.load_save_season_calendar import load_season_calendar
from pw_model.load_save.drivers_load_save import load_drivers
from pw_model.load_save.senior_staff_load_save import load_senior_staff
from pw_model.load_save.sponsors_load_save import load_sponsors
from pw_model.load_save.teams_load_save import load_teams
from pw_model.load_save.team_descriptions_load_save import load_team_descriptions
from pw_model.load_save.engine_suppliers_load_save import load_engine_suppliers
from pw_model.load_save.tyres_load_save import load_tyre_suppliers
from pw_model.load_save.team_colors_load_save import load_team_colors

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model
	from pw_model.driver import driver_model
	from pw_model.team import team_model
	from pw_model.senior_staff.commercial_manager import CommercialManager
	from pw_model.senior_staff.technical_director import TechnicalDirector
	from pw_model.senior_staff.team_principal import TeamPrincipalModel
	from pw_model.engine.engine_supplier_model import EngineSupplierModel
	from pw_model.sponsors.sponsor_model import SponsorModel
	from pw_model.track.track_model import TrackModel
	from pw_model.tyre.tyre_supplier_model import TyreSupplierModel

class LoadModes(Enum):
	SAVE_GAME = "save_game"
	ROSTER = "roster"
	MEMORY = "memory"

@dataclass
class RosterData:
	"""Container for data loaded from a roster"""
	tracks: List[TrackModel]
	calendar_dataframe: pd.DataFrame
	drivers: List[driver_model.DriverModel]
	future_drivers: List[tuple[str, driver_model.DriverModel]]
	teams: List[team_model.TeamModel]
	commercial_managers: List[CommercialManager]
	technical_directors: List[TechnicalDirector]
	team_principals: List[TeamPrincipalModel]
	future_managers: List[Union[CommercialManager, TechnicalDirector, TeamPrincipalModel]]
	sponsors: List["SponsorModel"]
	future_sponsors: List[tuple[str, "SponsorModel"]]
	engine_suppliers: List["EngineSupplierModel"]
	tyre_suppliers: List["TyreSupplierModel"]

	# 

class RosterLoader:
	"""Loads roster information from disk without mutating the model."""
	def __init__(self, model: "Model", roster_path: str, load_mode: LoadModes=LoadModes.ROSTER, conn: Union[None, sqlite3.Connection]=None) -> None:
			self.model = model
			self.roster_path = roster_path
			self.load_mode = load_mode

			if load_mode == LoadModes.ROSTER:
				# Initalise paths
				self.season_file = os.path.join(roster_path, "season.txt")
				assert os.path.isfile(self.season_file), f"Cannot Find {self.season_file}"

				self.tracks_folder = os.path.join(roster_path, "tracks")
				assert os.path.isdir(self.tracks_folder), f"Cannot Find {self.tracks_folder}"

				self.track_files = glob.glob(os.path.join(self.tracks_folder, "*.txt"))

			# Connect to database
			if load_mode in [LoadModes.ROSTER, LoadModes.SAVE_GAME]:
				self.conn = sqlite3.connect(fr"{roster_path}\\{load_mode.value}.db")
			elif load_mode == LoadModes.MEMORY:
				self.conn = conn

			# Load data			
			self.load()

	def load(self) -> RosterData:
		if self.load_mode == LoadModes.ROSTER:
			tracks = load_tracks(self.model, self.track_files)
		else:
			tracks = self.model.tracks

		calendar_dataframe = load_season_calendar(self.conn, tracks)
		drivers, future_drivers = load_drivers(self.conn, self.model)
		commercial_managers, technical_directors, team_principals, future_managers = load_senior_staff(self.conn, self.model)
		sponsors, future_sponsors = load_sponsors(self.conn)
		teams = load_teams(self.model, self.conn)
		load_team_descriptions(self.conn, teams)
		engine_suppliers = load_engine_suppliers(self.model, self.conn)
		tyre_suppliers = load_tyre_suppliers(self.model, self.conn)
		load_team_colors(teams, self.conn)

		self.loaded_data = RosterData(
			tracks=tracks,
			calendar_dataframe=calendar_dataframe,
			drivers=drivers,
			future_drivers=future_drivers,
			commercial_managers=commercial_managers,
			technical_directors=technical_directors,
			team_principals=team_principals,
			future_managers=future_managers,			
			sponsors=sponsors,			
			future_sponsors=future_sponsors,	
			teams=teams,		
			engine_suppliers=engine_suppliers,		
			tyre_suppliers=tyre_suppliers,			
		)



