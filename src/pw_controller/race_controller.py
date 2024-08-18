from tkinter import *
import threading

from race_model import race_model

class RaceController:
	def __init__(self, controller):
		self.controller = controller
		self.view = controller.view
		
		self.race_model = race_model.RaceModel("UI", self.controller.model, self.controller.model.season.current_track_model)


	def simulate_session(self, session):
		if session == "FP Friday":
			self.race_model.setup_practice(120*60, session)
		elif session == "FP Saturday":
			self.race_model.setup_practice(90*60, session)
		elif session == "Qualy":
			self.race_model.setup_qualfying(60*60, session)
		elif session == "Warmup":
			self.race_model.setup_practice(60*60, session)
		elif session == "Warmup":
			self.race_model.setup_practice(60*60, session)
		elif session == "Race":
			self.race_model.setup_race()
		
		simulation_thread = threading.Thread(target=self.race_model.simulate_session)
		# self.race_model.simulate_session()
		simulation_thread.start()

		simulation_thread.join() # wait for simulation to stop running

		# update lap chart
		if session == "Race":
			data = {"lap_chart_data": self.race_model.current_session.lap_chart_data}
			#  self.view.lap_chart_page.update_page(data)

		data = {
			"current_session_name": self.race_model.current_session_name,
			"standings_df": self.race_model.current_session.standings_df.copy(deep=True),
		}

		# SHOW THE RESULTS
		self.view.results_window.update_page(data)
		self.view.show_simulated_session_results()


	def continue_from_results(self):
		data = {
			"current_session_name": self.race_model.current_session_name,
			"fastest_lap_summary": f"{self.race_model.current_session.fastest_lap_driver}: {self.race_model.current_session.fastest_lap_time}",
			"leader": self.race_model.current_session.leader,
		}

		self.view.race_weekend_window.update_window(data)
		self.view.continue_from_results_page()
	
	# def return_to_main_window(self):
	# 	'''
	# 	Post race, remove race weekend, update advance button to allow progress to next week
	# 	'''
	# 	self.controller.update_standings_page()
	# 	self.controller.update_home_page()

	# 	self.view.return_to_main_window()
	# 	self.view.main_window.update_advance_btn("advance")

	def continue_from_lap_chart(self):
		self.view.continue_from_lap_chart()
	
	def show_lap_chart(self):
		self.view.show_lap_chart()