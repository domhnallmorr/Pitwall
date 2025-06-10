from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable, Any
import os

import flet as ft
from pw_view.custom_widgets import custom_container

if TYPE_CHECKING:
	from pw_view.view import View

class CustomDataTable:
	def __init__(self, view: View, column_names: list[str], row_height: int=30):
		self.view = view
		self.column_names = column_names

		columns = []
		for idx, col in enumerate(column_names):
			column_content = custom_container.HeaderContainer(self.view, col)
			columns.append(ft.DataColumn(column_content))

		self.data_table = ft.DataTable(
                        columns=columns,
						data_row_max_height=row_height,
						data_row_min_height=row_height,
						heading_row_color=ft.Colors.PRIMARY
                                                )
		
		self.container = custom_container.CustomContainer(self.view, self.data_table, expand=False)
		self.list_view = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=False)
		self.list_view.controls.append(self.container)


	def update_table_data(self, data: list[list[str]], flag_col_idx: Optional[int]=None, flags: Optional[list[str]]=None,
					   team_logo_col_idx: Optional[int]=None, team_logos: Optional[list[str]]=None,
					   sponsor_logo_col_idx: Optional[int]=None, sponsor_logos: Optional[list[str]]=None) -> None:
		rows = []

		for row_idx, row in enumerate(data):
			if row_idx % 2 == 0:
				bg_color = None
			else:
				bg_color = ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY)

			cells = []
			for col_idx, cell_text in enumerate(row):
				if col_idx == flag_col_idx and flags is not None:
					cells.append(self.gen_flag_cell(cell_text, flags[row_idx]))
				elif col_idx == team_logo_col_idx and team_logos is not None:
					cells.append(self.gen_team_logo_cell(cell_text, team_logos[row_idx]))
				elif col_idx == sponsor_logo_col_idx and sponsor_logos is not None:
					cells.append(self.gen_sponsor_logo_cell(cell_text, sponsor_logos[row_idx]))
				else:
					cells.append(ft.DataCell(ft.Text(cell_text)))

			rows.append(ft.DataRow(cells=cells, color=bg_color))

		self.data_table.rows = rows

	def gen_flag_cell(self, text: str, flag: str) -> ft.DataCell:
		flag_path = fr"{self.view.flags_small_path}\{flag}.png"

		cell = ft.DataCell(
                    ft.Row(
                        controls=[
                            ft.Image(
                                src=flag_path,
                                width=30,
                                height=20,
                                fit=ft.ImageFit.CONTAIN
                            ),
                            ft.Text(text)
                        ],
						)
					)
		
		return cell

	def gen_team_logo_cell(self, text: str, name: str) -> ft.DataCell:
		logo_path = fr"{self.view.team_logos_path}\{name.lower()}.png"

		cell = ft.DataCell(
                    ft.Row(
                        controls=[
                            ft.Image(
                                src=logo_path,
                                width=30,
                                height=30,
                                fit=ft.ImageFit.CONTAIN
                            ),
                            ft.Text(text)
                        ],
						)
					)
		
		return cell
	
	def gen_sponsor_logo_cell(self, text: str, name: str) -> ft.DataCell:
		if name is None:
			return ft.DataCell(ft.Text(text))

		logo_path = fr"{self.view.sponsor_logos_path}\{name.lower()}.png"

		cell = ft.DataCell(
                    ft.Row(
                        controls=[
                            ft.Image(
                                src=logo_path,
                                width=30,
                                height=30,
                                fit=ft.ImageFit.CONTAIN
                            ),
                            ft.Text(text)
						],
						)
					)
		
		return cell

	def assign_on_tap_callback(self, column_index: int, callback: Callable[[Any], Any]) -> None:
		"""Assigns an `on_tap` event to all cells in a specific column."""
		for row in self.data_table.rows:
			cell = row.cells[column_index]  # Get the specific column cell
			cell.on_tap = callback  # Assign the callback function