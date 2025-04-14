

from __future__ import annotations
from typing import TYPE_CHECKING

from pw_view.view_enums import ViewPageEnums

if TYPE_CHECKING:
	from pw_controller.pw_controller import Controller
	from pw_model.pw_base_model import Model

class TestingController:
	def __init__(self, controller: Controller):
		self.controller = controller

	@property	
	def model(self) -> Model:
		return self.controller.model

	def go_to_test(self):
		# Show the test configuration dialog
		self.controller.view.show_test_dialog()
		
	def confirm_test_options(self, attend_test: bool, distance_km: int):
		if attend_test:
			self.model.player_team_model.testing_model.run_test(distance_km)
			self.controller.page_update_controller.update_car_page()
		else:
			self.model.player_team_model.testing_model.skip_test()
		
		self.controller.page_update_controller.update_main_window()
		self.controller.page_update_controller.update_email_page()
		self.controller.view.main_window.update_email_button(self.model.inbox.new_emails)
		self.controller.view.main_window.change_page(ViewPageEnums.EMAIL)