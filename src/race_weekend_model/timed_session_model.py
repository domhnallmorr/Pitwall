'''
This is the model for timed sessions such as practice and qualifying
This differs from the grand prix model, in that cars are constantly in and out of the pits
	and also the session ends based on time rather than laps
'''
from __future__ import annotations
import copy
from typing import TYPE_CHECKING

from race_weekend_model import session_model
from race_weekend_model import commentary
from race_weekend_model.race_model_enums import SessionStatus, SessionMode, ParticipantStatus

if TYPE_CHECKING:
	from race_weekend_model.race_weekend_model import RaceWeekendModel

class TimedSessionModel(session_model.SessionModel):
	def __init__(self, race_weekend_model: RaceWeekendModel, session_time: int, session_type):
		super().__init__(race_weekend_model, session_type)

		self.session_time = session_time
		self.time_left = session_time
		self.session_type = session_type

		self.mode = "UI"

		self.setup_session()

	def setup_session(self) -> None:

		# SET STATUS COLUMN TO "PIT"
		self.standings_model.setup_initial_timed_session_standings()

		# SET PARTICPANTS STATUS
		for participant in self.race_weekend_model.participants:
			participant.status = ParticipantStatus.IN_PITS


	def advance(self, mode: str) -> None:
		assert mode in ["UI", SessionMode.SIMULATE] # simulate prevents any commentart messages from being generated
		self.mode = mode

		if self.status == SessionStatus.PRE_SESSION:
			self.status = SessionStatus.RUNNING

			if mode != SessionMode.SIMULATE:
				self.commentary_to_process.append(commentary.gen_practice_start_message())
			# self.update_participants_in_practice()
		
		else:
			if len(self.commentary_to_process) == 0:
				if self.status == SessionStatus.RUNNING:
					time_delta = 10
					self.find_particpants_leaving_pit_lane()
					self.update_participants_in_practice()

					self.time_left -= time_delta

					# UPDATE STANDINGS
					self.standings_model.update()

					# Update Gap To Leader Column
					# data = []
					# for idx, row in self.standings_df.iterrows():
					# 	if row["Position"] == 1:
					# 		if row["Fastest Lap"] is None: # no lap times set yet by any driver
					# 			data = None
					# 			break
					# 		else:
					# 			fastest_lap = row["Fastest Lap"] # fastest lap by any driver
					# 			data.append(0)
					# 	else:
					# 		if row["Fastest Lap"] is None:
					# 			data.append(None)
					# 		else:
					# 			data.append(row["Fastest Lap"] - fastest_lap)

					# self.standings_df["Gap to Leader"] = data
						

			else: # we have some commentary to process
				if self.race_weekend_model.mode == "headless":
					self.process_lastest_commentary()

		# HANDLE SESSION ENDING
		if self.time_left <= 0:
			self.status = SessionStatus.POST_SESSION
			self.end_session()

	def find_particpants_leaving_pit_lane(self) -> None:
		for p in self.race_weekend_model.participants:
			is_leaving = p.check_leaving_pit_lane(self.time_left)

			if is_leaving is True:
				if self.mode != SessionMode.SIMULATE:
					self.commentary_to_process.append(commentary.gen_leaving_pit_lane_message(p.name))

				# Update standings
				# self.standings_df.loc[self.standings_df["Driver"] == p.name, "Status"] = "out_lap"

	def update_participants_in_practice(self) -> None:
		participants_running = [p for p in self.race_weekend_model.participants if p.status == "running"]
		for p in self.race_weekend_model.participants:
			if p.status == "running":
				if p.next_update_time > self.time_left:
					self.standings_df.loc[self.standings_df["Driver"] == p.name, "Lap"] = p.practice_laps_completed
					self.standings_df.loc[self.standings_df["Driver"] == p.name, "Last Lap"] = p.laptime
					self.standings_df.loc[self.standings_df["Driver"] == p.name, "Fastest Lap"] = p.fastest_laptime
					p.update_practice(self.time_left)
				
			# UPDATE STATUS COLUMN FOR ALL
			self.standings_model.update_all_participant_status()


	def send_player_car_out(self, driver_name: str, fuel_load_laps: int, number_laps_to_run: int) -> None:
		particpant_model = self.race_weekend_model.get_particpant_model_by_name(driver_name)
		particpant_model.send_player_car_out(self.time_left, fuel_load_laps, number_laps_to_run)

	def end_session(self) -> None:
		fastest_driver = self.standings_model.leader
		fastest_laptime = self.standings_model.fastest_lap

		session_name = self.race_weekend_model.current_session_name

		self.race_weekend_model.results[session_name] = {}
		self.race_weekend_model.results[session_name]["p1"] = fastest_driver
		self.race_weekend_model.results[session_name]["fastest lap"] = fastest_laptime
		self.race_weekend_model.results[session_name]["results"] = self.standings_model.dataframe.copy(deep=True)