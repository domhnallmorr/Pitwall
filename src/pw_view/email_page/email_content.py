from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft

from pw_view.custom_widgets.custom_container import CustomContainer
from pw_view.view_enums import ViewPageEnums
from pw_model.email.email_enums import EmailTypeEnums

if TYPE_CHECKING:
	from pw_view.view import View

class EmailContent:
	def __init__(self, view: View):
		self.view = view
		self.setup_buttons()
		self.setup_widgets()

	def setup_buttons(self) -> None:
		self.car_development_btn = ft.ElevatedButton("View",
											   on_click=self.on_car_development_btn_click,
											   visible=False,
											   icon=ft.Icons.LINK,
											   )

	def setup_widgets(self) -> None:
		self.subject_text = ft.Text("Subject")
		self.from_text = ft.Text("From:")
		self.week_text = ft.Text("Week:")
		self.content_text = ft.Text("Select an email to view its content")

		content = ft.Column(
			controls= [
				self.subject_text,
				self.from_text,
				self.week_text,
				ft.Divider(),
				self.content_text,
				self.car_development_btn
			]
		)

		self.container = CustomContainer(self.view, content=content, expand=3)
		# self.email_content_container.height = self.view.main_app.window.height - 200

	def update(self, message: str, subject: str, week: int, email_type: EmailTypeEnums) -> None:
		self.subject_text.value = f"Subject: {subject}"
		self.week_text.value = f"Week: {week}"
		self.content_text.value = message

		if email_type == EmailTypeEnums.CAR_DEVELOPMENT:
			self.car_development_btn.visible = True
		else:
			self.car_development_btn.visible = False

		self.view.main_app.update()

	def on_car_development_btn_click(self, e: ft.ControlEvent) -> None:
		# switch to car page and select the car development tab
		self.view.car_page.tabs.selected_index = 3  # 0-based index
		self.view.main_window.change_page(ViewPageEnums.CAR)
