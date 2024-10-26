import copy

from pw_controller import calander_page_controller, driver_hire_controller, facilities_controller
from pw_model import pw_model, update_window_functions
from pw_view import view
from pw_controller import race_controller

class Controller:
	def __init__(self, app, run_directory, mode):
		self.app = app
		self.mode = mode
		roster = "1998_Roster"

		self.calendar_page_controller = calander_page_controller.CalendarPageController(self)
		self.driver_hire_controller = driver_hire_controller.PWDriverHireController(self)
		self.facilities_controller = facilities_controller.FacilitiesController(self)
		
		self.model = pw_model.Model(roster, run_directory)

		team_names = [t.name for t in self.model.teams]

		if self.mode in ["normal"]:
			self.view = view.View(self, team_names, run_directory)
		else:
			self.view = None # running headless tests


		self.update_staff_page()

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
		self.view.return_to_main_window()

	def refresh_ui(self):
		self.update_main_window()
		self.update_standings_page()
		self.update_grid_page()
		self.update_finance_page()
		self.update_staff_page()
		self.update_email_page()
		
	def advance(self):
		self.model.advance()

		if self.mode != "headless":
			self.update_main_window()
			self.update_email_page()
			self.update_standings_page()
			self.update_finance_page()

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
			self.update_finance_page()
			self.update_grid_page()
			self.update_staff_page()
			self.update_car_page()
			self.update_facilities_page(new_season=True)
			self.update_main_window()
			self.race_controller = race_controller.RaceController(self)

			self.update_standings_page()

	def update_home_page(self):
		data = {
			"next_race": self.model.season.next_race,
			"constructors_standings_df": self.model.season.standings_manager.constructors_standings_df.copy(deep=True),
			"team_average_stats": self.model.gen_team_average_stats(),
			"player_car": self.model.player_team_model.car_model.speed,
			"player_drivers": self.model.player_team_model.average_driver_skill,
			"player_managers": self.model.player_team_model.average_manager_skill,
			"player_staff": self.model.player_team_model.number_of_staff,
			"player_facilities": self.model.player_team_model.facilities_model.factory_rating,
			"player_sponsorship": self.model.player_team_model.finance_model.total_sponsorship,
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

	def update_staff_page(self):
		team_model = self.model.get_team_model(self.model.player_team)
		data = {
			"driver1": team_model.driver1,
			"driver1_age": team_model.driver1_model.age,
			"driver1_country": team_model.driver1_model.country,
			"driver1_speed": team_model.driver1_model.speed,
			"driver1_contract_length": team_model.driver1_model.contract.contract_length,
			"driver1_retiring": team_model.driver1_model.retiring,
			"player_requiring_driver1": self.model.staff_market.player_requiring_driver1,

			"driver2": team_model.driver2,
			"driver2_age": team_model.driver2_model.age,
			"driver2_country": team_model.driver2_model.country,
			"driver2_speed": team_model.driver2_model.speed,
			"driver2_contract_length": team_model.driver2_model.contract.contract_length,
			"driver2_retiring": team_model.driver2_model.retiring,
			"player_requiring_driver2": self.model.staff_market.player_requiring_driver2,

			"commercial_manager": team_model.commercial_manager,
			"commercial_manager_age": team_model.commercial_manager_model.age,
			"commercial_manager_contract_length": team_model.commercial_manager_model.contract.contract_length,
			"commercial_manager_skill": team_model.commercial_manager_model.skill,

			"technical_director": team_model.technical_director,
			"technical_director_age": team_model.technical_director_model.age,
			"technical_director_contract_length": team_model.technical_director_model.contract.contract_length,
			"technical_director_skill": team_model.technical_director_model.skill,

		}

		self.view.staff_page.update_page(copy.deepcopy(data))

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

	def update_grid_page(self):
		data = {
			"year": self.model.year,
			"grid_this_year_df": self.model.staff_market.grid_this_year_df.copy(deep=True),
			"grid_next_year_df": self.model.staff_market.grid_next_year_df.copy(deep=True),
		}

		self.view.grid_page.update_page(data)
		self.view.grid_page.change_display(None)

	def update_email_page(self):
		data = {
			"emails": copy.deepcopy(self.model.inbox.emails),
		}
		self.view.email_page.update_page(data)

	def update_finance_page(self):
		data = {
			"total_sponsorship": copy.deepcopy(self.model.player_team_model.finance_model.total_sponsorship),
			"prize_money": copy.deepcopy(self.model.player_team_model.finance_model.prize_money),
			"total_staff_costs_per_year": copy.deepcopy(self.model.player_team_model.finance_model.total_staff_costs_per_year),
			"technical_director_salary": copy.deepcopy(self.model.player_team_model.technical_director_model.contract.salary),
			"commercial_manager_salary": copy.deepcopy(self.model.player_team_model.commercial_manager_model.contract.salary),
			"race_costs": 500_000, # hard code this for now TODO, make it variable
			"balance_history": copy.deepcopy(self.model.player_team_model.finance_model.balance_history),
			"balance_history_dates": copy.deepcopy(self.model.player_team_model.finance_model.balance_history_dates),
		}
		self.view.finance_page.update_page(data)

	def update_car_page(self):
		car_speeds = [[team.name, team.car_model.speed] for team in self.model.teams]
		car_speeds.sort(key=lambda x: x[1], reverse=True) # sort, highest speed to lowest speed
		
		data = {
			"car_speeds": car_speeds,
		}

		self.view.car_page.update_page(data)

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
		
		# self.update_home_page()

		self.view.return_to_main_window()
		# self.view.main_window.update_advance_btn("advance")

	def post_race_actions(self):
		self.model.season.post_race_actions()
		self.model.save_career()

		self.update_standings_page()
		self.return_to_main_window()