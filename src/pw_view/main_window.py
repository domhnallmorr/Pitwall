from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

from pw_view import sidebar

if TYPE_CHECKING:
	from pw_view.view import View

class MainWindow(ft.View):
	def __init__(self, view: View):
		self.view = view

		self.setup_header_bar()
		self.nav_sidebar = sidebar.Sidebar(self.view)

		self.content_row = ft.Row([
			self.nav_sidebar, self.view.home_page
		],
		alignment=ft.MainAxisAlignment.START,
		vertical_alignment=ft.CrossAxisAlignment.START,
		expand=1,
		)
		# contents = [nav_sidebar, self.view.home_page]

		super().__init__(controls=[self.header, self.content_row])

	def setup_header_bar(self) -> None:
		self.team_text = ft.Text("Williams - $1,000,000", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)
		self.week_text = ft.Text("Week 1 - 1998", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)

		self.header = ft.Row(
			controls=[
				self.team_text,
				self.week_text
			],
			alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # Space between the items
			vertical_alignment=ft.CrossAxisAlignment.CENTER  # Align items to the center vertically
		)

	def change_page(self, page_name: str) -> None:
		
		contents = [self.nav_sidebar]

		if page_name == "home":
			contents.append(self.view.home_page)
		elif page_name == "email":
			contents.append(self.view.email_page)
			self.update_email_button(0) # reset email btn to remove number of new mails
		elif page_name == "standings":
			contents.append(self.view.standings_page)
		elif page_name == "calendar":
			contents.append(self.view.calendar_page)
		elif page_name == "staff":
			contents.append(self.view.staff_page)
		elif page_name == "hire_staff":
			contents.append(self.view.hire_staff_page)
		elif page_name == "grid":
			contents.append(self.view.grid_page)
		elif page_name == "finance":
			contents.append(self.view.finance_page)
		elif page_name == "car":
			contents.append(self.view.car_page)
		elif page_name == "facility":
			contents.append(self.view.facility_page)
		elif page_name == "upgrade_facility":
			contents.append(self.view.upgrade_facility_page)

		self.content_row = ft.Row(
			contents,
			alignment=ft.MainAxisAlignment.START,
			vertical_alignment=ft.CrossAxisAlignment.START,
			expand=1,		
		)			

		self.controls = [self.header, self.content_row]
		self.view.main_app.update()
		
	def update_window(self, team: str, date: str, in_race_week: bool) -> None:

		self.team_text.value = team

		self.week_text.value = date
		self.week_text.update()

		if in_race_week is True:
			self.nav_sidebar.update_advance_button("go_to_race")
		else:
			self.nav_sidebar.update_advance_button("advance")
		
		self.view.main_app.update()
		
	def update_email_button(self, number_of_emails: int) -> None:
		if number_of_emails > 0:
			self.nav_sidebar.email_btn.text = f"Email ({number_of_emails})"
		else:
			self.nav_sidebar.email_btn.text = f"Email"
