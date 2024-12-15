from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft
from flet.matplotlib_chart import MatplotlibChart
import matplotlib.pyplot as plt

from pw_view.custom_widgets import custom_container

if TYPE_CHECKING:
	from pw_view.view import View
	from pw_controller.page_update_typed_dicts import HomePageData

class HomePage(ft.Column):
	def __init__(self, view: View):

		self.view = view

		self.fig, self.axs = plt.subplots(1, 1, figsize=(12, 4)) # for team stats
		self.team_stats_chart = MatplotlibChart(self.fig, expand=True, transparent=True, original_size=False)

		self.setup_containers()

		self.setup_page()

		super().__init__(expand=1, controls=self.controls)

	def setup_containers(self) -> None:
		# STANDINGS
		self.current_team_pos_text = ft.Text("Current Position: 1st")
		standings_column = ft.Column(
			controls=[
				custom_container.HeaderContainer(self.view, "Standings", expand=False),
				self.current_team_pos_text
				]
		)

		self.standings_container = custom_container.CustomContainer(self.view, standings_column)

		# STAFF
		self.driver1_text = ft.Text("Driver1: XXX - Contract: 2 Year(s)")
		self.driver2_text = ft.Text("Driver2: XXX - Contract: 2 Year(s)")
		self.technical_director_text = ft.Text("Technical Director: XXX - Contract: 2 Year(s)")
		self.commercial_manager_text = ft.Text("Commercial Manager: XXX - Contract: 2 Year(s)")

		staff_column = ft.Column(
			controls=[
				custom_container.HeaderContainer(self.view, "Staff", expand=False),
				self.driver1_text,
				self.driver2_text,
				self.technical_director_text,
				self.commercial_manager_text,
				],
			expand=True
		)

		self.staff_container = custom_container.CustomContainer(self.view, staff_column)

		# NEXT RACE
		self.next_race_text = ft.Text("Some Grand Prix")
		self.next_race_week_text = ft.Text("Some Week")
		next_race_column = ft.Column(
			controls=[
				custom_container.HeaderContainer(self.view, "Next Race", expand=False),
				self.next_race_text,
				self.next_race_week_text
				],
				expand=True
		)

		self.next_race_container = custom_container.CustomContainer(self.view, next_race_column)

		# TEAM STATS CHART
		chart_column = ft.Column(
			controls=[
					custom_container.HeaderContainer(self.view, "Team Stats", expand=False),
					self.team_stats_chart,
			]
			)
		self.chart_container = custom_container.CustomContainer(self.view, chart_column)
		
	def update_page(self, data: HomePageData) -> None:
		self.update_plot(data)

		self.current_team_pos_text.value = f"Current Position: {data['current_position']}"

		self.driver1_text.value = f"Driver 1: {data['driver1']} - Contract: {data['driver1_contract']} Year(s)"
		self.driver2_text.value = f"Driver 2: {data['driver2']} - Contract: {data['driver2_contract']} Year(s)"
		self.technical_director_text.value = f"Technical Director: {data['technical_director']} - Contract: {data['technical_director_contract']} Year(s)"
		self.commercial_manager_text.value = f"Commercial Manager: {data['commercial_manager']} - Contract: {data['commercial_manager_contract']} Year(s)"

		self.next_race_text.value = f"Next Race: {data['next_race']}"
		self.next_race_week_text.value = f"Week: {data['next_race_week']}"

		self.view.main_app.update()

	def setup_page(self) -> None:
		row1 = ft.Row(
			controls=[
				ft.Container(content=self.standings_container, expand=True),
				ft.Container(content=self.staff_container, expand=True),
				ft.Container(content=self.next_race_container, expand=True),
				],
			expand=1,
			alignment=ft.MainAxisAlignment.SPACE_EVENLY
		)

		row2 = ft.Row(
			controls=[self.chart_container,],
			expand=1
		)

		page_controls = ft.Container(
			content=ft.Column(
				controls=[
							row1,
							row2
							],
							expand=True
			),
			expand=True
		)

		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				page_controls,
			],
			expand=True,
		)

		self.controls = [
			ft.Text("Home", theme_style=self.view.page_header_style),
			self.background_stack
		]

		self.view.main_app.update()

	def update_plot(self, data: HomePageData) -> None:
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
