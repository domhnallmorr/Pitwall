from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

class PlayerContract:
	def __init__(self):
		self.salary = 0
		self.contract_length = 999



class PlayerModel:
	def __init__(self, model: Model):
		self.model = model
		self.name = "The Player"
		self.retiring = False
		self.retired = False
		self.contract = PlayerContract()

		self.average_skill = 100