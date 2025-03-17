from __future__ import annotations
from typing import Optional, TYPE_CHECKING
import flet as ft

from pw_model.pw_model_enums import StaffRoles
from pw_view.staff_page.staff_dialogs import RejectionDialog, AcceptDialog
from pw_view.custom_widgets import custom_container

if TYPE_CHECKING:
	from pw_view.view import View

class HireStaffPage(ft.Column):
	def __init__(self, view: View):
		
		self.view = view
		self.accept_dialog = AcceptDialog(view)
		self.rejection_dialog = RejectionDialog()

		self.setup_contract_column()

		self.title_text = ft.Text("Hire Driver", theme_style=self.view.page_header_style)
		self.current_role = None # tracks wether player is hiring driver, technical director, etc

		super().__init__(expand=1)

	def update_free_agent_list(self, free_agents: list[str], role: StaffRoles, previously_approached: list[str]) -> None:
		title = role.value.title().replace("1", " 1").replace("2", " 2")
		self.title_text.value = f"Hire: {title}"
		self.current_role = role

		rows = []
		self.name_text_buttons: list[ft.TextButton] = []

		for name in free_agents:
			disabled = False
			if name in previously_approached:
				disabled = True

			self.name_text_buttons.append(ft.TextButton(name, data=name, on_click=self.update_staff, disabled=disabled))

			row = ft.DataRow(
				cells = [
						ft.DataCell(self.name_text_buttons[-1])
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

		self.free_agents_container = custom_container.CustomContainer(
			self.view,
			self.free_agents_column,
			expand=True
		)
		
		self.setup_page()

		self.update_staff(None, name=free_agents[0])
		
	def setup_contract_column(self) -> None:
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

		self.container_container = custom_container.CustomContainer(
			self.view,
			self.contract_column,
			expand=True
		)


	def setup_page(self) -> None:
		content_row = ft.Row(
			controls=[
				self.free_agents_container,
				self.container_container
			],
			expand=True
		)

		self.background_stack = ft.Stack(
			[
				self.view.background_image,
				content_row
			],
			expand=True
		)

		self.controls = [
			self.title_text,
			self.background_stack
		]

		self.view.main_app.update()

	def update_staff(self, e: ft.ControlEvent, name: Optional[str]=None) -> None:
		if name is None:
			name = e.control.data

		details = self.view.controller.staff_hire_controller.get_staff_details(name, self.current_role)
		self.name_text.value = f"Driver Name: {details['name']}"
		self.age_text.value = f"Driver Age: {details['age']}"

		self.offer_btn.data = name
		self.offer_btn.disabled = False
		self.view.main_app.update()

	def approach_staff(self, e: ft.ControlEvent) -> None:
		name = e.control.data

		if self.current_role in [StaffRoles.DRIVER1, StaffRoles.DRIVER2]:
			self.view.controller.staff_hire_controller.make_driver_offer(name, self.current_role)
			self.offer_btn.disabled = True
			self.disable_name_text_button(name)
			self.view.main_app.update()
		else:
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
			self.view.controller.staff_hire_controller.complete_hire(name, self.current_role)

	def show_accept_dialog(self, name: str, role: StaffRoles) -> None:
		self.accept_dialog.update_text_widget(name, role)

		if self.accept_dialog in self.view.main_app.overlay:
			self.view.main_app.overlay.remove(self.accept_dialog)
	
		self.view.main_app.overlay.append(self.accept_dialog)
		self.accept_dialog.open = True
		self.view.main_app.update()

	def show_rejection_dialog(self, name: str) -> None:
		self.rejection_dialog.update_text_widget(name)

		if self.rejection_dialog in self.view.main_app.overlay:
			self.view.main_app.overlay.remove(self.rejection_dialog)

		self.view.main_app.overlay.append(self.rejection_dialog)
		self.rejection_dialog.open = True
		self.view.main_app.update()

	def disable_name_text_button(self, name: str) -> None:
		for btn in self.name_text_buttons:
			if btn.data == name:
				btn.disabled = True
				break
		self.view.main_app.update()