import os
import flet as ft


class TitleScreen(ft.View):
	def __init__(self, view, run_directory):
		self.view = view

		self.setup_page(run_directory)

		controls = [
			self.background_stack,
		]

		# contents = [nav_sidebar, self.view.home_page]

		super().__init__(controls=controls, padding=0)

	def setup_page(self, run_directory: str) -> None:
		# Create a resizable image widget for the background
		image_path = fr"{self.view.run_directory}\pw_view\assets\title_screen.jpg"
		
		self.background_image = ft.Image(
			src=os.path.abspath(image_path),  # Use absolute path for the local image
			fit=ft.ImageFit.COVER  # Ensure it covers the entire area
		)

		# Create the buttons for "New Career", "Load", and "Quit"
		new_career_button = ft.ElevatedButton("New Career", on_click=self.new_career_click, width=200)

		if os.path.isfile(f"{run_directory}\\save_game.db"):
			disabled = False
		else:
			disabled = True
			
		load_button = ft.ElevatedButton("Load", on_click=self.load_game_click, width=200, disabled=disabled)
		quit_button = ft.ElevatedButton("Quit", on_click=self.quit_game_click, width=200)

		# Create a container for the buttons with some spacing and a light shadow
		button_container = ft.Column(
			[
				new_career_button,
				load_button,
				quit_button
			],
			spacing=20,  # Increased space between buttons for better separation
			alignment=ft.MainAxisAlignment.CENTER,
			horizontal_alignment=ft.CrossAxisAlignment.CENTER,
		)

		# Create a stack with the background image and buttons
		self.background_stack = ft.Stack(
			[
				# Add the resizable background image
				self.background_image,
				# Add the buttons on top of the image
				ft.Container(
					content=ft.Column(
						[
							ft.Text(
								"Pitwall",
								size=80,  # Increased size for the title
								color=ft.colors.WHITE,
								weight=ft.FontWeight.BOLD,
								bgcolor=ft.colors.BLACK54,  # Add a semi-transparent background to the text
							),
							button_container,
						],
						alignment=ft.MainAxisAlignment.CENTER,
						horizontal_alignment=ft.CrossAxisAlignment.CENTER,
						spacing=40  # Added spacing between the title and buttons
					),
					expand=True,  # This makes the container fill the entire window
					alignment=ft.Alignment(-0.75, -1.0),  # Center the content
				),
			],
			expand=True,  # Make sure the stack expands to fill the window
		)

		self.view.main_app.on_resized = self.resize_image
		self.resize_image(None)

	def new_career_click(self, e: ft.ControlEvent) -> None:
		e.control.disabled = True
		self.view.show_team_selection_screen()

	def load_game_click(self, e: ft.ControlEvent) -> None:
		self.view.controller.load_career()

	def quit_game_click(self, e: ft.ControlEvent) -> None:
		self.view.main_app.window.close()

	def resize_image(self, e: ft.ControlEvent) -> None:
        # Get the window's aspect ratio
		screen_width = self.view.main_app.window.width
		screen_height = self.view.main_app.window.height

        # Set image size dynamically to cover the screen fully
		self.background_image.width = screen_width
		self.background_image.height = screen_height

        # Force the page to update with the new image size
		self.view.main_app.update()

