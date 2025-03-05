from __future__ import annotations
from typing import TYPE_CHECKING

from pw_model.car_development.car_development_model import CarDevelopmentEnums

if TYPE_CHECKING:
	from pw_controller.pw_controller import Controller

class CarDevelopmentController:
	def __init__(self, controller: Controller):
		self.controller = controller
		

	def car_development_selected(self, development_type: CarDevelopmentEnums) -> None:
		def handle_dialog_result(e):
			if self.controller.view.confirm_dialog.choice is True:
				# update model
				self.controller.model.player_team_model.car_development_model.start_development(development_type)
				# update email
				self.controller.page_update_controller.update_email_page()
				# update car page
				self.controller.page_update_controller.update_car_page()

		# ask confirm
		self.controller.view.show_confirm_dialog(
			f"Start Development of {development_type.value.capitalize()} Upgrade?",
			on_result=handle_dialog_result
		)
