from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING, Union, Tuple
import flet as ft

from pw_view.custom_widgets import custom_container
from pw_view.custom_widgets.custom_buttons import buttons_row
from pw_view.car_page.car_comparison_graph import CarComparisonGraph
from pw_view.car_page.car_development_tab import CarDevelopmentTab

if TYPE_CHECKING:
	from pw_view.view import View
	from pw_controller.car_development.car_page_data import CarPageData

class CarPageTabEnums(Enum):
	CAR_DEVELOPMENT = "car_development"
	CAR_COMPARISON = "car_comparison"

class CarPage(ft.Column):
	def __init__(self, view: View):

		self.view = view
		self.setup_buttons_row()
		self.setup_tabs()

		contents = [
			ft.Text("Car", theme_style=self.view.page_header_style)
		]

		super().__init__(controls=contents, alignment=ft.MainAxisAlignment.START, expand=True)

		self.show_tab(CarPageTabEnums.CAR_DEVELOPMENT)

	def setup_buttons_row(self) -> None:
		self.car_development_btn = ft.TextButton("Car Development", on_click=self.display_car_development)
		self.car_comparison_btn = ft.TextButton("Car Comparison", on_click=self.display_car_comparison)

		self.car_development_btn.style = self.view.clicked_button_style
		self.buttons_row = buttons_row(self.view, [self.car_development_btn, self.car_comparison_btn])

	def setup_tabs(self) -> None:
		self.car_comparison_graph = CarComparisonGraph(self.view)
		self.car_development_tab = CarDevelopmentTab(self.view)

	def update_page(self, data: CarPageData) -> None:
		self.car_comparison_graph.setup_rows(data.car_speeds)
		self.car_development_tab.update_tab(data)
		self.car_comparison_container = custom_container.CustomContainer(self.view, self.car_comparison_graph, expand=False)

		self.view.main_app.update()

	def show_tab(self, tab_name: CarPageTabEnums) -> None:
		page_controls = [self.buttons_row]

		if tab_name == CarPageTabEnums.CAR_COMPARISON:
			page_controls.append(self.car_comparison_container)
		elif tab_name == CarPageTabEnums.CAR_DEVELOPMENT:
			page_controls.append(self.car_development_tab)
		
		column = ft.Column(
			controls=page_controls,
			expand=False,
			spacing=20
		)

		self.background_stack = ft.Stack(
			[
				# Add the resizable background image
				self.view.background_image,
				column
			],
			expand=True,  # Make sure the stack expands to fill the window
		)

		self.controls = [
			ft.Text("Car", theme_style=self.view.page_header_style),
			# car_comparison_container
			self.background_stack
		]

		self.view.main_app.update()
	def reset_tab_buttons(self) -> None:
		# When a button is clicked to view a different tab, reset all buttons style
		self.car_development_btn.style = None
		self.car_comparison_btn.style = None

	def display_car_development(self, e: ft.ControlEvent) -> None:
		self.reset_tab_buttons()
		self.car_development_btn.style = self.view.clicked_button_style

		self.show_tab(CarPageTabEnums.CAR_DEVELOPMENT)

	def display_car_comparison(self, e: ft.ControlEvent) -> None:
		self.reset_tab_buttons()
		self.car_comparison_btn.style = self.view.clicked_button_style

		self.show_tab(CarPageTabEnums.CAR_COMPARISON)