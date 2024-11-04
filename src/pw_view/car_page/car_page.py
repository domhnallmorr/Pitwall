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
			expand=True,
			spacing=20
		)

		car_comparison_container = custom_container.CustomContainer(self.view, column, expand=False)

		self.background_stack = ft.Stack(
			[
				# Add the resizable background image
				self.view.background_image,
				car_comparison_container
				# Add the buttons on top of the image
		# ft.Container(
		# 			content=ft.Column(
		# 				[
		# 					ft.Text(
		# 						"Pitwall",
		# 						size=80,  # Increased size for the title
		# 						color=ft.colors.WHITE,
		# 						weight=ft.FontWeight.BOLD,
		# 						bgcolor=ft.colors.BLACK54,  # Add a semi-transparent background to the text
		# 					),
		# 					button_container,
		# 				],
		# 				alignment=ft.MainAxisAlignment.CENTER,
		# 				horizontal_alignment=ft.CrossAxisAlignment.CENTER,
		# 				spacing=40  # Added spacing between the title and buttons
		# 			),
		# 			expand=True,  # This makes the container fill the entire window
		# 			alignment=ft.Alignment(-0.75, -1.0),  # Center the content
		# 		),
			],
			expand=False,  # Make sure the stack expands to fill the window
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
				expand=True,
			)
			car_speed_rows.append(row)

		return car_speed_rows