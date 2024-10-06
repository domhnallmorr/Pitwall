from typing import List
import flet as ft


class TeamSelectionScreen(ft.View):
	def __init__(self, view, team_names : List):
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

		# contents = [nav_sidebar, self.view.home_page]

		super().__init__(controls=controls)

	def start_career(self, e):
		self.view.controller.start_career(e.control.data)
		