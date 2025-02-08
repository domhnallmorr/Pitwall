from __future__ import annotations
from collections import deque
from typing import TYPE_CHECKING
import flet as ft

from pw_view.custom_widgets.custom_container import CustomContainer
from pw_view.email_page.email_tile import EmailTile
from pw_view.email_page.email_content import EmailContent
from pw_view.email_page.email_list import EmailList

from pw_model.email.email_model import EmailStatusEnums

if TYPE_CHECKING:
	from pw_view.view import View
	from pw_model.email.email_model import Email

class EmailPage(ft.Column): # type: ignore
	def __init__(self, view: View):

		self.view = view
		self.selected_email = None  # Track the currently selected email
		self.setup_page()

		super().__init__(controls=self.controls, alignment=ft.MainAxisAlignment.START, expand=True)

	def setup_page(self) -> None:
		self.email_content = EmailContent(self.view)
		self.email_list = EmailList(self.view, self)

		email_row = ft.Row(
			[
				self.email_list.container,  # Email list on the left, scrollable
				self.email_content.container
			],
			alignment=ft.MainAxisAlignment.START,
			vertical_alignment=ft.CrossAxisAlignment.START,
			expand=True
		)

		self.background_stack = ft.Stack(
			[
				# Add the resizable background image
				self.view.background_image,
				email_row
			],
			expand=True,  # Make sure the stack expands to fill the window
		)

		self.controls = [
					ft.Text("Email", theme_style=self.view.page_header_style),
					self.background_stack
		]

	def update_page(self, emails: deque[Email]) -> None:
		selected_id = self.selected_email.email.email_id if self.selected_email else None
		self.email_list.update_content(emails, selected_id)

		if selected_id not in [e.email_id for e in emails]: # show first email by default if previously selected email is no longer available
			self.show_email_content(self.email_list.email_tiles[0])
		
	def show_email_content(self, email_tile: EmailTile) -> None:
		if self.selected_email is not None:
			self.selected_email.tile_unselected()

		self.email_content.update(email_tile.email.message, email_tile.email.subject)

		email_tile.tile_selected()
		self.selected_email = email_tile
		self.view.controller.email_controller.email_clicked(email_tile.email.email_id)
		self.view.main_app.update()
