from __future__ import annotations
from typing import TYPE_CHECKING

from pw_controller.track_page.track_page_data import get_track_page_data
from pw_view.view_enums import ViewPageEnums

if TYPE_CHECKING:
	from pw_controller.pw_controller import Controller
	from pw_model.pw_base_model import Model

class TrackPageController:
	def __init__(self, controller: Controller):
		self.controller = controller

	@property	
	def model(self) -> Model:
		return self.controller.model
	

	def go_to_track_page(self, track: str):
		data = get_track_page_data(self.controller.model, track)
		self.controller.view.track_page.update_page(data)
		self.controller.view.main_window.change_page(ViewPageEnums.TRACKPAGE)

