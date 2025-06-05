from __future__ import annotations
from typing import TYPE_CHECKING
from pw_view.car_profile.car_profile_manager import CarProfileData

if TYPE_CHECKING:
	from pw_controller.pw_controller import Controller


class CarProfileController:
	def __init__(self, controller: Controller):
		self.controller = controller
		self.view = controller.view
		self.model = controller.model

		self.create_car_profiles()

	def create_car_profiles(self) -> None:
		data = []
		for team_model in self.model.teams:
			name = team_model.name
			primary_colour = team_model.team_colors_manager.primary_colour
			title_sponsor = team_model.finance_model.sponsorship_model.title_sponsor

			data.append(CarProfileData(name, primary_colour, title_sponsor))

		self.view.car_profile_manager.create_car_profiles(data)
