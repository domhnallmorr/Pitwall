import flet as ft

class StandingsPage(ft.Column):
	def __init__(self, view):

		self.view = view
		self.setup_standings_tables()
		self.setup_buttons_row()

		contents = [
			ft.Text("Standings", theme_style=self.view.page_header_style),
			self.buttons_row,
			self.drivers_table
		]

		super().__init__(controls=contents, expand=1)

	def setup_standings_tables(self):

		self.drivers_table = ft.DataTable(
			columns=[
                ft.DataColumn(ft.Text("Driver")),
                ft.DataColumn(ft.Text("Team")),
                ft.DataColumn(ft.Text("Points"), numeric=True),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Jacques Villeneuve")),
                        ft.DataCell(ft.Text("Williams")),
                        ft.DataCell(ft.Text("0")),
                    ],
                ),
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Jack")),
                        ft.DataCell(ft.Text("Brown")),
                        ft.DataCell(ft.Text("19")),
                    ],
                ),
            ],
        )

	def setup_buttons_row(self):
		self.buttons_row = ft.Row(
			controls=[
				ft.TextButton("Drivers", on_click=self.display_drivers),
				ft.TextButton("Constructors", on_click=self.display_constructors)
			]
		)

	def update_standings(self, data):
		
		# DRIVERS
		drivers_standings_df = data["drivers_standings_df"]
		constructors_standings_df = data["constructors_standings_df"]

		columns = []
		for col in drivers_standings_df.columns:
			columns.append(ft.DataColumn(ft.Text(col)))

		data = drivers_standings_df.values.tolist()
		rows = []

		for row in data:
			cells = []
			for cell in row:
				cells.append(ft.DataCell(ft.Text(cell)))

			rows.append(ft.DataRow(cells=cells))

		self.drivers_table = ft.DataTable(columns=columns, rows=rows, data_row_max_height=30, data_row_min_height=30)

		self.scrollable_drivers_table = ft.Column(
			controls=[self.drivers_table],
			height=self.view.main_app.window.height - self.view.vscroll_buffer,
			expand=True,  # Set height to show scrollbar if content exceeds this height
			scroll=ft.ScrollMode.AUTO  # Automatically show scrollbar when needed
		)

		# CONSTRUCTORS
		 
		columns = []
		for col in constructors_standings_df.columns:
			columns.append(ft.DataColumn(ft.Text(col)))

		data = constructors_standings_df.values.tolist()
		rows = []

		for row in data:
			cells = []
			for cell in row:
				cells.append(ft.DataCell(ft.Text(cell)))

			rows.append(ft.DataRow(cells=cells))

		self.constructors_table = ft.DataTable(columns=columns, rows=rows, data_row_max_height=30, data_row_min_height=30)		

		self.scrollable_constructors_table = ft.Column(
			controls=[self.constructors_table],
			height=700,
			# expand=True,  # Set height to show scrollbar if content exceeds this height
			scroll=ft.ScrollMode.AUTO  # Automatically show scrollbar when needed
		)

		contents = [
			ft.Text("Standings", theme_style=self.view.page_header_style),
			self.buttons_row,
			self.scrollable_drivers_table
		]

		self.controls = contents
		self.view.main_app.update()


	def display_drivers(self, e):
		self.arrange_controls("drivers")
		
	def display_constructors(self, e):
		self.arrange_controls("constructors")

	def arrange_controls(self, mode):
		assert mode in ["drivers", "constructors"]

		controls = [
			ft.Text("Standings", theme_style=self.view.page_header_style),
			self.buttons_row,
		]

		if mode == "drivers":
			controls.append(self.scrollable_drivers_table)
		elif mode == "constructors":
			controls.append(self.scrollable_constructors_table)
		
		self.controls = controls
		self.view.main_app.update()
