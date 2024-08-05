import customtkinter
import matplotlib
from matplotlib import style
style.use('dark_background')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import numpy as np

class CarPage(customtkinter.CTkFrame):
	def __init__(self, master, view):
		super().__init__(master)

		self.view = view
		self.setup_frames()
		self.setup_labels()
		self.setup_plot()
		self.configure_grid()

	def configure_grid(self):
		self.grid_columnconfigure(4, weight=1)
		self.grid_rowconfigure(4, weight=1)

		self.comparison_frame.grid_columnconfigure(0, weight=1)
		self.comparison_frame.grid_rowconfigure(2, weight=1)

	def setup_frames(self):
		self.comparison_frame = customtkinter.CTkFrame(self)
		self.comparison_frame.grid(row=4, column=4, padx=self.view.padx*3, pady=self.view.pady, sticky="NSEW")

	def setup_labels(self):
		customtkinter.CTkLabel(self, text="Car", font=self.view.page_title_font).grid(row=3, column=4, padx=self.view.padx*3, pady=self.view.pady, sticky="NW")

	def setup_plot(self):

		self.comparison_figure = Figure(figsize=(5,5), dpi=100, facecolor=self.view.dark_gray)
		self.comparison_axis = self.comparison_figure.add_subplot(111)

		self.comparison_canvas = FigureCanvasTkAgg(self.comparison_figure, self.comparison_frame)
		self.comparison_canvas.draw()
		self.comparison_canvas.get_tk_widget().grid(row=2, column=0, columnspan=8, pady=2,sticky="NSEW")	

	def update_plot(self, data):
		car_speeds = data["car_speeds"]

		teams = list(car_speeds.keys())
		y_pos = np.arange(len(teams))
		speeds = list(car_speeds.values())

		self.comparison_axis.barh(y_pos, speeds, align="center", color=self.view.light_gray)
		self.comparison_axis.set_yticks(y_pos)
		self.comparison_axis.set_yticklabels(teams)
		self.comparison_axis.invert_yaxis()  # labels read top-to-bottom
		self.comparison_axis.set_xlabel("Speed")
		self.comparison_axis.set_title("Team Comparison")