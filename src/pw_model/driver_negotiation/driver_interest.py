'''
Function(s) to determine a driver's interest in joining the player's team
'''
from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum
import random

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

class DriverInterest(Enum):
	VERY_INTERESTED = "Very interested"
	NOT_INTERESTED = "Not interested"

class DriverRejectionReason(Enum):
	TEAM_RATING = "Team's current rating is too low"
	NONE = "No reason given"

def determine_driver_interest(model: Model, driver: str) -> tuple[DriverInterest, DriverRejectionReason]:
	# Get current top 5 drivers
	current_drivers_by_rating = model.season.drivers_by_rating  # [['Michael Schumacher', 98], ['Mika Hakkinen', 87], ...]
	top_5_drivers = [driver[0] for driver in current_drivers_by_rating[:5]]
	
	# Get bottom 5 teams
	teams_by_rating = model.season.teams_by_rating  # [['McLaren', 90], ['Ferrari', 84], ...]
	worst_5_teams = [team[0] for team in teams_by_rating[-5:]]
	
	# If driver is in top 5 and player's team is in bottom 5
	if driver in top_5_drivers and model.player_team in worst_5_teams:
		return DriverInterest.NOT_INTERESTED, DriverRejectionReason.TEAM_RATING
		
	return random.choice(list(DriverInterest)), DriverRejectionReason.NONE
