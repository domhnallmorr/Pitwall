from __future__ import annotations
from enum import Enum
from typing import Optional, TYPE_CHECKING

import flet as ft
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from flet.matplotlib_chart import MatplotlibChart

from race_weekend_model.race_model_enums import SessionNames
from pw_view import view
from pw_view.custom_widgets import custom_container, custom_buttons
from pw_view.custom_widgets.custom_datatable import CustomDataTable

from pw_controller.race_controller import RaceSessionData

from race_weekend_model.race_model_enums import ParticipantStatus, RetirementReasons

if TYPE_CHECKING:
	from pw_view.view import View

class ResultsWindow(ft.View):
	def __init__(self, view: View):
		self.view = view

		self.setup_lap_chart()
		self.setup_laptimes_plot()
		
		self.header_text = ft.Text("Results", theme_style=self.view.page_header_style)
		
		# Setup tabs first since we'll need them in update_page
		self.setup_tabs()
		
		super().__init__(controls=[self.header_text])

	def setup_tabs(self) -> None:
		self.classification_tab = ft.Tab(
			text="Classification",
			icon=ft.Icons.TABLE_CHART,
			content=ft.Container(
				expand=False,
				alignment=ft.alignment.top_center
			)
		)
		
		self.pitstops_tab = ft.Tab(
			text="Pitstops",
			icon=ft.Icons.LOCAL_GAS_STATION,
			content=ft.Container(
				expand=False,
				alignment=ft.alignment.top_center
			)
		)

		self.lap_chart_tab = ft.Tab(
			text="Lap Chart",
			icon=ft.Icons.STACKED_LINE_CHART,
			content=ft.Container(
				expand=False,
				alignment=ft.alignment.top_center
			)
		)

		self.lap_times_tab = ft.Tab(
			text="Lap Times",
			icon=ft.Icons.TIMER,
			content=ft.Container(
				expand=False,
				alignment=ft.alignment.top_center
			)
		)

		self.commentary_tab = ft.Tab(
			text="Commentary",
			icon=ft.Icons.MIC,
			content=ft.Container(
				expand=False,
				alignment=ft.alignment.top_center
			)
		)

		self.tabs = ft.Tabs(
			selected_index=0,
			animation_duration=300,
			tabs=[
				self.classification_tab,
				self.pitstops_tab,
				self.lap_chart_tab,
				self.lap_times_tab,
				self.commentary_tab
			],
			expand=True
		)

	def setup_classification_table(self, standings_df: pd.DataFrame, current_session: Enum, driver_flags: list[str]) -> None:
		# Create a new column for formatted lap times
		standings_df["Formatted Lap"] = standings_df["Fastest Lap"].apply(self.ms_to_min_sec)
		
		if current_session == SessionNames.QUALIFYING:
			cols = ["Position", "Driver", "Team", "Formatted Lap", "Gap"]
			# create the gap column
			standings_df.loc[:, "Gap"] = standings_df["Gap to Leader"].apply(lambda x: self.ms_to_min_sec(x, interval=True))

		elif current_session == SessionNames.RACE:
			cols = ["Position", "Driver", "Team", "Formatted Lap", "Gap to Leader", "Gap Ahead", "Pit", "Grid"]
			
			# clean up Gap to Leader/ahead column
			data = []
			data_ahead = [] # for Gap Ahead column
			
			for idx, row in standings_df.iterrows():
				if idx == 0:
					data.append(f"{row['Lap']} Laps")
					data_ahead.append("-")
				else:
					if row["Status"] == ParticipantStatus.RETIRED:
						data.append(f"Retired Lap {row['Lap']} ({row['Retirement Reason'].value})")
						data_ahead.append("-")
					elif row["Lapped Status"] is None:
						'''
						Added this to catch cases where the gap is a string, rather than an int
						This is for the show results button on the race weekend window
						DF/column has already been string formatted, so just use the string value
						See below for Gap Ahead, same applies
						'''
						#TODO better handling for formatted df
						if type(row["Gap to Leader"]) is str:
							data.append(row["Gap to Leader"])
						else:
							data.append(self.ms_to_min_sec(row["Gap to Leader"], interval=True))
					else:
						data.append(row["Lapped Status"])

					if row["Status"] != ParticipantStatus.RETIRED:
						if type(row["Gap Ahead"]) is str:
							data_ahead.append(row["Gap Ahead"])
						else:
							data_ahead.append(self.ms_to_min_sec(row["Gap Ahead"], interval=True))
					
			standings_df["Gap to Leader"] = data
			standings_df["Gap Ahead"] = data_ahead

		# Use the new formatted column instead of overwriting the original
		standings_df = standings_df[cols]		

		standings_df = standings_df.rename(columns={"Formatted Lap": "Fastest Lap"})

		self.results_table = CustomDataTable(self.view, standings_df.columns.tolist())
		self.results_table.update_table_data(standings_df.values.tolist(), flag_col_idx=1, flags=driver_flags)

	def setup_pitstops_table(self, pit_stop_summary: dict, driver_flags: list[str]) -> None:
		data = []
		for driver in pit_stop_summary.keys():
			number_of_stops = str(len(pit_stop_summary[driver]))
			laps = ", ".join([str(lap) for lap in pit_stop_summary[driver]])
			data.append([driver, number_of_stops, laps])

		self.pitstops_table = CustomDataTable(self.view, ["Driver", "Stops", "Laps"])
		self.pitstops_table.update_table_data(data, flag_col_idx=0, flags=driver_flags)

	def setup_lap_chart(self) -> None:
		px = 1/plt.rcParams['figure.dpi']  # pixel in inches
		self.lap_chart_fig, self.lap_chart_ax = plt.subplots(figsize=(1820*px, 700*px))

	def update_lap_chart(self, lap_chart_data: dict) -> None:
		self.lap_chart_ax.cla()

		drivers = list(lap_chart_data.keys())
		for driver in lap_chart_data.keys():
			laps = lap_chart_data[driver][0]
			positions = lap_chart_data[driver][1]
			
			self.lap_chart_ax.plot(laps, positions, label=driver)

		self.lap_chart_ax.invert_yaxis()

		self.lap_chart_ax.set_xlabel("Lap")
		self.lap_chart_ax.set_ylabel("Position")

		self.lap_chart_ax.set_yticks(range(1, len(drivers) + 1))
		self.lap_chart_ax.set_yticklabels(drivers)
		self.lap_chart_ax.yaxis.tick_right()

		self.lap_chart_fig.subplots_adjust(left=0.02, top=0.98, bottom=0.08)
		self.lap_chart_ax.set_xlim(left=0)
		self.lap_chart_ax.grid()
		
		lap_chart = MatplotlibChart(self.lap_chart_fig, expand=True, transparent=True, original_size=False)
		self.lap_chart_container = custom_container.CustomContainer(self.view, lap_chart, expand=True)

	def setup_laptimes_plot(self) -> None:
		px = 1/plt.rcParams['figure.dpi']  # pixel in inches
		self.laptimes_fig, self.laptimes_ax = plt.subplots(figsize=(1820*px, 700*px))

	def update_laptimes_plot(self, lap_times: dict[str, list[int]]) -> None:
		self.laptimes_ax.cla()

		self.lap_times = lap_times
		self.drivers_list = list(lap_times.keys())

		self.driver1_dropdown = ft.Dropdown(
			options=[ft.dropdown.Option(d) for d in self.drivers_list],
			width=300,
			menu_height=200,
			hint_text="Choose Driver 1",
			on_change=self.update_lap_times_plot,
		)

		self.driver2_dropdown = ft.Dropdown(
			options=[ft.dropdown.Option(d) for d in self.drivers_list],
			width=300,
			menu_height=200,
			hint_text="Choose Driver 2",
			on_change=self.update_lap_times_plot,
		)

		dropdown_row = ft.Row(
			controls=[self.driver1_dropdown, self.driver2_dropdown]
		)

		laptimes_chart = MatplotlibChart(self.laptimes_fig, expand=True, transparent=True, original_size=False)

		column = ft.Column(
			controls=[
				dropdown_row,
				laptimes_chart
			],
		)

		self.lap_times_container = custom_container.CustomContainer(self.view, column, expand=True)

	def setup_commentary_table(self) -> None:
		self.commentary_table = CustomDataTable(self.view, ["Lap", "Message"])
		# Initially empty data
		self.commentary_table.update_table_data([], flag_col_idx=None, flags=None)

	def update_page(self, data: RaceSessionData) -> None:
		current_session = data["current_session"]
		standings_df = data["standings_df"]
		driver_flags = data["driver_flags"]
		
		# Update tabs visibility based on session type
		timed_session = current_session != SessionNames.RACE
		if timed_session:
			self.tabs.tabs = [self.classification_tab]
		else:
			self.tabs.tabs = [
				self.classification_tab,
				self.pitstops_tab,
				self.lap_chart_tab,
				self.lap_times_tab,
				self.commentary_tab
			]
			
			# Update race-specific tabs
			self.setup_pitstops_table(data["pit_stop_summary"], driver_flags)
			self.update_lap_chart(data["lap_chart_data"])
			self.update_laptimes_plot(data["lap_times_summary"])
			self.setup_commentary_table()  # Add this line
			self.commentary_table.update_table_data(data["commentary"].values.tolist()) 
			
			self.pitstops_tab.content.content = self.pitstops_table.list_view
			self.lap_chart_tab.content.content = self.lap_chart_container
			self.lap_times_tab.content.content = self.lap_times_container
			self.commentary_tab.content.content = self.commentary_table.list_view  # Add this line

		# Update classification tab
		self.setup_classification_table(standings_df, current_session, driver_flags)
		self.classification_tab.content.content = self.results_table.list_view

		continue_btn = custom_buttons.gen_continue_btn(
			self.view, 
			on_click_func=self.continue_to_race_weekend
		)
		
		self.continue_container = custom_container.CustomContainer(
			self.view, 
			continue_btn, 
			expand=False
		)

		self.content_column = ft.Column(
			controls=[self.tabs, self.continue_container],
			expand=True,
			spacing=20
		)

		self.background_stack = ft.Stack(
			[
				self.view.results_background_image,
				self.content_column,
			],
			expand=True,
		)

		contents = [
			self.header_text,
			self.background_stack,
		]

		self.controls = contents
		self.view.main_app.update()

	def continue_to_race_weekend(self, e: ft.ControlEvent) -> None:
		self.view.main_app.views.clear()
		self.view.main_app.views.append(self.view.race_weekend_window)

		self.view.main_app.update()

	def ms_to_min_sec(self, ms: Optional[int], interval: bool=False) -> str:
		if pd.isna(ms):  # This will catch both None and np.nan
			return "-" 
		
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

		# Track min/max laptimes excluding pit stops
		all_laptimes = []

		if driver1 is not None:
			lap_times = self.lap_times[driver1]
			lap_numbers = [i + 1 for i in range(len(lap_times))]
			self.laptimes_ax.plot(lap_numbers, lap_times, label=driver1)
			# Filter out pit stop laps (typically >20s slower than regular laps)
			regular_laps = [t for t in lap_times if t < min(lap_times) * 1.15]
			all_laptimes.extend(regular_laps)

		if driver2 is not None:
			lap_times = self.lap_times[driver2]
			lap_numbers = [i + 1 for i in range(len(lap_times))]
			self.laptimes_ax.plot(lap_numbers, lap_times, label=driver2)
			regular_laps = [t for t in lap_times if t < min(lap_times) * 1.15]
			all_laptimes.extend(regular_laps)

		if all_laptimes:
			# Set y-axis limits with some padding
			min_time = min(all_laptimes)
			max_time = max(all_laptimes)
			padding = (max_time - min_time) * 0.1  # 10% padding
			self.laptimes_ax.set_ylim(min_time - padding, max_time + padding)

		self.laptimes_ax.grid()
		self.laptimes_ax.legend()
		self.view.main_app.update()




