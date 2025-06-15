'''
Function(s) to determine a driver's interest in joining the player's team
'''
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from enum import Enum
import random

from pw_model.driver_negotiation.driver_classification import classify_driver
from pw_model.driver_negotiation.driver_negotiation_enums import DriverCategory
from pw_model.driver_negotiation.driver_salary_expectations import determine_driver_salary_expectation

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

class DriverInterest(Enum):
	ACCEPTED = "Accepted"
	COUNTER_OFFER = "Counter offer"
	NOT_INTERESTED = "Not interested"

class DriverRejectionReason(Enum):
	TEAM_RATING = "Team's current rating is too low"
	SALARY_OFFER = "Salary offer is too low"
	NONE = "No reason given"

def determine_driver_interest(model: Model, driver: str, salary_offered: int) -> tuple[DriverInterest, DriverRejectionReason]:
	# First check if driver is interested in team
	interest, reason = determine_interest_in_team(model, driver, model.player_team)

	if interest is DriverInterest.NOT_INTERESTED:
		return interest, reason # If not interested, return immediately
	
	# If interested, determine if they accept the offer
	salary_expectation = determine_driver_salary_expectation(model, driver)

	if salary_offered < salary_expectation: # if salary is too low, they are not interested in the offer
		return DriverInterest.NOT_INTERESTED, DriverRejectionReason.SALARY_OFFER # If salary is too low, return immediately

	else: # if salary is high enough, they are interested in the offer
		return DriverInterest.ACCEPTED, DriverRejectionReason.NONE
		

def determine_interest_in_team(model: Model, driver: str, team: str) -> tuple[DriverInterest | None, DriverRejectionReason | None]:
	# Get current top 5 drivers
	current_drivers_by_rating = model.season.drivers_by_rating  # [['Michael Schumacher', 98], ['Mika Hakkinen', 87], ...]
	top_5_drivers = [driver[0] for driver in current_drivers_by_rating[:5]]
	
	# Get bottom 5 teams
	teams_by_rating = model.season.teams_by_rating  # [['McLaren', 90], ['Ferrari', 84], ...]
	worst_5_teams = [team[0] for team in teams_by_rating[-5:]]
	
	# If driver is in top 5 and player's team is in bottom 5
	if driver in top_5_drivers and model.player_team in worst_5_teams:
		return DriverInterest.NOT_INTERESTED, DriverRejectionReason.TEAM_RATING
	else:
		return None, None
	



