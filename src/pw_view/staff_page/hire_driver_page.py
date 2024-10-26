from typing import Optional
import flet as ft

class HireDriverPage(ft.Column):
	def __init__(self, view):

		self.view = view
		self.setup_contract_column()

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
						ft.DataCell(ft.TextButton(name, data=name, on_click=self.update_driver))
				]
			)
			
			rows.append(row)

		columns=[
            ft.DataColumn(label=ft.Text("Name")),
		]

		self.free_agent_table = ft.DataTable(columns=columns, rows=rows, data_row_max_height=30, data_row_min_height=30, width=300)
		
		# Make table scrollable

		self.scrollable_free_agents_table = ft.Column(
			controls=[self.free_agent_table],
			height=self.view.main_app.window.height - self.view.vscroll_buffer,
			expand=True,  # Set height to show scrollbar if content exceeds this height
			scroll=ft.ScrollMode.AUTO  # Automatically show scrollbar when needed
		)

		self.free_agents_column = ft.Column(
			controls=[
				ft.Text("Free Agents", weight=ft.FontWeight.BOLD, size=25,),
				self.scrollable_free_agents_table,
			],
			expand=True
		)

		self.setup_page()

		self.update_driver(None, name=free_agents[0])
		
	def setup_contract_column(self):
		self.name_text = ft.Text("Driver Name: Some Driver")
		self.age_text = ft.Text("Driver Age: 99")
		self.contract_length_text = ft.Text("Contract Length: 2 years")

		self.offer_btn = ft.TextButton("Offer", on_click=self.approach_driver)

		self.contract_column = ft.Column(
			controls=[
				ft.Text("Contract Details", weight=ft.FontWeight.BOLD, size=25,),
				self.name_text,
				self.age_text,
				self.contract_length_text,
				self.offer_btn
			]
		)


	def setup_page(self):
		content_row = ft.Row(
			controls=[
				self.free_agents_column,
				self.contract_column
			],
			expand=True
		)

		self.controls = [
			ft.Text("Hire Driver", theme_style=self.view.page_header_style),
			content_row
		]

		self.view.main_app.update()

	def update_driver(self, e: ft.ControlEvent, name: Optional[str]=None) -> None:
		if name is None:
			name = e.control.data

		details = self.view.controller.driver_hire_controller.get_driver_details(name)
		self.name_text.value = f"Driver Name: {details['name']}"
		self.age_text.value = f"Driver Age: {details['age']}"

		self.offer_btn.data = name
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
		