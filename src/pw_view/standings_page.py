from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft
import pandas as pd

from pw_view.custom_widgets import custom_container
if TYPE_CHECKING:
	from pw_view.view import View

class StandingsPage(ft.Column):
	def __init__(self, view: View):

		self.view = view
		self.setup_standings_tables()
		self.setup_buttons_row()

		contents = [
			ft.Text("Standings", theme_style=self.view.page_header_style),
			self.buttons_row,
			self.drivers_table
		]

		super().__init__(controls=contents, alignment=ft.MainAxisAlignment.START, expand=True)

	def reset_tab_buttons(self) -> None:
		# When a button is clicked to view a different tab, reset all buttons style
		self.drivers_btn.style = None
		self.contructors_btn.style = None


	def setup_standings_tables(self) -> None:

		self.drivers_table = ft.DataTable(
			columns=[
                ft.DataColumn(ft.Text("Driver")),
                ft.DataColumn(ft.Text("Team")),
                ft.DataColumn(ft.Text("Points"), numeric=True),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Jacques Villeneuve")),
                        ft.DataCell(ft.Text("Williams")),
                        ft.DataCell(ft.Text("0")),
                    ],
                ),
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Jack")),
                        ft.DataCell(ft.Text("Brown")),
                        ft.DataCell(ft.Text("19")),
                    ],
                ),
            ],
        )

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

	def update_standings(self, drivers_standings_df: pd.DataFrame, constructors_standings_df: pd.DataFrame) -> None:
	
		# DRIVERS
		columns = []
		for col in drivers_standings_df.columns:
			column_content = custom_container.HeaderContainer(self.view, col)
			columns.append(ft.DataColumn(column_content))

		data = drivers_standings_df.values.tolist()
		rows = []

		for row in data:
			cells = []
			for cell in row:
				cells.append(ft.DataCell(ft.Text(cell)))

			rows.append(ft.DataRow(cells=cells))

		self.drivers_table = ft.DataTable(columns=columns, rows=rows, data_row_max_height=30, data_row_min_height=30,
									heading_row_color=ft.Colors.PRIMARY)

		self.scrollable_drivers_table = ft.ListView(expand=1, auto_scroll=True)
		self.scrollable_drivers_table.controls.append(custom_container.CustomContainer(self.view, self.drivers_table, expand=False))

		# CONSTRUCTORS
		 
		columns = []
		for col in constructors_standings_df.columns:
			column_content = custom_container.HeaderContainer(self.view, col)
			columns.append(ft.DataColumn(column_content))

		data = constructors_standings_df.values.tolist()
		rows = []

		for row in data:
			cells = []
			for idx, cell in enumerate(row):
				if constructors_standings_df.columns.values.tolist()[idx] == "Rnd":
					if cell is not None:
						cell += 1 # best result rnd is zero indexed in the dataframe
				cells.append(ft.DataCell(ft.Text(cell)))

			rows.append(ft.DataRow(cells=cells))

		self.constructors_table = ft.DataTable(columns=columns, rows=rows, data_row_max_height=30, data_row_min_height=30,
										 heading_row_color=ft.Colors.PRIMARY)		

		self.scrollable_constructors_table = ft.Column(
			controls=[self.constructors_table],
			# height=700,
			# expand=True,  # Set height to show scrollbar if content exceeds this height
			scroll=ft.ScrollMode.AUTO  # Automatically show scrollbar when needed
		)

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
			container = custom_container.CustomContainer(self.view, self.scrollable_drivers_table, expand=False)
		elif mode == "constructors":
			container = custom_container.CustomContainer(self.view, self.scrollable_constructors_table, expand=False)

		column = ft.Column(
			controls=[self.buttons_container, container],
			expand=False,
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
