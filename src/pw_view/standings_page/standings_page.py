import customtkinter
from CTkTable import *

class StandingsPage(customtkinter.CTkFrame):
	def __init__(self, master, view):
		super().__init__(master)

		self.view = view

		self.drivers_table = None

		self.setup_frames()
		self.setup_labels()
		self.setup_widgets()
		self.grid_configure()

	def grid_configure(self):
		self.grid_columnconfigure(4, weight=1)
		self.grid_rowconfigure(4, weight=1)

	def setup_frames(self):
		self.standings_frame = customtkinter.CTkFrame(self)
		self.standings_frame.grid(row=4, column=4, padx=self.view.padx_large, pady=self.view.pady_large, sticky="NSEW")

	def setup_labels(self):
		customtkinter.CTkLabel(self, text="Standings", font=self.view.page_title_font).grid(row=3, column=4, padx=self.view.padx*3, pady=self.view.pady, sticky="NW")

	def setup_widgets(self):
		self.tab_view = customtkinter.CTkTabview(master=self.standings_frame, anchor="nw")
		self.tab_view.grid(row=4, column=4, padx=self.view.padx_large, pady=self.view.pady_large, sticky="NSEW")

		self.tab_view.add("Drivers")  # add tab at the end
		self.tab_view.add("Constructors")  # add tab at the end

	def update_standings(self, data):

		# DRIVERS
		columns = data["drivers_standings_df"].columns.tolist()
		standings = data["drivers_standings_df"].values.tolist()
		standings.insert(0, columns)

		# add position
		for idx, row in enumerate(standings):
			if idx == 0:
				row.insert(0, "#")
			else:
				row.insert(0, idx)

		if self.drivers_table is not None:
			self.drivers_table.update_values(standings)
		else:
			self.drivers_table = CTkTable(master=self.tab_view.tab("Drivers"), values=standings)
			self.drivers_table.grid(row=1, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

		# CONSTRUCTORS
		columns = data["constructors_standings_df"].columns.tolist()
		standings = data["constructors_standings_df"].values.tolist()
		standings.insert(0, columns)

		# add position
		for idx, row in enumerate(standings):
			if idx == 0:
				row.insert(0, "#")
			else:
				row.insert(0, idx)
		
		self.contructors_table = CTkTable(master=self.tab_view.tab("Constructors"), values=standings)
		self.contructors_table.grid(row=1, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")