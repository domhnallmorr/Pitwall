import random
from typing import Tuple

from race_weekend_model import session_model, commentary
from race_weekend_model.race_model_enums import SessionNames, SessionStatus, SessionMode, ParticipantStatus

from pw_model.pw_base_model import Model
from race_weekend_model.commentary.commentary_model import CommentaryModel
from race_weekend_model.particpant_model import ParticpantModel
from race_weekend_model.session_model import SessionModel
from race_weekend_model import race_start_calculations
from race_weekend_model.race_model_enums import SessionNames, OvertakingStatus

class GrandPrixModel(session_model.SessionModel):
	def __init__(self, model: Model):
		super().__init__(model, SessionNames.RACE)

		self.current_lap = 1
		self.retirements: list[str] = []
		self.number_of_overtakes = 0
		
		# Add commentary model
		self.commentary_model = CommentaryModel()

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
		self.commentary_model.gen_leading_after_turn1_message(order_after_turn1[0][1].name)

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

			participant.overtaking_status = OvertakingStatus.NONE # Reset overtaking statuses at start of lap
			
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
						
						# Log potential overtaking situation
						print(f"Lap {self.current_lap} - {driver} vs {participant_ahead.name}:")
						print(f"  Delta: {delta}")
						print(f"  Gap ahead: {gap_ahead}")
						print(f"  Overtaking delta required: {self.race_weekend_model.track_model.overtaking_delta}")
						
						self.set_overtake_status(participant, participant_ahead, delta, gap_ahead)

						# if delta < 0 and abs(delta) >= self.race_weekend_model.track_model.overtaking_delta:
						# 	print(f"  Delta check passed")
							
						# 	if gap_ahead + delta <= 500:
						# 		print(f"  Gap check passed")
								
						# *********
						if participant.overtaking_status == OvertakingStatus.ATTACKING:
							print(f"  Status check passed")
							overtake_chance = random.randint(0, 100)
							print(f"  Overtake roll: {overtake_chance}/25")
							
							if overtake_chance < 25:  # overtake successful
								print(f"  OVERTAKE SUCCESSFUL: {participant.name} passes {participant_ahead.name}")
								self.number_of_overtakes += 1
								
								# Add time loss for executing the overtake
								overtake_penalty = random.randint(700, 1_500)
								participant.laptime_manager.laptime += overtake_penalty
								print(f"  Added {overtake_penalty}ms penalty for executing pass")

								# Recalculate delta with new penalty
								delta = participant.laptime_manager.laptime - laptime_ahead
								
								# Update passed car's laptime to ensure they end up behind
								orig_gap = gap_ahead + delta
								revised_laptime = participant_ahead.laptime_manager.laptime + orig_gap + random.randint(700, 1_500)
								participant_ahead.laptime_manager.recalculate_laptime_when_passed(revised_laptime)
								print(f"  Adjusted laptimes to reflect battle")
								
								if self.mode != SessionMode.SIMULATE:
									self.commentary_to_process.append(commentary.gen_overtake_message(participant.name, participant_ahead.name))
								
								self.commentary_model.gen_overtake_message(self.current_lap, participant.name, participant_ahead.name)
							else:
								print(f"  Overtake attempt failed")
								# Adjust laptime to maintain position behind after failed overtake
								revised_laptime = laptime_ahead + 200  # maintain 50ms gap
								participant.laptime_manager.recalculate_laptime_when_passed(revised_laptime)
								print(f"  Adjusted laptime after failed overtake: {participant.name} stays behind")

						elif participant.overtaking_status == OvertakingStatus.NONE:
							# Check if driver would end up ahead without proper overtake
							if gap_ahead + delta <= 0:
								# Adjust laptime to maintain small gap behind
								revised_laptime = laptime_ahead + 200  # maintain 50ms gap
								participant.laptime_manager.recalculate_laptime_when_passed(revised_laptime)
								print(f"  Prevented illegal position change: adjusted {participant.name}'s laptime")
					
					laptime_ahead = participant.laptime_manager.laptime
					participant_ahead = participant
					participant.complete_lap()

	def set_overtake_status(self, participant: ParticpantModel, participant_ahead: ParticpantModel, delta: int, gap_ahead: int) -> bool:
		# If ahead car is pitting or retired, don't need to process overtake
		if participant_ahead.status in [ParticipantStatus.PITTING_IN, ParticipantStatus.RETIRED]:
			participant.overtaking_status = OvertakingStatus.HOLD_BACK

		# car in front is attempting an overtake, hold back
		elif participant_ahead.overtaking_status == OvertakingStatus.ATTACKING:
			participant.overtaking_status = OvertakingStatus.HOLD_BACK

		# if not faster than car ahead, can't overtake		
		elif delta >= 0:
			participant.overtaking_status = OvertakingStatus.NONE

		# not close enough to overtake
		elif gap_ahead + delta >= 500:
			participant.overtaking_status = OvertakingStatus.NONE

		# if close enough and fast enough, attempt overtake
		elif abs(delta) >= self.race_weekend_model.track_model.overtaking_delta:
			participant.overtaking_status = OvertakingStatus.ATTACKING

			
	def handle_retirement(self, participant: ParticpantModel) -> None:
		if self.mode != SessionMode.SIMULATE:
			self.commentary_to_process.append(commentary.gen_retirement_message(participant.name))
			self.retirements.append(participant.name)

	def post_race_actions(self) -> None:
		self.winner = self.standings_model.leader
		
		# for determining crash damage in finance model
		self.player_driver1_crashed = self.race_weekend_model.player_driver1_participant.crashed 
		self.player_driver2_crashed = self.race_weekend_model.player_driver2_participant.crashed 

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

