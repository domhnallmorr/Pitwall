from typing import Union

import flet as ft

Number = Union[int, float]

def create_line_chart_data(x: list[Number], y: list[Number], color: str=ft.Colors.PRIMARY) -> ft.LineChartData:
	assert len(x) == len(y), "x and y must be the same length"
	
	data_points = [ft.LineChartDataPoint(x[i], y[i]) for i in range(len(x))]

	return ft.LineChartData(
		data_points=data_points,
		stroke_width=2,
		color=color,
		point=True,
	)

def create_line_chart(line_chart_data: list[ft.LineChartData], x_axis: ft.ChartAxis) -> ft.LineChart:
	return ft.LineChart(
		data_series=line_chart_data,
		border=ft.border.all(3, ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE)),
		expand=True,
		bottom_axis=x_axis,
		)

def create_chart_axis(labels: list[str], values: list[Number]) -> ft.ChartAxis:
	axis_labels: list[ft.ChartAxisLabel] = []

	for idx, label in enumerate(labels):
		label = ft.Container(
			# content=ft.Text(label, color=ft.Colors.PRIMARY),
			content=ft.Image(
				src=fr"C:\Users\domhn\Documents\python\Pitwall\src\pw_view\assets\flags_small\Belgium.png",
				width=20,
				height=20,
				fit=ft.ImageFit.CONTAIN
			),
			margin=ft.margin.only(top=10, left=10)
		)
		# label = ft.Text(label, color=ft.Colors.PRIMARY)
		chart_axis_label = ft.ChartAxisLabel(value=values[idx], label=label)
		axis_labels.append(chart_axis_label)

	return ft.ChartAxis(
		labels=axis_labels,
		labels_size=30,
	)

def create_country_axis(countries: list[str]) -> ft.ChartAxis:
	axis_labels: list[ft.ChartAxisLabel] = []

	for idx, country in enumerate(countries):
		label = ft.Container(
			content=ft.Image(
				src=fr"C:\Users\domhn\Documents\python\Pitwall\src\pw_view\assets\flags_small\{country}.png",
				width=20,
				height=20,
				fit=ft.ImageFit.CONTAIN
			),
			margin=ft.margin.only(top=10, left=10)
		)
		chart_axis_label = ft.ChartAxisLabel(value=idx+1, label=label)
		axis_labels.append(chart_axis_label)

	return ft.ChartAxis(
		labels=axis_labels,
		labels_size=30,
	)

def create_legend(labels: list[str], colors: list[str]) -> ft.Column:
	legend_items = []
	for label, color in zip(labels, colors):
		legend_items.append(
			ft.Row(
				controls=[
					ft.Container(
						width=10,
						height=10,
						bgcolor=color,
					),
					ft.Text(label),
				],
				spacing=5,
			)
		)

	return ft.Column(controls=legend_items, spacing=10)