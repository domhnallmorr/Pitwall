from __future__ import annotations
from typing import TYPE_CHECKING, Callable

import flet as ft

if TYPE_CHECKING:
	from pw_view.view import View
	from pw_model.email.email_model import Email
     
class EmailTile(ft.ListTile): # type: ignore
	def __init__(self, view: View, email: Email, on_click_callback: Callable[[EmailTile], None]):
		"""
        A single email tile representing an email in the list.

        Args:
            email (Email): The email data to display.
            on_click_callback (Callable): The function to call when this tile is clicked.
        """
		self.view = view
		self.title_text = ft.Text(f"RE: {email.subject}", color=view.dark_grey, weight="bold", size=15)
		self.subtitle_text = ft.Text(f"From: {email.sender}", color=view.dark_grey)
		self.email = email

		self.new_email_bg_color = ft.Colors.PRIMARY
		self.selected_email_bg_color = self.view.primary_selected_color
		self.default_bg_color = ft.Colors.GREY

		super().__init__(
            title=self.title_text,
            subtitle=self.subtitle_text,
            data=email,  # Store the email data for easy access later
            on_click=lambda e: on_click_callback(self),  # Pass email to the callback
            shape=ft.RoundedRectangleBorder(radius=5),
            bgcolor=ft.Colors.PRIMARY,
            dense=True,  # Make the tile compact
        )
        
	def tile_selected(self) -> None:
		self.bgcolor = self.selected_email_bg_color
		self.title_text.color = self.view.dark_grey
		self.subtitle_text.color = self.view.dark_grey

	def tile_unselected(self) -> None:
		self.bgcolor = self.default_bg_color
		self.title_text.color = self.view.dark_grey
		self.subtitle_text.color = self.view.dark_grey

