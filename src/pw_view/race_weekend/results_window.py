from typing import Optional

import flet as ft

class ResultsWindow(ft.View):
	def __init__(self, view):
		self.view = view

		self.header_text = ft.Text("Results", theme_style=self.view.page_header_style)
		self.continue_btn = ft.TextButton("Continue", on_click=self.continue_to_race_weekend)
		super().__init__(controls=[self.header_text])

	def update_page(self, data: dict) -> None:
		current_session_name = data["current_session_name"]
		standings_df = data["standings_df"]
		
		#TODO cleaup actions below should be moved to a stand alone function outside the class for unit testing
		# Format from ms to min:seconds
		standings_df.loc[:, "Fastest Lap"] = standings_df["Fastest Lap"].apply(self.ms_to_min_sec)
		
		if current_session_name == "Qualy":
			cols = ["Position", "Driver", "Team", "Fastest Lap", "Gap to Leader"]
			standings_df.loc[:, "Gap to Leader"] = standings_df["Gap to Leader"].apply(self.ms_to_min_sec, interval=True)

		elif current_session_name == "Race":
			cols = ["Position", "Driver", "Team", "Fastest Lap", "Gap to Leader", "Pit"]
			
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
		print(standings_df)
			

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

		container = ft.Container(
				# expand=1,
				content=self.results_table,
				bgcolor=self.view.dark_grey,
				margin=20,
				padding=10,
				# width=200,
				expand=True,
				border_radius=15,
			)

		contents = [
			self.header_text,
			container,
			self.continue_btn,
			# ft.TextButton("Continue", on_click=self.continue_to_race_weekend)
		]

		self.controls = contents
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
				