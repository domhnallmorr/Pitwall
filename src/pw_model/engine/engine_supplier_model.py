from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model


class EngineSupplierModel:
	def __init__(self, model: Model, name: str, resources: int, power: int):
		self.model = model
		self.name = name # name of company
		self.resources = resources # size of the company
		self.power = power # power of engine


	@property
	def overall_rating(self) -> int:
		return int((self.power + self.resources) / 2)