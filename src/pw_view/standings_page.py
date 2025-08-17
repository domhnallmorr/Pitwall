from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft
import pandas as pd

from pw_view.custom_widgets import custom_container
from pw_view.custom_widgets.custom_datatable import CustomDataTable
from pw_view.custom_widgets.results_table_multi import MultiDriverResultsTable

if TYPE_CHECKING:
	from pw_view.view import View

class StandingsPage(ft.Column):
	def __init__(self, view: View):
		self.view = view
		self.setup_tabs()

		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				self.tabs
			],
			expand=True
		)

		super().__init__(
			controls=[
				ft.Text("Standings", theme_style=self.view.page_header_style),
				self.background_stack
			],
			alignment=ft.MainAxisAlignment.START,
			expand=True
		)

	def setup_tabs(self) -> None:
		self.drivers_tab = ft.Tab(
			text="Drivers",
			icon=ft.Icons.SPORTS_MOTORSPORTS,
			content=ft.Container(
				expand=False,
				alignment=ft.alignment.top_center
			)
		)
		
		self.constructors_tab = ft.Tab(
			text="Constructors",
			icon=ft.Icons.FACTORY,
			content=ft.Container(
				expand=False,
				alignment=ft.alignment.top_center
			)
		)

		self.results_tab = ft.Tab(
			text="Results",
			icon=ft.Icons.TABLE_ROWS,
			content=ft.Container(
				expand=False,
				alignment=ft.alignment.top_center
			)
		)

		self.tabs = ft.Tabs(
			selected_index=0,
			animation_duration=300,
			tabs=[
				self.drivers_tab,
				self.constructors_tab,
				self.results_tab
			],
			expand=True
		)

	def update_standings(self, drivers_standings_df: pd.DataFrame, constructors_standings_df: pd.DataFrame,
					  drivers_flags: list[str], team_flags: list[str],
					  driver_results: list[list], race_countries: list[str]) -> None:
		# Store additional data for future use
		self.driver_results = driver_results
		self.race_countries = race_countries

		# DRIVERS
		self.drivers_table = CustomDataTable(self.view, drivers_standings_df.columns.tolist())
		self.drivers_table.update_table_data(drivers_standings_df.values.tolist(), flag_col_idx=0, flags=drivers_flags)
		self.drivers_table.assign_on_tap_callback(0, self.driver_column_clicked)
		self.drivers_tab.content.content = self.drivers_table.list_view

		# CONSTRUCTORS
		# Add 1 to Rnd column for display purposes (model uses 0-based indexing)
		display_df = constructors_standings_df.copy()
		display_df['Rnd'] = display_df['Rnd'].apply(lambda x: x + 1 if pd.notna(x) else x)
		
		self.constructors_table = CustomDataTable(self.view, display_df.columns.tolist())
		self.constructors_table.update_table_data(display_df.values.tolist(), flag_col_idx=0, flags=team_flags)
		self.constructors_tab.content.content = self.constructors_table.list_view

		# RESULTS
		self.results_table = MultiDriverResultsTable(self.view)
		self.results_table.update_results(race_countries, driver_results)
		self.results_tab.content.content = self.results_table.list_view

		# Reset to drivers view
		self.tabs.selected_index = 0
		self.view.main_app.update()

	def _extract_text(self, control: ft.Control) -> str:
			if hasattr(control, "value"):
					return control.value
			if hasattr(control, "content"):
					return self._extract_text(control.content)
			if hasattr(control, "controls"):
					for child in control.controls:
							text = self._extract_text(child)
							if text:
									return text
			return ""

	def driver_column_clicked(self, e: ft.ControlEvent) -> None:
			driver_clicked = self._extract_text(e.control)
			if driver_clicked:
					self.view.controller.driver_page_controller.go_to_driver_page(driver_clicked)