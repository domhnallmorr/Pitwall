
import flet as ft

class Sidebar(ft.Column):
	def __init__(self, view):
		self.view = view

		self.advance_btn = ft.TextButton("Advance", icon="play_arrow", on_click=self.advance)
		self.advance_btn.style = self.view.positive_button_style

		btn_width = 200
		nav_buttons = [
			ft.TextButton("Home", icon="home", on_click=lambda _: view.main_window.change_page("home"), width=btn_width, style=self.view.default_button_style),
			ft.TextButton("Email", icon="email", on_click=lambda _: view.main_window.change_page("email"), width=btn_width, style=self.view.default_button_style),
			ft.TextButton("Standings", icon="table_chart", on_click=lambda _: view.main_window.change_page("standings"), width=btn_width, style=self.view.default_button_style),
			ft.TextButton("Calendar", icon="CALENDAR_MONTH", on_click=lambda _: view.main_window.change_page("calendar"), width=btn_width, style=self.view.default_button_style),
			ft.TextButton("Staff", icon="account_box_rounded", on_click=lambda _: view.main_window.change_page("staff"), width=btn_width, style=self.view.default_button_style),
			ft.TextButton("Grid", icon="border_all", on_click=lambda _: view.main_window.change_page("grid"), width=btn_width, style=self.view.default_button_style),
			ft.TextButton("Finance", icon="attach_money", on_click=lambda _: view.main_window.change_page("finance"), width=btn_width, style=self.view.default_button_style),
			ft.TextButton("Car", icon="DIRECTIONS_CAR", on_click=lambda _: view.main_window.change_page("car"), width=btn_width, style=self.view.default_button_style),
			ft.TextButton("Facilities", icon="FACTORY", on_click=lambda _: view.main_window.change_page("facility"), width=btn_width, style=self.view.default_button_style),

			# self.advance_btn
		]

		# Arrange items in a Row with SPACE_BETWEEN to keep Advance at the bottom
		contents = [
            ft.Column(controls=nav_buttons, alignment=ft.MainAxisAlignment.START),  # Main items at the top
            self.advance_btn  # Advance button at the bottom
        ]

		width = 200

		super().__init__(controls=contents, width=width, alignment=ft.MainAxisAlignment.SPACE_BETWEEN, expand=False)

	def advance(self, e):
		self.advance_btn.disabled = True # disable to avoid potential double click

		self.view.main_app.update()
		self.view.controller.advance()

		self.advance_btn.disabled = False
		self.view.main_app.update()

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