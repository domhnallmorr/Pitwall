from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
	from pw_view.view import View


class ConfirmDialog(ft.AlertDialog):
	def __init__(self, view: View):
		self.view = view
		self.text_widget = ft.Text("Confirm?")
		self.choice = False
		self.on_result = None
		
		super().__init__(
			modal=True,
			title=ft.Text("Confirm"),
			content=self.text_widget,
			actions=[
				ft.TextButton("Yes", on_click=self.close_dialog, data=True),
				ft.TextButton("No", on_click=self.close_dialog, data=False),
			],
		)

	def close_dialog(self, e: ft.ControlEvent) -> None:
		self.choice = e.control.data
		self.open = False
		self.view.main_app.update()

		if self.on_result:
			self.on_result(e)
		
		
	def update_text_widget(self, message: str) -> None:
		self.text_widget.value = message
