
from pw_model.driver_market import driver_market

class FacilitiesController:
	def __init__(self, controller):
		self.controller = controller
	
	@property
	def model(self):
		return self.controller.model

	@property
	def view(self):
		return self.controller.view
	
	def clicked_update_facilities(self):
		current_facility_state = self.model.player_team_model.facilities_model.factory_rating
		self.view.upgrade_facility_page.update_current_state(current_facility_state)
		
		self.controller.view.main_window.change_page("upgrade_facility")

	def update_facilties(self, percentage, cost):
		self.model.player_team_model.facilities_model.update_facilties(percentage)
		self.model.player_team_model.finance_model.update_facilities_cost(cost)

		self.controller.view.facility_page.disable_upgrade_button() # ensure player can't update again this season

		self.controller.update_facilities_page()

		self.model.inbox.generate_player_facility_update_email()
		self.controller.update_email_page()
