import flet as ft

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

		column = ft.Column(
			controls=facility_rows,
			expand=True,
			spacing=20
		)

		facility_comparison_container = ft.Container(
			content=column,
			expand=True
		)

		self.controls = [
			ft.Text("Facilities", theme_style=self.view.page_header_style),
			self.update_button,
			facility_comparison_container,
		]

		self.view.main_app.update()

	def setup_widgets(self):
		self.update_button = ft.TextButton("Update", icon="upgrade", on_click=self.update_facilities)

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
				expand=True,
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
