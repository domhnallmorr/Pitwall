from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pw_controller.pw_controller import Controller

class EmailController:
	def __init__(self, controller: Controller):
		self.controller = controller

	def email_clicked(self, email_id: int) -> None:
		'''
		When an email is clicked in the view
		Need to mark it as read in the model
		'''

		self.controller.model.inbox.mark_email_as_read(email_id)
