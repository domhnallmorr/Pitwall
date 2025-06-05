from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model
	from pw_model.team.team_model import TeamModel

class TeamColorsManager:
	def __init__(self, model: Model, team_model: TeamModel):
		self.model = model
		self.primary_colour = "#FF0000"
