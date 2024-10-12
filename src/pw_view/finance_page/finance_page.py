import io
import flet as ft
from flet.plotly_chart import PlotlyChart
from flet.matplotlib_chart import MatplotlibChart

import plotly.graph_objects as go

import matplotlib
matplotlib.use("agg") # avoid main thread warning

import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.ticker import FuncFormatter
style.use("dark_background")

class FinancePage(ft.Column):
	def __init__(self, view):

		self.view = view

		self.setup_widgets()

		contents = [
			ft.Text("Finance", theme_style=self.view.page_header_style),
			ft.Row(
				controls=[
					self.summary_container,
					]
			),
			ft.Row(
				controls=[
					self.chart_container,
				],
				expand=True
				
			)
		]

		super().__init__(expand=1, controls=contents, alignment=ft.MainAxisAlignment.START, scroll="auto")

	def setup_widgets(self):
		self.sponsor_income_text = ft.Text(f"Sponsorship: $1")
		self.prize_money_income_text = ft.Text(f"Prize Money: $1")

		self.staff_costs_text = ft.Text(f"Staff: $1")
		self.commercial_manager_salary_text = ft.Text(f"Commercial Manager: $1")
		self.race_costs_text = ft.Text(f"Races: $1 (per race)")

		column = ft.Column(
			controls=[
					ft.Text("Income", weight=ft.FontWeight.BOLD, size=25,),
					self.sponsor_income_text,
					self.prize_money_income_text,
					ft.Divider(),

					ft.Text("Expenditure", weight=ft.FontWeight.BOLD, size=25,),
					self.staff_costs_text,
					self.commercial_manager_salary_text,
					self.race_costs_text,
			],
			expand=True
		)


		self.summary_container = ft.Container(
				# expand=1,
				content=column,
				bgcolor=self.view.dark_grey,
				margin=20,
				padding=10,
				width=200,
				expand=True,
			)
		
		self.setup_plot()

		self.chart_container = ft.Container(
				content=self.history_chart,
				bgcolor=self.view.dark_grey,
				margin=20,
				padding=10,
				# width=200,
				expand=True,
			)


	def update_page(self, data: dict):
		self.sponsor_income_text.value = f"Sponsorship: ${data['total_sponsorship']:,}"
		self.prize_money_income_text.value = f"Prize Money: ${data['prize_money']:,}"
		self.staff_costs_text.value = f"Staff Costs: ${data['total_staff_costs_per_year']:,}"
		self.commercial_manager_salary_text.value = f"Commercial Manager: ${data['commercial_manager_salary']:,}"
		self.race_costs_text.value = f"Race Costs: ${data['race_costs']:,} (per race)"

		self.update_history_chart(data)

	def setup_plot(self):
		self.fig, self.axs = plt.subplots(1, 1, figsize=(12, 3))

		self.fig.tight_layout()

		self.axs.set_xlabel("Date")
		self.axs.set_ylabel("Balance")

		self.fig.subplots_adjust(left=0.07, right=0.97, top=0.98, bottom=0.15)

		self.history_chart = MatplotlibChart(self.fig, expand=True, transparent=True, original_size=False)

	def update_history_chart(self, data):
		y_formatter = FuncFormatter(self.balance_formatter)

		self.axs.plot(data["balance_history_dates"], data["balance_history"], linestyle="-", color="#A0CAFD")

		self.axs.yaxis.set_major_formatter(y_formatter)

	def balance_formatter(self, x, pos):
		if x < 1_000_000:
			return f"${int(x/1_000)}K"
		else:
			return f"${int(x/1_000_000)}M"