from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft

from pw_view.custom_widgets.custom_container import CustomContainer

if TYPE_CHECKING:
	from pw_view.view import View

class EmailContent:
	def __init__(self, view: View):
		self.view = view
		self.setup_widgets()

	def setup_widgets(self) -> None:
		self.subject_text = ft.Text("Subject")
		self.from_text = ft.Text("From:")
		self.content_text = ft.Text("Select an email to view its content")

		content = ft.Column(
			controls= [
				self.subject_text,
				self.from_text,
				ft.Divider(),
				self.content_text
			]
		)

		self.container = CustomContainer(self.view, content=content, expand=3)
		# self.email_content_container.height = self.view.main_app.window.height - 200

	def update(self, message: str, subject: str) -> None:
		self.subject_text.value = f"Subject: {subject}"
		self.content_text.value = message