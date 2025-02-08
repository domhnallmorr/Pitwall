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

class StaffPage(ft.Column): # type: ignore
	def __init__(self, view: View):

		self.view = view
		self.setup_buttons_row()
		self.setup_driver_containers()
		self.setup_manager_containers()

		super().__init__(expand=1, controls=[])
		self.display_drivers(None)

	def reset_tab_buttons(self) -> None:
		# When a button is clicked to view a different tab, reset all buttons style

		self.drivers_btn.style = None
		self.manager_button.style = None
		self.workforce_btn.style = None

	def setup_buttons_row(self) -> None:
		self.manager_button = ft.TextButton("Management", on_click=self.display_managers,)

		self.drivers_btn = ft.TextButton("Drivers", on_click=self.display_drivers)
		self.workforce_btn = ft.TextButton("Workforce", on_click=self.display_workforce)

		self.buttons_row = ft.Row(
			controls=[
				self.drivers_btn,
				self.manager_button,
				self.workforce_btn,
			],
			expand=False,
			tight=True
		)

		self.buttons_container = custom_container.CustomContainer(self.view, self.buttons_row, expand=False)

		self.hire_workforce_button = ft.TextButton("Hire", icon="upgrade", on_click=self.hire_workforce)

		self.workforce_buttons_row = ft.Row(
			controls=[
				self.hire_workforce_button,
			],
			expand=False,
			tight=True
		)

		self.workforce_buttons_container = custom_container.CustomContainer(self.view, self.workforce_buttons_row, expand=False)

	def setup_driver_containers(self) -> None:		
		self.driver1_container = StaffDetailsContainer(self.view, StaffRoles.DRIVER1)
		self.driver2_container = StaffDetailsContainer(self.view, StaffRoles.DRIVER2)

		self.driver_row = ft.Row(
			# expand=1,
			controls=[
				self.driver1_container.container,
				self.driver2_container.container
			]
		)

	def setup_manager_containers(self) -> None:
		self.technical_director_container = StaffDetailsContainer(self.view, StaffRoles.TECHNICAL_DIRECTOR)
		self.commercial_manager_container = StaffDetailsContainer(self.view, StaffRoles.COMMERCIAL_MANAGER)

		self.manager_row = ft.Row(
			controls = [
				self.technical_director_container.container,
				self.commercial_manager_container.container,
			]
		)

	def update_page(self, data: StaffPageData, new_season: bool=False) -> None:
		if new_season is True:
			self.enable_hire_workforce_btn()

		self.driver1_container.update(data.drivers[0], data.staff_player_requies.player_requiring_driver1)
		self.driver2_container.update(data.drivers[1], data.staff_player_requies.player_requiring_driver2)
		self.technical_director_container.update(data.technical_director, data.staff_player_requies.player_requiring_technical_director)
		self.commercial_manager_container.update(data.commercial_manager, data.staff_player_requies.player_requiring_commercial_manager)

		self.workforce_container = self.setup_staff_value_progress_bars(data.staff_values)

		self.view.main_app.update()

	# TODO delete, moved to staff_details_container
	def replace_driver(self, e: ft.ControlEvent) -> None:
		self.view.controller.staff_hire_controller.launch_replace_staff(e.control.data)

	def display_drivers(self, e: ft.ControlEvent) -> None:
		self.reset_tab_buttons()
		self.drivers_btn.style = self.view.clicked_button_style

		page_controls = [self.buttons_container, self.driver_row]

		column = ft.Column(
			controls=page_controls,
			expand=False,
			spacing=20
		)

		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				column,
			],
			expand=True,
		)

		self.controls = [
			ft.Text("Staff", theme_style=self.view.page_header_style),
			self.background_stack
		]
		
		self.view.main_app.update()

	def display_managers(self, e: ft.ControlEvent) -> None:
		self.reset_tab_buttons()
		self.manager_button.style = self.view.clicked_button_style

		page_controls = [self.buttons_container, self.manager_row]

		column = ft.Column(
			controls=page_controls,
			expand=False,
			spacing=20
		)

		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				column,
			],
			expand=True
		)

		self.controls = [
			ft.Text("Staff", theme_style=self.view.page_header_style),
			self.background_stack
		]

		self.view.main_app.update()

	def display_workforce(self, e: ft.ControlEvent) -> None:
		self.reset_tab_buttons()
		self.workforce_btn.style = self.view.clicked_button_style

		page_controls = [self.buttons_container, self.workforce_container, self.workforce_buttons_container]

		column = ft.Column(
			controls=page_controls,
			expand=False,
			spacing=20
		)

		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				column,
			],
			expand=True
		)

		self.controls = [
			ft.Text("Staff", theme_style=self.view.page_header_style),
			self.background_stack
		]

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
			expand=True,
			spacing=20
		)

		workforce_container = custom_container.CustomContainer(self.view, column, expand=False)

		return workforce_container
	
	def hire_workforce(self, e: ft.ControlEvent) -> None:
		self.view.controller.staff_hire_controller.hire_workforce()

	def open_workforce_dialog(self, current_workforce: int) -> None:
		workforce_dialog = hire_workforce_modal.WorkforceDialog(self.view.main_app, self.view, initial_value=current_workforce)

		# Adding elements to page
		self.view.main_app.overlay.append(workforce_dialog)

		workforce_dialog.open = True
		self.view.main_app.update()

	def disable_hire_workforce_btn(self) -> None:
		self.hire_workforce_button.disabled = True

	def enable_hire_workforce_btn(self) -> None:
		self.hire_workforce_button.disabled = False
