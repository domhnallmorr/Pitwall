from __future__ import annotations
from enum import Enum
from typing import Optional, TYPE_CHECKING

import flet as ft
import matplotlib.pyplot as plt
import pandas as pd
from flet.matplotlib_chart import MatplotlibChart

from race_weekend_model.race_model_enums import SessionNames
from pw_view import view
from pw_view.custom_widgets import custom_container, custom_buttons
from pw_view.custom_widgets.custom_datatable import CustomDataTable

from pw_controller.race_controller import RaceSessionData

from race_weekend_model.race_model_enums import ParticipantStatus

if TYPE_CHECKING:
	from pw_view.view import View

class ResultsWindow(ft.View):
	def __init__(self, view: View):
		self.view = view

		self.setup_buttons_row()
		self.setup_lap_chart()
		self.setup_laptimes_plot()

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

	def update_page(self, data: RaceSessionData) -> None:
		current_session = data["current_session"]
		standings_df = data["standings_df"]
		driver_flags = data["driver_flags"]
		
		# update the buttons row
		timed_session = True
		if current_session == SessionNames.RACE:
			timed_session = False

			# update pitstop table (race only)
			self.setup_pitstops_table(data["pit_stop_summary"], driver_flags)
			self.update_lap_chart(data["lap_chart_data"])
			self.update_laptimes_plot(data["lap_times_summary"])

		self.update_buttons_row(timed_session)
		self.setup_classification_table(standings_df, current_session, driver_flags)

		self.content_column = ft.Column(
			controls=[self.buttons_container, self.results_table.list_view, self.continue_container],
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

		self.display_classification()
		self.view.main_app.update()

	def setup_classification_table(self, standings_df: pd.DataFrame, current_session: Enum, driver_flags: list[str]) -> None:
		#TODO cleaup actions below should be moved to a stand alone function outside the class for unit testing
		# Format from ms to min:seconds
		standings_df.loc[:, "Fastest Lap"] = standings_df["Fastest Lap"].apply(self.ms_to_min_sec)
		
		if current_session == SessionNames.QUALIFYING:
			cols = ["Position", "Driver", "Team", "Fastest Lap", "Gap"]
			# create the gap column, prior to V0.10.0, pandas gave warning for unsupported dtype when overwriting "Gap To Leader" col
			standings_df.loc[:, "Gap"] = standings_df["Gap to Leader"].apply(lambda x: self.ms_to_min_sec(x, interval=True))

		elif current_session == SessionNames.RACE:
			cols = ["Position", "Driver", "Team", "Fastest Lap", "Gap to Leader", "Pit", "Grid"]
			
			# cleanup Gap to Leader column
			data = []
			for idx, row in standings_df.iterrows():
				if idx == 0:
					data.append(f"{row['Lap']} Laps")
				else:
					if row["Status"] == ParticipantStatus.RETIRED:
						data.append(f"Retired Lap {row['Lap']}")
					elif row["Lapped Status"] is None:
						data.append(self.ms_to_min_sec(row["Gap to Leader"], interval=True))
					else:
						data.append(row["Lapped Status"])

			standings_df["Gap to Leader"] = data


		standings_df = standings_df[cols]		

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

		laptimes_chart = MatplotlibChart(self.laptimes_fig, expand=True, transparent=True, original_size=False)

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

		self.content_column.controls=[self.buttons_container, self.results_table.list_view, self.continue_container]
		self.view.main_app.update()

	def display_pitstops(self, e: ft.ControlEvent) -> None:
		self.reset_tab_buttons()
		self.pitstops_btn.style = self.view.clicked_button_style

		self.content_column.controls=[self.buttons_container, self.pitstops_table.list_view, self.continue_container]
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