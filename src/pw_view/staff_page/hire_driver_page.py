import flet as ft

class HireDriverPage(ft.Column):
	def __init__(self, view):

		self.view = view
		# self.setup_buttons_row()
		# self.setup_widgets()


		contents = [
			ft.Text("Hire Driver", theme_style=self.view.page_header_style),
			# self.buttons_row,
			# self.driver_row,
		]

		super().__init__(expand=1, controls=contents)

	def update_free_agent_list(self, free_agents):
		
		rows = []

		for name in free_agents:
			row = ft.DataRow(
				cells = [
					ft.DataCell(ft.Text(name)),
					ft.DataCell(ft.TextButton("Approach", data=name, on_click=self.approach_driver))
				]
			)
			
			rows.append(row)

		columns=[
            ft.DataColumn(label=ft.Text("Name")),
            ft.DataColumn(label=ft.Text("")), # btn column
		]

		self.free_agent_table = ft.DataTable(columns=columns, rows=rows, data_row_max_height=30, data_row_min_height=30)
		
		# Make table scrollable

		self.scrollable_free_agents_table = ft.Column(
			controls=[self.free_agent_table],
			height=self.view.main_app.window.height - self.view.vscroll_buffer,
			expand=True,  # Set height to show scrollbar if content exceeds this height
			scroll=ft.ScrollMode.AUTO  # Automatically show scrollbar when needed
		)

		contents = [
			ft.Text("Hire Driver", theme_style=self.view.page_header_style),
			self.scrollable_free_agents_table,
		]
		
		self.controls = contents
		self.view.main_app.update()

	def approach_driver(self, e):
		print(e.control.data)
		name = e.control.data

		self.dlg_modal = ft.AlertDialog(
			modal=True,
			title=ft.Text(f"Confirm"),
			content=ft.Text(f"Complete Hiring of {name}?"),
			actions=[
				ft.TextButton("Yes", on_click=self.handle_close),
				ft.TextButton("No", on_click=self.handle_close),
			],
			actions_alignment=ft.MainAxisAlignment.END,
			data=name
		)

		# self.view.main_app.open(dlg_modal)
		self.view.main_app.overlay.append(self.dlg_modal)
		self.dlg_modal.open = True
		self.view.main_app.update()
		
	def handle_close(self, e):
		name = self.dlg_modal.data
		self.view.main_app.close(self.dlg_modal)
		action = e.control.text


		if action.lower() == "yes":
			self.view.controller.driver_hire_controller.complete_hire(name)
		