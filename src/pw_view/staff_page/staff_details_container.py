from __future__ import annotations
from typing import TYPE_CHECKING, Union
import flet as ft

from pw_model.pw_model_enums import StaffRoles
from pw_view.custom_widgets.rating_widget import RatingWidget
from pw_view.custom_widgets.custom_container import CustomContainer, HeaderContainer
from pw_controller.staff_page.staff_page_data import DriverData, SeniorStaffData

if TYPE_CHECKING:
	from pw_view.view import View

class StaffDetailsContainer:
	def __init__(self, view: View, role: StaffRoles):
		self.view = view
		self.role = role
		self.SUBHEADER_FONT_SIZE = 18

		self.setup_text_widgets()
		self.setup_rating_widgets()
		self.setup_replace_button()
		self.setup_container()

	def setup_text_widgets(self) -> None:
		self.name_text = ft.Text("Name: Mr X")
		self.age_text = ft.Text("Age: x Years")
		self.country_text = ft.Text("Country: Some Country")

		self.salary_text = ft.Text("Salary: $0")
		self.contract_length_text = ft.Text("Contract Length: X Year(s)")
		self.contract_status_text = ft.Text("Contract Status: Status")

	def setup_rating_widgets(self) -> None:
		text_width = 110
		self.ability_widget = RatingWidget("Ability", text_width=text_width)

		if self.role in [StaffRoles.DRIVER1, StaffRoles.DRIVER2]:
			self.speed_widget = RatingWidget("Speed:", text_width=text_width)
			self.consistency_widget = RatingWidget("Consistency:", text_width=text_width)

	def setup_replace_button(self) -> None:
		self.replace_button = ft.TextButton("Replace", disabled=True, icon="find_replace", on_click=self.replace, data=self.role)

	def setup_header(self) -> HeaderContainer:
		return HeaderContainer(self.view, self.role.value)
	
	def setup_column(self) -> ft.Column:
		controls = [
			self.setup_header(),
			ft.Text("Personal Details", weight=ft.FontWeight.BOLD, size=self.SUBHEADER_FONT_SIZE,),
			self.name_text,
			self.age_text
		]

		if self.role in [StaffRoles.DRIVER1, StaffRoles.DRIVER2]:
			controls.append(self.country_text)
		
		controls.append(ft.Divider())

		# ------ CONTRACT ------
		controls.append(ft.Text("Contract", weight=ft.FontWeight.BOLD, size=self.SUBHEADER_FONT_SIZE,),)
		controls.append(self.salary_text)
		controls.append(self.contract_length_text)
		controls.append(self.contract_status_text)
		controls.append(self.replace_button)

		controls.append(ft.Divider())

		# Stats
		controls.append(ft.Text("Stats", weight=ft.FontWeight.BOLD, size=self.SUBHEADER_FONT_SIZE,))
		controls.append(self.ability_widget)

		if self.role in [StaffRoles.DRIVER1, StaffRoles.DRIVER2]:
			controls.append(self.speed_widget)
			controls.append(self.consistency_widget)

		return ft.Column(controls=controls, expand=True)

	def setup_container(self) -> None:
		self.container = CustomContainer(self.view, self.setup_column(), expand=True)

	def update(self, data: Union[DriverData, SeniorStaffData], player_requring_this_role: bool) -> None:
		self.name_text.value = f"Name: {data.name}"
		self.age_text.value = f"Age: {data.age} Years"

		self.salary_text.value = f"Salary: ${data.salary:,}"
		self.contract_length_text.value = f"Contract Length: {data.contract_length} Year(s)"

		# replace_btn_disabled = False
		if data.retiring is True:
			self.contract_status_text.value = "Contract Status: Retiring"
		elif data.contract_length < 2:
			self.contract_status_text.value = "Contract Status: Contract Expiring"
		else:
			self.contract_status_text.value = "Contract Status: Contracted"

		self.replace_button.disabled = not player_requring_this_role

		if self.role in [StaffRoles.DRIVER1, StaffRoles.DRIVER2]:
			self.country_text.value = f"Country: {data.country}"
			self.ability_widget.update_row(data.speed)
			self.speed_widget.update_row(data.speed)
			self.consistency_widget.update_row(data.consistency)

		elif self.role in [StaffRoles.TECHNICAL_DIRECTOR, StaffRoles.COMMERCIAL_MANAGER]:
			self.ability_widget.update_row(data.skill)
			
	def replace(self, e: ft.ControlEvent) -> None:
		self.view.controller.staff_hire_controller.launch_replace_staff(e.control.data)