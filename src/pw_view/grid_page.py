from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft
import pandas as pd
from pw_view.custom_widgets import custom_container
from pw_view.custom_widgets.custom_datatable import CustomDataTable

if TYPE_CHECKING:
	from pw_view.view import View

class GridPage(ft.Column): # type: ignore
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

		self.grid_this_year_table = CustomDataTable(self.view, grid_this_year_df.columns.tolist())
		self.grid_this_year_table.update_table_data(grid_this_year_df.values.tolist())

		# NEXT YEAR
		self.grid_next_year_table = CustomDataTable(self.view, grid_next_year_announced_df.columns.tolist())
		self.grid_next_year_table.update_table_data(grid_next_year_announced_df.values.tolist())
		
	def change_display(self, e: ft.ControlEvent) -> None:
		self.reset_tab_buttons()

		if e is None:
			mode = "current"
		else:
			mode = e.control.data

		if mode == "current":
			self.current_year_btn.style = self.view.clicked_button_style
			container = self.grid_this_year_table.list_view
		elif mode == "next":
			self.next_year_btn.style = self.view.clicked_button_style
			container = self.grid_next_year_table.list_view

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