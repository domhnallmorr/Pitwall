from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

from pw_view.custom_widgets.custom_container import CustomContainer
from pw_view.email_page.email_tile import EmailTile

from pw_model.email.email_model import EmailStatusEnums

if TYPE_CHECKING:
	from pw_view.view import View
	from pw_view.email_page.email_page import EmailPage
	from pw_view.email_page.email_tile import EmailTile
	from pw_model.email.email_model import Email

class EmailList(ft.ListView):
	def __init__(self, view: View, email_page: EmailPage):
		self.email_page = email_page
		self.view = view
		super().__init__(controls=[], spacing=4)

		self.setup_container()

	def setup_container(self) -> None:
		self.container = CustomContainer(self.view, content=self)

	def update_content(self, emails: list[Email], selected_id: int) -> None:
		self.create_email_tiles(emails)
		self.controls = self.email_tiles

		# make read tiles grey
		for email_tile in self.email_tiles:
			if email_tile.email.status == EmailStatusEnums.READ:
				email_tile.tile_unselected()
			
			if email_tile.email.email_id == selected_id:
				email_tile.tile_selected()

	def create_email_tiles(self, emails: list[Email]) -> None:
		self.email_tiles: list[EmailTile] = [self.create_email_tile(email) for email in emails]

	#TODO check email can't be accidently modifed by view here
	def create_email_tile(self, email: Email) -> ft.ListTile:
		return EmailTile(self.view, email, self.email_page.show_email_content)