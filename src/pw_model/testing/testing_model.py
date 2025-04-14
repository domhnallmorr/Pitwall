from __future__ import annotations
from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

class TestingModel:
	def __init__(self, model: Model):
		self.model = model
		self.setup_new_season()

	def setup_new_season(self) -> None:
		self.testing_progress = 0

	def run_test(self, distance_km: int) -> None:
		self.determine_test_progress(distance_km)
		self.post_test_actions(distance_km)

	def skip_test(self) -> None:
		self.post_test_actions(0) # distance_km is 0 as the test is skipped

	def post_test_actions(self, distance_km: int) -> None:
		# Update finances
		self.model.player_team_model.finance_model.apply_testing_costs(distance_km)

		# Update calendar
		self.model.season.calendar.post_test_actions()

	def determine_test_progress(self, distance_km: int) -> None:
		inbox = self.model.inbox

		progress_delta = int((100 / 2_000) * distance_km)
		self.testing_progress += progress_delta

		if self.testing_progress >= 100:
			car_model = self.model.player_team_model.car_model
			car_model.implement_testing_progess(1)
			self.testing_progress = 0
			inbox.generate_testing_progress_email()
		else:
			inbox.generate_testing_completed_email(distance_km)

class TestingRandomiser:
	pass