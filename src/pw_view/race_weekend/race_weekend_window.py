from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING

import flet as ft

from pw_view.custom_widgets import custom_container, custom_buttons
from race_weekend_model.race_model_enums import SessionNames

if TYPE_CHECKING:
	from pw_view.view import View

def create_session_header_text(session: str) -> ft.Text:

	return ft.Text(text=session)


class RaceWeekendWindow(ft.View):
	def __init__(self, view: View, data: dict):
		self.view = view
		self.simulate_buttons: dict[SessionNames, ft.TextButton] = {}
		self.view_results_buttons: dict[SessionNames, ft.TextButton] = {}
		self.simulate_btns_clicked: list[SessionNames] = []

		flag_path = fr"{self.view.flags_small_path}\{data['country']}.png"
		flag = ft.Image(
                                src=flag_path,
								)
		self.header_text = ft.Text(data["race_title"], theme_style=self.view.page_header_style)
		self.header_row = ft.Row(controls=[flag, self.header_text])

		# friday_container = self.setup_session_container("Friday Practice")
		# saturday_container = self.setup_session_container("Saturday Practice")
		self.qualy_container = self.setup_session_container(SessionNames.QUALIFYING)
		# warmup_container = self.setup_session_container("Warmup")
		self.race_container = self.setup_session_container(SessionNames.RACE)

		self.continue_btn = custom_buttons.gen_continue_btn(self.view, on_click_func=self.return_to_main_window)
		self.continue_btn.disabled = True

		self.continue_container = custom_buttons.buttons_row(view, [self.continue_btn])

		# self.continue_btn = ft.TextButton("Continue", disabled=True, on_click=self.return_to_main_window)
		self.simulate_buttons[SessionNames.QUALIFYING].disabled = False
		
		# comment out to remove practice sessions for now, will add back later when they are of value
		# controls = [self.header_text, friday_container, saturday_container, qualy_container, warmup_container, race_container, self.continue_btn]
		
		controls = self.setup_page()

		super().__init__(controls=controls, scroll="auto")

	def setup_page(self) -> list[ft.Control]:
		self.content_column = ft.Column(
			controls=[self.qualy_container, self.race_container, self.continue_container],
			expand=True,
			spacing=20
		)

		self.background_stack = ft.Stack(
			[
				self.view.race_background_image,
				self.content_column,
			],
			expand=False,
		)

		controls = [
			self.header_row,
			self.background_stack,
		]

		return controls

	def setup_session_container(self, session_type: Enum) -> ft.Container:
		
		row1 = ft.Row(
			controls=[ft.Text(session_type.value, theme_style=self.view.header2_style)]
		)

		self.simulate_buttons[session_type] = ft.TextButton("Simulate", icon=ft.Icons.REFRESH, on_click=self.simulate, disabled=True, data=session_type)
		row2_controls: list[ft.Control] = [self.simulate_buttons[session_type]]

		if session_type in [SessionNames.QUALIFYING, SessionNames.RACE]:
			view_results_btn = ft.TextButton(
				"View Results",
				icon=ft.Icons.TABLE_CHART,
				on_click=self.show_session_results,
				disabled=True,
				data=session_type,
			)
			self.view_results_buttons[session_type] = view_results_btn
			row2_controls.append(view_results_btn)

		row2 = ft.Row(
			controls=row2_controls,
			spacing=20,
		)

		column = ft.Column(
			controls=[row1, row2]
		)

		container = custom_container.CustomContainer(self.view, column, expand=False)

		return container
	
	def simulate(self, e: ft.ControlEvent) -> None:
		session_type = e.control.data

		if session_type not in self.simulate_btns_clicked: # make sure simulate only happens once per session
			self.simulate_btns_clicked.append(session_type)

			self.simulate_buttons[session_type].disabled = True
			self.view.main_app.update()
			
			# if "friday" in session_title.lower():
			# 	self.simulate_buttons["Saturday Practice"].disabled = False

			# elif "saturday" in session_title.lower():
			# 	self.simulate_buttons[race_model_enums.SessionNames.QUALIFYING].disabled = False	

			if session_type == SessionNames.QUALIFYING:
				self.simulate_buttons[SessionNames.RACE].disabled = False

			# elif "warmup" in session_title.lower():
			# 	self.simulate_buttons["Race"].disabled = False

			elif session_type == SessionNames.RACE:
				self.continue_btn.disabled = False
				
			self.view.controller.race_controller.simulate_session(session_type)
		
		# Enable view results button
		if session_type in self.view_results_buttons:
			self.view_results_buttons[session_type].disabled = False

	def return_to_main_window(self, e: ft.ControlEvent) -> None:
		self.continue_btn.disabled = True
		self.view.main_app.update()
		
		self.view.controller.post_race_actions()

	def show_session_results(self, e: ft.ControlEvent) -> None:
		session_type = e.control.data
		
		if session_type is None:
			return

		self.view.controller.race_controller.show_session_results(session_type)
		