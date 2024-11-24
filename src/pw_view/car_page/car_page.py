import flet as ft

from pw_view.custom_widgets import custom_container

class CarPage(ft.Column):
	def __init__(self, view):

		self.view = view

		contents = [
			ft.Text("Car", theme_style=self.view.page_header_style)
		]

		super().__init__(controls=contents, alignment=ft.MainAxisAlignment.START, expand=True)

	def update_page(self, data):
		car_speed_rows = self.setup_car_speed_progress_bars(data)

		column = ft.Column(
			controls=car_speed_rows,
			expand=False,
			tight=True,
			spacing=20
		)

		car_comparison_container = custom_container.CustomContainer(self.view, column, expand=False)

		self.background_stack = ft.Stack(
			[
				# Add the resizable background image
				self.view.background_image,
				car_comparison_container
			],
			expand=True,  # Make sure the stack expands to fill the window
		)



		self.controls = [
			ft.Text("Car", theme_style=self.view.page_header_style),
			# car_comparison_container
			self.background_stack
		]

		self.view.main_app.update()

	def setup_car_speed_progress_bars(self, data):
		car_speed_rows = []

		for team in data["car_speeds"]:
			team_name = team[0]
			speed = team[1]
			
			row = ft.Row(
				controls=[
					ft.Text(f"{team_name}:", width=100),
					ft.ProgressBar(value=speed/100, width=500, expand=True, bar_height=28)
				],
				expand=False,
			)
			car_speed_rows.append(row)

		return car_speed_rows