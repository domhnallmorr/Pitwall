from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

from pw_model.finance.finance_data import FinanceData
from pw_view.finance_page.overview_tab import OverviewTab
from pw_view.finance_page.sponsors_tab import SponsorsTab

if TYPE_CHECKING:
	from pw_view.view import View

class FinancePage(ft.Column):
	def __init__(self, view: View):
		self.view = view
		self.setup_tabs()

		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				self.tabs
			],
			expand=True
		)

		super().__init__(
			controls=[
				ft.Text("Finance", theme_style=self.view.page_header_style),
				self.background_stack
			],
			alignment=ft.MainAxisAlignment.START,
			expand=True
		)

	def setup_tabs(self) -> None:
		self.overview_tab = OverviewTab(self.view)
		self.sponsors_tab = SponsorsTab(self.view)

		self.tabs = ft.Tabs(
			selected_index=0,
			animation_duration=300,
			tabs=[
				ft.Tab(
					text="Overview",
					icon=ft.Icons.BUSINESS,
					content=ft.Container(
						content=self.overview_tab,
						expand=False,
						alignment=ft.alignment.top_center
					)
				),
				ft.Tab(
					text="Sponsors",
					icon=ft.Icons.CASES,
					content=ft.Container(
						content=self.sponsors_tab,
						expand=False,
						alignment=ft.alignment.top_center
					)
				),
			],
			expand=True
		)

	def update_page(self, data: FinanceData) -> None:
		self.overview_tab.update_tab(data)
		self.sponsors_tab.update_tab(data)
		
		self.view.main_app.update()
