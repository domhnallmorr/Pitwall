
from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

from pw_view.view_enums import ViewPageEnums

if TYPE_CHECKING:
	from pw_view.view import View

class Sidebar(ft.Column): # type: ignore
	def __init__(self, view: View):
		self.view = view
		btn_width = 200
		
		self.advance_btn = ft.TextButton("Advance", icon="play_arrow", width=btn_width, on_click=self.advance)
		self.advance_btn.style = self.view.positive_button_style
		
		# Store all navigation buttons in a dictionary for easy access
		self.nav_buttons = {
			ViewPageEnums.HOME: ft.TextButton("Home", icon="home", width=btn_width, style=self.view.default_button_style),
			ViewPageEnums.EMAIL: ft.TextButton("Email", icon="email", width=btn_width, style=self.view.default_button_style),
			ViewPageEnums.STANDINGS: ft.TextButton("Standings", icon="table_chart", width=btn_width, style=self.view.default_button_style),
			ViewPageEnums.CALENDAR: ft.TextButton("Calendar", icon="CALENDAR_MONTH", width=btn_width, style=self.view.default_button_style),
			ViewPageEnums.STAFF: ft.TextButton("Staff", icon="account_box_rounded", width=btn_width, style=self.view.default_button_style),
			ViewPageEnums.GRID: ft.TextButton("Grid", icon="border_all", width=btn_width, style=self.view.default_button_style),
			ViewPageEnums.FINANCE: ft.TextButton("Finance", icon="attach_money", width=btn_width, style=self.view.default_button_style),
			ViewPageEnums.CAR: ft.TextButton("Car", icon="DIRECTIONS_CAR", width=btn_width, style=self.view.default_button_style),
			ViewPageEnums.FACILITY: ft.TextButton("Facilities", icon="FACTORY", width=btn_width, style=self.view.default_button_style),
		}
		
		# Set click handlers for all buttons
		for page_enum, button in self.nav_buttons.items():
			button.on_click = lambda e, pe=page_enum: self.on_nav_button_click(pe)
			
		self.email_btn = self.nav_buttons[ViewPageEnums.EMAIL]  # Store reference to email button
		
		# Arrange items in a Column with SPACE_BETWEEN to keep Advance at the bottom
		contents = [
			ft.Column(controls=list(self.nav_buttons.values()), alignment=ft.MainAxisAlignment.START),  # Main items at the top
			self.advance_btn  # Advance button at the bottom
		]
		
		width = 200
		super().__init__(controls=contents, width=width, alignment=ft.MainAxisAlignment.SPACE_BETWEEN, expand=False)
		
		# Set initial button style without changing page
		self.set_active_button(ViewPageEnums.HOME)

	def reset_button_styles(self) -> None:
		"""Reset all navigation button styles to default"""
		for button in self.nav_buttons.values():
			button.style = self.view.default_button_style

	def set_active_button(self, page_enum: str) -> None:
		"""Set the active button style without changing page"""
		self.reset_button_styles()
		self.nav_buttons[page_enum].style = self.view.default_button_clicked_style

	def on_nav_button_click(self, page_enum: str) -> None:
		"""Handle navigation button clicks"""
		self.set_active_button(page_enum)
		self.view.main_window.change_page(page_enum)
		self.view.main_app.update()

	def advance(self, e: ft.ControlEvent) -> None:
		self.advance_btn.disabled = True  # disable to avoid potential double click
		self.view.main_app.update()
		self.view.controller.advance()
		self.advance_btn.disabled = False
		self.view.main_app.update()

	def go_to_race_weekend(self, e: ft.ControlEvent) -> None:
		self.view.controller.go_to_race_weekend()

	def update_advance_button(self, mode: str) -> None:
		assert mode in ["advance", "go_to_race"]

		if mode == "go_to_race":
			self.advance_btn.text = "Go To Race"
			self.advance_btn.on_click = self.go_to_race_weekend

		if mode == "advance":
			self.advance_btn.text = "Advance"
			self.advance_btn.on_click = self.advance

		self.view.main_app.update()
