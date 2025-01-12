from __future__ import annotations
from typing import TYPE_CHECKING

from race_weekend_model import timed_session_model
from race_weekend_model.race_model_enums import SessionNames

if TYPE_CHECKING:
	from race_weekend_model.race_weekend_model import RaceWeekendModel

# Commented out class below was used until V0.15.0
# it is used to simualte the full 60min session
# with cars entering and leaving the pits throughout the session
# Have replaced it with a much simplified class for now
# Will add this more "advanced" model back in at some point

# class QualyModel(timed_session_model.TimedSessionModel):
# 	def __init__(self, model: RaceWeekendModel, session_time: int):
# 		super().__init__(model, session_time, SessionNames.QUALIFYING)

# 		self.generate_practice_runs()

# 	def generate_practice_runs(self) -> None:
# 		for participant in self.race_weekend_model.participants:
# 			# participant.setup_session()
# 			# if participant not in [self.model.player_driver1, self.model.player_driver2]:
# 			participant.generate_qualy_runs()
		
class QualyModel(timed_session_model.TimedSessionModel):
	def __init__(self, race_weekend_model: RaceWeekendModel, session_time: int):
		self.race_weekend_model = race_weekend_model

		super().__init__(race_weekend_model, session_time, SessionNames.QUALIFYING)

	def generate_results(self) -> None:
		for participant in self.race_weekend_model.participants:
			participant.laptime_manager.calculate_qualfying_laptime()
			
		self.standings_model.update()
		self.end_session()
