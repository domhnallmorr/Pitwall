from __future__ import annotations
from typing import TYPE_CHECKING
import os

import flet as ft

from pw_view import main_window, standings_page, grid_page
from pw_view.email_page.email_page import EmailPage
from pw_view.title_screen import title_screen
from pw_view.team_selection.team_selection_screen import TeamSelectionScreen
from pw_view.race_weekend import race_weekend_window, results_window
from pw_view.calendar_page import calendar_page
from pw_view.home_page import home_page
from pw_view.staff_page import staff_page, hire_staff_page
from pw_view.finance_page import finance_page
from pw_view.car_page import car_page
from pw_view.facility_page import facility_page, upgrade_facility_page
from pw_view.track_page.track_page import TrackPage

from pw_view.view_enums import ViewPageEnums

if TYPE_CHECKING:
	from pw_controller.pw_controller import Controller

class View:
	def __init__(self, controller: Controller, team_names: list[str], run_directory: str):
		self.controller = controller
		self.run_directory = run_directory

		self.main_app = self.controller.app

		self.page_header_style = ft.TextThemeStyle.DISPLAY_MEDIUM
		self.header2_style = ft.TextThemeStyle.DISPLAY_SMALL
		
		self.header3_style = ft.TextThemeStyle.LABEL_MEDIUM

		self.container_header2_size = 25
		self.SUBHEADER_FONT_SIZE = 18

		self.container_border_radius = 15

		self.dark_grey = "#23232A"
		self.primary_selected_color = "#7FA1C9"

		self.vscroll_buffer = 200
		
		self.default_button_style = ft.ButtonStyle(alignment=ft.alignment.center_left)
		self.default_button_clicked_style = ft.ButtonStyle(alignment=ft.alignment.center_left,
               										 side=ft.Border(left=ft.BorderSide(5, "blue")))

		self.positive_button_style = ft.ButtonStyle(color="#111418",
											  icon_color="#111418",
											  bgcolor={ft.ControlState.DEFAULT: ft.Colors.LIGHT_GREEN, ft.ControlState.DISABLED: ft.Colors.GREY},
											  alignment=ft.alignment.center_left,)
		self.clicked_button_style = ft.ButtonStyle(color=ft.Colors.BLACK, bgcolor=ft.Colors.PRIMARY)

		self.flags_small_path = fr"{self.run_directory}\pw_view\assets\flags_small"
		self.track_maps_path = fr"{self.run_directory}\pw_view\assets\track_maps"

		self.setup_background_images()
		self.setup_pages()
		self.setup_windows(team_names)

		self.main_app.views.append(self.main_window)
		# self.view_page_enums: ViewPageEnums = ViewPageEnums()

	def setup_background_images(self) -> None:
		image_path = fr"{self.run_directory}\pw_view\assets\background_image.jpg"
		self.background_image = ft.Image(
			src=os.path.abspath(image_path),  # Use absolute path for the local image
			fit=ft.ImageFit.COVER  # Ensure it covers the entire area
		)

		image_path = fr"{self.run_directory}\pw_view\assets\results_background_image.jpg"
		self.results_background_image = ft.Image(
			src=os.path.abspath(image_path),  # Use absolute path for the local image
			fit=ft.ImageFit.COVER  # Ensure it covers the entire area
		)

		image_path = fr"{self.run_directory}\pw_view\assets\race_background_image.jpg"
		self.race_background_image = ft.Image(
			src=os.path.abspath(image_path),  # Use absolute path for the local image
			fit=ft.ImageFit.COVER  # Ensure it covers the entire area
		)

	def setup_pages(self) -> None:
		self.home_page = home_page.HomePage(self)
		self.email_page = EmailPage(self)
		self.standings_page = standings_page.StandingsPage(self)
		self.calendar_page = calendar_page.CalendarPage(self)
		self.staff_page = staff_page.StaffPage(self)
		self.hire_staff_page = hire_staff_page.HireStaffPage(self)
		self.grid_page = grid_page.GridPage(self)
		self.finance_page = finance_page.FinancePage(self)
		self.car_page = car_page.CarPage(self)
		self.facility_page = facility_page.FacilityPage(self)
		self.upgrade_facility_page = upgrade_facility_page.UpgradeFacilitiesPage(self)
		self.track_page = TrackPage(self)

		self.results_window = results_window.ResultsWindow(self)

	def setup_windows(self, team_names: list[str]) -> None:
		self.title_screen = title_screen.TitleScreen(self, self.run_directory)
		self.main_window = main_window.MainWindow(self)
		self.team_selection_screen = TeamSelectionScreen(self, team_names)

	def go_to_race_weekend(self, data: dict) -> None:

		self.race_weekend_window = race_weekend_window.RaceWeekendWindow(self, data)
		self.main_app.views.append(self.race_weekend_window)

		self.main_app.update()

	def show_simulated_session_results(self) -> None:
		# self.results_window.continue_btn.disabled = True
		self.main_app.views.append(self.results_window)

		self.main_app.update()
		# self.results_window.continue_btn.disabled = False
		self.main_app.update() # update again, this is to avoid a problem where the continue button on the results page would not work if the user clicked on it too quickly (on_click not fully assigned by flet?????)

	def return_to_main_window(self, mode: str="post_race") -> None:
		assert mode in ["post_race", "load", "start_career"]
		self.main_app.views.clear()
		self.main_app.views.append(self.main_window)

		if mode == "post_race": # avoid updating the adance button when loading a career
			self.main_window.nav_sidebar.update_advance_button("advance")

		self.main_app.update()

		# Hack to get background image to appear on home page when the game starts
		if mode == "start_career":
			self.main_window.change_page(ViewPageEnums.HOME)

		self.main_app.update()

	def show_title_screen(self) -> None:
		self.main_app.views.append(self.title_screen)

		self.main_app.update()

	def show_team_selection_screen(self) -> None:
		# First update the team selection screen to show the first team details
		self.controller.team_selection_controller.setup_default_team()
		self.main_app.views.append(self.team_selection_screen)

		self.main_app.update()		

	def show_game_over_dialog(self) -> None:
		game_over_dialog = ft.AlertDialog(
            title=ft.Text("Game Over!", size=24, weight=ft.FontWeight.BOLD),
            content=ft.Text("Your game is finished. Better luck next time!", size=18),
            actions=[
                ft.TextButton("Exit", on_click=lambda e: self.main_app.window.close())
            ],
            actions_alignment=ft.MainAxisAlignment.END,
			modal=True
        )

		self.main_app.open(game_over_dialog)

