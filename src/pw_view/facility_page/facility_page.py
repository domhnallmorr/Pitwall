import flet as ft

from pw_view.custom_widgets import custom_container

class FacilityPage(ft.Column):
	def __init__(self, view):

		self.view = view
		self.setup_widgets()

		contents = [
			ft.Text("Facilities", theme_style=self.view.page_header_style)
		]

		super().__init__(controls=contents, alignment=ft.MainAxisAlignment.START, expand=True)

	def update_page(self, data):
		facility_rows = self.setup_facilities_progress_bars(data)

		facility_column = ft.Column(
			controls=facility_rows,
			expand=False,
			tight=True,
			spacing=20
		)

		facility_comparison_container = custom_container.CustomContainer(self.view, facility_column, expand=False)

		column = ft.Column(
			controls=[
				self.buttons_container,
				facility_comparison_container,
			],
			expand=False,
			tight=True
		)

		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				column
			],
			expand=True
		)

		self.controls = [
			ft.Text("Facilities", theme_style=self.view.page_header_style),
			self.background_stack
			# self.update_button,
			# facility_comparison_container,
		]

		self.view.main_app.update()

	def setup_widgets(self):
		self.update_button = ft.TextButton("Update", icon="upgrade", on_click=self.update_facilities)

		self.buttons_row = ft.Row(
			controls=[
				self.update_button,
			],
			expand=False,
			tight=True
		)

		self.buttons_container = custom_container.CustomContainer(self.view, self.buttons_row, expand=False)

	def setup_facilities_progress_bars(self, data):
		facility_rows = []

		for team in data["facility_values"]:
			team_name = team[0]
			facility = team[1]
			
			row = ft.Row(
				controls=[
					ft.Text(f"{team_name}:", width=100),
					ft.ProgressBar(value=facility/100, width=500, expand=True, bar_height=28)
				],
				expand=False,
			)
			facility_rows.append(row)

		return facility_rows
	
	def update_facilities(self, e):
		self.view.controller.facilities_controller.clicked_update_facilities()
		
	def disable_upgrade_button(self):
		self.update_button.disabled = True
		self.view.main_app.update()

	def enable_upgrade_button(self):
		self.update_button.disabled = False
		self.view.main_app.update()
