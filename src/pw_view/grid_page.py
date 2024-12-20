from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft
import pandas as pd
from pw_view.custom_widgets import custom_container

if TYPE_CHECKING:
	from pw_view.view import View

class GridPage(ft.Column):
	def __init__(self, view: View):

		self.view = view

		self.setup_buttons_row()
		
		contents = [
			ft.Text("Grid", theme_style=self.view.page_header_style),
		]

		super().__init__(controls=contents, alignment=ft.MainAxisAlignment.START, expand=True)

	def reset_tab_buttons(self) -> None:
		# When a button is clicked to view a different tab, reset all buttons style
		self.current_year_btn.style = None
		self.next_year_btn.style = None

	def setup_buttons_row(self) -> None:
		self.current_year_btn = ft.TextButton("1998", on_click=self.change_display, data="current")
		self.next_year_btn = ft.TextButton("1999", on_click=self.change_display, data="next")

		self.buttons_row = ft.Row(
			controls=[
				self.current_year_btn,
				self.next_year_btn,
			],
			expand=False,
			tight=True
		)

		self.buttons_container = custom_container.CustomContainer(self.view, self.buttons_row, expand=False)
	
	def update_page(self, year: int, grid_this_year_df: pd.Dataframe, grid_next_year_announced_df: pd.DataFrame) -> None:
		# THIS YEAR
		self.current_year_btn.text = str(year)
		self.next_year_btn.text = str(year + 1)

		columns = []
		for col in grid_this_year_df.columns:
			column_content = custom_container.HeaderContainer(self.view, col)
			columns.append(ft.DataColumn(column_content))

		df_data = grid_this_year_df.values.tolist()
		rows = []

		for row in df_data:
			cells = []
			for cell in row:
				cells.append(ft.DataCell(ft.Text(cell)))

			rows.append(ft.DataRow(cells=cells))

		self.grid_this_year_table = ft.DataTable(columns=columns, rows=rows, data_row_max_height=30, data_row_min_height=30,
										   heading_row_color=ft.Colors.PRIMARY)

		self.scrollable_grid_this_year_table = ft.Column(
			controls=[self.grid_this_year_table],
			# height=self.view.main_app.window.height - self.view.vscroll_buffer,
			# expand=True,  # Set height to show scrollbar if content exceeds this height
			scroll=ft.ScrollMode.AUTO  # Automatically show scrollbar when needed
		)

		# NEXT YEAR
		columns = []
		for col in grid_next_year_announced_df.columns:
			column_content = custom_container.HeaderContainer(self.view, col)
			columns.append(ft.DataColumn(column_content))

		df_data = grid_next_year_announced_df.values.tolist()
		rows = []

		for row in df_data:
			cells = []
			for cell in row:
				cells.append(ft.DataCell(ft.Text(cell)))

			rows.append(ft.DataRow(cells=cells))

		self.grid_next_year_table = ft.DataTable(columns=columns, rows=rows, data_row_max_height=30, data_row_min_height=30,
										   heading_row_color=ft.Colors.PRIMARY)

		self.scrollable_grid_next_year_table = ft.Column(
			controls=[self.grid_next_year_table],
			# height=self.view.main_app.window.height - self.view.vscroll_buffer,
			# expand=False,  # Set height to show scrollbar if content exceeds this height
			scroll=ft.ScrollMode.AUTO  # Automatically show scrollbar when needed
		)


	def change_display(self, e: ft.ControlEvent) -> None:
		self.reset_tab_buttons()

		if e is None:
			mode = "current"
		else:
			mode = e.control.data

		if mode == "current":
			self.current_year_btn.style = self.view.clicked_button_style
			container = custom_container.CustomContainer(self.view, self.scrollable_grid_this_year_table, expand=False)
		elif mode == "next":
			self.next_year_btn.style = self.view.clicked_button_style
			container = custom_container.CustomContainer(self.view, self.scrollable_grid_next_year_table, expand=False)

		column = ft.Column(
			controls=[self.buttons_container, container],
			expand=False,
			spacing=10
		)

		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				column
			],
			expand=True
		)

		page_controls = [
			ft.Text("Grid", theme_style=self.view.page_header_style),
			self.background_stack
		]

		self.controls = page_controls
		self.view.main_app.update()