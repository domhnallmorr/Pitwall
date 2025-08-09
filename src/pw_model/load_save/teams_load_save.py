from __future__ import annotations
from typing import TYPE_CHECKING
import sqlite3

from pw_model.team import team_model
from pw_model.car import car_model
from pw_model.team.suppliers_model import SupplierDeals
from pw_model.load_save.team_sponsors_load_save import load_team_sponsors

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

def load_teams(model: Model, conn: sqlite3.Connection) -> list[team_model.TeamModel]:
	sponsors_df = load_team_sponsors(conn)

	teams = []

	table_name = "teams"

	cursor = conn.execute(f'PRAGMA table_info({table_name})')
	columns = cursor.fetchall()
	column_names = [column[1] for column in columns]

	name_idx = column_names.index("Name")
	country_idx = column_names.index("Country")
	team_principal_idx = column_names.index("TeamPrincipal")
	driver1_idx = column_names.index("Driver1")
	driver2_idx = column_names.index("Driver2")
	car_speed_idx = column_names.index("CarSpeed")
	number_of_staff_idx = column_names.index("NumberofStaff")
	facilities_idx = column_names.index("Facilities")

	# Engine Supplier
	engine_supplier_idx = column_names.index("EngineSupplier")
	engine_supplier_deal_idx = column_names.index("EngineSupplierDeal")
	engine_supplier_cost_idx = column_names.index("EngineSupplierCosts")

	# Tyre Suuplier
	tyre_supplier_idx = column_names.index("TyreSupplier")
	tyre_supplier_deal_idx = column_names.index("TyreSupplierDeal")
	tyre_supplier_cost_idx = column_names.index("TyreSupplierCosts")
	
	balance_idx = column_names.index("StartingBalance")

	commercial_manager_idx = column_names.index("CommercialManager")
	technical_director_idx = column_names.index("TechnicalDirector")

	cursor = conn.cursor()
	cursor.execute(f"SELECT * FROM {table_name}")
	teams_table = cursor.fetchall()

	for idx, row in enumerate(teams_table):
		if row[0].lower() == "default":
			name = row[name_idx]
			country = row[country_idx]
			team_principal = row[team_principal_idx]
			driver1 = row[driver1_idx]
			driver2 = row[driver2_idx]
			car_speed = row[car_speed_idx]

			facilities = row[facilities_idx]
			number_of_staff = row[number_of_staff_idx]

			engine_supplier = row[engine_supplier_idx]
			engine_supplier_deal = SupplierDeals(row[engine_supplier_deal_idx])
			engine_supplier_cost = row[engine_supplier_cost_idx]

			tyre_supplier = row[tyre_supplier_idx]
			tyre_supplier_deal = SupplierDeals(row[tyre_supplier_deal_idx])
			tyre_supplier_cost = row[tyre_supplier_cost_idx]

			starting_balance = row[balance_idx]
			title_sponsor = str(sponsors_df.loc[sponsors_df["Team"] == name, "TitleSponsor"].iloc[0])
			other_sponsorship = int(sponsors_df.loc[sponsors_df["Team"] == name, "OtherSponsorsValue"].iloc[0])

			commercial_manager = row[commercial_manager_idx]
			technical_director = row[technical_director_idx]

			car = car_model.CarModel(car_speed)
			team = team_model.TeamModel(model, name, country, team_principal, driver1, driver2, car, number_of_staff, facilities,
							   starting_balance, other_sponsorship, title_sponsor,
							   commercial_manager, technical_director,
							   engine_supplier, engine_supplier_deal, engine_supplier_cost,
							   tyre_supplier, tyre_supplier_deal, tyre_supplier_cost,
							   idx)
			
			teams.append(team)

	return teams