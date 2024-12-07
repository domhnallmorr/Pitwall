from __future__ import annotations
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pw_model.team.team_model import TeamModel

class FacilityModel:
	def __init__(self,
			  team: TeamModel,
			  factory_rating :int):
		
		self.team = team
		self.model = team.model
		self.factory_rating = factory_rating

	def end_season(self) -> None:
		self.factory_rating -= 4 # factory quality decreases year by year

		self.factory_rating = max(1, self.factory_rating) # avoid negative or zero values

		if self.team.is_player_team is False:
			should_update = self.should_update()

			if should_update is True:
				self.factory_rating += random.randint(20, 40)

				self.factory_rating = min(100, self.factory_rating) # avoid rating above 100

				self.model.inbox.generate_facility_update_email(self.team)

	def should_update(self) -> bool:
		should_update = False

		if self.factory_rating < 75: # don't update if above 75
			
			if self.factory_rating < 10:
				should_update = True
			else:
				# Generate a random number between 0 and 1
				random_value = random.random()

				upgrade_threshold = 0.2  # Example: 20% chance of upgrading

				if random_value < upgrade_threshold:
					should_update = True

		return should_update
	
	def update_facilties(self, percentage: int) -> None:
		self.factory_rating += percentage

		self.factory_rating = min(100, self.factory_rating) # ensure it's less then equal to 100

	# def to_dict(self):
	# 	return {
	# 		"factory_rating": self.factory_rating,
	# 	}
