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
		self.current_calendar_data = None  # Store the full calendar data

		self.header_text = ft.Text("Calendar", theme_style=self.view.page_header_style)
		
		# Define a fixed width for all filter buttons
		button_width = 120
		
		# Create filter buttons wrapped in containers
		self.filter_buttons = ft.Row(
			controls=[
				ft.Container(
					content=ft.TextButton(
						text="All",
						icon="FILTER_ALT",
						style=ft.ButtonStyle(color=ft.Colors.PRIMARY),
						on_click=lambda _: self.filter_calendar("All"),
						width=button_width
					),
					border=ft.border.only(bottom=ft.border.BorderSide(2, ft.Colors.PRIMARY)),
					data="active"
				),
				ft.Container(
					content=ft.TextButton(
						text="Race",
						style=ft.ButtonStyle(color=ft.Colors.WHITE70),
						on_click=lambda _: self.filter_calendar("Race"),
						width=button_width
					),
					border=None,
					data="inactive"
				),
				ft.Container(
					content=ft.TextButton(
						text="Testing",
						style=ft.ButtonStyle(color=ft.Colors.WHITE70),
						on_click=lambda _: self.filter_calendar("Testing"),
						width=button_width
					),
					border=None,
					data="inactive"
				),
			],
			alignment=ft.MainAxisAlignment.START
		)

		super().__init__(
			controls=[self.header_text],
			expand=1
		)

	def update_page(self, calendar: pd.DataFrame) -> None:
		self.current_calendar_data = calendar.copy(deep=True)
		self.filter_calendar("All")  # Initial display with all sessions

	def filter_calendar(self, filter_type: str) -> None:
		# Update button styles and icons
		for container in self.filter_buttons.controls:
			button = container.content
			if button.text == filter_type:
				button.style.color = ft.Colors.PRIMARY
				button.icon = "FILTER_ALT"
				container.border = ft.border.only(bottom=ft.border.BorderSide(2, ft.Colors.PRIMARY))
				container.data = "active"
			else:
				button.style.color = ft.Colors.WHITE70
				button.icon = None
				container.border = None
				container.data = "inactive"

		# Filter the data
		filtered_data = self.current_calendar_data.copy(deep=True)
		if filter_type != "All":
			filtered_data = filtered_data[filtered_data["SessionType"] == filter_type]

		# Add round numbers, using "-" for testing sessions
		race_counter = 1
		round_numbers = []
		for session_type in filtered_data["SessionType"]:
			if session_type == "Race":
				round_numbers.append(race_counter)
				race_counter += 1
			else:
				round_numbers.append("-")
		
		filtered_data.insert(0, "#", round_numbers)

		# Update table
		column_names = filtered_data.columns.values.tolist()
		self.calendar_table = CustomDataTable(self.view, column_names)
		flags = filtered_data["Country"].values.tolist()
		self.calendar_table.update_table_data(filtered_data.values.tolist(), flag_col_idx=3, flags=flags)
		self.calendar_table.assign_on_tap_callback(2, self.track_column_clicked)

		# Create content column with filter buttons and table
		content_column = ft.Column(
			controls=[
				ft.Container(  # Added container for padding
					content=self.filter_buttons,
					padding=ft.padding.only(left=20)  # Add left padding
				),
				self.calendar_table.list_view
			],
			expand=True
		)

		# Update layout
		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				content_column
			],
			expand=True
		)

		self.controls = [
			self.header_text,
			self.background_stack
		]
		
		self.view.main_app.update()

	def track_column_clicked(self, e: ft.ControlEvent) -> None:
		track_clicked = e.control.content.value
		self.track_page_controller.go_to_track_page(track_clicked)
