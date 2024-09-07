import flet as ft

def create_session_header_text(session):

	return ft.Text(text=session)


class RaceWeekendWindow(ft.View):
	def __init__(self, view, data):
		self.view = view
		self.simulate_buttons = {}
		self.simulate_btns_clicked = []

		self.header_text = ft.Text(data["race_title"], theme_style=self.view.page_header_style)

		friday_container = self.setup_session_container("Friday Practice")
		saturday_container = self.setup_session_container("Saturday Practice")
		qualy_container = self.setup_session_container("Qualifying")
		warmup_container = self.setup_session_container("Warmup")
		race_container = self.setup_session_container("Race")

		self.continue_btn = ft.TextButton("Continue", disabled=True, on_click=self.return_to_main_window)
		self.simulate_buttons["Friday Practice"].disabled = False
		
		controls = [self.header_text, friday_container, saturday_container, qualy_container, warmup_container, race_container, self.continue_btn]

		super().__init__(controls=controls)

	def setup_session_container(self, session_title):
		
		row1 = ft.Row(
			controls=[ft.Text(session_title, theme_style=self.view.header2_style)]
		)

		self.simulate_buttons[session_title] = ft.TextButton("Simulate", on_click=self.simulate, disabled=True, data=session_title)
		row2 = ft.Row(
			controls=[self.simulate_buttons[session_title]]
		)

		column = ft.Column(
			controls=[row1, row2]
		)


		container = ft.Container(
			content=column,
			bgcolor=self.view.dark_grey,
			margin=20,
			padding=10
		)

		return container
	
	def simulate(self, e):
		session_title = e.control.data

		if session_title not in self.simulate_btns_clicked: # make sure simulate only happens once per session
			self.simulate_btns_clicked.append(session_title)

			self.simulate_buttons[session_title].disabled = True
			
			if "friday" in session_title.lower():
				self.simulate_buttons["Saturday Practice"].disabled = False
				self.view.controller.race_controller.simulate_session("FP Friday")

			elif "saturday" in session_title.lower():
				self.simulate_buttons["Qualifying"].disabled = False
				self.view.controller.race_controller.simulate_session("FP Saturday")			

			elif "qualifying" in session_title.lower():
				self.simulate_buttons["Warmup"].disabled = False
				self.view.controller.race_controller.simulate_session("Qualy")	

			elif "warmup" in session_title.lower():
				self.simulate_buttons["Race"].disabled = False
				self.view.controller.race_controller.simulate_session("Warmup")	

			elif "race" in session_title.lower():
				self.continue_btn.disabled = False
				self.view.controller.race_controller.simulate_session("Race")


	def return_to_main_window(self, e):
		self.view.controller.return_to_main_window()
		