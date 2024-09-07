import flet as ft

from pw_view import sidebar

class MainWindow(ft.View):
	def __init__(self, view):
		self.view = view

		self.setup_header_bar()
		self.nav_sidebar = sidebar.Sidebar(self.view)

		self.content_row = ft.Row([
			self.nav_sidebar, self.view.home_page
		],
		alignment=ft.MainAxisAlignment.START,
		vertical_alignment=ft.CrossAxisAlignment.START
		)
		# contents = [nav_sidebar, self.view.home_page]

		super().__init__(controls=[self.header, self.content_row])

	def setup_header_bar(self):
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


	def change_page(self, page_name):
		
		contents = [self.nav_sidebar]

		if page_name == "home":
			contents.append(self.view.home_page)
		elif page_name == "email":
			contents.append(self.view.email_page)
		elif page_name == "standings":
			contents.append(self.view.standings_page)
		elif page_name == "calendar":
			contents.append(self.view.calendar_page)
		elif page_name == "staff":
			contents.append(self.view.staff_page)
		elif page_name == "hire_driver":
			contents.append(self.view.hire_driver_page)
		elif page_name == "grid":
			contents.append(self.view.grid_page)

		self.content_row = ft.Row(
			contents,
			alignment=ft.MainAxisAlignment.START,
			vertical_alignment=ft.CrossAxisAlignment.START			
		)			

		self.controls = [self.header, self.content_row]
		self.view.main_app.update()
		
	def update_window(self, data):
		self.team_text.value = data["team"]

		self.week_text.value = data["date"]
		self.week_text.update()

		if data["in_race_week"] is True:
			self.nav_sidebar.update_advance_button("go_to_race")
		else:
			self.nav_sidebar.update_advance_button("advance")
			

