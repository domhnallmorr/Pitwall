import copy

from flet import Page

from pw_controller import calander_page_controller, facilities_controller
from pw_controller.staff_page import staff_hire_controller
from pw_model import pw_base_model
from pw_view import view
from pw_controller import race_controller, page_update_controller
from pw_controller.email_page.email_controller import EmailController
from pw_controller.team_selection.team_selection_controller import TeamSelectionController
from pw_controller.track_page.track_page_controller import TrackPageController
from pw_controller.game_modes import GameModes

class Controller:
	def __init__(self, app: Page, run_directory: str, mode: str):
		self.app = app
		self.mode = mode
		roster = "1998_Roster"

		self.page_update_controller = page_update_controller.PageUpdateController(self)
		self.calendar_page_controller = calander_page_controller.CalendarPageController(self)
		self.staff_hire_controller = staff_hire_controller.StaffHireController(self)
		self.facilities_controller = facilities_controller.FacilitiesController(self)
		self.email_controller = EmailController(self)
		self.team_selection_controller = TeamSelectionController(self)
		self.track_page_controller = TrackPageController(self)
		
		self.model = pw_base_model.Model(roster, run_directory)

		team_names = [t.name for t in self.model.teams]

		if self.mode in [GameModes.NORMAL]:
			self.view = view.View(self, team_names, run_directory)
			self.page_update_controller.update_staff_page()
		else:
			self.view = None # running headless

		self.setup_new_season()
		
		if self.mode in [GameModes.NORMAL]:
			self.view.show_title_screen()
		
	def start_career(self, team: str) -> None:
		self.model.start_career(team)
		
		self.setup_new_season()
		self.view.return_to_main_window(mode="start_career")

	def load_career(self) -> None:
		self.model.load_career()
		#TODO not redefining the race controller here will result in errors in post race actions
		self.race_controller = race_controller.RaceController(self)

		self.refresh_ui()
		self.page_update_controller.update_main_window()
		self.view.return_to_main_window(mode="load")

	# TODO check if can remove this, seems redundant now
	def refresh_ui(self) -> None:
		self.page_update_controller.update_main_window()

		self.page_update_controller.refresh_ui()
		
	def advance(self) -> None:
		self.model.advance()

		if self.mode != GameModes.HEADLESS:
			self.page_update_controller.update_main_window()

			self.page_update_controller.refresh_ui()

		if self.model.season.calendar.current_week == 1:
			self.setup_new_season()

		self.update_email_button()

		self.check_game_over()

	def setup_new_season(self) -> None:
		
		if self.mode in [GameModes.NORMAL]:
			# Setup the calander page to show the races upcoming in the new season
			self.page_update_controller.update_main_window()
			self.race_controller = race_controller.RaceController(self)

			self.page_update_controller.refresh_ui(new_season=True)

	def update_email_button(self) -> None:
		self.view.main_window.update_email_button(self.model.inbox.new_emails)


	def go_to_race_weekend(self) -> None:
		self.race_controller = race_controller.RaceController(self)
		data = {
			"race_title": self.model.season.calendar.current_track_model.title,
			"country": self.model.season.calendar.current_track_model.country
		}
		self.view.go_to_race_weekend(data)

	def return_to_main_window(self) -> None:
		'''
		Post race, remove race weekend, update advance button to allow progress to next week
		'''
		
		self.page_update_controller.refresh_ui()
		self.view.return_to_main_window()
		# self.view.main_window.update_advance_btn("advance")

	def post_race_actions(self) -> None:
		winner = self.race_controller.race_model.current_session.winner
		player_driver1_crashed = self.race_controller.race_model.current_session.player_driver1_crashed
		player_driver2_crashed = self.race_controller.race_model.current_session.player_driver2_crashed

		self.model.season.post_race_actions(winner, player_driver1_crashed, player_driver2_crashed)
		self.model.save_career()

		self.page_update_controller.update_standings_page()
		self.return_to_main_window()

	def check_game_over(self) -> None:
		game_over = False

		if self.model.year == 2024:
			game_over = True

		if game_over is False and self.model.player_team is not None:
			if self.model.player_team_model.finance_model.consecutive_weeks_in_debt >= 2:
				game_over = True

		if game_over is True:
			self.view.show_game_over_dialog()
