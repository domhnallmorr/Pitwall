from __future__ import annotations
from typing import TYPE_CHECKING

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
			self.staff_hire_controller.complete_hire(self.current_name, self.current_role)

	def update_text_widget(self, name: str, role: StaffRoles) -> None:
		self.current_name = name
		self.current_role = role
		self.text_widget.value = f"{name} has accepted your offer as {role.value}. Do you want to complete the signing?"