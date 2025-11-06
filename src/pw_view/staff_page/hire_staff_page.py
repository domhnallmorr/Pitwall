from __future__ import annotations
from typing import Optional, TYPE_CHECKING
import os

import flet as ft

from pw_model.pw_model_enums import StaffRoles
from pw_model.driver_negotiation.driver_interest import DriverRejectionReason
from pw_view.staff_page.staff_dialogs import RejectionDialog, AcceptDialog, DriverOfferDialog
from pw_view.custom_widgets import custom_container
from pw_view.custom_widgets.rating_widget import RatingWidget
from pw_view.custom_widgets.custom_datatable import CustomDataTable

if TYPE_CHECKING:
	from pw_view.view import View

class HireStaffPage(ft.Column):
	def __init__(self, view: View):
		
		self.view = view
		self.accept_dialog = AcceptDialog(view)
		self.rejection_dialog = RejectionDialog()

		self.setup_contract_column()

		self.title_text = ft.Text("Hire Driver", theme_style=self.view.page_header_style)
		self.current_role = None # tracks wether player is hiring driver, technical director, etc

		super().__init__(expand=1)

	def update_free_agent_list(self, free_agents: list[str], role: StaffRoles,
							pay_drivers: list[str],
							ratings: list[int]) -> None:
		title = role.value.title().replace("1", " 1").replace("2", " 2")
		self.title_text.value = f"Hire: {title}"
		self.current_role = role

		columns = ["Name", "Ability"]
		data = [[name, ratings[idx]] for idx, name in enumerate(free_agents)]

		# Add pay driver column for drivers
		if role in [StaffRoles.DRIVER1, StaffRoles.DRIVER2]:
			columns.append("Pay Driver")

			for row in data:
				if row[0] in pay_drivers:
					row.append("Yes")
				else:
					row.append("")

		self.free_agent_table = CustomDataTable(self.view, columns, header_text="Free Agents")
		self.free_agent_table.update_table_data(data, rating_col_idx=1, ratings=ratings)
		self.free_agent_table.assign_on_tap_callback(0, self.update_staff)

		# header = custom_container.CustomContainer(self.view, ft.Text("Free Agents", weight=ft.FontWeight.BOLD, size=25,), expand=False)
		# self.free_agents_column = ft.Column(
		# 	controls=[
		# 		self.free_agent_table.list_view,
		# 	],
		# 	expand=True
		# )

		# self.free_agents_container = custom_container.CustomContainer(
		# 	self.view,
		# 	self.free_agents_column,
		# 	expand=True
		# )
		
		self.setup_page()

		self.update_staff(None, name=free_agents[0])
		
	def setup_contract_column(self) -> None:
		self.name_text = ft.Text("Driver Name: Some Driver")
		self.age_text = ft.Text("Driver Age: 99")
		self.contract_length_text = ft.Text("Contract Length: 2 years")

		image_path = os.path.abspath(fr"{self.view.driver_images_path}\driver_placeholder.png")
		self.image = ft.Image(
			src=image_path,
			width=150,
			height=150,
			fit=ft.ImageFit.CONTAIN,
	  	)

		self.offer_btn = ft.TextButton("Offer", on_click=self.approach_staff)

		self.details_column = ft.Column(
			controls=[
				self.name_text,
				self.age_text,
				self.contract_length_text,
				self.offer_btn,
			],
			expand=False
		)

		self.image_column = ft.Column(
			controls=[
				self.image,
			],
		)

		self.contract_row = ft.Row(
			controls=[
				self.details_column,
				ft.VerticalDivider(),
				self.image_column,
			],
			expand=False
		)

		self.contract_column = ft.Column(
			controls=[
				custom_container.HeaderContainer(self.view, "Details", expand=False),
				self.contract_row,
			],
			expand=False
		)

		self.contract_container = custom_container.CustomContainer(
			self.view,
			self.contract_column,
			expand=True
		)


	def setup_page(self) -> None:
		content_row = ft.Row(
			controls=[
				self.free_agent_table.list_view,
				self.contract_container
			],
			vertical_alignment=ft.CrossAxisAlignment.START,
			expand=True
		)

		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				content_row
			],
			expand=True
		)

		self.controls = [
			self.title_text,
			self.background_stack
		]

		self.view.main_app.update()

	def update_staff(self, e: ft.ControlEvent, name: Optional[str]=None) -> None:
		if name is None:
			name = e.control.data

		details = self.view.controller.staff_hire_controller.get_staff_details(name, self.current_role)
		self.name_text.value = f"Name: {details['name']}"
		self.age_text.value = f"Age: {details['age']}"

		self.offer_btn.data = name

		if details["rejected_player_offer"] is True:
			self.offer_btn.disabled = True
		else:
			self.offer_btn.disabled = False

		# Update image
		if self.current_role in [StaffRoles.DRIVER1, StaffRoles.DRIVER2]:
			self.image.src = fr"{self.view.driver_images_path}\{name.lower()}.png"
		else:
			self.image.src = fr"{self.view.manager_images_path}\{name.lower()}.png"
		
		self.view.main_app.update()

	def approach_staff(self, e: ft.ControlEvent) -> None:
		name = e.control.data

		if self.current_role in [StaffRoles.DRIVER1, StaffRoles.DRIVER2]:
			self.view.controller.staff_hire_controller.open_driver_offer_dialog(name, self.current_role)
			# self.offer_btn.disabled = True
			# self.disable_name_text_button(name)
		else:
			self.dlg_modal = ft.AlertDialog(
				modal=True,
				title=ft.Text(f"Confirm"),
				content=ft.Text(f"Complete Hiring of {name}?"),
				actions=[
					ft.TextButton("Yes", on_click=self.handle_close),
					ft.TextButton("No", on_click=self.handle_close),
				],
				actions_alignment=ft.MainAxisAlignment.END,
				data=name
			)

			self.view.main_app.overlay.append(self.dlg_modal)
			self.dlg_modal.open = True
			self.view.main_app.update()

	def open_driver_offer_dialog(self, driver_name: str, current_salary: int, pay_driver: bool) -> None:
		offer_dialog = DriverOfferDialog(self.view.main_app, self.view, driver_name, current_salary, pay_driver)
		self.view.main_app.overlay.append(offer_dialog)
		offer_dialog.open = True
		self.view.main_app.update()

	def handle_close(self, e: ft.ControlEvent) -> None:
		name = self.dlg_modal.data
		self.view.main_app.close(self.dlg_modal)
		action = e.control.text

		if action.lower() == "yes":
			self.view.controller.staff_hire_controller.complete_hire(name, self.current_role)

	def show_accept_dialog(self, name: str, role: StaffRoles, salary: int) -> None:
		self.disable_offer_button() #ensure player can't approach same driver twice
		self.accept_dialog.update_text_widget(name, role, salary)

		if self.accept_dialog in self.view.main_app.overlay:
			self.view.main_app.overlay.remove(self.accept_dialog)
	
		self.view.main_app.overlay.append(self.accept_dialog)
		self.accept_dialog.open = True
		self.view.main_app.update()

	def show_rejection_dialog(self, name: str, reason: DriverRejectionReason) -> None:
		self.disable_offer_button() #ensure player can't approach same driver twice
		self.rejection_dialog.update_text_widget(name, reason)

		if self.rejection_dialog in self.view.main_app.overlay:
			self.view.main_app.overlay.remove(self.rejection_dialog)

		self.view.main_app.overlay.append(self.rejection_dialog)
		self.rejection_dialog.open = True
		self.view.main_app.update()

	def disable_name_text_button(self, name: str) -> None:
		for btn in self.name_text_buttons:
			if btn.data == name:
				btn.disabled = True
				break
		self.view.main_app.update()

	def disable_offer_button(self) -> None:
		self.offer_btn.disabled = True
		self.view.main_app.update()
