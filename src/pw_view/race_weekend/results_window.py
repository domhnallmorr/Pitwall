
import flet as ft

class ResultsWindow(ft.View):
	def __init__(self, view):
		self.view = view

		self.header_text = ft.Text("Results", theme_style=self.view.page_header_style)
		self.continue_btn = ft.TextButton("Continue", on_click=self.continue_to_race_weekend)
		super().__init__(controls=[self.header_text])

	def update_page(self, data):
		standings_df = data["standings_df"]

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

		contents = [
			self.header_text,
			self.results_table,
			self.continue_btn,
			# ft.TextButton("Continue", on_click=self.continue_to_race_weekend)
		]

		self.controls = contents
		self.view.main_app.update()

	def continue_to_race_weekend(self, e):
		self.view.main_app.views.clear()
		self.view.main_app.views.append(self.view.race_weekend_window)

		self.view.main_app.update()
