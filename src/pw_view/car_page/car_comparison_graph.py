from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft
from flet import (
	LineChart,
	LineChartData,
	LineChartDataPoint,
	ChartAxis,
	ChartGridLines,
)
import matplotlib.pyplot as plt
from flet.matplotlib_chart import MatplotlibChart

from pw_view.helper_functions.chart_functions import create_line_chart_data, create_line_chart, create_chart_axis, create_legend
from pw_view.helper_functions.chart_functions import create_country_axis

if TYPE_CHECKING:
	from pw_view.view import View

SpeedHistory = dict[str, list[int]]

class CarComparisonGraph(ft.Row): # type: ignore
	def __init__(self, view: View):
		self.view = view

		x = [1, 2 , 3]
		y = [100, 20, 36]

		data_1 = [create_line_chart_data(x, y)]
		x_values = [i+1 for i in range(16)]
		x_labels = [str(i) for i in x_values]
		self.chart = create_line_chart(data_1, create_chart_axis(x_labels, x_values))
		self.legend = ft.Column()

		super().__init__(controls=[self.chart, self.legend], expand=True, tight=True, spacing=20)

	def update_plot(self, car_speed_history: dict[str, list[int]], team_colors: dict[str, str], countries: list[str]) -> None:
		first_team = list(car_speed_history.keys())[0]
		# create a list of LineChartData objects
		line_chart_data = []
		for team in car_speed_history.keys():
			history = car_speed_history[team]
			color = team_colors[team]
			x = [i for i in range(1, len(history) + 1)]
			y = history
			line_chart_data.append(create_line_chart_data(x, y, color=color))

		self.chart.data_series = line_chart_data
		self.chart.bottom_axis = create_country_axis(countries)
		self.chart.min_x = 1
		self.chart.max_x = 16

		if len(car_speed_history[first_team]) > 0:	
			self.chart.min_y = min(min(history) for history in car_speed_history.values()) - 10
			self.chart.max_y = max(max(history) for history in car_speed_history.values()) + 10
		
		self.legend.controls = [create_legend(car_speed_history.keys(), team_colors.values())]

