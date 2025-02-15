from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft
import pandas as pd
from pw_view.custom_widgets import custom_container
from pw_view.custom_widgets.custom_datatable import CustomDataTable

if TYPE_CHECKING:
	from pw_view.view import View

class CalendarPage(ft.Column): # type: ignore
	def __init__(self, view: View):

		self.view = view
		self.track_page_controller = view.controller.track_page_controller

		self.header_text = ft.Text("Calendar", theme_style=self.view.page_header_style)
		contents = [
			self.header_text
		]

		super().__init__(controls=contents, expand=1)

	def update_page(self, calendar: pd.DataFrame) -> None:
		# Add a Round column based on index, maybe this should be added to the model

		calendar.insert(0, "#", calendar.index + 1)

		column_names = calendar.columns.values.tolist()

		self.calendar_table = CustomDataTable(self.view, column_names)
		flags = calendar["Country"].values.tolist()
		self.calendar_table.update_table_data(calendar.values.tolist(), flag_col_idx=3, flags=flags)
		self.calendar_table.assign_on_tap_callback(2, self.track_column_clicked)

		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				self.calendar_table.list_view
			],
			expand=True
		)

		contents = [
			self.header_text,
			self.background_stack
		]

		self.controls = contents
		self.view.main_app.update()

	def track_column_clicked(self, e: ft.ControlEvent) -> None:
		track_clicked = e.control.content.value
		self.track_page_controller.go_to_track_page(track_clicked)