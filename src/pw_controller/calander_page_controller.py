from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pw_controller.pw_controller import Controller
	from pw_model.pw_base_model import Model
	from pw_view.view import View

class CalendarPageController:
	def __init__(self, controller: Controller):
		self.controller = controller

	@property	
	def model(self) -> Model:
		return self.controller.model

	@property	
	def view(self) -> View:
		return self.controller.view

	def update_track_frame(self, idx: int) -> None:

		calendar_row = self.model.calendar.iloc[idx]

		track_model = self.model.get_track_model(calendar_row["Track"])
		
		data = {
			"title": track_model.title,
			"track": track_model.name,
		}

		self.view.calendar_page.update_track_frame(data)