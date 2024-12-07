from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

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

		super().__init__(controls=contents)

	def setup_page(self) -> None:
		self.email_content = ft.Text("Select an email to view its content")

	def update_page(self, data: dict) -> None:

		emails = data["emails"]
		email_tiles = []
		for email in emails:
			email_tiles.append(self.create_email_tile(email))

		email_list = ft.ListView(
			controls=email_tiles
		)
		

		email_list_container = ft.Container(
			content=email_list,
			width=400,
			height=self.view.main_app.window.height - 200,  # Updated to use Page.window.height
			border=ft.border.all(2, ft.Colors.WHITE),
		)

		email_row = ft.Row(
			[
				email_list_container,  # Email list on the left, scrollable
				ft.Column(controls=[self.email_content], expand=False, alignment=ft.alignment.top_left),  # Email content on the right
			],
			alignment=ft.MainAxisAlignment.START,
			vertical_alignment=ft.CrossAxisAlignment.START
		)

		self.controls = [
			ft.Column(
				controls=[
					ft.Text("Email", theme_style=self.view.page_header_style),
					email_row
				]
			)
		]
		 
		self.view.main_app.update()

	#TODO check email can't be accidently modifed by view here
	def create_email_tile(self, email: Email) -> None:
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
