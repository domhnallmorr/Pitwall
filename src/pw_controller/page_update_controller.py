'''
A controller dedicated to refreshing the off track UI pages
'''
import copy
from pw_model.pw_model_enums import StaffRoles

class PageUpdateController:
	def __init__(self, controller):
		self.controller = controller

	@property
	def model(self):
		return self.controller.model
	
	@property
	def view(self):
		return self.controller.view
	
	def refresh_ui(self, new_season: bool=False):
		self.update_calendar_page()
		self.update_car_page()
		self.update_email_page()
		self.update_finance_page()
		self.update_grid_page()
		self.update_home_page()
		self.update_staff_page(new_season)
		self.update_standings_page()

	def update_staff_page(self, new_season: bool=False) -> None:
		team_model = self.model.get_team_model(self.model.player_team)

		staff_values = [[team.name, team.number_of_staff] for team in self.model.teams]
		staff_values.sort(key=lambda x: x[1], reverse=True) # sort, highest to lowest

		data = {
			"driver1": team_model.driver1,
			"driver1_age": team_model.driver1_model.age,
			"driver1_country": team_model.driver1_model.country,
			"driver1_speed": team_model.driver1_model.speed,
			"driver1_contract_length": team_model.driver1_model.contract.contract_length,
			"driver1_salary": team_model.driver1_model.contract.salary,
			"driver1_retiring": team_model.driver1_model.retiring,
			"player_requiring_driver1": self.model.staff_market.player_requiring_driver1,

			"driver2": team_model.driver2,
			"driver2_age": team_model.driver2_model.age,
			"driver2_country": team_model.driver2_model.country,
			"driver2_speed": team_model.driver2_model.speed,
			"driver2_contract_length": team_model.driver2_model.contract.contract_length,
			"driver2_salary": team_model.driver2_model.contract.salary,
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
			"player_requiring_technical_director": self.model.staff_market.compile_teams_requiring_manager(StaffRoles.TECHNICAL_DIRECTOR),

			"staff_values": staff_values,

		}

		self.view.staff_page.update_page(copy.deepcopy(data), new_season)

	def update_standings_page(self):
		data = {
			"drivers_standings_df": self.model.season.standings_manager.drivers_standings_df,#.copy(deep=True),
			"constructors_standings_df": self.model.season.standings_manager.constructors_standings_df#.copy(deep=True)
		}

		self.view.standings_page.update_standings(data)

	def update_email_page(self):
		data = {
			"emails": copy.deepcopy(self.model.inbox.emails),
		}
		self.view.email_page.update_page(data)

	def update_finance_page(self) -> None:
		data = {
			"total_sponsorship": copy.deepcopy(self.model.player_team_model.finance_model.total_sponsorship),
			"prize_money": copy.deepcopy(self.model.player_team_model.finance_model.prize_money),
			"drivers_payments": copy.deepcopy(self.model.player_team_model.finance_model.drivers_payments),
			"total_income": copy.deepcopy(self.model.player_team_model.finance_model.total_income),
			
			"total_staff_costs_per_year": copy.deepcopy(self.model.player_team_model.finance_model.total_staff_costs_per_year),
			"drivers_salary": copy.deepcopy(self.model.player_team_model.finance_model.drivers_salary),
			"technical_director_salary": copy.deepcopy(self.model.player_team_model.technical_director_model.contract.salary),
			"commercial_manager_salary": copy.deepcopy(self.model.player_team_model.commercial_manager_model.contract.salary),
			"race_costs": 8_000_000, # hard code this for now TODO, make it variable
			"car_costs": self.model.player_team_model.finance_model.car_cost, 
			"total_expenditure": copy.deepcopy(self.model.player_team_model.finance_model.total_expenditure), # hard code this for now TODO, make it variable
			
			"balance_history": copy.deepcopy(self.model.player_team_model.finance_model.balance_history),
			"balance_history_dates": copy.deepcopy(self.model.player_team_model.finance_model.balance_history_dates),
		}

		self.view.finance_page.update_page(data)

	def update_grid_page(self):
		data = {
			"year": self.model.year,
			"grid_this_year_df": self.model.staff_market.grid_this_year_df.copy(deep=True),
			"grid_next_year_df": self.model.staff_market.grid_next_year_df.copy(deep=True),
			"grid_next_year_announced_df": self.model.staff_market.grid_next_year_announced_df.copy(deep=True),
		}

		self.view.grid_page.update_page(data)
		self.view.grid_page.change_display(None)

	def update_home_page(self):
		data = {
			"next_race": self.model.season.next_race,
			"next_race_week": self.model.season.next_race_week,
			"current_position": self.model.player_team_model.current_position + 1, # pos is zero indexed
			"constructors_standings_df": self.model.season.standings_manager.constructors_standings_df.copy(deep=True),

			"driver1": self.model.player_team_model.driver1,
			"driver1_contract": self.model.player_team_model.driver1_model.contract.contract_length,
			"driver2": self.model.player_team_model.driver2,
			"driver2_contract": self.model.player_team_model.driver2_model.contract.contract_length,
			"technical_director": self.model.player_team_model.technical_director,
			"technical_director_contract": self.model.player_team_model.technical_director_model.contract.contract_length,

			"team_average_stats": self.model.gen_team_average_stats(),
			"player_car": self.model.player_team_model.car_model.speed,
			"player_drivers": self.model.player_team_model.average_driver_skill,
			"player_managers": self.model.player_team_model.average_manager_skill,
			"player_staff": self.model.player_team_model.number_of_staff,
			"player_facilities": self.model.player_team_model.facilities_model.factory_rating,
			"player_sponsorship": self.model.player_team_model.finance_model.total_sponsorship,
		}
		self.view.home_page.update_page(data)

	def update_calendar_page(self):
		data = {
			"calendar": self.model.calendar.copy(deep=True)
		}

		self.view.calendar_page.update_page(data)

	def update_car_page(self):
		car_speeds = [[team.name, team.car_model.speed] for team in self.model.teams]
		car_speeds.sort(key=lambda x: x[1], reverse=True) # sort, highest speed to lowest speed
		
		data = {
			"car_speeds": car_speeds,
		}

		self.view.car_page.update_page(data)