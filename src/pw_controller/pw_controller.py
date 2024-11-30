import copy

from pw_controller import calander_page_controller, staff_hire_controller, facilities_controller
from pw_model import pw_base_model
from pw_view import view
from pw_controller import race_controller, page_update_controller

class Controller:
	def __init__(self, app, run_directory, mode):
		self.app = app
		self.mode = mode
		roster = "1998_Roster"

		self.page_update_controller = page_update_controller.PageUpdateController(self)
		self.calendar_page_controller = calander_page_controller.CalendarPageController(self)
		self.staff_hire_controller = staff_hire_controller.StaffHireController(self)
		self.facilities_controller = facilities_controller.FacilitiesController(self)
		
		self.model = pw_base_model.Model(roster, run_directory)

		team_names = [t.name for t in self.model.teams]

		if self.mode in ["normal"]:
			self.view = view.View(self, team_names, run_directory)
		else:
			self.view = None # running headless tests

		self.page_update_controller.update_staff_page()

		# if self.mode in ["normal"]:
		# 	self.view.setup_race_pages()

		self.setup_new_season()
		
		self.view.show_title_screen()
		
	def start_career(self, team : str):
		self.model.start_career(team)
		
		self.setup_new_season()
		self.view.return_to_main_window()

	def load_career(self):
		self.model.load_career()
		#TODO not redefining the race controller here will result in errors in post race actions
		self.race_controller = race_controller.RaceController(self)

		self.refresh_ui()
		self.page_update_controller.update_main_window()
		self.view.return_to_main_window(mode="load")

	# TODO check if can remove this, seems redundant now
	def refresh_ui(self):
		self.page_update_controller.update_main_window()

		self.page_update_controller.refresh_ui()
		
	def advance(self):
		self.model.advance()

		if self.mode != "headless":
			self.page_update_controller.update_main_window()

			self.page_update_controller.refresh_ui()

		if self.model.season.current_week == 1:
			self.setup_new_season()

		self.update_email_button()

	def setup_new_season(self):
		
		if self.mode != "headless":
			# Setup the calander page to show the races upcoming in the new season
			self.update_facilities_page(new_season=True)
			self.page_update_controller.update_main_window()
			self.race_controller = race_controller.RaceController(self)

			self.page_update_controller.refresh_ui(new_season=True)

	def update_email_button(self):
		data = {"new_emails": self.model.inbox.new_emails}
		self.view.main_window.update_email_button(self.model.inbox.new_emails)

	def update_facilities_page(self, new_season=False):
		'''
		new_season is passed here to
		'''

		facility_values = [[team.name, team.facilities_model.factory_rating] for team in self.model.teams]
		facility_values.sort(key=lambda x: x[1], reverse=True) # sort, highest speed to lowest speed
		
		data = {
			"facility_values": facility_values,
		}

		self.view.facility_page.update_page(data)

		if new_season is True:
			self.view.facility_page.enable_upgrade_button()

	def go_to_race_weekend(self):
		self.race_controller = race_controller.RaceController(self)
		data = {
			"race_title": self.model.season.current_track_model.title
		}
		self.view.go_to_race_weekend(data)

	def return_to_main_window(self):
		'''
		Post race, remove race weekend, update advance button to allow progress to next week
		'''
		
		self.page_update_controller.refresh_ui()
		self.view.return_to_main_window()
		# self.view.main_window.update_advance_btn("advance")

	def post_race_actions(self):
		self.model.season.post_race_actions()
		self.model.save_career()

		self.page_update_controller.update_standings_page()
		self.return_to_main_window()