from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

from pw_view import sidebar
from pw_view.view_enums import ViewPageEnums, AdvanceModeEnums
from pw_model.pw_model_enums import CalendarState

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
		self.header_team_logo = ft.Image(
			src=fr"{self.view.team_logos_path}\warrick.png",
			width=50,
			height=50,
			# fit=ft.ImageFit.CONTAIN
		)
		self.team_text = ft.Text("Williams - $1,000,000", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)
		self.week_text = ft.Text("Week 1 - 1998", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)

		name_logo_row = ft.Row(
			controls=[self.header_team_logo, self.team_text],
			alignment=ft.MainAxisAlignment.START,
			vertical_alignment=ft.CrossAxisAlignment.CENTER
		)

		self.header = ft.Row(
			controls=[
				name_logo_row,				# Team name and logo row
				self.week_text
			],
			alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # Space between the items
			vertical_alignment=ft.CrossAxisAlignment.CENTER  # Align items to the center vertically
		)

	def change_page(self, page_name: str) -> None:
		
		contents = [self.nav_sidebar]

		if page_name == ViewPageEnums.HOME:
			contents.append(self.view.home_page)
		elif page_name == ViewPageEnums.EMAIL:
			contents.append(self.view.email_page)
			self.update_email_button(0) # reset email btn to remove number of new mails
		elif page_name == ViewPageEnums.STANDINGS:
			contents.append(self.view.standings_page)
		elif page_name == ViewPageEnums.CALENDAR:
			contents.append(self.view.calendar_page)
		elif page_name == ViewPageEnums.STAFF:
			contents.append(self.view.staff_page)
		elif page_name == "hire_staff":
			contents.append(self.view.hire_staff_page)
		elif page_name == ViewPageEnums.GRID:
			contents.append(self.view.grid_page)
		elif page_name == ViewPageEnums.FINANCE:
			contents.append(self.view.finance_page)
		elif page_name == ViewPageEnums.CAR:
			contents.append(self.view.car_page)
		elif page_name == ViewPageEnums.FACILITY:
			contents.append(self.view.facility_page)
		elif page_name == "upgrade_facility":
			contents.append(self.view.upgrade_facility_page)
		elif page_name == ViewPageEnums.TRACKPAGE:
			contents.append(self.view.track_page)
		elif page_name == ViewPageEnums.DRIVER:
			contents.append(self.view.driver_page)

		self.content_row = ft.Row(
			contents,
			alignment=ft.MainAxisAlignment.START,
			vertical_alignment=ft.CrossAxisAlignment.START,
			expand=1,		
		)			

		self.controls = [self.header, self.content_row]
		self.view.main_app.update()
		
	def update_window(self, team_name: str, team: str, date: str, state: CalendarState) -> None:
		self.header_team_logo.src = fr"{self.view.team_logos_path}\{team_name.lower()}.png"
		self.team_text.value = team
		
		# Format would be like "Week 1 - 1998 (PRE_SEASON)"
		self.week_text.value = f"{date} ({state.value.title()})"
		self.week_text.update()

		if state == CalendarState.RACE_WEEK:
			self.nav_sidebar.update_advance_button(AdvanceModeEnums.GO_TO_RACE)
		elif state in [CalendarState.IN_SEASON_TESTING, CalendarState.PRE_SEASON_TESTING]:
			self.nav_sidebar.update_advance_button(AdvanceModeEnums.GO_TO_TEST)
		else:
			self.nav_sidebar.update_advance_button(AdvanceModeEnums.ADVANCE)
		
		self.view.main_app.update()
		
	def update_email_button(self, number_of_emails: int) -> None:
		if number_of_emails > 0:
			self.nav_sidebar.email_btn.text = f"Email ({number_of_emails})"
		else:
			self.nav_sidebar.email_btn.text = f"Email"
