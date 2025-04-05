from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
	from pw_view.view import View

class UpgradeFacilitiesDialog(ft.AlertDialog):
	def __init__(self, page: ft.Page, view: View, current_state: int):
		super().__init__(
			modal=True,
			title=ft.Text("Upgrade Facilities")
		)
		
		self.page = page
		self.view = view
		self.upgrade_percentage = 30
		self.cost = 20_000_000
		
		self.setup_widgets(current_state)
		
		# Use a container to organize the dialog's content
		self.content = ft.Container(
			content=ft.Column(
				[
					self.current_state_text,
					self.select_scope_row,
					self.update_percentage_text,
				],
				alignment=ft.MainAxisAlignment.CENTER,
				horizontal_alignment=ft.CrossAxisAlignment.CENTER
			),
			padding=20,
			width=600,
			height=200,
			alignment=ft.alignment.center
		)
		
		# Dialog action buttons
		self.actions = [
			ft.TextButton("Upgrade", on_click=self.confirm_upgrade),
			ft.TextButton("Cancel", on_click=self.close_dialog),
		]
		self.actions_alignment = ft.MainAxisAlignment.END

	def setup_widgets(self, current_state: int) -> None:
		self.current_state_text = ft.Text(f"Current State: {current_state}")

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

		self.update_percentage_text = ft.Text(
			"30%, Cost: $20,000,000", 
			text_align=ft.TextAlign.CENTER, 
			width=540
		)
		
		self.update_progress_bar()

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

		self.cost = 10_000_000 + (int(self.progress_bar.value * 20_000_000))
		self.update_percentage_text.value = f"{self.upgrade_percentage}%, Cost: ${self.cost:,}"
		self.page.update()

	def confirm_upgrade(self, e: ft.ControlEvent) -> None:
		current_state = int(self.current_state_text.value.split(":")[1])

		if current_state + self.upgrade_percentage > 100:
			self.show_error_dialog()
		else:
			self.view.controller.facilities_controller.update_facilties(
				self.upgrade_percentage, 
				self.cost
			)
			self.close_dialog(None)

	def show_error_dialog(self) -> None:
		error_dialog = ft.AlertDialog(
			modal=True,
			title=ft.Text("Unable to update"),
			content=ft.Text("The requested upgrade cannot be performed."),
			actions=[
				ft.TextButton("Close", on_click=lambda e: self.close_error_dialog(error_dialog)),
			],
			actions_alignment=ft.MainAxisAlignment.END,
		)
		
		self.page.overlay.append(error_dialog)
		error_dialog.open = True
		self.page.update()

	def close_error_dialog(self, dialog: ft.AlertDialog) -> None:
		dialog.open = False
		self.page.update()

	def close_dialog(self, e: ft.ControlEvent) -> None:
		self.open = False
		self.page.update()
