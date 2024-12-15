from __future__ import annotations
from typing import TYPE_CHECKING

from race_model import timed_session_model

if TYPE_CHECKING:
	from race_model.race_model import RaceModel

class QualyModel(timed_session_model.TimedSessionModel):
	def __init__(self, model: RaceModel, session_time: int):
		super().__init__(model, session_time)

		self.generate_practice_runs()

	def generate_practice_runs(self) -> None:
		for participant in self.race_model.participants:
			participant.setup_session()
			# if participant not in [self.model.player_driver1, self.model.player_driver2]:
			participant.generate_qualy_runs()
		
	