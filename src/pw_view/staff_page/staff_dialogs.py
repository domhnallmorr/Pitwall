from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import flet as ft

from pw_model.pw_model_enums import StaffRoles
from pw_model.driver_negotiation.driver_interest import DriverRejectionReason

if TYPE_CHECKING:
	from pw_view.view import View

class RejectionDialog(ft.AlertDialog):
	def __init__(self) -> None:
		
		self.text_widget = ft.Text("Some one has declined your offer")
		
		super().__init__(
			modal=True,
			title=ft.Text("Contract Rejected"),
			content=self.text_widget,
			actions=[
				ft.TextButton("OK", on_click=self.close_dialog)
			],
		)
		# self.on_dismiss = on_dismiss

	def close_dialog(self, e: ft.ControlEvent) -> None:
		self.open = False
		if self.on_dismiss:
			self.on_dismiss()
		self.update()

	def update_text_widget(self, name: str, reason: DriverRejectionReason) -> None:
		if reason == DriverRejectionReason.NONE:
			self.text_widget.value = f"{name} has declined your offer. No reason was provided."
		else:
			self.text_widget.value = f"{name} has declined your offer.\nReason: {reason.value}."

class AcceptDialog(ft.AlertDialog):
	def __init__(self, view: View):
		self.view = view
		self.staff_hire_controller = view.controller.staff_hire_controller

		self.text_widget = ft.Text("Some one has accepted your offer")
		
		super().__init__(
			modal=True,
			title=ft.Text("Contract Accepted"),
			content=self.text_widget,
			actions=[
				ft.TextButton("Yes", on_click=self.close_dialog, data=True),
				ft.TextButton("No", on_click=self.close_dialog, data=False),
			],
		)
		# self.on_dismiss = on_dismiss

	def close_dialog(self, e: ft.ControlEvent) -> None:
		self.open = False
		self.view.main_app.update()
		
		if e.control.data is True:
			self.staff_hire_controller.complete_hire(self.current_name, self.current_role, self.salary)

	def update_text_widget(self, name: str, role: StaffRoles, salary: int) -> None:
		self.salary = salary
		self.current_name = name
		self.current_role = role
		self.text_widget.value = f"{name} has accepted your offer as {role.value}. Do you want to complete the signing?"

class DriverOfferDialog(ft.AlertDialog):
	def __init__(self, page: ft.Page, view: View, driver_name: str, current_salary: int, pay_driver: bool):
		super().__init__(
			modal=True, 
			title=ft.Text(f"Offer Contract to {driver_name}")
		)
		
		self.page = page
		self.view = view
		self.driver_name = driver_name
		self.current_salary = current_salary  # The current salary of the driver being offered a contract
		self.pay_driver = pay_driver

		self.clause_width = 100
		self.current_width = 100
		
		# Start with a default salary of 1,000,000
		if self.pay_driver is True:
			color = ft.Colors.GREEN
		else:
			color = ft.Colors.PRIMARY
			
		self.salary_input = ft.TextField(
			value=f"${current_salary:,}", 
			width=200, 
			read_only=True,
			color=color
		)
		
		if self.pay_driver is True:
			disabled = True
		else:
			disabled = False

		self.increase_button = ft.ElevatedButton(
			"+", 
			on_click=self.increase_salary,
			disabled=disabled
		)
		self.decrease_button = ft.ElevatedButton(
			"-", 
			on_click=self.decrease_salary,
			disabled=disabled
		)
		
		self.setup_header_row()
		self.setup_salary_row()
		
		self.content = ft.Container(
			content=ft.Column(
				[
					self.header_row,
					ft.Divider(),
					self.salary_row,
				],
				alignment=ft.MainAxisAlignment.CENTER,
				horizontal_alignment=ft.CrossAxisAlignment.CENTER
			),
			padding=20,
			width=600,
			height=200,
			alignment=ft.alignment.center
		)
		
		self.actions = [
			ft.TextButton("Make Offer", on_click=self.make_offer),
			ft.TextButton("Cancel", on_click=self.close_dialog),
		]

	def setup_header_row(self) -> None:
		self.header_row = ft.Row(
			[
				# An empty placeholder where you might want to align text below
				ft.Text("", width=self.clause_width),
				
				# "Current" text styled as bold and a bit larger
				ft.Text(
					"Current",
					width=self.current_width,
					weight=ft.FontWeight.BOLD,     # Make the text bold
					size=16,                       # Increase font size
					color=ft.Colors.PRIMARY
				),
				
				# Another placeholder
				ft.Text("", width=60),
				
				# "Your Offer" also styled similarly
				ft.Text(
					"Your Offer",
					width=200,
					weight=ft.FontWeight.BOLD,
					size=16,
					color=ft.Colors.PRIMARY
				),
			],
			alignment=ft.MainAxisAlignment.START,
		)

	def setup_salary_row(self) -> None:
		self.salary_row = ft.Row(
			[
				ft.Text("Salary Offer:", width=self.clause_width),
				ft.Text(f"${self.current_salary:,}", width=self.current_width),
				self.decrease_button,
				self.salary_input,
				self.increase_button,
			],
			alignment=ft.MainAxisAlignment.CENTER,
		)

	def increase_salary(self, e: ft.ControlEvent) -> None:
		current = int(self.salary_input.value.replace(",", "").replace("$", ""))
		self.salary_input.value = f"{current + 50_000:,}"
		self.page.update()
	
	def decrease_salary(self, e: ft.ControlEvent) -> None:
		current = int(self.salary_input.value.replace(",", "").replace("$", ""))
		if current > 50_000:  # Prevent going below 500,000
			self.salary_input.value = f"{current - 50_000:,}"
			self.page.update()
	
	def make_offer(self, e: ft.ControlEvent) -> None:
		salary = int(self.salary_input.value.replace(",", "").replace("$", ""))

		self.view.controller.staff_hire_controller.make_driver_offer(
			self.driver_name, 
			self.view.hire_staff_page.current_role,
			salary
		)
		
		self.close_dialog(None)
			
	def close_dialog(self, e: Optional[ft.ControlEvent]) -> None:
		self.open = False
		self.page.update()
