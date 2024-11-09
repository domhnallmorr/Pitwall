import copy
from pw_model.staff_market import staff_market

class StaffHireController:
	def __init__(self, controller):
		self.controller = controller

		self.driver_idx = None # variable to track which driver_idx (driver1, driver2) the player wants to replace
	@property
	def model(self):
		return self.controller.model

	def launch_replace_driver(self, driver_idx: str) -> None:
		assert driver_idx in ["driver1", "driver2"]
		
		self.driver_idx = driver_idx

		free_agents = self.controller.model.staff_market.get_free_agents(for_player_team=True)

		self.controller.view.hire_driver_page.update_free_agent_list(free_agents)

		self.controller.view.main_window.change_page("hire_driver")

		self.controller.view.main_app.update()

	def complete_hire(self, driver_hired: str) -> None:
		
		self.model.staff_market.complete_driver_hiring(driver_hired, self.model.player_team, self.driver_idx)
		self.controller.update_grid_page()
		self.controller.update_email_page()
		self.controller.page_update_controller.update_staff_page()
		self.controller.view.main_window.change_page("email")

	def get_driver_details(self, driver_name: str) -> dict:
		return copy.deepcopy(self.controller.model.get_driver_model(driver_name).details)
	
	def hire_workforce(self):
		current_workforce = self.controller.model.player_team_model.number_of_staff
		# Open the dialog in view
		self.controller.view.staff_page.open_workforce_dialog(current_workforce)

	def update_workforce(self, number_of_staff: int) -> None:
		self.controller.model.player_team_model.number_of_staff = number_of_staff
		self.controller.view.staff_page.disable_hire_workforce_btn()
		self.controller.page_update_controller.refresh_ui()
		self.controller.view.staff_page.display_workforce(None)

