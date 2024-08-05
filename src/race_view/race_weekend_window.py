import customtkinter


class RaceWeekendWindow(customtkinter.CTkFrame):
	def __init__(self, master, view):
		super().__init__(master)

		self.view = view

		self.setup_frames()
		self.setup_labels()
		self.setup_buttons()
		self.grid_configure()

	def grid_configure(self):
		self.grid_columnconfigure(4, weight=1)

	def setup_frames(self):
		self.friday_practice_frame = customtkinter.CTkFrame(self)
		self.friday_practice_frame.grid(row=2, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

		self.saturday_practice_frame = customtkinter.CTkFrame(self)
		self.saturday_practice_frame.grid(row=3, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

		self.qualy_frame = customtkinter.CTkFrame(self)
		self.qualy_frame.grid(row=4, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

		self.warmup_frame = customtkinter.CTkFrame(self)
		self.warmup_frame.grid(row=5, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

		self.race_frame = customtkinter.CTkFrame(self)
		self.race_frame.grid(row=6, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

	def setup_labels(self):
		self.title_label = customtkinter.CTkLabel(self, text="RACE WEEKEND", font=self.view.page_title_font)
		self.title_label.grid(row=0, column=4, padx=self.view.padx*3, pady=self.view.pady, sticky="NW")

		self.race_title_label = customtkinter.CTkLabel(self, text="X GRAND PRIX", font=self.view.header1_font)
		self.race_title_label.grid(row=1, column=4, padx=self.view.padx*3, pady=self.view.pady, sticky="NW")

		customtkinter.CTkLabel(self.friday_practice_frame, text="FRIDAY PRACTICE", font=self.view.header2_font).grid(row=4, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")
		customtkinter.CTkLabel(self.friday_practice_frame, text="Session Length: 120 minutes", font=self.view.normal_font).grid(row=5, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")

		self.friday_fastest_label = customtkinter.CTkLabel(self.friday_practice_frame, text="", font=self.view.normal_font, anchor="w")
		self.friday_fastest_label.grid(row=5, column=5, padx=self.view.padx, pady=self.view.pady, sticky="NW")

		customtkinter.CTkLabel(self.saturday_practice_frame, text="SATURDAY PRACTICE", font=self.view.header2_font).grid(row=4, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")
		customtkinter.CTkLabel(self.saturday_practice_frame, text="Session Length: 90 minutes", font=self.view.normal_font).grid(row=5, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")
		
		customtkinter.CTkLabel(self.qualy_frame, text="QUALIFYING", font=self.view.header2_font).grid(row=4, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")
		customtkinter.CTkLabel(self.qualy_frame, text="Session Length: 60 minutes", font=self.view.normal_font).grid(row=5, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")
		
		customtkinter.CTkLabel(self.warmup_frame, text="SUNDAY WARMUP", font=self.view.header2_font).grid(row=4, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")
		customtkinter.CTkLabel(self.warmup_frame, text="Session Length: 30 minutes", font=self.view.normal_font).grid(row=5, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")
		
		customtkinter.CTkLabel(self.race_frame, text="RACE", font=self.view.header2_font).grid(row=4, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")
	
	def setup_buttons(self):
		self.friday_btn = customtkinter.CTkButton(self.friday_practice_frame, text="Simulate", command=lambda session="FP Friday": self.view.controller.race_controller.simulate_session(session))
		self.friday_btn.grid(row=6, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")

		self.saturday_btn = customtkinter.CTkButton(self.saturday_practice_frame, text="Simulate", state="disabled", command=lambda session="FP Saturday": self.view.controller.race_controller.simulate_session(session))
		self.saturday_btn.grid(row=6, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")

		self.qualy_btn = customtkinter.CTkButton(self.qualy_frame, text="Simulate", state="disabled", command=lambda session="Qualy": self.view.controller.race_controller.simulate_session(session))
		self.qualy_btn.grid(row=6, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")

		self.warmup_btn = customtkinter.CTkButton(self.warmup_frame, text="Simulate", state="disabled", command=lambda session="Warmup": self.view.controller.race_controller.simulate_session(session))
		self.warmup_btn.grid(row=6, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")

		self.race_btn = customtkinter.CTkButton(self.race_frame, text="Simulate", state="disabled", command=lambda session="Race": self.view.controller.race_controller.simulate_session(session))
		self.race_btn.grid(row=6, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")

		self.lap_chart_btn = customtkinter.CTkButton(self.race_frame, text="Lap Chart", command=self.view.controller.race_controller.show_lap_chart)
		
		self.continue_btn = customtkinter.CTkButton(self, text="Continue", command=self.view.controller.race_controller.return_to_main_window)

	def update_window(self, data):
		assert "current_session_name" in data.keys()
		assert data["current_session_name"] in ["FP Friday", "FP Saturday", "Qualy", "Warmup", "Race"]

		if data["current_session_name"] == "FP Friday":
			self.friday_btn.configure(state="disabled")
			self.saturday_btn.configure(state="normal")

			self.friday_fastest_label.configure(text=f"\tFastest Lap - {data['fastest_lap_summary']}")
			
		if data["current_session_name"] == "FP Saturday":
			self.saturday_btn.configure(state="disabled")
			self.qualy_btn.configure(state="normal")

			# customtkinter.CTkLabel(self.saturday_practice_frame, text=f"\tFastest Lap - {data['fastest_lap_summary']}", font=self.view.normal_font, anchor="w").grid(row=5, column=5, padx=self.view.padx, pady=self.view.pady, sticky="NW")

		if data["current_session_name"] == "Qualy":
			self.qualy_btn.configure(state="disabled")
			self.warmup_btn.configure(state="normal")

			# customtkinter.CTkLabel(self.qualy_frame, text=f"\tFastest Lap - {data['fastest_lap_summary']}", font=self.view.normal_font, anchor="w").grid(row=5, column=5, padx=self.view.padx, pady=self.view.pady, sticky="NW")

		if data["current_session_name"] == "Warmup":
			self.warmup_btn.configure(state="disabled")
			self.race_btn.configure(state="normal")

			# customtkinter.CTkLabel(self.warmup_frame, text=f"\tFastest Lap - {data['fastest_lap_summary']}", font=self.view.normal_font, anchor="w").grid(row=5, column=5, padx=self.view.padx, pady=self.view.pady, sticky="NW")

		if data["current_session_name"] == "Race":
			self.race_btn.configure(state="disabled")
			
			# customtkinter.CTkLabel(self.race_frame, text=f"\tWinner - {data['leader']}", font=self.view.normal_font, anchor="w").grid(row=5, column=5, padx=self.view.padx, pady=self.view.pady, sticky="NW")

			#add continue back to main window btn
			self.lap_chart_btn.grid(row=6, column=5, padx=self.view.padx, pady=self.view.pady, sticky="NW")
			self.continue_btn.grid(row=7, column=4, padx=self.view.padx, pady=self.view.pady, sticky="E")		

	def reset_window(self):
		'''
		reset window in preparation for the next race
		'''

		self.friday_btn.configure(state="normal")
		self.saturday_btn.configure(state="disabled")
		self.qualy_btn.configure(state="disabled")
		self.warmup_btn.configure(state="disabled")
		self.race_btn.configure(state="disabled")

		self.friday_fastest_label.configure(text="")
		self.continue_btn.grid_forget()

	def update_race_details(self, data):
		self.race_title_label.configure(text=data["race_title"])
		