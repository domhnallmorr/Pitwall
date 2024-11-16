import flet as ft

from pw_view.custom_widgets import custom_container

class CalendarPage(ft.Column):
	def __init__(self, view):

		self.view = view

		self.header_text = ft.Text("Calendar", theme_style=self.view.page_header_style)
		contents = [
			self.header_text
		]

		super().__init__(controls=contents, expand=1)

	def update_page(self, data):
		calendar = data["calendar"]

		# Add a Round column based on index, maybe this should be added to the model

		calendar.insert(0, "#", calendar.index + 1)

		columns = []

		column_names = calendar.columns.values.tolist()
		for idx, col in enumerate(column_names):
			column_content = custom_container.HeaderContainer(self.view, col)
			columns.append(ft.DataColumn(column_content))

		data = calendar.values.tolist()
		rows = []

		for row in data:
			cells = []
			for cell in row:
				cells.append(ft.DataCell(ft.Text(cell)))

			rows.append(ft.DataRow(cells=cells))

		self.calendar_table = ft.DataTable(columns=columns, rows=rows, data_row_max_height=30, data_row_min_height=30,
									 heading_row_color=ft.colors.PRIMARY, border_radius=15,)

		column = ft.Column(
			controls=[self.calendar_table],
			expand=False,
			tight=True,
			spacing=20
		)

		container = custom_container.CustomContainer(self.view, column, expand=False)

		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				container
			],
			expand=True
		)

		contents = [
			self.header_text,
			self.background_stack
		]

		self.controls = contents
		self.view.main_app.update()
