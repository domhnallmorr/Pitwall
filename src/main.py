from enum import Enum
import logging 
import os 
import time

import flet as ft

from pw_controller import pw_controller
from pw_controller.game_modes import GameModes

def main(page: ft.Page):
	# disable debug messages
	flet_logger = logging.getLogger("flet_core")
	flet_logger.setLevel(logging.WARNING)

	flet_logger = logging.getLogger("flet_runtime")
	flet_logger.setLevel(logging.WARNING)

	flet_logger = logging.getLogger("flet")
	flet_logger.setLevel(logging.WARNING)

	matplotlib_logger = logging.getLogger("matplotlib")
	matplotlib_logger.setLevel(logging.WARNING)

	pil_logger = logging.getLogger("PIL.PngImagePlugin")
	pil_logger.setLevel(logging.WARNING)

	page.theme_mode = ft.ThemeMode.DARK
	page.window.padding = 0

	page.window.maximized = True

	version = "1.21.0"
	page.title = f"Pitwall {version}"
	
	run_directory = os.path.dirname(os.path.join(os.path.abspath(__file__)))

	controller = pw_controller.Controller(page, run_directory, GameModes.NORMAL)

	page.window.full_screen = True
	page.update()

ft.app(target=main)

