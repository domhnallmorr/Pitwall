import flet as ft

from pw_view.custom_widgets import custom_container, custom_buttons

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
		self.qualy_container = self.setup_session_container("Qualifying")
		warmup_container = self.setup_session_container("Warmup")
		self.race_container = self.setup_session_container("Race")

		self.continue_btn = custom_buttons.gen_continue_btn(self.view, on_click_func=self.return_to_main_window)
		self.continue_btn.disabled = True

		self.continue_container = custom_buttons.buttons_row(view, [self.continue_btn])

		# self.continue_btn = ft.TextButton("Continue", disabled=True, on_click=self.return_to_main_window)
		self.simulate_buttons["Qualifying"].disabled = False
		
		# comment out to remove practice sessions for now, will add back later when they are of value
		# controls = [self.header_text, friday_container, saturday_container, qualy_container, warmup_container, race_container, self.continue_btn]
		
		controls = self.setup_page()

		super().__init__(controls=controls, scroll="auto")

	def setup_page(self) -> list:
		self.content_column = ft.Column(
			controls=[self.qualy_container, self.race_container, self.continue_container],
			expand=True,
			spacing=20
		)

		self.background_stack = ft.Stack(
			[
				self.view.race_background_image,
				self.content_column,
			],
			expand=False,
		)

		controls = [
			self.header_text,
			self.background_stack,
		]

		return controls

	def setup_session_container(self, session_title: str) -> ft.Container:
		
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

		container = custom_container.CustomContainer(self.view, column, expand=False)

		return container
	
	def simulate(self, e):
		session_title = e.control.data

		if session_title not in self.simulate_btns_clicked: # make sure simulate only happens once per session
			self.simulate_btns_clicked.append(session_title)

			self.simulate_buttons[session_title].disabled = True
			self.view.main_app.update()
			
			if "friday" in session_title.lower():
				self.simulate_buttons["Saturday Practice"].disabled = False
				self.view.controller.race_controller.simulate_session("FP Friday")

			elif "saturday" in session_title.lower():
				self.simulate_buttons["Qualifying"].disabled = False
				self.view.controller.race_controller.simulate_session("FP Saturday")			

			elif "qualifying" in session_title.lower():
				self.simulate_buttons["Race"].disabled = False
				self.view.controller.race_controller.simulate_session("Qualy")	

			elif "warmup" in session_title.lower():
				self.simulate_buttons["Race"].disabled = False
				self.view.controller.race_controller.simulate_session("Warmup")	

			elif "race" in session_title.lower():
				self.continue_btn.disabled = False
				self.view.controller.race_controller.simulate_session("Race")


	def return_to_main_window(self, e):
		self.continue_btn.disabled = True
		self.view.main_app.update()
		
		self.view.controller.post_race_actions()
		