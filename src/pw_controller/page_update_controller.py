'''
A controller dedicated to refreshing the off track UI pages
'''
from __future__ import annotations
import copy
from typing import TYPE_CHECKING

import pandas as pd

from pw_model.pw_model_enums import StaffRoles
from pw_model.finance import finance_data
from pw_controller.car_development.car_page_data import get_car_page_data, CarPageData
from pw_controller.page_update_typed_dicts import HomePageData
from pw_controller.staff_page.staff_page_data import get_staff_page_data

if TYPE_CHECKING:
	from pw_controller.pw_controller import Controller
	from pw_model.pw_base_model import Model
	from pw_view.view import View

class PageUpdateController:
	def __init__(self, controller: Controller):
		self.controller = controller

	@property
	def model(self) -> Model:
		return self.controller.model
	
	@property
	def view(self) -> View:
		return self.controller.view
	
	def refresh_ui(self, new_season: bool=False) -> None:
		self.update_calendar_page()
		self.update_car_page()
		self.update_email_page()
		self.update_finance_page()
		self.update_grid_page()
		self.update_home_page()
		self.update_staff_page(new_season)
		self.update_standings_page()
		self.update_facilities_page()

	def update_staff_page(self, new_season: bool=False) -> None:
		data = get_staff_page_data(self.model)
		self.view.staff_page.update_page(data, new_season)

	def update_standings_page(self) -> None:
		drivers_standings_df = self.model.season.standings_manager.drivers_standings_df.copy(deep=True)
		constructors_standings_df = self.model.season.standings_manager.constructors_standings_df.copy(deep=True)

		drivers_flags = [self.model.entity_manager.get_driver_model(d).country for d in drivers_standings_df["Driver"].values]
		team_flags = [self.model.entity_manager.get_team_model(t).country for t in constructors_standings_df["Team"].values]
		self.view.standings_page.update_standings(drivers_standings_df, constructors_standings_df, drivers_flags, team_flags)

	def update_email_page(self) -> None:
		emails = copy.deepcopy(self.model.inbox.emails)
		self.view.email_page.update_page(emails)

	def update_finance_page(self) -> None:
		data: finance_data.FinanceData = {
			"profit": copy.deepcopy(self.model.player_team_model.finance_model.season_profit),
			"title_sponsor": copy.deepcopy(self.model.player_team_model.finance_model.sponsorship_model.title_sponsor),

			"title_sponsor_value": copy.deepcopy(self.model.player_team_model.finance_model.sponsorship_model.title_sponsor_value),
			"other_sponsorship": copy.deepcopy(self.model.player_team_model.finance_model.sponsorship_model.other_sponsorship),
			"prize_money": copy.deepcopy(self.model.player_team_model.finance_model.prize_money),
			"drivers_payments": copy.deepcopy(self.model.player_team_model.finance_model.drivers_payments),
			"total_income": copy.deepcopy(self.model.player_team_model.finance_model.total_income),
			
			"total_staff_costs_per_year": copy.deepcopy(self.model.player_team_model.finance_model.total_staff_costs_per_year),
			"drivers_salary": copy.deepcopy(self.model.player_team_model.finance_model.drivers_salary),
			"technical_director_salary": copy.deepcopy(self.model.player_team_model.technical_director_model.contract.salary),
			"commercial_manager_salary": copy.deepcopy(self.model.player_team_model.commercial_manager_model.contract.salary),
			"engine_supplier_cost": copy.deepcopy(self.model.player_team_model.supplier_model.engine_supplier_cost),
			"tyre_supplier_cost": copy.deepcopy(self.model.player_team_model.supplier_model.tyre_supplier_cost),
			"race_costs": self.model.player_team_model.finance_model.transport_costs_model.estimated_season_costs,
			"damage_costs": self.model.player_team_model.finance_model.damage_costs_model.damage_costs_this_season, 
			"car_development_costs": copy.deepcopy(self.model.player_team_model.finance_model.car_development_costs_model.costs_this_season),
			"total_expenditure": copy.deepcopy(self.model.player_team_model.finance_model.total_expenditure), # hard code this for now TODO, make it variable
			
			"balance_history": copy.deepcopy(self.model.player_team_model.finance_model.balance_history),
			"balance_history_dates": copy.deepcopy(self.model.player_team_model.finance_model.balance_history_dates),
			"summary_df": self.model.player_team_model.finance_model.sponsorship_model.summary_df,
		}

		self.view.finance_page.update_page(data)

	def update_grid_page(self) -> None:
		year = self.model.year
		grid_this_year_df = self.model.staff_market.grid_this_year_df.copy(deep=True)
		grid_next_year_announced_df = self.model.staff_market.grid_next_year_announced_df.copy(deep=True)
		sponsors_this_year_df = self.model.sponsor_market.sponsors_this_year_df.copy(deep=True)
		sponsors_next_year_announced_df = self.model.sponsor_market.sponsors_next_year_announced_df.copy(deep=True)

		self.view.grid_page.update_page(
			year,
			grid_this_year_df,
			grid_next_year_announced_df,
			sponsors_this_year_df,
			sponsors_next_year_announced_df
		)

	def update_home_page(self) -> None:
		data: HomePageData = {
			"next_race": self.model.season.calendar.next_race,
			"next_race_week": self.model.season.calendar.next_race_week,
			"current_position": self.model.player_team_model.current_position + 1, # pos is zero indexed
			"constructors_standings_df": self.model.season.standings_manager.constructors_standings_df.copy(deep=True),

			"driver1": self.model.player_team_model.driver1,
			"driver1_contract": self.model.player_team_model.driver1_model.contract.contract_length,
			"driver2": self.model.player_team_model.driver2,
			"driver2_contract": self.model.player_team_model.driver2_model.contract.contract_length,
			"technical_director": self.model.player_team_model.technical_director,
			"technical_director_contract": self.model.player_team_model.technical_director_model.contract.contract_length,
			"commercial_manager": self.model.player_team_model.commercial_manager,
			"commercial_manager_contract": self.model.player_team_model.commercial_manager_model.contract.contract_length,

			"team_average_stats": self.model.gen_team_average_stats(),
			"player_car": self.model.player_team_model.car_model.speed,
			"player_drivers": self.model.player_team_model.average_driver_skill,
			"player_managers": self.model.player_team_model.average_manager_skill,
			"player_staff": self.model.player_team_model.number_of_staff,
			"player_facilities": self.model.player_team_model.facilities_model.factory_rating,
			"player_sponsorship": self.model.player_team_model.finance_model.sponsorship_model.total_sponsor_income,
		}
		self.view.home_page.update_page(data)

	def update_calendar_page(self) -> None:
		calendar: pd.DataFrame = self.model.season.calendar.dataframe.copy(deep=True)
		self.view.calendar_page.update_page(calendar)

	def update_car_page(self) -> None:
		data = get_car_page_data(self.model)
		
		self.view.car_page.update_page(data)

	def update_main_window(self) -> None:
		player_team_model = self.model.entity_manager.get_team_model(self.model.player_team)
		team = f"{self.model.player_team} - ${player_team_model.finance_model.balance:,}"
		date = f"Week {self.model.season.calendar.current_week} - {self.model.year}"
		state = self.model.season.calendar.state

		self.view.main_window.update_window(team, date, state)

	def update_facilities_page(self, new_season: bool=False) -> None:
		'''
		new_season is passed here to
		'''

		facility_values = [[team.name, team.facilities_model.factory_rating] for team in self.model.teams]
		facility_values.sort(key=lambda x: x[1], reverse=True) # sort, highest speed to lowest speed
		
		data = {
			"facility_values": facility_values,
		}

		self.view.facility_page.update_page(data)

		if new_season is True:
			self.view.facility_page.enable_upgrade_button()
