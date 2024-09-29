
import flet as ft

class Sidebar(ft.Column):
	def __init__(self, view):
		self.view = view

		self.advance_btn = ft.TextButton("Advance", icon="play_arrow", on_click=self.advance)

		contents = [
			ft.TextButton("Home", icon="home", on_click=lambda _: view.main_window.change_page("home")),
			ft.TextButton("Email", icon="email", on_click=lambda _: view.main_window.change_page("email")),
			ft.TextButton("Standings", icon="table_chart", on_click=lambda _: view.main_window.change_page("standings")),
			ft.TextButton("Calendar", icon="CALENDAR_MONTH", on_click=lambda _: view.main_window.change_page("calendar")),
			ft.TextButton("Staff", icon="account_box_rounded", on_click=lambda _: view.main_window.change_page("staff")),
			ft.TextButton("Grid", icon="border_all", on_click=lambda _: view.main_window.change_page("grid")),
			ft.TextButton("Finance", icon="attach_money", on_click=lambda _: view.main_window.change_page("finance")),
			ft.TextButton("Car", icon="DIRECTIONS_CAR", on_click=lambda _: view.main_window.change_page("car")),
			ft.TextButton("Facilities", icon="FACTORY", on_click=lambda _: view.main_window.change_page("facility")),
			ft.Divider(),
			self.advance_btn
		]

		width = 200

		super().__init__(controls=contents, width=width)

	def advance(self, e):
		self.view.controller.advance()

	def go_to_race_weekend(self, e):
		self.view.controller.go_to_race_weekend()

	def update_advance_button(self, mode):
		assert mode in ["advance", "go_to_race"]

		if mode == "go_to_race":
			self.advance_btn.text = "Go To Race"
			self.advance_btn.on_click = self.go_to_race_weekend

		if mode == "advance":
			self.advance_btn.text = "Advance"
			self.advance_btn.on_click = self.advance

		self.view.main_app.update()