from __future__ import annotations

from typing import TYPE_CHECKING
import flet as ft

if TYPE_CHECKING:
	from pw_view.view import View

class TeamSelectionScreen(ft.View):
	def __init__(self, view: View, team_names: list[str]):
		self.view = view
		
		team_buttons = []

		for name in team_names:
			team_buttons.append(ft.ElevatedButton(name, data=name, on_click=self.start_career, width=200))


		controls = [
			ft.Text("Select Team", theme_style=self.view.page_header_style),
			ft.Column(
				team_buttons
			),
		]

		super().__init__(controls=controls)

	def start_career(self, e: ft.ControlEvent) -> None:
		self.view.controller.start_career(e.control.data)
		