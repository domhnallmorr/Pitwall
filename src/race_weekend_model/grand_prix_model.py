import random
from typing import Tuple

from race_weekend_model import session_model, commentary
from race_weekend_model.race_model_enums import SessionNames, SessionStatus, SessionMode

from pw_model.pw_base_model import Model
from race_weekend_model.particpant_model import ParticpantModel
from race_weekend_model.session_model import SessionModel

class GrandPrixModel(session_model.SessionModel):
	def __init__(self, model: Model):
		super().__init__(model)

		self.current_lap = 1
		self.retirements: list[str] = []

		if SessionNames.QUALIFYING.value in self.race_model.results.keys():
			self.setup_grid_order()

		self.setup_participant_start_fuel_and_tyres()

	@property
	def leader(self) -> str:
		return str(self.standings_df.iloc[0]["Driver"])
	
	def setup_grid_order(self) -> None:
		self.standings_df = self.race_model.starting_grid.apply_grid_order_to_standings(self.standings_df)

	def setup_participant_start_fuel_and_tyres(self) -> None:
		for p in self.race_model.participants:
			p.setup_start_fuel_and_tyres()

	# def run_race(self) -> None:
	# 	while self.status != SessionStatus.POST_SESSION:
	# 		self.advance()

	# 		self.process_headless_commentary()
	# 	self.process_headless_commentary()

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
					self.update_fastest_lap()
					self.update_standings()
					self.current_lap += 1
			
					if self.current_lap > self.race_model.track_model.number_of_laps or self.current_lap == 999:
						if self.mode != SessionMode.SIMULATE:
							self.commentary_to_process.append(commentary.gen_race_over_message(self.leader))
						self.status = SessionStatus.POST_SESSION
						self.post_race_actions()
						
						# self.log_event("Race Over")

	def calculate_start(self) -> None:
		# Calculate Turn 1
		order_after_turn1 = self.calculate_run_to_turn1()

		# redefine particpants based on turn1 order
		self.participants = [o[1] for o in order_after_turn1]

		'''
		just spread field out after turn1
		'''
		for idx, p in enumerate(self.participants):
			p.laptime = self.race_model.track_model.base_laptime + 6_000 + (idx * 1_000) + random.randint(100, 1500)
			p.complete_lap()

		self.update_standings()

		# set fastest lap to leader
		self.fastest_laptime_driver = self.participants[0].name
		self.fastest_laptime = self.participants[0].laptime
		self.fastest_laptime_lap = 1

		self.current_lap += 1

	def calculate_run_to_turn1(self) -> list[Tuple[float, ParticpantModel]]:
		dist_to_turn1 = self.race_model.track_model.dist_to_turn1
		average_speed = 47.0 #m/s

		order_after_turn1: list[Tuple[float, ParticpantModel]] = []
		for idx, p in enumerate([self.race_model.get_particpant_model_by_name(n) for n in self.standings_df["Driver"].values.tolist()]):
			random_factor = random.randint(-2000, 2000)/1000
			time_to_turn1: float = round(dist_to_turn1 / (average_speed + random_factor), 3)
			particpant_model: ParticpantModel = p
			order_after_turn1.append((time_to_turn1, particpant_model))
			
			dist_to_turn1 += 5 # add 5 meters per grid slot

		order_after_turn1 = sorted(order_after_turn1, key=lambda x: x[0], reverse=False)
		'''
		example of order_after_turn1
		[time_to_turn1, particpant model]
		[[12.761, <RaceEngineParticpantModel Mark Webber>], [13.124, <RaceEngineParticpantModel Sebastian Vettel>], [13.68, <RaceEngineParticpantModel Fernando Alonso>],]
		'''

		if self.mode != SessionMode.SIMULATE:
			self.commentary_to_process.append(commentary.gen_lead_after_turn1_message(order_after_turn1[0][1].name))
		
		return order_after_turn1

	def update_standings(self) -> None:
		for driver in self.standings_df["Driver"]:
			particpant_model = self.race_model.get_particpant_model_by_name(driver)
			particpant_model.update_fastest_lap()
			self.standings_df.loc[self.standings_df["Driver"] == driver, "Total Time"] = particpant_model.total_time
			self.standings_df.loc[self.standings_df["Driver"] == driver, "Last Lap"] = particpant_model.laptime
			self.standings_df.loc[self.standings_df["Driver"] == driver, "Lap"] = particpant_model.current_lap
			self.standings_df.loc[self.standings_df["Driver"] == driver, "Status"] = particpant_model.status
	
		self.standings_df = self.standings_df.sort_values(by=["Lap", "Total Time"], ascending=[False, True])
		
		# RESET INDEX AND POSITION COLUMNS
		self.standings_df.reset_index(drop=True, inplace=True)
		self.standings_df["Position"] = self.standings_df.index + 1
		
		# CALC GAP TO CAR IN FRONT
		self.standings_df["Gap Ahead"] = self.standings_df["Total Time"].diff()

		leader_time = self.standings_df.loc[self.standings_df["Position"] == 1, "Total Time"].values[0]
		self.standings_df["Gap to Leader"] = (self.standings_df["Total Time"] - leader_time)

		# UPDATE GAPS TO LEADER IN PARTICIPANT MODEL AND CHECK IF LAPPED
		for idx, row in self.standings_df.iterrows():
			particpant_model = self.race_model.get_particpant_model_by_name(row["Driver"])	
			particpant_model.positions_by_lap.append(idx + 1)
			particpant_model.gaps_to_leader.append(row["Gap to Leader"])
			
			if row["Gap to Leader"] > self.race_model.track_model.base_laptime:
				self.standings_df.at[idx, "Lapped Status"] = f"lapped {int(row['Gap to Leader']/self.race_model.track_model.base_laptime)}" # add number of laps down to status

			# UPDATE NUMBER OF PITSTOPS
			self.standings_df.at[idx, "Pit"] = particpant_model.number_of_pitstops

			# UPDATE FASTEST LAP
			self.standings_df.at[idx, "Fastest Lap"] = particpant_model.fastest_laptime

		# self.log_event("\nCurrent Standings:\n" + self.standings_df.to_string(index=False))

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

		for idx, row in self.standings_df.iterrows():
			driver = row["Driver"]
			participant = self.race_model.get_particpant_model_by_name(driver)
			
			# ONLY PROCESS IF STILL RUNNING
			if participant.status != "retired":
				# print("not retired")

				gap_ahead = row["Gap Ahead"]
				participant.calculate_laptime(gap_ahead)

				# IF RETIRED THIS LAP
				if participant.status == "retired":
					if self.mode != SessionMode.SIMULATE:
						self.commentary_to_process.append(commentary.gen_retirement_message(participant.name))
					self.retirements.append(participant.name)
					# self.log_event(f"{participant.name} retires")
					laptime_ahead = None

				else:
					if participant.status == "pitting in":
						if self.mode != SessionMode.SIMULATE:
							self.commentary_to_process.append(commentary.gen_entering_pit_lane_message(participant.name))
					
					# print(laptime_ahead)
					if idx > 0 and laptime_ahead is not None: # laptime_ahead being None indicates car in front has retired
						delta = participant.laptime - laptime_ahead
							# self.log_event(f"{participant.name} Pitting In")
						
						if gap_ahead + delta <= 500 and participant_ahead.status not in ["pitting in", "retired"]: # if car ahead is about to pit, don't handle for overtaking
							# self.log_event(f"{driver} Attacking {participant_ahead.name}")
							if self.mode != SessionMode.SIMULATE:
								self.commentary_to_process.append(commentary.gen_attacking_message(driver, participant_ahead.name))

							if random.randint(0, 100) < 25: # overtake successfull
								# self.log_event(f"{participant.name} passes {participant_ahead.name}")
								if self.mode != SessionMode.SIMULATE:
									self.commentary_to_process.append(commentary.gen_overtake_message(participant.name, participant_ahead.name))

								# add some random time to overtaking car, held up when passing
								participant.laptime += random.randint(700, 1_500)

								# recalculate delta due to laptime updated above
								delta = participant.laptime - laptime_ahead 
								
								#update participant that has been passed so laptime brings them behind overtaking car
								orig_gap = gap_ahead + delta
								#if orig_gap >= 0:
								revised_laptime = participant_ahead.laptime + orig_gap + random.randint(700, 1_500)
								participant_ahead.recalculate_laptime_when_passed(revised_laptime)
							else: # overtake unsuccessfull
								participant.laptime = laptime_ahead + random.randint(100, 1_400)
								
					laptime_ahead = participant.laptime
					participant_ahead = participant
					participant.complete_lap()

	def post_race_actions(self) -> None:
		# update driver stats
		for idx, row in self.standings_df.iterrows():
			driver = row["Driver"]
			participant = self.race_model.get_particpant_model_by_name(driver)

			participant.driver.season_stats.starts_this_season += 1

			if idx == 0: # update wins
				participant.driver.season_stats.wins_this_season += 1
				participant.driver.team_model.season_stats.wins_this_season += 1
			if idx in [0, 1, 2]: # podiums
				participant.driver.season_stats.podiums_this_season += 1
				participant.driver.team_model.season_stats.podiums_this_season += 1
			if row["Status"] == "retired":
				participant.driver.season_stats.dnfs_this_season += 1
				participant.driver.team_model.season_stats.dnfs_this_season += 1

		self.race_model.model.season.standings_manager.update_standings(self.standings_df)
		
		self.generate_lap_chart_data()
		self.generate_pit_stop_summary()
		self.generate_lap_times_summary()

	def generate_lap_chart_data(self) -> None:
		self.lap_chart_data = {}

		for idx, row in self.standings_df.iterrows():
			driver = row["Driver"]
			participant = self.race_model.get_particpant_model_by_name(driver)

			self.lap_chart_data[driver] = [[i + 1 for i in range(len(participant.positions_by_lap))], participant.positions_by_lap]
			
			# add the starting position as Lap 0
			self.lap_chart_data[driver][0].insert(0, 0)
			self.lap_chart_data[driver][1].insert(0, row["Grid"])
		
	def generate_pit_stop_summary(self) -> None:
		self.pit_stop_summary = {
			p.name: p.pitstop_laps for p in self.race_model.participants
		}

	def generate_lap_times_summary(self) -> None:
		self.lap_times_summary = {
			p.name: p.laptimes for p in self.race_model.participants
		}