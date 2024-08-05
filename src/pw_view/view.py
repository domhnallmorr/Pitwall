from tkinter import ttk
from tkinter import *

import customtkinter

from pw_view import home_page, main_window, calendar_page, icons
from pw_view.calendar_page import calendar_page
from pw_view.car_page import car_page
from pw_view.email_page import email_page
from pw_view.standings_page import standings_page
from race_view import race_weekend_window, results_page, lap_chart_page

class View:
	def __init__(self, controller):
		self.controller = controller

		self.pady = 5
		self.padx = 7

		self.padx_large = 25 # if a large gap is needed
		self.pady_large = 25 # if a large gap is needed
		
		self.success_color = "#33871C"
		self.success_color_darker = "#194F0A"
		self.warning_color = "#f56342"
		self.warning_color_darker = "#e0340d"

		self.light_gray = "#666464"
		self.dark_gray = "#2B2B2B"

		self.normal_font = ("Verdana", 15)
		self.page_title_font = ("Verdana", 30)
		self.header1_font = ("Verdana", 24)
		self.header2_font = ("Verdana", 20)

		icons.setup_icons(self)

		self.setup_pages()

	def setup_pages(self):
		self.main_window = main_window.MainWindow(self.controller.app, self)
		self.main_window.pack(expand=True, fill=BOTH, side=LEFT)

		self.calendar_page = calendar_page.CalendarPage(self.main_window.page_frame, self)
		self.car_page = car_page.CarPage(self.main_window.page_frame, self)
		self.email_page = email_page.EmailPage(self.main_window.page_frame, self)
		self.standings_page = standings_page.StandingsPage(self.main_window.page_frame, self)

		self.home_page = home_page.HomePage(self.main_window.page_frame, self)
		self.home_page.grid(row=0, column=0, sticky="NSEW")
		self.current_page = self.home_page

	def setup_race_pages(self):
		self.race_weekend_window = race_weekend_window.RaceWeekendWindow(self.controller.app, self)
		self.results_page = results_page.ResultsPage(self.controller.app, self)
		self.lap_chart_page = lap_chart_page.LapChartPage(self.controller.app, self)

	def change_window(self, window):
		self.current_page.grid_forget()

		if window == "home":
			self.current_page = self.home_page

		elif window == "calendar":
			self.current_page = self.calendar_page

		elif window == "car":
			self.current_page = self.car_page

		elif window == "email":
			self.current_page = self.email_page

		elif window == "standings":
			self.current_page = self.standings_page

		self.current_page.grid(row=0, column=0, sticky="NSEW")

	def go_to_race_weekend(self, data):
		self.race_weekend_window.update_race_details(data)
		self.main_window.pack_forget()
		self.race_weekend_window.pack(expand=True, fill=BOTH, side=LEFT)

	def return_to_main_window(self):
		'''
		return from race weekend window
		'''
		self.race_weekend_window.reset_window()
		self.race_weekend_window.pack_forget()
		self.main_window.pack(expand=True, fill=BOTH, side=LEFT)
		self.change_window("home")


	def show_simulated_session_results(self):
		'''
		simulate session is called from weekend page, so remove that first, then show results page
		'''
		self.race_weekend_window.pack_forget()
		self.results_page.pack(expand=True, fill=BOTH, side=LEFT)

	def continue_from_results_page(self):
		self.results_page.pack_forget()
		self.race_weekend_window.pack(expand=True, fill=BOTH, side=LEFT)

	def show_lap_chart(self):
		self.race_weekend_window.pack_forget()
		self.lap_chart_page.pack(expand=True, fill=BOTH, side=LEFT)

	def continue_from_lap_chart(self):
		self.lap_chart_page.pack_forget()
		self.race_weekend_window.pack(expand=True, fill=BOTH, side=LEFT)
