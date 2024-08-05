

import customtkinter

from pw_view.calendar_page import calendar_race_widget

class CalendarPage(customtkinter.CTkFrame):
	def __init__(self, master, view):
		super().__init__(master)

		self.view = view
		self.calendar_page_controller = self.view.controller.calendar_page_controller

		self.race_labels = []
		self.setup_frames()
		self.setup_labels()
		self.grid_configure()

	def grid_configure(self):
		self.grid_columnconfigure(4, weight=1)
		self.grid_columnconfigure(5, weight=4)

		self.grid_rowconfigure(4, weight=4)

		self.calander_frame.grid_columnconfigure(4, weight=1)
		self.track_frame.grid_columnconfigure(4, weight=1)

	def setup_frames(self):
		self.calander_frame = customtkinter.CTkScrollableFrame(self)
		self.calander_frame.grid(row=4, column=4, padx=self.view.padx_large, pady=self.view.pady_large, sticky="NSEW")

		self.track_frame = customtkinter.CTkFrame(self)
		self.track_frame.grid(row=4, column=5, padx=self.view.padx_large, pady=self.view.pady_large, sticky="NSEW")

	def setup_labels(self):
		customtkinter.CTkLabel(self, text="Calander", font=self.view.page_title_font).grid(row=3, column=4, padx=self.view.padx*3, pady=self.view.pady, sticky="NW")

		self.year_label = customtkinter.CTkLabel(self.calander_frame, text="1998 Calander", font=self.view.header1_font, anchor="w")
		self.year_label.grid(row=0, column=4, padx=self.view.padx, pady=self.view.pady_large, ipadx=0, sticky="W")

		self.race_title_label = customtkinter.CTkLabel(self.track_frame, text="Grand Prix", font=self.view.header1_font, anchor="w")
		self.race_title_label.grid(row=0, column=4, padx=self.view.padx, pady=(self.view.pady_large, self.view.pady), ipadx=0, sticky="EW")

		self.race_track_label = customtkinter.CTkLabel(self.track_frame, text="Some Track", font=self.view.normal_font, anchor="w")
		self.race_track_label.grid(row=1, column=4, padx=self.view.padx, pady=self.view.pady, ipadx=0, sticky="EW")

	def setup_widgets(self, calander):
		'''
		This gets called by the controller when a new season starts, so that we have the correct calander
		'''
		self.race_labels = []
		row = 1
		for idx, race in calander.iterrows():

			self.race_labels.append(calendar_race_widget.RaceWidget(self.calander_frame, self.view, self, idx, race["Location"], race["Country"]))
			self.race_labels[-1].grid(row=row, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

			row += 1

	def update_track_frame(self, data):
		self.race_title_label.configure(text=data["title"])
		self.race_track_label.configure(text=data["track"])

