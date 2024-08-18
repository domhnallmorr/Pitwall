import flet as ft

class HomePage(ft.Column):
	def __init__(self, view):

		self.view = view

		contents = [
			ft.Text("Home", theme_style=self.view.page_header_style)
		]

		super().__init__(controls=contents, alignment=ft.MainAxisAlignment.START)

	def update_page(self, data):
		pass