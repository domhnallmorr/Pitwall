from typing import Optional

import flet as ft
import matplotlib.pyplot as plt
import pandas as pd
from flet.matplotlib_chart import MatplotlibChart

from pw_view import view
from pw_view.custom_widgets import custom_container, custom_buttons

class ResultsWindow(ft.View):
	def __init__(self, view):
		self.view = view

		self.setup_buttons_row()

		self.header_text = ft.Text("Results", theme_style=self.view.page_header_style)
		
		super().__init__(controls=[self.header_text])

	def setup_buttons_row(self) -> None:
		self.classification_btn = ft.TextButton("Classification", on_click=self.display_classification)
		self.pitstops_btn = ft.TextButton("Pitstops", on_click=self.display_pitstops)
		self.lap_chart_btn = ft.TextButton("Lap Chart", on_click=self.display_lap_chart)
		self.lap_times_btn = ft.TextButton("Lap Times", on_click=self.display_lap_times_chart)

		continue_btn = custom_buttons.gen_continue_btn(self.view, on_click_func=self.continue_to_race_weekend)

		self.buttons_row = ft.Row(
			controls=[
				self.classification_btn,
				self.pitstops_btn,
			],
			expand=False,
			tight=True
		)

		self.buttons_container = custom_container.CustomContainer(self.view, self.buttons_row, expand=False)

		continue_row = ft.Row(
			controls=[
				continue_btn,
			],
			expand=False,
			tight=True
		)

		self.continue_container = custom_container.CustomContainer(self.view, continue_row, expand=False)

	def reset_tab_buttons(self) -> None:
		# When a button is clicked to view a different tab, reset all buttons style
		self.classification_btn.style = None
		self.pitstops_btn.style = None
		self.lap_chart_btn.style = None
		self.lap_times_btn.style = None

	def update_buttons_row(self, timed_session: bool) -> None:
		# update the buttons row depending on if the results are for the race or one of the timed sessions
		# e.g. pit stops tab not relevant to timed sessions

		if timed_session is False: # grand prix
			self.buttons_row.controls = [self.classification_btn, self.pitstops_btn, self.lap_chart_btn, self.lap_times_btn]
		else:
			self.buttons_row.controls = [self.classification_btn]

		self.view.main_app.update()

	def update_page(self, data: dict) -> None:
		current_session_name = data["current_session_name"]
		standings_df = data["standings_df"]
		
		# update the buttons row
		timed_session = True
		if current_session_name == "Race":
			timed_session = False

			# update pitstop table (race only)
			self.setup_pitstops_table(data["pit_stop_summary"])
			self.setup_lap_chart(data["lap_chart_data"])
			self.setup_laptimes_plot(data["lap_times_summary"])

		self.update_buttons_row(timed_session)
		self.setup_classification_table(standings_df, current_session_name)

		self.content_column = ft.Column(
			controls=[self.buttons_container, self.classification_container, self.continue_container],
			expand=True,
			spacing=20
		)

		self.background_stack = ft.Stack(
			[
				self.view.results_background_image,
				self.content_column,
			],
			expand=False,
		)

		contents = [
			self.header_text,
			self.background_stack,
		]

		self.controls = contents

		self.display_classification()
		self.view.main_app.update()

	def setup_classification_table(self, standings_df: pd.DataFrame, current_session_name: str) -> None:
		#TODO cleaup actions below should be moved to a stand alone function outside the class for unit testing
		# Format from ms to min:seconds
		standings_df.loc[:, "Fastest Lap"] = standings_df["Fastest Lap"].apply(self.ms_to_min_sec)
		
		if current_session_name == "Qualy":
			cols = ["Position", "Driver", "Team", "Fastest Lap", "Gap to Leader"]
			standings_df.loc[:, "Gap to Leader"] = standings_df["Gap to Leader"].apply(self.ms_to_min_sec, interval=True)

		elif current_session_name == "Race":
			cols = ["Position", "Driver", "Team", "Fastest Lap", "Gap to Leader", "Pit", "Grid"]
			
			# cleanup Gap to Leader column
			data = []
			for idx, row in standings_df.iterrows():
				if idx == 0:
					data.append(f"{row['Lap']} Laps")
				else:
					if row["Status"] == "retired":
						data.append(f"Retired Lap {row['Lap']}")
					elif row["Lapped Status"] is None:
						data.append(self.ms_to_min_sec(row["Gap to Leader"], interval=True))
					else:
						data.append(row["Lapped Status"])

			standings_df["Gap to Leader"] = data


		standings_df = standings_df[cols]		

		columns = []
		for col in standings_df.columns:
			columns.append(ft.DataColumn(ft.Text(col)))

		data = standings_df.values.tolist()
		rows = []

		for row in data:
			cells = []
			for cell in row:
				cells.append(ft.DataCell(ft.Text(cell)))

			rows.append(ft.DataRow(cells=cells))

		self.results_table = ft.DataTable(columns=columns, rows=rows, data_row_max_height=30, data_row_min_height=30)
	
		self.classification_container = custom_container.CustomContainer(self.view, self.results_table, expand=False)

	def setup_pitstops_table(self, pit_stop_summary: dict) -> None:
		columns = [ft.DataColumn(ft.Text("Driver")), ft.DataColumn(ft.Text("Stops")), ft.DataColumn(ft.Text("Laps"))]
		rows = []

		for driver in pit_stop_summary.keys():
			cells = []
			number_of_stops = str(len(pit_stop_summary[driver]))
			laps = ", ".join([str(lap) for lap in pit_stop_summary[driver]])

			cells.append(ft.DataCell(ft.Text(driver)))
			cells.append(ft.DataCell(ft.Text(number_of_stops)))
			cells.append(ft.DataCell(ft.Text(laps)))

			rows.append(ft.DataRow(cells=cells))

		self.pitstops_table = ft.DataTable(columns=columns, rows=rows, data_row_max_height=30, data_row_min_height=30)

		self.pitstops_container = custom_container.CustomContainer(self.view, self.pitstops_table, expand=False)

	def setup_lap_chart(self, lap_chart_data: dict) -> None:
		px = 1/plt.rcParams['figure.dpi']  # pixel in inches
		fig, ax = plt.subplots(figsize=(1820*px, 700*px))

		drivers = list(lap_chart_data.keys())
		for driver in lap_chart_data.keys():
			laps = lap_chart_data[driver][0]
			positions = lap_chart_data[driver][1]
			
			ax.plot(laps, positions, label=driver)

		ax.invert_yaxis()

		ax.set_xlabel("Lap")
		ax.set_ylabel("Position")

		ax.set_yticks(range(1, len(drivers) + 1))
		ax.set_yticklabels(drivers)
		ax.yaxis.tick_right()

		fig.subplots_adjust(left=0.02, top=0.98, bottom=0.08)
		ax.set_xlim(left=0)
		ax.grid()
		
		lap_chart = MatplotlibChart(fig, expand=True, transparent=True, original_size=False)
		self.lap_chart_container = custom_container.CustomContainer(self.view, lap_chart, expand=True)

	def setup_laptimes_plot(self, lap_times: dict) -> None:
		self.lap_times = lap_times
		
		px = 1/plt.rcParams['figure.dpi']  # pixel in inches
		fig, self.laptimes_ax = plt.subplots(figsize=(1820*px, 700*px))

		self.drivers_list = list(lap_times.keys())

		self.driver1_dropdown = ft.Dropdown(
			options=[ft.dropdown.Option(d) for d in self.drivers_list],
			width=300,
			max_menu_height=200,
			hint_text="Choose Driver 1",
			on_change=self.update_lap_times_plot,
		)

		self.driver2_dropdown = ft.Dropdown(
			options=[ft.dropdown.Option(d) for d in self.drivers_list],
			width=300,
			max_menu_height=200,
			hint_text="Choose Driver 2",
			on_change=self.update_lap_times_plot,
		)

		dropdown_row = ft.Row(
			controls=[self.driver1_dropdown, self.driver2_dropdown]
		)

		laptimes_chart = MatplotlibChart(fig, expand=True, transparent=True, original_size=False)

		column = ft.Column(
			controls=[
				dropdown_row,
				laptimes_chart
			],
		)

		self.lap_times_container = custom_container.CustomContainer(self.view, column, expand=True)

	def display_classification(self, e: Optional[ft.ControlEvent]=None) -> None:
		self.reset_tab_buttons()
		self.classification_btn.style = self.view.clicked_button_style

		self.content_column.controls=[self.buttons_container, self.classification_container, self.continue_container]
		self.view.main_app.update()

	def display_pitstops(self, e: ft.ControlEvent) -> None:
		self.reset_tab_buttons()
		self.pitstops_btn.style = self.view.clicked_button_style

		self.content_column.controls=[self.buttons_container, self.pitstops_container, self.continue_container]
		self.view.main_app.update()

	def display_lap_chart(self, e: ft.ControlEvent) -> None:
		self.reset_tab_buttons()
		self.lap_chart_btn.style = self.view.clicked_button_style

		self.content_column.controls=[self.buttons_container, self.lap_chart_container, self.continue_container]
		self.view.main_app.update()		

	def display_lap_times_chart(self, e: ft.ControlEvent) -> None:
		self.reset_tab_buttons()
		self.lap_times_btn.style = self.view.clicked_button_style

		self.content_column.controls=[self.buttons_container, self.lap_times_container, self.continue_container]
		self.view.main_app.update()	

	def continue_to_race_weekend(self, e: ft.ControlEvent) -> None:
		self.view.main_app.views.clear()
		self.view.main_app.views.append(self.view.race_weekend_window)

		self.view.main_app.update()

	def ms_to_min_sec(self, ms: Optional[int], interval: bool=False) -> str:
		if ms is None:  # Check if the value is None
			return "-" 
		else:
			minutes = ms // 60000
			seconds = (ms % 60000) / 1000
			
			if interval is False:
				return f"{int(minutes)}:{seconds:06.3f}"
			else:
				if ms < 60_000: # less than 1 min
					return f"+{seconds:06.3f}"
				else:
					return f"+{int(minutes)}:{seconds:06.3f}"
				
	def update_lap_times_plot(self, e: ft.ControlEvent) -> None:
		driver1 = self.driver1_dropdown.value
		driver2 = self.driver2_dropdown.value

		# clear plot
		self.laptimes_ax.cla()

		if driver1 is not None:
			lap_times = self.lap_times[driver1]
			lap_numbers = [i + 1 for i in range(len(lap_times))]
			self.laptimes_ax.plot(lap_numbers, lap_times, label=driver1)

		if driver2 is not None:
			lap_times = self.lap_times[driver2]
			lap_numbers = [i + 1 for i in range(len(lap_times))]
			self.laptimes_ax.plot(lap_numbers, lap_times, label=driver2)

		self.laptimes_ax.grid()
		self.laptimes_ax.legend()
		self.view.main_app.update()