from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
	from pw_view.view import View

class UpgradeFacilitiesPage(ft.Column):
	def __init__(self, view: View):

		self.view = view

		self.setup_widgets()

		self.upgrade_percentage = 30
		self.cost = 20_000_000

		contents = [
			ft.Text("Upgrade Facilities", theme_style=self.view.page_header_style),
			self.current_state_text,
			self.select_scope_row,
			self.update_percentage_text,
			self.upgrade_button,
		]

		super().__init__(controls=contents, alignment=ft.MainAxisAlignment.START)

	# def update_page(self, data):
	# 	pass

	def setup_widgets(self) -> None:
		self.current_state_text = ft.Text("Current State: 100")

		self.decrease_btn = ft.TextButton("-", on_click=self.decrease_percentage)
		self.increase_btn = ft.TextButton("+", on_click=self.increase_percentage)

		self.progress_bar = ft.ProgressBar(value=0.5, width=500, expand=True, bar_height=28)

		self.select_scope_row = ft.Row(
			controls=[
				self.decrease_btn,
				self.progress_bar,
				self.increase_btn,
			]
		)

		self.update_percentage_text = ft.Text("30%, Cost: $20,000,000", text_align=ft.TextAlign.CENTER, width=540)

		self.upgrade_button = ft.TextButton("Upgrade", icon="update", on_click=self.confirm_upgrade)
	
	def decrease_percentage(self, e: ft.ControlEvent) -> None:
		if self.upgrade_percentage > 20:
			self.upgrade_percentage -= 1

		self.update_progress_bar()

	def increase_percentage(self, e: ft.ControlEvent) -> None:
		if self.upgrade_percentage < 40:
			self.upgrade_percentage += 1

		self.update_progress_bar()

	def update_progress_bar(self) -> None:

		value = round((self.upgrade_percentage - 20) / 20, 2)
		self.progress_bar.value = value

		# TODO create a function in model to calculate this
		self.cost = 10_000_000 + (int(self.progress_bar.value * 20_000_000))
		self.update_percentage_text.value = f"{self.upgrade_percentage}%, Cost: ${self.cost :,}"
		self.view.main_app.update()

	def update_current_state(self, current_state: int) -> None:
		self.current_state_text.value = f"Current State: {current_state}"

	def confirm_upgrade(self, e: ft.ControlEvent) -> None:
		current_state = int(self.current_state_text.value.split(":")[1])

		if current_state + self.upgrade_percentage > 100:
			self.dlg_modal = ft.AlertDialog(
				modal=True,
				title=ft.Text(f"Unable to update"),
				content=ft.Text(f"The requested upgrade cannot be performed."),
				actions=[
					ft.TextButton("Close", on_click=self.handle_close),
				],
				actions_alignment=ft.MainAxisAlignment.END,
			)
		else:
			self.dlg_modal = ft.AlertDialog(
				modal=True,
				title=ft.Text(f"Confirm"),
				content=ft.Text(f"Confirm Upgrade of Facilities?"),
				actions=[
					ft.TextButton("Yes", on_click=self.handle_close),
					ft.TextButton("No", on_click=self.handle_close),
				],
				actions_alignment=ft.MainAxisAlignment.END,
				data=self.update_percentage_text
			)

			# self.view.main_app.open(dlg_modal)
		self.view.main_app.overlay.append(self.dlg_modal)
	
		self.dlg_modal.open = True
		self.view.main_app.update()

	def handle_close(self, e: ft.ControlEvent) -> None:
		name = self.dlg_modal.data
		self.view.main_app.close(self.dlg_modal)
		action = e.control.text

		if action.lower() == "yes":
			self.view.controller.facilities_controller.update_facilties(self.upgrade_percentage, self.cost)
			