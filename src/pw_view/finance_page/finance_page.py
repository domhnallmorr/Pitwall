from __future__ import annotations
import io
from typing import TYPE_CHECKING
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

from pw_model.finance.finance_data import FinanceData
from pw_view.custom_widgets import custom_container

if TYPE_CHECKING:
	from pw_view.view import View

class FinancePage(ft.Column): # type: ignore
	def __init__(self, view: View):

		self.view = view

		self.setup_widgets()

		column = ft.Column(
			controls=[
				self.summary_row,
				ft.Row(
					controls=[
						self.chart_container,
					],
					expand=True
				)
			]
		)
		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				column
			],
			expand=True
		)

		contents = [
			ft.Text("Finance", theme_style=self.view.page_header_style),
			self.background_stack

		]

		super().__init__(expand=1, controls=contents)

	def setup_widgets(self) -> None:
		self.profit_text = ft.Text(f"Profit/Loss This Season: $1")
		self.title_sponsor_text = ft.Text(f"Title Sponsor: Some Sponsor")

		self.title_sponsor_value_text = ft.Text(f"Title Sponsorship: $1")
		self.sponsor_income_text = ft.Text(f"Sponsorship: $1")
		self.prize_money_income_text = ft.Text(f"Prize Money: $1")
		self.drivers_payments_text = ft.Text(f"Drivers Payments: $1")
		self.total_income_text = ft.Text(f"Total: $1")

		self.staff_costs_text = ft.Text(f"Staff: $1")
		self.drivers_salary_text = ft.Text(f"Drivers Salary: $1")
		self.technical_director_salary_text = ft.Text(f"Technical Director: $1")
		self.commercial_manager_salary_text = ft.Text(f"Commercial Manager: $1")
		self.race_costs_text = ft.Text(f"Races: $1 (per race)")
		self.car_costs_text = ft.Text(f"Car Costs: $1")
		self.total_expenditure_text = ft.Text(f"Total: $1")

		self.summary_header = custom_container.HeaderContainer(self.view, "Summary")
		self.income_header = custom_container.HeaderContainer(self.view, "Income")
		self.expenditure_header = custom_container.HeaderContainer(self.view, "Expenditure")

		#SUMMARY
		column = ft.Column(
			controls=[
					self.summary_header,
					self.profit_text,
					self.title_sponsor_text,
					ft.Text(),# dummy text widget so that income and expenditure have the same number of rows
					ft.Text(),
					ft.Text(),
					ft.Text(),
					ft.Text(),
					ft.Text(),
			],
			expand=True
		)

		self.summary_container = custom_container.CustomContainer(self.view, column, expand=True)

		# INCOME
		column = ft.Column(
			controls=[
					self.income_header,
					# ft.Text("Income", weight=ft.FontWeight.BOLD, size=25,),
					self.title_sponsor_value_text,
					self.sponsor_income_text,
					self.prize_money_income_text,
					self.drivers_payments_text,
					ft.Text(),# dummy text widget so that income and expenditure have the same number of rows
					ft.Text(),# dummy text widget so that income and expenditure have the same number of rows
					ft.Divider(),
					self.total_income_text
			],
			expand=True
		)

		self.income_container = custom_container.CustomContainer(self.view, column, expand=True)

		column = ft.Column(
			controls=[
					self.expenditure_header,
					self.staff_costs_text,
					self.drivers_salary_text,
					self.technical_director_salary_text,
					self.commercial_manager_salary_text,
					self.race_costs_text,
					self.car_costs_text,
					ft.Divider(),
					self.total_expenditure_text
			],
			expand=True
		)
		
		self.expenditure_container = custom_container.CustomContainer(self.view, column, expand=True)

		self.summary_row = ft.Row(controls=[self.summary_container, self.income_container, self.expenditure_container], expand=False)

		self.setup_plot()

		self.chart_container: custom_container.CustomContainer #for mypy
		self.chart_container = custom_container.CustomContainer(self.view, self.history_chart, expand=True)

	def update_page(self, data: FinanceData) -> None:
		self.profit_text.value = f"Profit/Loss This Season: ${data['profit']:,}"
		self.title_sponsor_text.value = f"Title Sponsor: {data['title_sponsor']}"

		self.title_sponsor_value_text.value = f"Title Sponsorship: ${data['title_sponsor_value']:,}"
		self.sponsor_income_text.value = f"Other Sponsorship: ${data['other_sponsorship']:,}"
		self.prize_money_income_text.value = f"Prize Money: ${data['prize_money']:,}"
		self.drivers_payments_text.value = f"Drivers Payments: ${data['drivers_payments']:,}"
		self.total_income_text.value = f"Total: ${data['total_income']:,}"

		self.staff_costs_text.value = f"Staff Costs: ${data['total_staff_costs_per_year']:,}"
		self.drivers_salary_text.value = f"Drivers Salary: ${data['drivers_salary']:,}"
		self.technical_director_salary_text.value = f"Technical Director: ${data['technical_director_salary']:,}"
		self.commercial_manager_salary_text.value = f"Commercial Manager: ${data['commercial_manager_salary']:,}"
		self.race_costs_text.value = f"Transport Costs: ${data['race_costs']:,} (Estimated)"
		self.car_costs_text.value = f"Car Costs: ${data['car_costs']:,}"
		self.total_expenditure_text.value = f"Total: ${data['total_expenditure']:,}"

		self.update_history_chart(data)

	def setup_plot(self) -> None:
		self.fig, self.axs = plt.subplots(1, 1, figsize=(12, 3))

		self.fig.tight_layout()

		self.axs.set_xlabel("Date")
		self.axs.set_ylabel("Balance")

		self.fig.subplots_adjust(left=0.08, right=0.97, top=0.98, bottom=0.15)

		self.history_chart = MatplotlibChart(self.fig, expand=True, transparent=True, original_size=False)

	def update_history_chart(self, data: FinanceData) -> None:
		y_formatter = FuncFormatter(self.balance_formatter)

		self.axs.plot(data["balance_history_dates"], data["balance_history"], linestyle="-", color="#A0CAFD")

		self.axs.yaxis.set_major_formatter(y_formatter)

	def balance_formatter(self, x: int, pos: float) -> str:
		if x < 1_000_000:
			return f"${int(x/1_000)}K"
		else:
			return f"${int(x/1_000_000)}M"