import flet as ft

from flet.matplotlib_chart import MatplotlibChart

import matplotlib.pyplot as plt

class HomePage(ft.Column):
	def __init__(self, view):

		self.view = view

		self.fig, self.axs = plt.subplots(1, 1, figsize=(12, 4)) # for team stats
		self.team_stats_chart = MatplotlibChart(self.fig, expand=True, transparent=True, original_size=False)

		self.setup_containers()

		controls = [
			ft.Text("Home", theme_style=self.view.page_header_style),
			ft.Row(
				controls=[
					self.summary_container,
					# self.staff_container,
					self.chart_container,
					self.next_race_container
				],
			),	
		]

		super().__init__(expand=1, controls=controls, alignment=ft.MainAxisAlignment.START)

	def setup_containers(self):
		self.summary_container = ft.Container(
			content=ft.Column(
				controls=[
					ft.Text("Summary", size=self.view.container_header2_size),
				],
			),
			bgcolor=self.view.dark_grey,
			border_radius=self.view.container_border_radius,
		)

		self.standings_container = ft.Container(
			content=ft.Column(
				controls=[
					ft.Text("Standings", size=self.view.container_header2_size)
				],
			),
			bgcolor=self.view.dark_grey,
			border_radius=self.view.container_border_radius
		)

		self.chart_container = ft.Container(
			content=ft.Column(
				controls=[
					ft.Text("Team Stats", size=self.view.container_header2_size),
					self.team_stats_chart,
				],
			),
			bgcolor=self.view.dark_grey,
			border_radius=self.view.container_border_radius,
			expand=1,
		)

		self.next_race_container = ft.Container(
			content=ft.Column(
				controls=[
					ft.Text("Next Race", size=self.view.container_header2_size),
				],
			),
			bgcolor=self.view.dark_grey,
			border_radius=self.view.container_border_radius,
			expand=1,			
		)

	def update_page(self, data):
		self.update_plot(data)

		controls = [
			ft.Text("Home", theme_style=self.view.page_header_style),
			ft.Row(
				controls=[
					# self.staff_container,
					ft.Column(
						controls=[
							self.chart_container,
						],
						expand=True
					)
				],
				expand=1,
			),	
		]


		self.controls = controls
		self.view.main_app.update()

	def update_plot(self, data):
		self.axs.clear()

		team_avg_stats = data["team_average_stats"]
		
		# redefine staff ans sponsorship as values between 0 and 100
		team_avg_stats["staff"] = int((team_avg_stats["staff"]/team_avg_stats["max_staff"]) * 100)
		data["player_staff"] = int((data["player_staff"]/team_avg_stats["max_staff"]) * 100)

		team_avg_stats["sponsorship"] = int((team_avg_stats["sponsorship"]/team_avg_stats["max_sponsorship"]) * 100)
		data["player_sponsorship"] = int((data["player_sponsorship"]/team_avg_stats["max_sponsorship"]) * 100)

		averages = [
			team_avg_stats["car_speed"],   
			team_avg_stats["driver_skill"],   
			team_avg_stats["managers"],   
			team_avg_stats["staff"],   
			team_avg_stats["facilities"],   
			team_avg_stats["sponsorship"],   
			  ]
		
		# Data for the bar chart
		categories = ["Car", "Drivers", "Managers", "Staff", "Facilities", "Sponsors"]
		player_values = [data["player_car"], data["player_drivers"], data["player_managers"], data["player_staff"], data["player_facilities"], data["player_sponsorship"]]
		delta_to_100 = [100 - v for v in player_values]

		self.axs.bar(categories, player_values, bottom=0, width=0.2, align="edge", color="#A0CAFD")
		self.axs.bar(categories, delta_to_100, bottom=player_values, color="grey", width=0.2, align="edge")
		
		handles = []
		for i, avg in enumerate(averages):
			handle = self.axs.scatter(i-0.03, avg, color="gold", zorder=5, label="Average on Grid", marker=">")
			handles.append([handle])

		self.axs.legend(handles=handles[0], loc="upper right", bbox_to_anchor=(0.99, 1.11), frameon=False)
		self.fig.subplots_adjust(left=0.07, right=0.97, top=0.90, bottom=0.15)
