from __future__ import annotations
from typing import TYPE_CHECKING, List, Callable, Any

import flet as ft

from pw_view.custom_widgets import custom_container

if TYPE_CHECKING:
	from pw_view.view import View


class MultiDriverResultsTable:
	"""A DataTable showing results for multiple drivers across a season."""

	def __init__(self, view: View, row_height: int = 30) -> None:
		self.view = view

		self.data_table = ft.DataTable(
			columns=[],
			rows=[],
			data_row_max_height=row_height,
			data_row_min_height=row_height,
		)

		self.container = custom_container.CustomContainer(self.view, self.data_table, expand=False)
		self.list_view = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=False)
		self.list_view.controls.append(self.container)

	def _color_for_result(self, result: str | int | None) -> str | None:
		"""Return a hex color for podium positions, else None."""
		if result is None:
			return None, None
		try:
			r = int(result)
		except (ValueError, TypeError):
			return None, None
		if r == 1:
			return "#FFD700", "#000000"  # gold
		if r == 2:
			return "#C0C0C0", "#000000"  # silver
		if r == 3:
			return "#CD7F32", "#000000"  # bronze
		if r <= 6:
			return "#0E8501", None
		return None, None

	def _result_cell(self, value: str | int | None) -> ft.DataCell:
		"""Create a DataCell with conditional background color."""
		text = "-" if value is None else str(value)
		bg, fg = self._color_for_result(value)

		content = ft.Container(
			content=ft.Text(text, text_align=ft.TextAlign.CENTER, color=fg),
			bgcolor=bg,                 # None leaves default background
			alignment=ft.alignment.center,
			padding=5,
			border_radius=6,
		)
		return ft.DataCell(content)

	def update_results(self, race_countries: list[str], drivers_results: list[list[str]]) -> None:
		"""Populate the table with multiple drivers' results."""
		columns = [ft.DataColumn(ft.Text("Driver"))]
		for country in race_countries:
			flag_path = fr"{self.view.flags_small_path}\\{country}.png"
			columns.append(ft.DataColumn(ft.Image(src=flag_path, width=30, height=20, fit=ft.ImageFit.CONTAIN)))
		self.data_table.columns = columns

		rows = []
		for row_idx, row in enumerate(drivers_results):
			if len(row) != len(race_countries) + 1:
				raise ValueError("Each driver's results must match the number of races plus the driver name")
			driver_name, *results = row

			cells = [ft.DataCell(ft.Text(driver_name))]
			# use colored cells for each race result
			for res in results:
				cells.append(self._result_cell(res))

			# keep your alternating row shading (shows on non-podium cells)
			bg_color = None if row_idx % 2 == 0 else ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY)
			rows.append(ft.DataRow(cells=cells, color=bg_color))

		self.data_table.rows = rows
		self.assign_on_tap_callback(0, self.driver_column_clicked)
		
	def driver_column_clicked(self, e: ft.ControlEvent) -> None:
			driver_clicked = e.control.content.value
			self.view.controller.driver_page_controller.go_to_driver_page(driver_clicked)

	def assign_on_tap_callback(self, column_index: int, callback: Callable[[Any], Any]) -> None:
		"""Assigns an `on_tap` event to all cells in a specific column."""
		for row in self.data_table.rows:
			cell = row.cells[column_index]  # Get the specific column cell
			cell.on_tap = callback  # Assign the callback function