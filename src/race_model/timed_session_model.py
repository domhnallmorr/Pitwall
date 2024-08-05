from race_model import session_model
from race_model import commentary

class TimedSessionModel(session_model.SessionModel):
	def __init__(self, race_model, session_time):
		super().__init__(race_model)

		self.session_time = session_time
		self.time_left = session_time

		self.mode = "UI"

		self.setup_session()

	def setup_session(self):

		# SET STAUS COLUMN TO "PIT"
		self.standings_df["Status"] = "PIT"

		# SET PARTICPANTS STATUS
		for participant in self.race_model.participants:
			participant.status = "in_pits"


	def advance(self, mode):
		assert mode in ["UI", "simulate"] # simulate prevents any commentart messages from being generated
		self.mode = mode

		if self.status == "pre_session":
			self.status = "running"

			if mode != "simulate":
				self.commentary_to_process.append(commentary.gen_practice_start_message())
			# self.update_participants_in_practice()
		
		else:
			if len(self.commentary_to_process) == 0:
				if self.status == "running":
					time_delta = 10
					self.find_particpants_leaving_pit_lane()
					self.update_participants_in_practice()

					self.time_left -= time_delta

					# UPDATE STANDINGS
					self.standings_df.sort_values("Fastest Lap", inplace=True)
					self.refresh_standings_column() # in SessionModel

			else: # we have some commentary to process
				if self.race_model.mode == "headless":
					self.process_lastest_commentary()

		# HANDLE SESSION ENDING
		if self.time_left <= 0:
			self.status = "post_session"
			self.end_session()

	def find_particpants_leaving_pit_lane(self):
		for p in self.race_model.participants:
			is_leaving = p.check_leaving_pit_lane(self.time_left)

			if is_leaving is True:
				if self.mode != "simulate":
					self.commentary_to_process.append(commentary.gen_leaving_pit_lane_message(p.name))

				# Update standings
				self.standings_df.loc[self.standings_df["Driver"] == p.name, "Status"] = "out_lap"

	def update_participants_in_practice(self):
		participants_running = [p for p in self.race_model.participants if p.status == "running"]
		for p in self.race_model.participants:
			if p.status == "running":
				if p.next_update_time > self.time_left:
					self.standings_df.loc[self.standings_df["Driver"] == p.name, "Lap"] = p.practice_laps_completed
					self.standings_df.loc[self.standings_df["Driver"] == p.name, "Last Lap"] = p.laptime
					self.standings_df.loc[self.standings_df["Driver"] == p.name, "Fastest Lap"] = p.fastest_laptime
					p.update_practice(self.time_left)
				
			# UPDATE STATUS COLUMN FOR ALL
			self.standings_df.loc[self.standings_df["Driver"] == p.name, "Status"] = p.status


	def send_player_car_out(self, driver_name, fuel_load_laps, number_laps_to_run):
		particpant_model = self.race_model.get_particpant_model_by_name(driver_name)
		particpant_model.send_player_car_out(self.time_left, fuel_load_laps, number_laps_to_run)

	def end_session(self):
		fastest_driver = self.standings_df.iloc[0]["Driver"]
		fastest_laptime = self.standings_df.iloc[0]["Fastest Lap"]

		session_name = self.race_model.current_session_name

		self.race_model.results[session_name] = {}
		self.race_model.results[session_name]["p1"] = fastest_driver
		self.race_model.results[session_name]["fastest lap"] = fastest_laptime
		self.race_model.results[session_name]["results"] = self.standings_df.copy(deep=True)