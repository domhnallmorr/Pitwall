
import customtkinter
from tksheet import Sheet
from tkinter import *

from CTkTable import *

class HomePage(customtkinter.CTkFrame):
	def __init__(self, master, view):
		super().__init__(master)

		self.view = view

		self.setup_frames()
		self.setup_labels()
		self.setup_tables()

	def setup_frames(self):
		self.team_frame = customtkinter.CTkFrame(self)
		self.team_frame.grid(row=4, column=4, padx=self.view.padx_large, pady=self.view.pady_large, sticky="NSEW")

		self.standings_frame = customtkinter.CTkFrame(self)
		self.standings_frame.grid(row=5, column=4, padx=self.view.padx_large, pady=self.view.pady_large, sticky="NSEW")

		self.next_race_frame = customtkinter.CTkFrame(self)
		self.next_race_frame.grid(row=4, column=5, columnspan=2, padx=self.view.padx_large, pady=self.view.pady_large, sticky="NSEW")
		
		self.driver1_frame = customtkinter.CTkFrame(self)
		self.driver1_frame.grid(row=5, column=5, padx=self.view.padx_large, pady=self.view.pady_large, sticky="NSEW")

		self.driver2_frame = customtkinter.CTkFrame(self)
		self.driver2_frame.grid(row=5, column=6, padx=self.view.padx_large, pady=self.view.pady_large, sticky="NSEW")

	def setup_labels(self):
		self.title_label = customtkinter.CTkLabel(self, text="HOME", font=self.view.page_title_font)
		self.title_label.grid(row=0, column=4, padx=self.view.padx*3, pady=self.view.pady, sticky="NW")

		customtkinter.CTkLabel(self.team_frame, text="Team", font=self.view.header1_font).grid(row=0, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")
		customtkinter.CTkLabel(self.driver1_frame, text="Driver 1", font=self.view.header1_font).grid(row=0, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")
		customtkinter.CTkLabel(self.driver2_frame, text="Driver 2", font=self.view.header1_font).grid(row=0, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")
		customtkinter.CTkLabel(self.standings_frame, text="Standings", font=self.view.header1_font).grid(row=0, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")
		customtkinter.CTkLabel(self.next_race_frame, text="Next Race", font=self.view.header1_font).grid(row=0, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")
	
		# Team Labels
		self.team_name_label = customtkinter.CTkLabel(self.team_frame, text="Williams", font=self.view.normal_font)
		self.team_name_label.grid(row=2, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")

		# Driver Labels
		self.driver1_name_label = customtkinter.CTkLabel(self.driver1_frame, text="Jacques Villeneuve", font=self.view.normal_font)
		self.driver1_name_label.grid(row=2, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")

		self.driver1_age_label = customtkinter.CTkLabel(self.driver1_frame, text="Age: 28", font=self.view.normal_font)
		self.driver1_age_label.grid(row=3, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")

		self.driver2_name_label = customtkinter.CTkLabel(self.driver2_frame, text="Heinz-Harald Frentzen", font=self.view.normal_font)
		self.driver2_name_label.grid(row=2, column=4, padx=(0, self.view.padx), pady=self.view.pady, sticky="NW")

		self.driver2_age_label = customtkinter.CTkLabel(self.driver2_frame, text="Age: 29", font=self.view.normal_font)
		self.driver2_age_label.grid(row=3, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")

		# Next Race
		self.next_race_name_label = customtkinter.CTkLabel(self.next_race_frame, text="Australian Grand Prix", font=self.view.normal_font)
		self.next_race_name_label.grid(row=2, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NW")

	def setup_tables(self):
		value = [
			[1, "Williams", 0],
			[2, "Ferrari", 0],
			[3, "Benetton", 0],
			[4, "McLaren", 0],
			[5, "Jordan", 0],
			[6, "Prost", 0],
			[7, "Sauber", 0],
			[8, "Stewart", 0],
			[9, "Arrows", 0],
			[10, "Tyrell", 0],
			[11, "Minardi", 0],
		 ]

		self.standings_table = CTkTable(master=self.standings_frame, values=value)
		self.standings_table.grid(row=1, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

	def update_page(self, data):
		self.next_race_name_label.configure(text=data["next_race"])

		standings = data["constructors_standings_df"][["Team", "Points"]].values.tolist()
		for idx, s in enumerate(standings):
			standings[idx].insert(0, idx + 1)

		self.standings_table.update_values(standings)

		