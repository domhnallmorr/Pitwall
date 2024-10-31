import flet as ft

class GridPage(ft.Column):
	def __init__(self, view):

		self.view = view

		self.setup_buttons_row()
		
		contents = [
			ft.Text("Grid", theme_style=self.view.page_header_style),
		]

		super().__init__(controls=contents, alignment=ft.MainAxisAlignment.START)

	def setup_buttons_row(self):
		self.current_year_btn = ft.TextButton("1998", on_click=self.change_display, data="current")
		self.next_year_btn = ft.TextButton("1999", on_click=self.change_display, data="next")

		self.buttons_row = ft.Row(
			controls=[
				self.current_year_btn,
				self.next_year_btn,
			]
		)

	def update_page(self, data):
		# THIS YEAR
		self.current_year_btn.text = data["year"]
		self.next_year_btn.text = data["year"] + 1
		
		grid_this_year_df = data["grid_this_year_df"]

		columns = []
		for col in grid_this_year_df.columns:
			columns.append(ft.DataColumn(ft.Text(col)))

		df_data = grid_this_year_df.values.tolist()
		rows = []

		for row in df_data:
			cells = []
			for cell in row:
				cells.append(ft.DataCell(ft.Text(cell)))

			rows.append(ft.DataRow(cells=cells))

		self.grid_this_year_table = ft.DataTable(columns=columns, rows=rows, data_row_max_height=30, data_row_min_height=30)

		self.scrollable_grid_this_year_table = ft.Column(
			controls=[self.grid_this_year_table],
			height=self.view.main_app.window.height - self.view.vscroll_buffer,
			expand=True,  # Set height to show scrollbar if content exceeds this height
			scroll=ft.ScrollMode.AUTO  # Automatically show scrollbar when needed
		)

		# NEXT YEAR
		grid_next_year_df = data["grid_next_year_announced_df"]

		columns = []
		for col in grid_next_year_df.columns:
			columns.append(ft.DataColumn(ft.Text(col)))

		df_data = grid_next_year_df.values.tolist()
		rows = []

		for row in df_data:
			cells = []
			for cell in row:
				cells.append(ft.DataCell(ft.Text(cell)))

			rows.append(ft.DataRow(cells=cells))

		self.grid_next_year_table = ft.DataTable(columns=columns, rows=rows, data_row_max_height=30, data_row_min_height=30)

		self.scrollable_grid_next_year_table = ft.Column(
			controls=[self.grid_next_year_table],
			height=self.view.main_app.window.height - self.view.vscroll_buffer,
			expand=True,  # Set height to show scrollbar if content exceeds this height
			scroll=ft.ScrollMode.AUTO  # Automatically show scrollbar when needed
		)


	def change_display(self, e):
		controls = [
			ft.Text("Grid", theme_style=self.view.page_header_style),
			self.buttons_row,
		]	

		if e is None:
			mode = "current"
		else:
			mode = e.control.data

		if mode == "current":
			controls.append(self.scrollable_grid_this_year_table)
		elif mode == "next":
			controls.append(self.scrollable_grid_next_year_table)
			
		self.controls = controls
		self.view.main_app.update()