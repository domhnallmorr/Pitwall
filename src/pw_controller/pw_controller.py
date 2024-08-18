import copy

from pw_controller import calander_page_controller
from pw_model import pw_model, update_window_functions
from pw_view import view
from pw_controller import race_controller

class Controller:
	def __init__(self, app, run_directory, mode):
		self.app = app
		self.mode = mode
		roster = "1998_Roster"

		self.calendar_page_controller = calander_page_controller.CalendarPageController(self)
		
		self.model = pw_model.Model(roster, run_directory)

		if self.mode in ["normal"]:
			self.view = view.View(self)
		else:
			self.view = None # running headless tests

		self.update_standings_page()
		#TODO maybe consider creating the race_controller when we go the a race weekend
		self.race_controller = race_controller.RaceController(self)

		# if self.mode in ["normal"]:
		# 	self.view.setup_race_pages()

		self.setup_new_season()
		
		# self.update_main_window()
		

	def advance(self):
		self.model.advance()

		if self.mode != "headless":
			self.update_main_window()

		if self.model.season.current_week == 1:
			self.setup_new_season()

	def update_main_window(self):
		data = update_window_functions.get_main_window_data(self.model)
		self.view.main_window.update_window(data)
		# self.update_email_button()

	def setup_new_season(self):
		
		if self.mode != "headless":
			# Setup the calander page to show the races upcoming in the new season
			self.update_email_page()
			self.update_calendar_page()
			self.update_standings_page()
			self.update_home_page()

	def update_home_page(self):
		data = {
			"next_race": self.model.season.next_race,
			"constructors_standings_df": self.model.season.standings_manager.constructors_standings_df.copy(deep=True)
		}
		self.view.home_page.update_page(data)

	def update_email_button(self):
		data = {"number_unread": self.model.inbox.number_unread}
		self.view.main_window.update_email_button(data)

	def update_standings_page(self):
		data = {
			"drivers_standings_df": self.model.season.standings_manager.drivers_standings_df.copy(deep=True),
			"constructors_standings_df": self.model.season.standings_manager.constructors_standings_df.copy(deep=True)
		}

		self.view.standings_page.update_standings(data)

	def update_car_page(self):
		car_speeds = {}
		for team in self.model.teams:
			car_speeds[team.name] = team.car_model.speed
		
		data = {
			"car_speeds": car_speeds
		}

		self.view.car_page.update_plot(data)

	def update_calendar_page(self):
		data = {
			"calendar": self.model.calendar.copy(deep=True)
		}

		self.view.calendar_page.update_page(data)


	def update_email_page(self):
		data = {
			"emails": copy.deepcopy(self.model.inbox.emails),
		}
		self.view.email_page.update_page(data)

	def go_to_race_weekend(self):
		data = {
			"race_title": self.model.season.current_track_model.title
		}
		self.view.go_to_race_weekend(data)

	def return_to_main_window(self):
		'''
		Post race, remove race weekend, update advance button to allow progress to next week
		'''
		self.update_standings_page()
		# self.update_home_page()

		self.view.return_to_main_window()
		# self.view.main_window.update_advance_btn("advance")