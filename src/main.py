import logging 
import os 

import flet as ft

from pw_controller import pw_controller

def main(page: ft.Page):
	# disable flet debug messages
	flet_logger = logging.getLogger("flet_core")
	flet_logger.setLevel(logging.WARNING)

	flet_logger = logging.getLogger("flet_runtime")
	flet_logger.setLevel(logging.WARNING)


	page.theme_mode = ft.ThemeMode.DARK
	page.window.maximized = True
	version = "0.0.3"
	page.title = f"Pitwall {version}"
	
	run_directory = os.path.dirname(os.path.join(os.path.abspath(__file__)))

	controller = pw_controller.Controller(page, run_directory, "normal")
	page.update()

ft.app(target=main)

