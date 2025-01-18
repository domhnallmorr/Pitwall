from __future__ import annotations
from collections import deque
from typing import TYPE_CHECKING
import flet as ft

from pw_view.custom_widgets.custom_container import CustomContainer

if TYPE_CHECKING:
	from pw_view.view import View
	from pw_model.email.email_model import Email

class EmailPage(ft.Column):
	def __init__(self, view: View):

		self.view = view
		self.setup_page()

		contents = [
			ft.Text("Email", theme_style=self.view.page_header_style)
		]

		super().__init__(controls=contents, alignment=ft.MainAxisAlignment.START, expand=True)

	def setup_page(self) -> None:
		self.email_content = ft.Text("Select an email to view its content")
		self.email_content_container = CustomContainer(self.view, content=self.email_content, expand=3)
		self.email_content_container.height = self.view.main_app.window.height - 200

	def update_page(self, emails: deque[Email]) -> None:
		self.email_content_container.height = self.view.main_app.window.height - 200

		email_tiles = []
		for email in emails:
			email_tiles.append(self.create_email_tile(email))

		email_list = ft.ListView(
			controls=email_tiles
		)
		
		email_list_container = CustomContainer(self.view, content=email_list, expand=2, height=self.view.main_app.window.height - 200)

		email_row = ft.Row(
			[
				email_list_container,  # Email list on the left, scrollable
				self.email_content_container
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
		 
		self.view.main_app.update()

	#TODO check email can't be accidently modifed by view here
	def create_email_tile(self, email: Email) -> ft.ListTile:
		return ft.ListTile(
                title=ft.Text(f"RE: {email.subject}"),
                subtitle=ft.Text(f"From: {email.sender}"),
                data=email,
                on_click=self.show_email_content,

				shape=ft.RoundedRectangleBorder(radius=5),
				bgcolor="SECONDARY_CONTAINER"
            )
	
	def show_email_content(self, e: ft.ControlEvent) -> None:
		self.email_content.value = e.control.data.message
		self.view.main_app.update()
