import customtkinter
from CTkTable import *

import matplotlib
from matplotlib import style
style.use('dark_background')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

class LapChartPage(customtkinter.CTkFrame):
	def __init__(self, master, view):
		super().__init__(master)

		self.view = view
		self.results_table = None

		self.setup_frames()
		self.setup_labels()
		self.setup_buttons()
		self.setup_plot()
		self.configure_grid()

	def configure_grid(self):
		self.grid_columnconfigure(4, weight=1)
		self.grid_rowconfigure(1, weight=1)

		self.chart_frame.grid_columnconfigure(0, weight=1)
		self.chart_frame.grid_rowconfigure(2, weight=1)

	def setup_frames(self):
		self.chart_frame = customtkinter.CTkFrame(self)
		self.chart_frame.grid(row=1, column=4, padx=self.view.padx, pady=self.view.pady, sticky="NSEW")

	def setup_labels(self):
		self.title_label = customtkinter.CTkLabel(self, text="LAP CHART", font=self.view.page_title_font)
		self.title_label.grid(row=0, column=4, padx=self.view.padx*3, pady=self.view.pady, sticky="NW")

	def setup_plot(self):
		self.chart_figure = Figure(figsize=(5,5), dpi=100, facecolor=self.view.dark_gray)
		self.chart_axis = self.chart_figure.add_subplot(111)

		self.comparison_canvas = FigureCanvasTkAgg(self.chart_figure, self.chart_frame)
		self.comparison_canvas.draw()
		self.comparison_canvas.get_tk_widget().grid(row=2, column=0, columnspan=8, pady=2,sticky="NSEW")	

	def setup_buttons(self):
		self.continue_button = customtkinter.CTkButton(self.chart_frame, text="Continue", command=self.view.controller.race_controller.continue_from_lap_chart)
		self.continue_button.grid(row=3, column=7, columnspan=1, padx=self.view.padx, pady=self.view.pady, sticky="E")
	
	def update_page(self, data):
		self.chart_axis.cla()

		for driver in data["lap_chart_data"].keys():
			x = data["lap_chart_data"][driver][0]
			y = data["lap_chart_data"][driver][1]

			self.chart_axis.plot(x, y, label=driver)

		drivers = list(data["lap_chart_data"].keys())
		self.chart_axis.set_yticks([idx + 1 for idx in range(len(drivers))])
		self.chart_axis.set_yticklabels(drivers)
		self.chart_axis.yaxis.tick_right()
		self.chart_axis.invert_yaxis()

		self.comparison_canvas.draw()
