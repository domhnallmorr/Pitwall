
from pw_model.staff_market import staff_market

class PWDriverHireController:
	def __init__(self, controller):
		self.controller = controller

		self.driver_idx = None # variable to track which driver_idx (driver1, driver2) the player wants to replace
	@property
	def model(self):
		return self.controller.model

	def launch_replace_driver(self, driver_idx):
		assert driver_idx in ["driver1", "driver2"]
		
		self.driver_idx = driver_idx

		free_agents = self.controller.model.driver_market.get_free_agents()

		self.controller.view.hire_driver_page.update_free_agent_list(free_agents)

		self.controller.view.main_window.change_page("hire_driver")

		self.controller.view.main_app.update()

	def complete_hire(self, driver_hired):
		
		self.model.driver_market.complete_driver_hiring(driver_hired, self.model.player_team, self.driver_idx)
		self.controller.update_grid_page()
		self.controller.update_email_page()
		self.controller.update_staff_page()
