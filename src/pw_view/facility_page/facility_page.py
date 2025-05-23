from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

from pw_view.custom_widgets import custom_container
from pw_view.facility_page.upgrade_facility_page import UpgradeFacilitiesDialog

if TYPE_CHECKING:
	from pw_view.view import View

class FacilityPage(ft.Column):
	def __init__(self, view: View):

		self.view = view
		self.setup_widgets()

		contents = [
			ft.Text("Facilities", theme_style=self.view.page_header_style)
		]

		super().__init__(controls=contents, alignment=ft.MainAxisAlignment.START, expand=True)

	def update_page(self, data: dict) -> None:
		facility_rows = self.setup_facilities_progress_bars(data)

		facility_column = ft.Column(
			controls=facility_rows,
			expand=False,
			tight=True,
			spacing=20
		)

		facility_comparison_container = custom_container.CustomContainer(self.view, facility_column, expand=False)

		column = ft.Column(
			controls=[
				self.buttons_container,
				facility_comparison_container,
			],
			expand=False,
			tight=True
		)

		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				column
			],
			expand=True
		)

		self.controls = [
			ft.Text("Facilities", theme_style=self.view.page_header_style),
			self.background_stack
		]

		self.view.main_app.update()

	def setup_widgets(self) -> None:
		self.update_button = ft.TextButton("Update", icon="upgrade", on_click=self.update_facilities)

		self.buttons_row = ft.Row(
			controls=[
				self.update_button,
			],
			expand=False,
			tight=True
		)

		self.buttons_container = custom_container.CustomContainer(self.view, self.buttons_row, expand=False)

	def setup_facilities_progress_bars(self, data: dict) -> list[ft.Row]:
		facility_rows = []

		for team in data["facility_values"]:
			team_name = team[0]
			facility = team[1]
			
			row = ft.Row(
				controls=[
					ft.Text(f"{team_name}:", width=100),
					ft.Container(
						content=ft.ProgressBar(value=facility/100, width=500, expand=True, bar_height=28),
						height=28,
						expand=True
					)
				],
				expand=False,
			)
			facility_rows.append(row)

		return facility_rows
	
	def update_facilities(self, e: ft.ControlEvent) -> None:
		self.view.controller.facilities_controller.clicked_update_facilities()
		
	def disable_upgrade_button(self) -> None:
		self.update_button.disabled = True
		self.view.main_app.update()

	def enable_upgrade_button(self) -> None:
		self.update_button.disabled = False
		self.view.main_app.update()

	def open_upgrade_dialog(self, current_state: int) -> None:
		upgrade_dialog = UpgradeFacilitiesDialog(self.view.main_app, self.view, current_state)
		self.view.main_app.overlay.append(upgrade_dialog)
		upgrade_dialog.open = True
		self.view.main_app.update()
