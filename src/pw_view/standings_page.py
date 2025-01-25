from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft
import pandas as pd

from pw_view.custom_widgets import custom_container
from pw_view.custom_widgets.custom_datatable import CustomDataTable

if TYPE_CHECKING:
	from pw_view.view import View

class StandingsPage(ft.Column): # type: ignore
	def __init__(self, view: View):

		self.view = view
		self.setup_buttons_row()

		contents = [
			ft.Text("Standings", theme_style=self.view.page_header_style),
			self.buttons_row,
		]

		super().__init__(controls=contents, alignment=ft.MainAxisAlignment.START, expand=True)

	def reset_tab_buttons(self) -> None:
		# When a button is clicked to view a different tab, reset all buttons style
		self.drivers_btn.style = None
		self.contructors_btn.style = None

	def setup_buttons_row(self) -> None:
		self.drivers_btn = ft.TextButton("Drivers", on_click=self.display_drivers, expand=False)
		self.contructors_btn = ft.TextButton("Constructors", on_click=self.display_constructors, expand=False)

		self.buttons_row = ft.Row(
			controls=[
				self.drivers_btn,
				self.contructors_btn
			],
			expand=False,
			tight=True
		)

		self.buttons_container = custom_container.CustomContainer(self.view, self.buttons_row, expand=False)

	def update_standings(self, drivers_standings_df: pd.DataFrame, constructors_standings_df: pd.DataFrame,
					  drivers_flags: list[str], team_flags: list[str]) -> None:
	
		# DRIVERS
		self.drivers_table = CustomDataTable(self.view, drivers_standings_df.columns.tolist())
		self.drivers_table.update_table_data(drivers_standings_df.values.tolist(), flag_col_idx=0, flags=drivers_flags)

		# CONSTRUCTORS
		self.constructors_table = CustomDataTable(self.view, constructors_standings_df.columns.tolist())
		self.constructors_table.update_table_data(constructors_standings_df.values.tolist(), flag_col_idx=0, flags=team_flags)		 

		self.display_drivers(None)
		self.view.main_app.update()


	def display_drivers(self, e: ft.ControlEvent) -> None:
		self.reset_tab_buttons()
		self.drivers_btn.style = self.view.clicked_button_style
		self.arrange_controls("drivers")
		
	def display_constructors(self, e: ft.ControlEvent) -> None:
		self.reset_tab_buttons()
		self.contructors_btn.style = self.view.clicked_button_style
		self.arrange_controls("constructors")

	def arrange_controls(self, mode: str) -> None:
		assert mode in ["drivers", "constructors"]

		if mode == "drivers":
			container = self.drivers_table.list_view
		elif mode == "constructors":
			container = self.constructors_table.list_view

		column = ft.Column(
			controls=[self.buttons_container, container],
			expand=True,
			spacing=20
		)

		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				column
			],
			expand=True
		)

		page_controls = [
			ft.Text("Standings", theme_style=self.view.page_header_style),
			self.background_stack
		]

		self.controls = page_controls
		self.view.main_app.update()
