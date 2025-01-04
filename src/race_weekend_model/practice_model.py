from race_model import timed_session_model

class PracticeModel(timed_session_model.TimedSessionModel):
	def __init__(self, race_model, session_time):
		super().__init__(race_model, session_time)

		self.generate_practice_runs()

	def generate_practice_runs(self):
		for participant in self.race_model.participants:
			participant.setup_session()
			# if participant not in [self.race_model.player_driver1, self.race_model.player_driver2]:
			participant.generate_practice_runs(self.time_left, "FP")
		
	