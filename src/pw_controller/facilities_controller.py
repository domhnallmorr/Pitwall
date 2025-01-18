from __future__ import annotations
from typing import TYPE_CHECKING
from pw_model.staff_market import staff_market

if TYPE_CHECKING:
	from pw_controller.pw_controller import Controller
	from pw_model.pw_base_model import Model
	from pw_view.view import View

class FacilitiesController:
	def __init__(self, controller: Controller):
		self.controller = controller
	
	@property
	def model(self) -> Model:
		return self.controller.model

	@property
	def view(self) -> View:
		return self.controller.view
	
	def clicked_update_facilities(self) -> None:
		current_facility_state = self.model.player_team_model.facilities_model.factory_rating
		self.view.upgrade_facility_page.update_current_state(current_facility_state)
		
		self.controller.view.main_window.change_page("upgrade_facility")

	def update_facilties(self, percentage: int, cost: int) -> None:
		self.model.player_team_model.facilities_model.update_facilties(percentage)
		self.model.player_team_model.finance_model.update_facilities_cost(cost)

		self.controller.view.facility_page.disable_upgrade_button() # ensure player can't update again this season

		self.controller.page_update_controller.update_facilities_page()

		self.model.inbox.generate_player_facility_update_email()
		self.controller.page_update_controller.update_email_page()
		self.controller.view.main_window.change_page("facility")
