import random
from typing import Tuple

from race_weekend_model import session_model, commentary
from race_weekend_model.race_model_enums import SessionNames, SessionStatus, SessionMode, ParticipantStatus

from pw_model.pw_base_model import Model
from race_weekend_model.particpant_model import ParticpantModel
from race_weekend_model.session_model import SessionModel
from race_weekend_model import race_start_calculations
from race_weekend_model.race_model_enums import SessionNames

class GrandPrixModel(session_model.SessionModel):
	def __init__(self, model: Model):
		super().__init__(model, SessionNames.RACE)

		self.current_lap = 1
		self.retirements: list[str] = []

		self.standings_model.setup_grid_order()
		self.setup_participant_start_fuel_and_tyres()
	
	def setup_participant_start_fuel_and_tyres(self) -> None:
		for p in self.race_weekend_model.participants:
			p.setup_start_fuel_and_tyres()

	def advance(self, mode: str) -> None:
		self.mode = mode
		if self.status == SessionStatus.PRE_SESSION:
			if self.mode != SessionMode.SIMULATE:
				self.commentary_to_process.append(commentary.gen_race_start_message())
			self.calculate_start()
			self.status = SessionStatus.RUNNING

		else: # process lap
			if len(self.commentary_to_process) == 0:
				if self.status == SessionStatus.RUNNING:
					self.calculate_lap()
					self.standings_model.update()
					self.current_lap += 1
			
					if self.current_lap > self.race_weekend_model.track_model.number_of_laps or self.current_lap == 999:
						if self.mode != SessionMode.SIMULATE:
							self.commentary_to_process.append(commentary.gen_race_over_message(self.leader))
						self.status = SessionStatus.POST_SESSION
						self.post_race_actions()
						
						# self.log_event("Race Over")

	def calculate_start(self) -> None:
		# Calculate Turn 1
		order_after_turn1 = race_start_calculations.calculate_run_to_turn1(self.race_weekend_model)

		# redefine particpants based on turn1 order
		self.participants = [o[1] for o in order_after_turn1]

		'''
		just spread field out after turn1
		'''
		for idx, p in enumerate(self.participants):
			p.laptime_manager.calculate_first_lap_laptime(idx)
			p.complete_lap()

		self.standings_model.update()

		# set fastest lap to leader
		# self.fastest_laptime_driver = self.participants[0].name
		# self.fastest_laptime = self.participants[0].laptime
		# self.fastest_laptime_lap = 1

		self.current_lap += 1

	def calculate_lap(self) -> None:
		'''
		Process
			
			determine driver strategy (push/conserve)
			determine which drivers are fighting for position (within 1s of car in front)
			calculate laptime for each driver, account for dirty air
			determine any mistakes
			determine if overtake if attempted and successfull
			adjust laptimes accordingly
			update standings
			update tyre wear and fuel load
		'''

		for idx, row in self.standings_model.dataframe.iterrows():
			driver = row["Driver"]
			participant = self.race_weekend_model.get_particpant_model_by_name(driver)
			
			# ONLY PROCESS IF STILL RUNNING
			if participant.status is not ParticipantStatus.RETIRED:
				# print("not retired")

				gap_ahead = row["Gap Ahead"]
				participant.calculate_laptime(gap_ahead)

				# IF RETIRED THIS LAP
				if participant.status is ParticipantStatus.RETIRED:
					self.handle_retirement(participant)
					laptime_ahead = None

				else:
					if participant.status is ParticipantStatus.PITTING_IN:
						if self.mode != SessionMode.SIMULATE:
							self.commentary_to_process.append(commentary.gen_entering_pit_lane_message(participant.name))
					
					# print(laptime_ahead)
					if idx > 0 and laptime_ahead is not None: # laptime_ahead being None indicates car in front has retired
						delta = participant.laptime_manager.laptime - laptime_ahead
							# self.log_event(f"{participant.name} Pitting In")
						
						if gap_ahead + delta <= 500 and participant_ahead.status not in [ParticipantStatus.PITTING_IN, ParticipantStatus.RETIRED]: # if car ahead is about to pit, don't handle for overtaking
							# self.log_event(f"{driver} Attacking {participant_ahead.name}")
							if self.mode != SessionMode.SIMULATE:
								self.commentary_to_process.append(commentary.gen_attacking_message(driver, participant_ahead.name))

							if random.randint(0, 100) < 25: # overtake successfull
								# self.log_event(f"{participant.name} passes {participant_ahead.name}")
								if self.mode != SessionMode.SIMULATE:
									self.commentary_to_process.append(commentary.gen_overtake_message(participant.name, participant_ahead.name))

								# add some random time to overtaking car, held up when passing
								participant.laptime_manager.laptime += random.randint(700, 1_500)

								# recalculate delta due to laptime updated above
								delta = participant.laptime_manager.laptime - laptime_ahead 
								
								#update participant that has been passed so laptime brings them behind overtaking car
								orig_gap = gap_ahead + delta
								#if orig_gap >= 0:
								revised_laptime = participant_ahead.laptime_manager.laptime + orig_gap + random.randint(700, 1_500)
								participant_ahead.laptime_manager.recalculate_laptime_when_passed(revised_laptime)
							else: # overtake unsuccessfull
								participant.laptime_manager.laptime = laptime_ahead + random.randint(100, 1_400)
								
					laptime_ahead = participant.laptime_manager.laptime
					participant_ahead = participant
					participant.complete_lap()

	def handle_retirement(self, participant: ParticpantModel) -> None:
		if self.mode != SessionMode.SIMULATE:
			self.commentary_to_process.append(commentary.gen_retirement_message(participant.name))
			self.retirements.append(participant.name)

	def post_race_actions(self) -> None:
		self.winner = self.standings_model.leader
		
		# update driver stats
		for idx, row in self.standings_model.dataframe.iterrows():
			driver = row["Driver"]
			participant = self.race_weekend_model.get_particpant_model_by_name(driver)

			participant.driver.season_stats.starts_this_season += 1

			if idx == 0: # update wins
				participant.driver.season_stats.wins_this_season += 1
				participant.driver.team_model.season_stats.wins_this_season += 1
			if idx in [0, 1, 2]: # podiums
				participant.driver.season_stats.podiums_this_season += 1
				participant.driver.team_model.season_stats.podiums_this_season += 1
			if row["Status"] == ParticipantStatus.RETIRED:
				participant.driver.season_stats.dnfs_this_season += 1
				participant.driver.team_model.season_stats.dnfs_this_season += 1

		self.race_weekend_model.model.season.standings_manager.update_standings(self.standings_model.dataframe.copy(deep=True))
		
		self.generate_lap_chart_data()
		self.generate_pit_stop_summary()
		self.generate_lap_times_summary()

	def generate_lap_chart_data(self) -> None:
		self.lap_chart_data = {}

		for idx, row in self.standings_model.dataframe.iterrows():
			driver = row["Driver"]
			participant = self.race_weekend_model.get_particpant_model_by_name(driver)

			self.lap_chart_data[driver] = [[i + 1 for i in range(len(participant.positions_by_lap))], participant.positions_by_lap]
			
			# add the starting position as Lap 0
			self.lap_chart_data[driver][0].insert(0, 0)
			self.lap_chart_data[driver][1].insert(0, row["Grid"])
		
	def generate_pit_stop_summary(self) -> None:
		participants = [self.race_weekend_model.get_particpant_model_by_name(driver) for driver in self.standings_model.dataframe["Driver"].values]
		self.pit_stop_summary = {
			p.name: p.pitstop_laps for p in participants
		}

	def generate_lap_times_summary(self) -> None:
		self.lap_times_summary = {
			p.name: p.laptime_manager.laptimes for p in self.race_weekend_model.participants
		}