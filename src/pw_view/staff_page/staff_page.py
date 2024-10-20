import flet as ft

class StaffPage(ft.Column):
	def __init__(self, view):

		self.view = view
		self.setup_buttons_row()
		self.setup_widgets()
		self.setup_driver_containers()
		self.setup_manager_containers()

		contents = [
			ft.Text("Staff", theme_style=self.view.page_header_style),
			self.buttons_row,
			self.driver_row,
		]

		super().__init__(expand=1, controls=contents)

	def setup_buttons_row(self):
		self.manager_button = ft.TextButton("Management", on_click=self.display_managers,
									  style=ft.ButtonStyle(
                								color={
													ft.ControlState.FOCUSED: ft.colors.WHITE,
													}
													)
										)


		self.buttons_row = ft.Row(
			# expand=1,
			controls=[
				ft.TextButton("Drivers", on_click=self.display_drivers),
				self.manager_button
			]
		)

	def setup_widgets(self):
		self.driver_name_texts = [ft.Text(f"Driver1"), ft.Text(f"Driver2")]
		self.driver_age_texts = [ft.Text(f"25"), ft.Text(f"32")]
		self.driver_country_texts = [ft.Text(f"UK"), ft.Text(f"USA")]

		self.driver_contract_length_texts = [ft.Text(f"2"), ft.Text(f"3")]
		self.driver_contract_status_texts = [ft.Text(f"Contracted"), ft.Text(f"Contracted")]

		self.driver_ability_texts = [ft.Text(f"80"), ft.Text(f"65")]

		self.driver_replace_buttons = [
			ft.TextButton("Replace", disabled=True, icon="find_replace", on_click=self.replace_driver, data="driver1"),
			ft.TextButton("Replace", disabled=True, icon="find_replace", on_click=self.replace_driver, data="driver2")
			]

		self.technical_director_text = ft.Text(f"Technical Director Name")
		self.technical_director_age_text = ft.Text(f"Technical Director Age")
		self.technical_director_contract_length_text = ft.Text(f"Technical Director Contact Length")
		self.technical_director_contract_status_text = ft.Text(f"Status: Contracted")
		self.technical_director_skill_text = ft.Text(f"Ability: 100")

		self.commercial_manager_text = ft.Text(f"Commercial Manager Name")
		self.commercial_manager_age_text = ft.Text(f"Commercial Manager Age")
		self.commercial_manager_contract_length_text = ft.Text(f"Commercial Manager Contact Length")
		self.commercial_manager_contract_status_text = ft.Text(f"Status: Contracted")
		self.commercial_manager_skill_text = ft.Text(f"Ability: 100")

	def setup_driver_containers(self):
		self.driver_containers = []

		for idx in [0, 1]:
			column = ft.Column(
				# expand=1,
				controls=[
					ft.Text("Personal Details", weight=ft.FontWeight.BOLD, size=25,),
					self.driver_name_texts[idx],
					self.driver_age_texts[idx],
					self.driver_country_texts[idx],
					ft.Divider(),

					ft.Text("Contract", weight=ft.FontWeight.BOLD, size=25,),
					self.driver_contract_length_texts[idx], # length left on contract
					self.driver_contract_status_texts[idx], # status
					self.driver_replace_buttons[idx], # replace button
					ft.Divider(),

					ft.Text("Stats", weight=ft.FontWeight.BOLD, size=25,),
					self.driver_ability_texts[idx],
					],
				expand=True
			)

			#TODO make this contain a custom class with inheritence
			container = ft.Container(
				# expand=1,
				content=column,
				bgcolor=self.view.dark_grey,
				margin=20,
				padding=10,
				width=200,
				expand=True,
				border_radius=15,
			)

			self.driver_containers.append(container)

		self.driver_row = ft.Row(
			# expand=1,
			controls=[
				self.driver_containers[0],
				self.driver_containers[1],
			]
		)

	def setup_manager_containers(self):
		self.manager_containers = []

		for manager in ["Technical Director", "Commercial Manager"]:
			controls = [
				ft.Text(manager, weight=ft.FontWeight.BOLD, size=35,),
				ft.Text("Personal Details", weight=ft.FontWeight.BOLD, size=25,),
				]

			if manager == "Technical Director":
				controls.append(self.technical_director_text)
				controls.append(self.technical_director_age_text)

			elif manager == "Commercial Manager":
				controls.append(self.commercial_manager_text)
				controls.append(self.commercial_manager_age_text)
			controls.append(ft.Divider())
			
			# CONTRACT ----------------------
			controls.append(ft.Text("Contract", weight=ft.FontWeight.BOLD, size=25,))

			if manager == "Technical Director":
				controls.append(self.technical_director_contract_length_text)
				controls.append(self.technical_director_contract_status_text)
			elif manager == "Commercial Manager":
				controls.append(self.commercial_manager_contract_length_text)
				controls.append(self.commercial_manager_contract_status_text)

			controls.append(ft.Divider())

			# STATS ----------------------
			controls.append(ft.Text("Stats", weight=ft.FontWeight.BOLD, size=25,))
			if manager == "Technical Director":
				controls.append(self.technical_director_skill_text)
			elif manager == "Commercial Manager":
				controls.append(self.commercial_manager_skill_text)

			column = ft.Column(
				# expand=1,
				controls=controls,
				expand=True
			)

			#TODO make this contain a custom class with inheritence
			container = ft.Container(
				# expand=1,
				content=column,
				bgcolor=self.view.dark_grey,
				margin=20,
				padding=10,
				width=200,
				expand=True,
				border_radius=15,
			)

			self.manager_containers.append(container)

		self.manager_row = ft.Row(
			controls = [
				self.manager_containers[0],
				self.manager_containers[1],
			]
		)

	def update_page(self, data):
		self.driver_name_texts[0].value = f"Name: {data['driver1']}"
		self.driver_name_texts[1].value = f"Name: {data['driver2']}"

		self.driver_age_texts[0].value = f"Age: {data['driver1_age']} Years"
		self.driver_age_texts[1].value = f"Age: {data['driver2_age']} Years"

		self.driver_country_texts[0].value = f"Country: {data['driver1_country']}"
		self.driver_country_texts[1].value = f"Country: {data['driver2_country']}"

		# Ability
		self.driver_ability_texts[0].value = f"Ability: {data['driver1_speed']}"
		self.driver_ability_texts[1].value = f"Ability: {data['driver2_speed']}"

		# Contract Length
		self.driver_contract_length_texts[0].value = f"Contract Length: {data['driver1_contract_length']} Years"
		self.driver_contract_length_texts[1].value = f"Contract Length: {data['driver2_contract_length']} Years"

		# Contract Status

		for idx, driver_idx in enumerate(["driver1", "driver2"]):
			text = "Contracted"

			if data[f"{driver_idx}_retiring"] is True:
				text = "Retiring"
			elif data[f"{driver_idx}_contract_length"] < 2:
				text = "Contract Expiring"

			self.driver_contract_status_texts[idx].value = f"Status: {text}"

		# Enable/Disable replace buttons
		for idx, r in enumerate([data["player_requiring_driver1"], data["player_requiring_driver2"]]):
			if r is True:
				self.driver_replace_buttons[idx].disabled = False
			else:
				self.driver_replace_buttons[idx].disabled = True # can't replace a driver if a driver is in place for next year, disable button

		# Update technical director
		self.technical_director_text.value = f"Name: {data['technical_director']}"
		self.technical_director_age_text.value = f"Age: {data['technical_director_age']}"
		self.technical_director_contract_length_text.value = f"Contract Length: {data['technical_director_contract_length']} Years"
		self.technical_director_skill_text.value = f"Ability: {data['technical_director_skill']}"

		# Update commercial manager
		self.commercial_manager_text.value = f"Name: {data['commercial_manager']}"
		self.commercial_manager_age_text.value = f"Age: {data['commercial_manager_age']}"
		self.commercial_manager_contract_length_text.value = f"Contract Length: {data['commercial_manager_contract_length']} Years"
		self.commercial_manager_skill_text.value = f"Ability: {data['commercial_manager_skill']}"

		self.view.main_app.update()

	def replace_driver(self, e):

		self.view.controller.driver_hire_controller.launch_replace_driver(e.control.data)

	def display_drivers(self, e):
		self.controls = [
			ft.Text("Staff", theme_style=self.view.page_header_style),
			self.buttons_row,
			self.driver_row,
		]

		self.view.main_app.update()

	def display_managers(self, e):
		self.controls = [
			ft.Text("Staff", theme_style=self.view.page_header_style),
			self.buttons_row,
			self.manager_row,
		]

		self.view.main_app.update()