from __future__ import annotations
import os
from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
	from pw_view.view import View

class TitleScreen(ft.View):
	def __init__(self, view: View, run_directory: str):
		self.view = view

		self.setup_page(run_directory)

		controls = [
			self.background_stack,
		]

		# contents = [nav_sidebar, self.view.home_page]

		super().__init__(controls=controls, padding=0)

	def setup_page(self, run_directory: str) -> None:
		image_path = fr"{self.view.run_directory}\pw_view\assets\title_screen.jpg"

		self.background_image = ft.Image(
			src=os.path.abspath(image_path),
			fit=ft.ImageFit.COVER
		)

		# Button style: translucent, outlined, subtle glow, hover animation
		button_style = ft.ButtonStyle(
			bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
			shape=ft.RoundedRectangleBorder(radius=10),
			side=ft.BorderSide(1, ft.Colors.WHITE),
			color=ft.Colors.WHITE,
			overlay_color=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
			padding=ft.Padding(12, 16, 12, 16),
			animation_duration=300,
		)

		disabled_style = ft.ButtonStyle(
				bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
				shape=ft.RoundedRectangleBorder(radius=10),
				side=ft.BorderSide(1, ft.Colors.WHITE),
				color=ft.Colors.with_opacity(0.3, ft.Colors.WHITE),  # Faded text
				overlay_color=ft.Colors.with_opacity(0.0, ft.Colors.WHITE),  # No hover overlay
				padding=ft.Padding(12, 16, 12, 16),
				animation_duration=300,
			)

		new_career_button = ft.ElevatedButton("New Career", on_click=self.new_career_click, width=220, style=button_style)

		load_button = ft.ElevatedButton(
			"Load",
			on_click=self.load_game_click,
			width=220,
			disabled=not os.path.isfile(f"{run_directory}\\save_game.db"),
			style=button_style if os.path.isfile(f"{run_directory}\\save_game.db") else disabled_style
		)

		quit_button = ft.ElevatedButton("Quit", on_click=self.quit_game_click, width=220, style=button_style)

		def glow_button(button: ft.ElevatedButton) -> ft.Container:
			return ft.Container(
				content=button,
				shadow=ft.BoxShadow(
					spread_radius=0,
					blur_radius=8,
					color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
					blur_style=ft.ShadowBlurStyle.NORMAL
				)
			)

		button_container = ft.Row(
			[
				glow_button(new_career_button),
				glow_button(load_button),
				glow_button(quit_button),
			],
			spacing=20,
			alignment=ft.MainAxisAlignment.CENTER,
			# horizontal_alignment=ft.CrossAxisAlignment.CENTER,
		)

		# Shift content downward to avoid covering the title
		self.background_stack = ft.Stack(
			[
				self.background_image,
				ft.Container(
					content=button_container,
					expand=True,
					alignment=ft.Alignment(-1.0, 0.80),  # Lowered from center to let PITWALL breathe
				),
			],
			expand=True,
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

		#TODO move all this to the view
		self.view.background_image.width = screen_width
		self.view.background_image.height = screen_height

		self.view.results_background_image.width = screen_width
		self.view.results_background_image.height = screen_height

        # Force the page to update with the new image size
		self.view.main_app.update()

