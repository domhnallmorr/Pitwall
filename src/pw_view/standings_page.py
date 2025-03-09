from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft
import pandas as pd

from pw_view.custom_widgets import custom_container
from pw_view.custom_widgets.custom_datatable import CustomDataTable

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
			content=ft.Container(
				expand=False,
				alignment=ft.alignment.top_center
			)
		)
		
		self.constructors_tab = ft.Tab(
			text="Constructors",
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
				self.constructors_tab
			],
			expand=True
		)

	def update_standings(self, drivers_standings_df: pd.DataFrame, constructors_standings_df: pd.DataFrame,
					  drivers_flags: list[str], team_flags: list[str]) -> None:
		# DRIVERS
		self.drivers_table = CustomDataTable(self.view, drivers_standings_df.columns.tolist())
		self.drivers_table.update_table_data(drivers_standings_df.values.tolist(), flag_col_idx=0, flags=drivers_flags)
		self.drivers_tab.content.content = self.drivers_table.list_view

		# CONSTRUCTORS
		# Add 1 to Rnd column for display purposes (model uses 0-based indexing)
		display_df = constructors_standings_df.copy()
		display_df['Rnd'] = display_df['Rnd'].apply(lambda x: x + 1 if pd.notna(x) else x)
		
		self.constructors_table = CustomDataTable(self.view, display_df.columns.tolist())
		self.constructors_table.update_table_data(display_df.values.tolist(), flag_col_idx=0, flags=team_flags)
		self.constructors_tab.content.content = self.constructors_table.list_view

		# Reset to drivers view
		self.tabs.selected_index = 0
		self.view.main_app.update()
