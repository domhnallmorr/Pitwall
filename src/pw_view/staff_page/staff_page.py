from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

from pw_view.custom_widgets import custom_container
from pw_view.staff_page import hire_workforce_modal, staff_details_container
from pw_view.staff_page.staff_details_container import StaffDetailsContainer
from pw_view.custom_widgets import rating_widget
from pw_model.pw_model_enums import StaffRoles
from pw_controller.staff_page.staff_page_data import StaffPageData

if TYPE_CHECKING:
	from pw_view.view import View

class StaffPage(ft.Column):
	def __init__(self, view: View):
		self.view = view
		self.setup_workforce_buttons()
		self.setup_staff_containers()
		self.setup_tabs()

		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				self.tabs
			],
			expand=True
		)

		super().__init__(
			controls=[
				ft.Text("Staff", theme_style=self.view.page_header_style),
				self.background_stack
			],
			alignment=ft.MainAxisAlignment.START,
			expand=True
		)

	def setup_workforce_buttons(self) -> None:
		self.hire_workforce_button = ft.TextButton(
			"Hire", 
			icon="upgrade", 
			on_click=self.hire_workforce
		)

		self.workforce_buttons_row = ft.Row(
			controls=[self.hire_workforce_button],
			expand=False,
			tight=True
		)

		self.workforce_buttons_container = custom_container.CustomContainer(
			self.view, 
			self.workforce_buttons_row, 
			expand=False
		)

	def setup_staff_containers(self) -> None:
		# Drivers
		self.driver1_container = StaffDetailsContainer(self.view, StaffRoles.DRIVER1)
		self.driver2_container = StaffDetailsContainer(self.view, StaffRoles.DRIVER2)
		self.driver_row = ft.Row(
			controls=[
				self.driver1_container.container,
				self.driver2_container.container
			],
			expand=False,
			alignment=ft.MainAxisAlignment.CENTER  # Center the containers horizontally
		)

		# Management
		self.technical_director_container = StaffDetailsContainer(self.view, StaffRoles.TECHNICAL_DIRECTOR)
		self.commercial_manager_container = StaffDetailsContainer(self.view, StaffRoles.COMMERCIAL_MANAGER)
		self.manager_row = ft.Row(
			controls=[
				self.technical_director_container.container,
				self.commercial_manager_container.container,
			],
			expand=False,
			alignment=ft.MainAxisAlignment.CENTER  # Center the containers horizontally
		)

	def setup_tabs(self) -> None:
		self.drivers_tab = ft.Tab(
			text="Drivers",
			icon=ft.Icons.SPORTS_MOTORSPORTS,
			content=ft.Container(
				content=ft.Column(
					[self.driver_row],
					expand=False,
					horizontal_alignment=ft.CrossAxisAlignment.CENTER  # Center the row vertically
				),
				expand=False,
				alignment=ft.alignment.top_center
			)
		)
		
		self.management_tab = ft.Tab(
			text="Management",
			icon=ft.Icons.WORK,
			content=ft.Container(
				content=ft.Column(
					[self.manager_row],
					expand=False,
					horizontal_alignment=ft.CrossAxisAlignment.CENTER  # Center the row vertically
				),
				expand=False,
				alignment=ft.alignment.top_center
			)
		)

		self.workforce_tab = ft.Tab(
			text="Workforce",
			icon=ft.Icons.PEOPLE,
			content=ft.Container(
				expand=False,
				alignment=ft.alignment.top_center
			)
		)

		self.tabs = ft.Tabs(
			selected_index=0,
			animation_duration=300,
			tabs=[
				self.drivers_tab,
				self.management_tab,
				self.workforce_tab
			],
			expand=True
		)

	def update_page(self, data: StaffPageData, new_season: bool=False) -> None:
		if new_season is True:
			self.enable_hire_workforce_btn()

		# Update staff containers
		self.driver1_container.update(data.drivers[0], data.staff_player_requires.player_requiring_driver1)
		self.driver2_container.update(data.drivers[1], data.staff_player_requires.player_requiring_driver2)
		self.technical_director_container.update(data.technical_director, data.staff_player_requires.player_requiring_technical_director)
		self.commercial_manager_container.update(data.commercial_manager, data.staff_player_requires.player_requiring_commercial_manager)

		# Update workforce tab content
		workforce_content = ft.Column(
			controls=[
				self.setup_staff_value_progress_bars(data.staff_values),
				self.workforce_buttons_container
			],
			expand=False,
			spacing=20
		)
		self.workforce_tab.content.content = workforce_content

		self.view.main_app.update()

	def setup_staff_value_progress_bars(self, staff_values: list[tuple[str, int]]) -> ft.Container:
		staff_value_rows = [custom_container.HeaderContainer(self.view, f"Number of Staff")]
		
		max_staff = max(v[1] for v in staff_values)

		for team in staff_values:
			team_name = team[0]
			staff_value = team[1]
			
			row = ft.Row(
				controls=[
					ft.Text(f"{team_name} ({staff_value}):", width=100),
					ft.Container(
						content=ft.ProgressBar(value=staff_value/max_staff, width=500, expand=True, bar_height=28),
						height=28,
						expand=True
					)
				],
				expand=True,
			)
			staff_value_rows.append(row)

		column = ft.Column(
			controls=staff_value_rows,
			expand=False,
			spacing=20
		)

		return custom_container.CustomContainer(self.view, column, expand=False)

	def hire_workforce(self, e: ft.ControlEvent) -> None:
		self.view.controller.staff_hire_controller.hire_workforce()

	def open_workforce_dialog(self, current_workforce: int) -> None:
		workforce_dialog = hire_workforce_modal.WorkforceDialog(self.view.main_app, self.view, initial_value=current_workforce)
		self.view.main_app.overlay.append(workforce_dialog)
		workforce_dialog.open = True
		self.view.main_app.update()

	def disable_hire_workforce_btn(self) -> None:
		self.hire_workforce_button.disabled = True

	def enable_hire_workforce_btn(self) -> None:
		self.hire_workforce_button.disabled = False
