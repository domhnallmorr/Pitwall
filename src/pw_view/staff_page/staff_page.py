from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

from pw_view.custom_widgets import custom_container
from pw_view.staff_page import hire_workforce_modal
from pw_view.custom_widgets import rating_widget
from pw_model.pw_model_enums import StaffRoles

if TYPE_CHECKING:
	from pw_view.view import View

class StaffPage(ft.Column):
	def __init__(self, view: View):

		self.view = view
		self.setup_buttons_row()
		self.setup_widgets()
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

	def setup_widgets(self) -> None:
		self.driver_name_texts = [ft.Text(f"Driver1"), ft.Text(f"Driver2")]
		self.driver_age_texts = [ft.Text(f"25"), ft.Text(f"32")]
		self.driver_country_texts = [ft.Text(f"UK"), ft.Text(f"USA")]

		self.driver_salary_texts = [ft.Text(f"0"), ft.Text(f"0")]
		self.driver_contract_length_texts = [ft.Text(f"2"), ft.Text(f"3")]
		self.driver_contract_status_texts = [ft.Text(f"Contracted"), ft.Text(f"Contracted")]

		self.driver_ability_widgets = [rating_widget.RatingWidget("Ability:"), rating_widget.RatingWidget("Ability:")]

		self.staff_replace_buttons = [
			ft.TextButton("Replace", disabled=True, icon="find_replace", on_click=self.replace_driver, data=StaffRoles.DRIVER1),
			ft.TextButton("Replace", disabled=True, icon="find_replace", on_click=self.replace_driver, data=StaffRoles.DRIVER2),
			ft.TextButton("Replace", disabled=True, icon="find_replace", on_click=self.replace_driver, data=StaffRoles.TECHNICAL_DIRECTOR),
			ft.TextButton("Replace", disabled=True, icon="find_replace", on_click=self.replace_driver, data=StaffRoles.COMMERCIAL_MANAGER)
			]

		self.technical_director_text = ft.Text(f"Technical Director Name")
		self.technical_director_age_text = ft.Text(f"Technical Director Age")
		self.technical_director_contract_length_text = ft.Text(f"Technical Director Contact Length")
		self.technical_director_contract_status_text = ft.Text(f"Status: Contracted")
		self.technical_director_ability_widget = rating_widget.RatingWidget("Ability:")

		self.commercial_manager_text = ft.Text(f"Commercial Manager Name")
		self.commercial_manager_age_text = ft.Text(f"Commercial Manager Age")
		self.commercial_manager_contract_length_text = ft.Text(f"Commercial Manager Contact Length")
		self.commercial_manager_contract_status_text = ft.Text(f"Status: Contracted")
		self.commercial_manager_ability_widget = rating_widget.RatingWidget("Ability:")

	def setup_driver_containers(self) -> None:
		self.driver_containers = []

		for idx in [0, 1]:
			column = ft.Column(
				# expand=1,
				controls=[
					custom_container.HeaderContainer(self.view, f"Driver {idx + 1}"), # header
					ft.Text("Personal Details", weight=ft.FontWeight.BOLD, size=18,),
					self.driver_name_texts[idx],
					self.driver_age_texts[idx],
					self.driver_country_texts[idx],
					ft.Divider(),

					ft.Text("Contract", weight=ft.FontWeight.BOLD, size=18,),
					self.driver_salary_texts[idx], # length left on contract
					self.driver_contract_length_texts[idx], # length left on contract
					self.driver_contract_status_texts[idx], # status
					self.staff_replace_buttons[idx], # replace button
					ft.Divider(),

					ft.Text("Stats", weight=ft.FontWeight.BOLD, size=18,),
					self.driver_ability_widgets[idx],
					],
				expand=True
			)

			container = custom_container.CustomContainer(self.view, column, expand=True)

			self.driver_containers.append(container)

		self.driver_row = ft.Row(
			# expand=1,
			controls=[
				self.driver_containers[0],
				self.driver_containers[1],
			]
		)

	def setup_manager_containers(self) -> None:
		self.manager_containers = []

		for manager in ["Technical Director", "Commercial Manager"]:
			controls = [
				custom_container.HeaderContainer(self.view, manager),
				ft.Text("Personal Details", weight=ft.FontWeight.BOLD, size=18,),
				]

			if manager == "Technical Director":
				controls.append(self.technical_director_text)
				controls.append(self.technical_director_age_text)

			elif manager == "Commercial Manager":
				controls.append(self.commercial_manager_text)
				controls.append(self.commercial_manager_age_text)
			controls.append(ft.Divider())
			
			# CONTRACT ----------------------
			controls.append(ft.Text("Contract", weight=ft.FontWeight.BOLD, size=18,))

			if manager == "Technical Director":
				controls.append(self.technical_director_contract_length_text)
				controls.append(self.technical_director_contract_status_text)
				controls.append(self.staff_replace_buttons[2])
			elif manager == "Commercial Manager":
				controls.append(self.commercial_manager_contract_length_text)
				controls.append(self.commercial_manager_contract_status_text)
				controls.append(self.staff_replace_buttons[3])

			controls.append(ft.Divider())

			# STATS ----------------------
			controls.append(ft.Text("Stats", weight=ft.FontWeight.BOLD, size=18,))
			if manager == "Technical Director":
				controls.append(self.technical_director_ability_widget)
			elif manager == "Commercial Manager":
				controls.append(self.commercial_manager_ability_widget)

			column = ft.Column(
				# expand=1,
				controls=controls,
				expand=True
			)

			container = custom_container.CustomContainer(self.view, column, expand=True)
			self.manager_containers.append(container)

		self.manager_row = ft.Row(
			controls = [
				self.manager_containers[0],
				self.manager_containers[1],
			]
		)

	def update_page(self, data: dict, new_season: bool=False) -> None:
		if new_season is True:
			self.enable_hire_workforce_btn()
			
		self.driver_name_texts[0].value = f"Name: {data['driver1']}"
		self.driver_name_texts[1].value = f"Name: {data['driver2']}"

		self.driver_age_texts[0].value = f"Age: {data['driver1_age']} Years"
		self.driver_age_texts[1].value = f"Age: {data['driver2_age']} Years"

		self.driver_country_texts[0].value = f"Country: {data['driver1_country']}"
		self.driver_country_texts[1].value = f"Country: {data['driver2_country']}"

		# Ability
		self.driver_ability_widgets[0].update_row(data["driver1_speed"])
		self.driver_ability_widgets[1].update_row(data["driver2_speed"])
		
		# Contract Salary
		self.driver_salary_texts[0].value = f"Salary: ${data['driver1_salary']:,}"
		self.driver_salary_texts[1].value = f"Salary: ${data['driver2_salary']:,}"

		# Contract Length
		self.driver_contract_length_texts[0].value = f"Contract Length: {data['driver1_contract_length']} Years"
		self.driver_contract_length_texts[1].value = f"Contract Length: {data['driver2_contract_length']} Years"

		# Contract Status

		for idx, driver_idx in enumerate(["driver1", "driver2"]):
			text = "Contracted"

			if data[f"{driver_idx}_retiring"] is True:
				text = "Retiring"
			elif data[f"{driver_idx}_contract_length"] < 2:
				text = "Contract Expiring"

			self.driver_contract_status_texts[idx].value = f"Status: {text}"

		# Enable/Disable replace buttons
		for idx, r in enumerate([data["player_requiring_driver1"], data["player_requiring_driver2"],
						   data["player_requiring_technical_director"], data["player_requiring_commercial_manager"]]):
			self.staff_replace_buttons[idx].disabled = not r
		
		# Update technical director
		self.technical_director_text.value = f"Name: {data['technical_director']}"
		self.technical_director_age_text.value = f"Age: {data['technical_director_age']}"
		self.technical_director_contract_length_text.value = f"Contract Length: {data['technical_director_contract_length']} Years"
		self.technical_director_ability_widget.update_row(data["technical_director_skill"])

		# Update commercial manager
		self.commercial_manager_text.value = f"Name: {data['commercial_manager']}"
		self.commercial_manager_age_text.value = f"Age: {data['commercial_manager_age']}"
		self.commercial_manager_contract_length_text.value = f"Contract Length: {data['commercial_manager_contract_length']} Years"
		self.commercial_manager_ability_widget.update_row(data["commercial_manager_skill"])

		self.workforce_container = self.setup_staff_value_progress_bars(data)

		self.view.main_app.update()

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

		self.controls = [
			ft.Text("Staff", theme_style=self.view.page_header_style),
			self.buttons_row,
			self.driver_row,
		]

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

	def setup_staff_value_progress_bars(self, data: dict) -> ft.Container:
		staff_value_rows = [custom_container.HeaderContainer(self.view, f"Number of Staff")]
		
		max_staff = max(v[1] for v in data["staff_values"])

		for team in data["staff_values"]:
			team_name = team[0]
			staff_value = team[1]
			
			row = ft.Row(
				controls=[
					ft.Text(f"{team_name} ({staff_value}):", width=100),
					ft.ProgressBar(value=staff_value/max_staff, width=500, expand=True, bar_height=28)
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
