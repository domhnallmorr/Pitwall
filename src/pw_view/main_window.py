import customtkinter
from tksheet import Sheet


class MainWindow(customtkinter.CTkFrame):
	def __init__(self, master, view):
		super().__init__(master)

		self.view = view

		self.setup_widgets()
		self.configure_grid()

	def configure_grid(self):
		self.grid_columnconfigure(1, weight=1)
		self.grid_rowconfigure(1, weight=1)

		self.header_frame.grid_columnconfigure(8, weight=1)
		self.sidebar_frame.grid_rowconfigure(20, weight=1)

		self.page_frame.grid_columnconfigure(0, weight=1)
		self.page_frame.grid_rowconfigure(0, weight=1)

	def setup_widgets(self):
		self.home_icon = customtkinter.CTkImage(light_image=self.view.home_icon2, size=(15, 15))
		self.email_icon = customtkinter.CTkImage(light_image=self.view.email_icon2, size=(15, 15))
		self.calendar_icon = customtkinter.CTkImage(light_image=self.view.calendar_icon2, size=(15, 15))
		self.standings_icon = customtkinter.CTkImage(light_image=self.view.table_icon2, size=(15, 15))
		self.car_icon = customtkinter.CTkImage(light_image=self.view.car_icon2, size=(15, 15))
		self.advance_icon = customtkinter.CTkImage(light_image=self.view.advance_icon2, size=(15, 15))

		self.header_frame = customtkinter.CTkFrame(self)
		self.header_frame.grid(row=0, column=0, columnspan=2, sticky="EW")
	
		self.sidebar_frame = customtkinter.CTkFrame(self, fg_color="transparent")
		self.sidebar_frame.grid(row=1, column=0, padx=0, pady=0, sticky="NSEW")

		self.page_frame = customtkinter.CTkFrame(self, fg_color="transparent")
		self.page_frame.grid(row=1, column=1, padx=0, pady=0, sticky="NSEW")

		# HEADER LABELS
		self.header_label = customtkinter.CTkLabel(self.header_frame, text="Williams $5,762,308", font=self.view.normal_font)
		self.header_label.grid(row=0, column=0, padx=self.view.padx, sticky="NW")

		self.week_label = customtkinter.CTkLabel(self.header_frame, text="Week 1 - 1998", font=self.view.normal_font)
		self.week_label.grid(row=0, column=8, padx=self.view.padx, sticky="NE")

		# SIDEBAR BUTTONS
		self.home_btn = customtkinter.CTkButton(master=self.sidebar_frame, text="Home", image=self.home_icon, anchor="w",
										   command=lambda window="home": self.view.change_window(window))
		self.home_btn.grid(row=0, column=0, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

		self.email_btn = customtkinter.CTkButton(master=self.sidebar_frame, text="Email", image=self.email_icon, anchor="w",
										   command=lambda window="email": self.view.change_window(window))
		self.email_btn.grid(row=1, column=0, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

		# self.team_btn = customtkinter.CTkButton(master=self.sidebar_frame, text="Team", command=self.view.controller.show_player_team_page)
		# self.team_btn.grid(row=2, column=0, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

		self.standings_btn = customtkinter.CTkButton(master=self.sidebar_frame, text="Standings", image=self.standings_icon, anchor="w",
					       command=lambda window="standings": self.view.change_window(window))
		self.standings_btn.grid(row=3, column=0, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

		self.calender_btn = customtkinter.CTkButton(master=self.sidebar_frame, text="Calendar", image=self.calendar_icon, anchor="w",
					      command=lambda window="calendar": self.view.change_window(window))
		self.calender_btn.grid(row=4, column=0, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

		self.finances_btn = customtkinter.CTkButton(master=self.sidebar_frame, text="Finances",
					      command=lambda window="finance": self.view.change_window(window))
		self.finances_btn.grid(row=5, column=0, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

		self.sponsors_btn = customtkinter.CTkButton(master=self.sidebar_frame, text="Sponsors",
					      command=lambda window="sponsors": self.view.change_window(window))
		self.sponsors_btn.grid(row=6, column=0, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

		self.car_btn = customtkinter.CTkButton(master=self.sidebar_frame, text="Car", image=self.car_icon, anchor="w",
					      command=lambda window="car": self.view.change_window(window))
		self.car_btn.grid(row=7, column=0, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

		self.advance_btn = customtkinter.CTkButton(master=self.sidebar_frame, text="Advance", fg_color=self.view.success_color, image=self.advance_icon, anchor="w",
					     							hover_color=self.view.success_color_darker, command=self.view.controller.advance)
		self.advance_btn.grid(row=20, column=0, padx=self.view.padx, pady=self.view.pady, sticky="SW")

	def update_window(self, data):
		self.week_label.configure(text=data["date"])

		if data["in_race_week"] is True:
			self.advance_btn.configure(text="Go To Race", command=self.view.controller.go_to_race_weekend)
		else:
			self.advance_btn.configure(text="Advance")

		# if "player_team" in data.keys():
		# 	self.header_label.configure(text=data["player_team"])

		# if data["new_mails"] > 0:
		# 	self.email_btn.configure(text=f"Email ({data['new_mails']})")
		# else:
		# 	self.email_btn.configure(text=f"Email")
		

	def update_advance_btn(self, mode):
		if mode == "advance":
			self.advance_btn.configure(text="Advance", command=self.view.controller.advance)
		else:
			self.advance_btn.configure(text="Go To Race Weekend", command=lambda window="race_weekend": self.view.change_window(window))