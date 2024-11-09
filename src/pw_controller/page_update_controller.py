'''
A controller dedicated to refreshing the off track UI pages
'''
import copy

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
		self.update_finance_page()
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

			"staff_values": staff_values,

		}

		self.view.staff_page.update_page(copy.deepcopy(data), new_season)

	def update_standings_page(self):
		data = {
			"drivers_standings_df": self.model.season.standings_manager.drivers_standings_df.copy(deep=True),
			"constructors_standings_df": self.model.season.standings_manager.constructors_standings_df.copy(deep=True)
		}

		self.view.standings_page.update_standings(data)

	def update_finance_page(self) -> None:
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
