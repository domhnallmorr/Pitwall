from __future__ import annotations
from typing import TYPE_CHECKING
import random

from enum import Enum
from pw_model.finance.car_development_costs import CarDevelopmentCostsEnums

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model
	from pw_model.team.team_model import TeamModel

class CarDevelopmentEnums(Enum):
	NONE = "none"
	MINOR = "minor"
	MEDIUM = "medium"
	MAJOR = "major"

class CarDevelopmentStatusEnums(Enum):
	NOT_STARTED = "not started"
	IN_PROGRESS = "in progress"
	COMPLETED = "completed"



class CarDevelopmentModel:
	def __init__(self, model: Model, team_model: TeamModel):
		self.model = model
		self.team_model = team_model
		self.car_model = team_model.car_model
		self.current_status = CarDevelopmentStatusEnums.NOT_STARTED
		self.time_left = 0
		self.current_development_type = CarDevelopmentEnums.NONE
		self.planned_updates = []
	@property
	def is_player_team(self) -> bool:
		return self.team_model.is_player_team

	def setup_new_season(self) -> None:
		self.planned_updates = []

		if self.is_player_team is False:
			self.gen_ai_updates()

	def start_development(self, development_type: CarDevelopmentEnums) -> None:
		self.current_development_type = development_type
		self.current_status = CarDevelopmentStatusEnums.IN_PROGRESS

		if development_type == CarDevelopmentEnums.MINOR:
			self.time_left = 5
			cost = CarDevelopmentCostsEnums.MINOR.value
		elif development_type == CarDevelopmentEnums.MEDIUM:
			self.time_left = 7
			cost = CarDevelopmentCostsEnums.MEDIUM.value
		elif development_type == CarDevelopmentEnums.MAJOR:
			self.time_left = 10
			cost = CarDevelopmentCostsEnums.MAJOR.value
			
		self.team_model.finance_model.car_development_costs_model.start_development(cost, self.time_left)
		self.model.inbox.generate_car_development_started_email(development_type.value, self.time_left, cost)

	def advance(self) -> None:
		if self.is_player_team is False:
			self.implement_ai_update()
			
		if self.current_status == CarDevelopmentStatusEnums.IN_PROGRESS and self.is_player_team is True: # only player team can have in progress development at the moment, so this is fine for now. This will need to be changed in the future.
			self.time_left -= 1

			if self.time_left == 0:
				self.complete_development()

	def complete_development(self) -> None:
		speed_increase = self.calculate_speed_increase()
		self.car_model.implement_car_development(speed_increase)

		if self.is_player_team is True:
			self.current_status = CarDevelopmentStatusEnums.COMPLETED
			self.model.inbox.generate_car_development_completed_email(self.current_development_type.value, speed_increase)
		else:
			self.model.inbox.generate_ai_development_completed_email(self.current_development_type.value, self.team_model.name)	

	def calculate_speed_increase(self) -> int:
		if self.current_development_type == CarDevelopmentEnums.MINOR:
			return 1
		elif self.current_development_type == CarDevelopmentEnums.MEDIUM:
			return 3
		elif self.current_development_type == CarDevelopmentEnums.MAJOR:
			return 5

	def gen_ai_updates(self) -> None:  # FOR AI CONTROLLED TEAMS
		number_of_updates = random.randint(2, 6)
		race_weeks = self.team_model.model.season.calendar.race_weeks[1:] # skip first race week
		
		# Select random race weeks for updates, ensuring they're spread out
		min_gap = max(2, len(race_weeks) // (number_of_updates * 2))  # Ensure minimum gap between updates
		available_weeks = race_weeks.copy()
		selected_weeks = []
		
		while len(selected_weeks) < number_of_updates and available_weeks:
			week = random.choice(available_weeks)
			
			# Check if this week maintains minimum gap from other selected weeks
			if not selected_weeks or min(abs(week - w) for w in selected_weeks) >= min_gap:
				selected_weeks.append(week)
				# Remove nearby race weeks from available weeks to maintain spacing
				available_weeks = [w for w in available_weeks 
								 if abs(w - week) >= min_gap]
		
		# Sort weeks chronologically
		selected_weeks.sort()
		
		# For each selected week, randomly choose update type
		for week in selected_weeks:
			weights = [0.5, 0.35, 0.15]  # Probabilities for MINOR, MEDIUM, MAJOR
			update_type = random.choices(
				[CarDevelopmentEnums.MINOR, 
				 CarDevelopmentEnums.MEDIUM, 
				 CarDevelopmentEnums.MAJOR], 
				weights=weights
			)[0]
			
			# Store the planned update
			self.planned_updates.append((week, update_type))

	def implement_ai_update(self) -> None:  # FOR AI CONTROLLED TEAMS		
		if self.model.game_data.current_week() in [u[0] for u in self.planned_updates]:
			for update in self.planned_updates:
				if update[0] == self.model.game_data.current_week():
					self.current_development_type = update[1]
					self.complete_development()
					break
			