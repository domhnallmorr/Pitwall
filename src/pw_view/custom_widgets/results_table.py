from __future__ import annotations
from typing import TYPE_CHECKING, List

import flet as ft

from pw_view.custom_widgets import custom_container

if TYPE_CHECKING:
	from pw_view.view import View


class DriverResultsTable:
	"""A small DataTable showing a driver's results across a season."""

	def __init__(self, view: View, row_height: int = 30) -> None:
		self.view = view

		self.data_table = ft.DataTable(
			columns=[],
			rows=[],
			data_row_max_height=row_height,
			data_row_min_height=row_height,
			# heading_row_color=ft.Colors.PRIMARY,
		)

		self.container = custom_container.CustomContainer(self.view, self.data_table, expand=False)
		self.list_view = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=False)
		self.list_view.controls.append(self.container)

	def update_results(self, race_countries: List[str], results: List[str]) -> None:
		"""Populate the table with results data."""
		if not (len(race_countries) == len(results)):
			raise ValueError("All input lists must be the same length")

		# Replace None with "-"
		results = [result if result is not None else "-" for result in results]

		columns = []
		for country in race_countries:
			flag_path = fr"{self.view.flags_small_path}\{country}.png"
			columns.append(ft.DataColumn(ft.Image(src=flag_path, width=30, height=20, fit=ft.ImageFit.CONTAIN)))
		self.data_table.columns = columns

		race_cells = [ft.DataCell(ft.Text(str(p))) for p in results]

		self.data_table.rows = [ft.DataRow(cells=race_cells)]