from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft

from pw_view.custom_widgets.custom_container import CustomContainer
from pw_view.custom_widgets.rating_widget import RatingWidget
from pw_model.car_development.car_development_model import CarDevelopmentEnums, CarDevelopmentStatusEnums
from pw_model.finance.car_development_costs import CarDevelopmentCostsEnums

if TYPE_CHECKING:
	from pw_view.view import View
	from pw_controller.car_development.car_page_data import CarPageData

class CarDevelopmentTab(ft.Column): # type: ignore
	def __init__(self, view: View):

		self.view = view
		self.setup_widgets()
		self.setup_container()

		super().__init__(controls=[self.container], expand=False,
			tight=True,
			spacing=20)

	def setup_widgets(self) -> None:
		self.current_status_header = ft.Text("Current Status", weight=ft.FontWeight.BOLD, size=self.view.SUBHEADER_FONT_SIZE,)
		self.current_status_text = ft.Text("No Developments in Progress")
		self.progress_bar = RatingWidget("Progress:", min_value=0, max_value=100, text_width=100, number_of_stars=10)

		self.available_updates_header = ft.Text("Available Updates", weight=ft.FontWeight.BOLD, size=self.view.SUBHEADER_FONT_SIZE,)

		width = 140
		self.major_update_text = ft.Text("Major Update:", width=width, weight=ft.FontWeight.BOLD)
		self.medium_update_text = ft.Text("Medium Update:", width=width, weight=ft.FontWeight.BOLD)
		self.minor_update_text = ft.Text("Minor Update:", width=width, weight=ft.FontWeight.BOLD)

		width = 200
		self.major_update_time_text = ft.Text("Time to Complete: 10 weeks", width=width)
		self.medium_update_time_text = ft.Text("Time to Complete: 7 weeks", width=width)
		self.minor_update_time_text = ft.Text("Time to Complete: 5 weeks", width=width)

		width = 160
		self.major_cost_text = ft.Text(f"Cost: ${CarDevelopmentCostsEnums.MAJOR.value:,}", width=width)
		self.medium_cost_text = ft.Text(f"Cost: ${CarDevelopmentCostsEnums.MEDIUM.value:,}", width=width)
		self.minor_cost_text = ft.Text(f"Cost: ${CarDevelopmentCostsEnums.MINOR.value:,}", width=width)

		self.major_develop_btn = ft.TextButton("Start Development", on_click=self.start_development, data=CarDevelopmentEnums.MAJOR)
		self.medium_develop_btn = ft.TextButton("Start Development", on_click=self.start_development, data=CarDevelopmentEnums.MEDIUM)
		self.minor_develop_btn = ft.TextButton("Start Development", on_click=self.start_development, data=CarDevelopmentEnums.MINOR)

		spacing = 20
		self.major_row = ft.Row(controls=[self.major_update_text, self.major_update_time_text, self.major_cost_text, self.major_develop_btn], spacing=spacing)
		self.medium_row = ft.Row(controls=[self.medium_update_text, self.medium_update_time_text, self.medium_cost_text, self.medium_develop_btn], spacing=spacing)
		self.minor_row = ft.Row(controls=[self.minor_update_text, self.minor_update_time_text, self.minor_cost_text, self.minor_develop_btn], spacing=spacing)

	def setup_container(self) -> None:
		self.container = CustomContainer(self.view, self.setup_column(), expand=True)

	def setup_column(self) -> None:
		controls = [
			self.current_status_header,
			self.current_status_text,
			self.progress_bar,
			ft.Divider(),
			self.available_updates_header,
			self.major_row,
			self.medium_row,
			self.minor_row
		]

		return ft.Column(controls=controls, expand=False, tight=True, spacing=20)
	
	def start_development(self, e: ft.ControlEvent) -> None:
		self.view.controller.car_development_controller.car_development_selected(e.control.data)
	
	def update_tab(self, data: CarPageData) -> None:
		self.current_status_text.value = f"Current Status: {data.current_status.capitalize()}"

		if data.current_status == CarDevelopmentStatusEnums.IN_PROGRESS.value:
			disabled = True  # prevent starting new development if one is already in progress
			self.progress_bar.update_row(data.progress)  # Update progress bar with current progress
		else:
			disabled = False
			self.progress_bar.update_row(0)  # Reset progress bar when no development in progress

		self.major_develop_btn.disabled = disabled
		self.medium_develop_btn.disabled = disabled
		self.minor_develop_btn.disabled = disabled

		self.view.main_app.update()
