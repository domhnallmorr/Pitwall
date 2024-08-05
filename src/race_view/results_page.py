import customtkinter
from CTkTable import *

class ResultsPage(customtkinter.CTkFrame):
	def __init__(self, master, view):
		super().__init__(master)

		self.view = view
		self.results_table = None

		self.setup_frames()
		self.setup_labels()
		self.setup_buttons()
		self.configure_grid()

	def configure_grid(self):
		self.grid_columnconfigure(4, weight=1)
		self.grid_rowconfigure(1, weight=1)

	def setup_frames(self):
		self.results_frame = customtkinter.CTkFrame(self)
		self.results_frame.grid(row=1, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

	def setup_labels(self):
		self.title_label = customtkinter.CTkLabel(self, text="RESULTS", font=self.view.page_title_font)
		self.title_label.grid(row=0, column=4, padx=self.view.padx*3, pady=self.view.pady, sticky="NW")

		self.session_label = customtkinter.CTkLabel(self.results_frame, text="SESSION", font=self.view.header2_font)
		self.session_label.grid(row=0, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")

	def update_page(self, data):
		if self.results_table is None:
			self.results_table = CTkTable(master=self.results_frame, values=data["standings_df"].values.tolist())
			self.results_table.grid(row=1, column=4, columnspan=2, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")
		else:
			self.results_table.update_values(data["standings_df"].values.tolist())

		text = "SESSION"

		if data["current_session_name"] == "FP Friday":
			text = "FRIDAY PRACTICE"
		elif data["current_session_name"] == "FP Saturday":
			text = "SATURDAY PRACTICE"
		elif data["current_session_name"] == "Qualy":
			text = "QUALIFYING"
		elif data["current_session_name"] == "Warmup":
			text = "WARMUP"

		self.session_label.configure(text=text)

	def setup_buttons(self):
		self.continue_button = customtkinter.CTkButton(self.results_frame, text="Continue", command=self.view.controller.race_controller.continue_from_results)
		self.continue_button.grid(row=2, column=5, columnspan=1, padx=self.view.padx, pady=self.view.pady, sticky="E")