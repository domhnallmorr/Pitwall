import flet as ft

from pw_view.custom_widgets import custom_container

class GridPage(ft.Column):
	def __init__(self, view):

		self.view = view

		self.setup_buttons_row()
		
		contents = [
			ft.Text("Grid", theme_style=self.view.page_header_style),
		]

		super().__init__(controls=contents, alignment=ft.MainAxisAlignment.START, expand=True)

	def reset_tab_buttons(self) -> None:
		# When a button is clicked to view a different tab, reset all buttons style
		self.current_year_btn.style = None
		self.next_year_btn.style = None

	def setup_buttons_row(self):
		self.current_year_btn = ft.TextButton("1998", on_click=self.change_display, data="current")
		self.next_year_btn = ft.TextButton("1999", on_click=self.change_display, data="next")

		self.buttons_row = ft.Row(
			controls=[
				self.current_year_btn,
				self.next_year_btn,
			],
			expand=False,
			tight=True
		)

		self.buttons_container = custom_container.CustomContainer(self.view, self.buttons_row, expand=False)

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
			# height=self.view.main_app.window.height - self.view.vscroll_buffer,
			# expand=True,  # Set height to show scrollbar if content exceeds this height
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
			# height=self.view.main_app.window.height - self.view.vscroll_buffer,
			# expand=False,  # Set height to show scrollbar if content exceeds this height
			scroll=ft.ScrollMode.AUTO  # Automatically show scrollbar when needed
		)


	def change_display(self, e):
		self.reset_tab_buttons()

		if e is None:
			mode = "current"
		else:
			mode = e.control.data

		if mode == "current":
			self.current_year_btn.style = self.view.clicked_button_style
			container = custom_container.CustomContainer(self.view, self.scrollable_grid_this_year_table, expand=False)
		elif mode == "next":
			self.next_year_btn.style = self.view.clicked_button_style
			container = custom_container.CustomContainer(self.view, self.scrollable_grid_next_year_table, expand=False)

		column = ft.Column(
			controls=[self.buttons_container, container],
			expand=False,
			spacing=10
		)

		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				column
			],
			expand=False
		)

		page_controls = [
			ft.Text("Grid", theme_style=self.view.page_header_style),
			self.background_stack
		]

		self.controls = page_controls
		self.view.main_app.update()