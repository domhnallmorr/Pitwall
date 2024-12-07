from __future__ import annotations
import copy
from enum import Enum
from typing import TYPE_CHECKING

from pw_model.staff_market import staff_market
from pw_model.staff_market import driver_transfers, manager_transfers
from pw_model.pw_model_enums import StaffRoles

if TYPE_CHECKING:
	from pw_controller.pw_controller import Controller
	from pw_model.pw_base_model import Model
	from pw_model.senior_staff.senior_staff import StaffPersonDetails

class StaffHireController:
	def __init__(self, controller: Controller):
		self.controller = controller

		self.driver_idx = None # variable to track which driver_idx (driver1, driver2) the player wants to replace

	@property
	def model(self) -> Model:
		return self.controller.model

	def launch_replace_staff(self, role: Enum) -> None:
		assert role in [StaffRoles.DRIVER1, StaffRoles.DRIVER2, StaffRoles.TECHNICAL_DIRECTOR, StaffRoles.COMMERCIAL_MANAGER]
		
		self.role = role

		if role in [StaffRoles.DRIVER1, StaffRoles.DRIVER2]:
			free_agents = driver_transfers.get_free_agents(self.model, for_player_team=True)
		else:
			free_agents = manager_transfers.get_free_agents(self.model, role, for_player_team=True)

		self.controller.view.hire_staff_page.update_free_agent_list(free_agents, role)
		self.controller.view.main_window.change_page("hire_staff")
		self.controller.view.main_app.update()

	def complete_hire(self, driver_hired: str, role: Enum) -> None:
		
		self.model.staff_market.complete_hiring(driver_hired, self.model.player_team, role)
		self.controller.page_update_controller.update_grid_page()
		self.controller.page_update_controller.update_email_page()
		self.controller.page_update_controller.update_staff_page()
		self.controller.view.main_window.change_page("email")

	def get_staff_details(self, name: str, role: Enum) -> StaffPersonDetails:
		'''
		returns typeddict with personal details of the staff member
		'''
		if role in [StaffRoles.DRIVER1, StaffRoles.DRIVER2]:
			return copy.deepcopy(self.controller.model.get_driver_model(name).details)
		elif role == StaffRoles.TECHNICAL_DIRECTOR:
			return copy.deepcopy(self.controller.model.get_technical_director_model(name).details)
		elif role == StaffRoles.COMMERCIAL_MANAGER:
			return copy.deepcopy(self.controller.model.get_commercial_manager_model(name).details)
	
	def hire_workforce(self) -> None:
		current_workforce = self.controller.model.player_team_model.number_of_staff
		# Open the dialog in view
		self.controller.view.staff_page.open_workforce_dialog(current_workforce)

	def update_workforce(self, number_of_staff: int) -> None:
		self.controller.model.player_team_model.number_of_staff = number_of_staff
		self.controller.view.staff_page.disable_hire_workforce_btn()
		self.controller.page_update_controller.refresh_ui()
		self.controller.view.staff_page.display_workforce(None)

