from __future__ import annotations
import sqlite3
from typing import Union, Optional, TYPE_CHECKING
from io import StringIO

import pandas as pd
import numpy as np

from pw_model import load_roster
from pw_model.pw_model_enums import StaffRoles, CalendarState
from pw_model.load_save.drivers_load_save import save_drivers, load_drivers
from pw_model.load_save.driver_offers_load_save import save_driver_offers, load_driver_offers
from pw_model.load_save.driver_season_stats_load_save import save_drivers_season_stats, load_drivers_season_stats
from pw_model.load_save.email_load_save import save_email, load_email
from pw_model.load_save.finance_load_save import save_finance_model, load_finance_model
from pw_model.load_save.general_load_save import save_general, load_general
from pw_model.load_save.team_sponsors_load_save import save_team_sponsors
from pw_model.load_save.sponsors_load_save import load_sponsors, save_sponsors
from pw_model.load_save.standings_load_save import save_standings, load_standings
from pw_model.load_save.car_development_load_save import save_car_development, load_car_development
from pw_model.load_save.calendar_load_save import save_calendar, load_calendar
from pw_model.load_save.transport_costs_load_save import save_transport_costs_model, load_transport_costs
from pw_model.load_save.team_principal_load_save import save_team_principals
from pw_model.load_save.technical_directors_load_save import save_technical_directors
from pw_model.load_save.tyres_load_save import save_tyre_suppliers, load_tyre_suppliers
from pw_model.load_save.staff_market_load_save import save_grid_this_year, save_grid_next_year, save_new_contracts_df, load_grid_this_year, load_grid_next_year
from pw_model.load_save.testing_load_save import save_testing_model, load_testing
from pw_model.load_save.sponsor_market_load_save import save_sponsors_this_year, save_sponsors_next_year, save_sponsor_new_contracts_df, load_sponsors_market
from pw_model.load_save.team_descriptions_load_save import save_team_descriptions
from pw_model.load_save.engine_suppliers_load_save import save_engine_suppliers
from pw_model.load_save.team_colors_load_save import save_team_colors
from pw_model.load_save.roster_loader import LoadModes

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def save_game(model: Model, mode: str="file") -> sqlite3.Connection:
	assert mode in ["file", "memory"]
	
	if mode == "file":
		save_file = sqlite3.connect(rf"{model.run_directory}\save_game.db")
	elif mode == "memory":
		save_file = sqlite3.connect(":memory:")
	
	save_general(model, save_file)
	save_drivers(model, save_file)
	save_drivers_season_stats(model, save_file)
	save_commercial_managers(model, save_file)
	save_technical_directors(model, save_file)
	save_teams(model, save_file)
	save_teams_stats(model, save_file)
	save_grid_this_year(model, save_file)
	save_grid_next_year(model, save_file)
	save_new_contracts_df(model, save_file)
	save_standings(model, save_file)
	save_email(model, save_file)
	save_calendar(model, save_file)
	save_team_sponsors(model, save_file)
	save_driver_offers(model, save_file)
	save_team_principals(model, save_file)
	save_tyre_suppliers(model, save_file)
	save_sponsors(model, save_file)
	save_sponsors_this_year(model, save_file)
	save_sponsors_next_year(model, save_file)
	save_sponsor_new_contracts_df(model, save_file)
	save_team_descriptions(model, save_file)
	save_engine_suppliers(model, save_file)
	save_team_colors(model, save_file)

	if model.player_team_model is not None:
		save_car_development(model, save_file)
		save_finance_model(model, save_file)
		save_testing_model(model, save_file)
		save_transport_costs_model(model.player_team_model.finance_model.transport_costs_model, save_file)

	save_file.commit()

	if mode == "file":
		save_file.close() # only close if we are saving to file, if in memory, keep the connection open

	return save_file


def save_commercial_managers(model: Model, save_file: sqlite3.Connection) -> None:
	cursor = save_file.cursor()
	# TODO condense into a single "managers" table
	cursor.execute('''
	CREATE TABLE IF NOT EXISTS "commercial_managers" (
	"Year"	TEXT,
	"Name"	TEXT,
	"Age"	INTEGER,
	"Skill"	INTEGER,
	"Salary"	INTEGER,
	"ContractLength"	INTEGER,
	"RetiringAge"	INTEGER,
	"Retiring"	INTEGER,
	"Retired"	INTEGER
			)'''
				)
	
	cursor.execute("DELETE FROM commercial_managers") # clear existing data

	for idx, list_type in enumerate([model.commercial_managers, model.future_managers]):
		for commercial_manager in list_type:
			process = False
			if idx == 0:
				year = "default"
				process = True
			elif idx == 1:
				if commercial_manager[1].role == StaffRoles.COMMERCIAL_MANAGER:
					year = commercial_manager[0]
					commercial_manager = commercial_manager[1]
					process = True

			if process is True:

				cursor.execute('''
					INSERT INTO commercial_managers (year, name, age, skill, salary, contractlength, retiringage, retiring, retired) 
					VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
				''', (
					year,
					commercial_manager.name, 
					commercial_manager.age,
					commercial_manager.skill,
					commercial_manager.contract.salary,
					commercial_manager.contract.contract_length,
					commercial_manager.retiring_age,
					commercial_manager.retiring,
					commercial_manager.retired,
				))



def save_teams(model: Model, save_file: sqlite3.Connection) -> None:

	cursor = save_file.cursor()

	cursor.execute('''
	CREATE TABLE IF NOT EXISTS "teams" (
	"Year"	TEXT,
	"Name"	TEXT,
	"Country"	TEXT,
	"TeamPrincipal"	TEXT,
	"Driver1"	TEXT,
	"Driver2"	TEXT,
	"CarSpeed"	INTEGER,
	"NumberofStaff"	INTEGER,
	"Facilities"	INTEGER,
	"StartingBalance"	INTEGER,
	"CommercialManager"	TEXT,
	"TechnicalDirector"	TEXT,
	"EngineSupplier"	TEXT,
	"EngineSupplierDeal"	TEXT,
	"EngineSupplierCosts"	INTEGER,
	"TyreSupplier"	TEXT,
	"TyreSupplierDeal"	TEXT,
	"TyreSupplierCosts"	INTEGER	
	)'''
				)
	
	cursor.execute("DELETE FROM teams") # clear existing data

	for team in model.teams:

		cursor.execute('''
			INSERT INTO teams (year, name, country, TeamPrincipal, Driver1,
				 Driver2, CarSpeed, NumberofStaff, Facilities, StartingBalance,
				 CommercialManager, TechnicalDirector, EngineSupplier, EngineSupplierDeal, EngineSupplierCosts,
				 TyreSupplier, TyreSupplierDeal, TyreSupplierCosts) 
			VALUES (?, ?, ?, ?, ?,
				 ?, ?, ?, ?, ?,
				 ?, ?, ?, ?, ?,
				 ?, ?, ?)
		''', (
			"default",
			team.name, 
			team.country, 
			team.team_principal,
			team.driver1,
			team.driver2, 
			team.car_model.speed, 
			team.number_of_staff, 
			team.facilities_model.factory_rating, 
			team.finance_model.balance, 
			team.commercial_manager,
			team.technical_director,
			team.supplier_model.engine_supplier,
			team.supplier_model.engine_supplier_deal.value,
			team.supplier_model.engine_supplier_cost,
			team.supplier_model.tyre_supplier,
			team.supplier_model.tyre_supplier_deal.value,
			team.supplier_model.tyre_supplier_cost
		))

def save_teams_stats(model: Model, save_file: sqlite3.Connection) -> None:
	cursor = save_file.cursor()

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS "teams_stats" (
		"Name"	TEXT,
		"StartsThisSeason"	INTEGER,
		"PointsThisSeason"	INTEGER,
		"PolesThisSeason"	INTEGER,
		"WinsThisSeason"	INTEGER,
		"PodiumsThisSeason"	INTEGER,
		"DNFsThisSeason"	INTEGER,
		"BestResultThisSeason"	INTEGER,
		"BestResultRndThisSeason"	INTEGER
		)'''
				)
	
	cursor.execute("DELETE FROM teams_stats") # clear existing data

	for team in model.teams:
		name = team.name
		starts_this_season = team.season_stats.starts_this_season
		points_this_season = team.season_stats.points_this_season
		poles_this_season = team.season_stats.poles_this_season
		wins_this_season = team.season_stats.wins_this_season
		podiums_this_season = team.season_stats.podiums_this_season
		dnfs_this_season = team.season_stats.dnfs_this_season
		best_result_this_season = team.season_stats.best_result_this_season
		rnd_best_result_scored = team.season_stats.rnd_best_result_scored

		cursor.execute('''
				INSERT INTO teams_stats (name, startsthisseason, pointsthisseason, polesthisseason, winsthisseason, podiumsthisseason, dnfsthisseason, bestresultthisseason, bestresultrndthisseason)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
		))


def load(model: Model, save_file: Union[None, sqlite3.Connection, str]=None, mode: str="file") -> None:
	assert mode in ["file", "memory"]

	if mode == "file":
		load_mode = LoadModes.SAVE_GAME
		if save_file is None:
			conn = sqlite3.connect(f"{model.run_directory}\\save_game.db")
		elif isinstance(save_file, str):
			conn = sqlite3.connect(save_file)
		else:
			raise ValueError("Invalid type for 'save_file' when mode is 'file'")
	elif mode == "memory":
		load_mode = LoadModes.MEMORY
		if isinstance(save_file, sqlite3.Connection):
			conn = save_file
		else:
			raise ValueError("Invalid type for 'save_file' when mode is 'memory'")
	
	model.load_roster(model.run_directory, load_mode=load_mode, conn=conn)
	# load_drivers(conn, model)
	# load_sponsors(conn)
	load_drivers_season_stats(conn, model)
	# load_senior_staff(conn, model)
	# load_teams(conn, model)
	load_teams_stats(conn, model)
	load_general(conn, model)
	load_standings(conn, model)
	load_grid_this_year(conn, model)
	load_grid_next_year(conn, model)
	load_email(conn, model)
	# load_calendar(conn, model)
	load_driver_offers(conn, model)
	# load_tyre_suppliers(model, conn)
	load_sponsors_market(conn, model)

	if model.player_team_model is not None:
		load_transport_costs(conn, model.player_team_model.finance_model.transport_costs_model)
		load_finance_model(model, conn)
		load_car_development(conn, model)
		load_testing(conn, model)



def load_senior_staff(conn: sqlite3.Connection, model: Model) -> None:
	commercial_managers, technical_directors, team_principals, future_managers = load_roster.load_senior_staff(model, conn)
	model.commercial_managers = commercial_managers
	model.technical_directors = technical_directors
	model.future_managers = future_managers
	model.team_principals = team_principals  # Add this line to properly handle team principals

def load_teams(conn: sqlite3.Connection, model: Model) -> None:
	teams = load_roster.load_teams(model, conn)
	model.teams = teams

def load_teams_stats(conn: sqlite3.Connection, model: Model) -> None:
	stats_df = pd.read_sql('SELECT * FROM teams_stats', conn)

	for idx, row in stats_df.iterrows():
		name = row["Name"]
		points_this_season = row["PointsThisSeason"]
		poles_this_season = row["PolesThisSeason"]
		wins_this_season = row["WinsThisSeason"]
		podiums_this_season = row["PodiumsThisSeason"]
		dnfs_this_season = row["DNFsThisSeason"]
		best_result_this_season = row["BestResultThisSeason"]
		rnd_best_result_scored = row["BestResultRndThisSeason"]

		team_model = model.entity_manager.get_team_model(name)
		team_model.season_stats.points_this_season = points_this_season
		team_model.season_stats.poles_this_season = poles_this_season
		team_model.season_stats.wins_this_season = wins_this_season
		team_model.season_stats.podiums_this_season = podiums_this_season
		team_model.season_stats.dnfs_this_season = dnfs_this_season
		team_model.season_stats.best_result_this_season = best_result_this_season
		team_model.season_stats.rnd_best_result_scored = rnd_best_result_scored




