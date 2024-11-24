from pw_model.senior_staff import senior_staff
from pw_model.pw_model_enums import StaffRoles
import random

class CommercialManager(senior_staff.SeniorStaff):
	def __init__(self,
			  model,
			  name : str,
			  age : int,
			  skill : int,
			  salary : float,
			  contract_length : float):
		
		super().__init__(model, name, age, skill, salary, contract_length)
		self.role = StaffRoles.COMMERCIAL_MANAGER

	@property
	def team_model(self):
		current_team = None

		for team in self.model.teams:
			if self.name == team.commercial_manager:
				current_team = team
				break

		return current_team
	
	def determine_yearly_sponsorship(self):
		'''
		First determine min and max possible sponsorship
		'''
		min_sponsorship, max_sponsorship = self.determine_possible_sponsorship()


		'''
		Sponsorship for upcoming season is linearly interpolated based on skill, with a little variance
		'''

		# Linearly interpolate the sponsorship based on the skill
		sponsorship = min_sponsorship + (self.skill / 100) * (max_sponsorship - min_sponsorship)

		# TODO add number of staff and finishing position to this calc

        # Add random variance: ±5% around the calculated sponsorship
		variance = random.uniform(-0.15, 0.15)  # Variance between -15% and +15%
		sponsorship_with_variance = sponsorship * (1 + variance)

 		# Ensure the sponsorship stays within the defined range
		sponsorship_with_variance = int(max(min_sponsorship, min(sponsorship_with_variance, max_sponsorship)))

		return sponsorship_with_variance
	
	def determine_possible_sponsorship(self):
		min_sponsorship = 1_000_000
		max_sponsorship = 50_000_000

		'''
		Account for size of team
		'''

		if self.team_model.number_of_staff < 150:
			max_sponsorship = 40_000_000
		if self.team_model.number_of_staff < 120:
			max_sponsorship = 30_000_000
		if self.team_model.number_of_staff < 100:
			max_sponsorship = 20_000_000

		return min_sponsorship, max_sponsorship