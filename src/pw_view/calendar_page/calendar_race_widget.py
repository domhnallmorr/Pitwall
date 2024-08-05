
import customtkinter

class RaceWidget(customtkinter.CTkFrame):
	def __init__(self, master, view, calander_page, idx, location, country):
		super().__init__(master)

		self.view = view
		self.calander_page = calander_page
		self.idx = idx # round number, zero indexed
		self.location = location
		self.country = country

		self.setup_labels()
		self.grid_configure()

		self.round_label.bind("<Enter>", self.on_enter)
		self.round_label.bind("<Leave>", self.on_leave)
		
		self.track_label.bind("<Enter>", self.on_enter)
		self.track_label.bind("<Leave>", self.on_leave)
		
		self.country_label.bind("<Enter>", self.on_enter)
		self.country_label.bind("<Leave>", self.on_leave)

	def grid_configure(self):
		self.grid_columnconfigure(0, weight=1)

	def setup_labels(self):
		self.round_label = customtkinter.CTkLabel(self, text=f"Round {self.idx + 1}", font=self.view.header2_font, anchor="w")
		self.round_label.grid(row=0, column=0, padx=self.view.padx, pady=0, sticky="NSEW")

		self.track_label = customtkinter.CTkLabel(self, text=f"{self.location}", font=self.view.normal_font)
		self.track_label.grid(row=1, column=0, padx=self.view.padx, pady=0, sticky="NSEW")

		self.country_label = customtkinter.CTkLabel(self, text=f"{self.country}", font=self.view.normal_font)
		self.country_label.grid(row=2, column=0, padx=self.view.padx, pady=0, sticky="NSEW")	

	def on_enter(self, event):
		self.configure(fg_color=self.view.light_gray)
		self.round_label.configure(fg_color=self.view.light_gray)
		self.track_label.configure(fg_color=self.view.light_gray)
		self.country_label.configure(fg_color=self.view.light_gray)

		self.calander_page.calendar_page_controller.update_track_frame(self.idx)

	def on_leave(self, event):
		self.configure(fg_color=self.view.dark_gray)
		self.round_label.configure(fg_color=self.view.dark_gray)
		self.track_label.configure(fg_color=self.view.dark_gray)
		self.country_label.configure(fg_color=self.view.dark_gray)