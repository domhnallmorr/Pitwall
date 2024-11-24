from enum import Enum
from typing import Optional
import flet as ft

from pw_model.pw_model_enums import StaffRoles

class HireStaffPage(ft.Column):
	def __init__(self, view):

		self.view = view
		self.setup_contract_column()

		self.title_text = ft.Text("Hire Driver", theme_style=self.view.page_header_style)
		self.curent_role = None # tracks wether player is hiring driver, technical director, etc

		contents = [
			self.title_text,
			# self.buttons_row,
			# self.driver_row,
		]

		super().__init__(expand=1, controls=contents)

	def update_free_agent_list(self, free_agents: list, role: Enum):
		self.title_text.value = role.value
		self.curent_role = role

		rows = []

		for name in free_agents:
			row = ft.DataRow(
				cells = [
						ft.DataCell(ft.TextButton(name, data=name, on_click=self.update_staff))
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

		self.free_agents_container = ft.Container(
				content=self.free_agents_column,
				bgcolor=self.view.dark_grey,
				margin=20,
				padding=10,
				width=200,
				expand=True,
				border_radius=15,
			)
		
		self.setup_page()

		self.update_staff(None, name=free_agents[0])
		
	def setup_contract_column(self):
		self.name_text = ft.Text("Driver Name: Some Driver")
		self.age_text = ft.Text("Driver Age: 99")
		self.contract_length_text = ft.Text("Contract Length: 2 years")

		self.offer_btn = ft.TextButton("Offer", on_click=self.approach_staff)

		self.contract_column = ft.Column(
			controls=[
				ft.Text("Contract Details", weight=ft.FontWeight.BOLD, size=25,),
				self.name_text,
				self.age_text,
				self.contract_length_text,
				self.offer_btn
			]
		)

		self.container_container = ft.Container(
				# expand=1,
				content=self.contract_column,
				bgcolor=self.view.dark_grey,
				margin=20,
				padding=10,
				width=200,
				expand=True,
				border_radius=15,
			)


	def setup_page(self):
		content_row = ft.Row(
			controls=[
				self.free_agents_container,
				self.container_container
			],
			expand=True
		)

		self.controls = [
			ft.Text("Hire Driver", theme_style=self.view.page_header_style),
			content_row
		]

		self.view.main_app.update()

	def update_staff(self, e: ft.ControlEvent, name: Optional[str]=None) -> None:
		if name is None:
			name = e.control.data

		details = self.view.controller.staff_hire_controller.get_staff_details(name, self.curent_role)
		self.name_text.value = f"Driver Name: {details['name']}"
		self.age_text.value = f"Driver Age: {details['age']}"

		self.offer_btn.data = name
		self.view.main_app.update()

	def approach_staff(self, e: ft.ControlEvent) -> None:
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
		
	def handle_close(self, e: ft.ControlEvent) -> None:
		name = self.dlg_modal.data
		self.view.main_app.close(self.dlg_modal)
		action = e.control.text

		if action.lower() == "yes":
			self.view.controller.staff_hire_controller.complete_hire(name, self.curent_role)
		