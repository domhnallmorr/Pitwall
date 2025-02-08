from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pw_model.team.team_model import TeamModel
	from pw_model.pw_base_model import Model

class SponsorModel:
	def __init__(self, model: Model, team_model: TeamModel,
			 other_sponsorship: int, title_sponsor: str, title_sponsor_value: int):
		
		self.model = model
		self.game_data = model.game_data
		self.team_model = team_model
		self.other_sponsorship = other_sponsorship
		self.title_sponsor = title_sponsor
		self.title_sponsor_value = title_sponsor_value

		self.setup_new_season(new_season=False)

	@property
	def total_sponsor_income(self) -> int:
		return self.title_sponsor_value + self.other_sponsorship
	
	@property
	def title_sponsor_payment_per_race(self) -> int:
		return int(self.title_sponsor_value / self.game_data.get_number_of_races())
	
	@property
	def other_sponsor_payment_per_race(self) -> int:
		return int(self.other_sponsorship / self.game_data.get_number_of_races())
	
	def setup_new_season(self, new_season: bool=True) -> None:
		'''
		new_season can be set to False to avoid recomputing some values
		This is mainly done when the game starts, so values from the roster are used 
		instead of being recalculated
		'''
		self.other_sponser_payments :list[int] = [] # list of payments paid per race
		self.title_sponser_payments :list[int] = [] # list of payments paid per race

		if new_season is True:
			# determine other sponsorship for season
			self.other_sponsorship = self.team_model.commercial_manager_model.determine_yearly_sponsorship()
			self.model.inbox.new_sponsor_income_email(self.other_sponsorship)

	def process_sponsor_post_race_payments(self) -> None:
		self.other_sponser_payments.append(self.other_sponsor_payment_per_race)
		self.title_sponser_payments.append(self.title_sponsor_payment_per_race)
	
