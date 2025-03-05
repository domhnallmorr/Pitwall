from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pw_controller.pw_controller import Controller


class DriverNegotiationController:
	def __init__(self, controller: Controller):
		self.controller = controller

	def negotiate_contract(self, driver: str):
		

