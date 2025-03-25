from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pw_model.tyre.tyre_supplier_model import TyreSupplierModel
	from pw_model.pw_base_model import Model

class TyreCompound:
	def __init__(self, supplier: TyreSupplierModel, name: str, grip: int, wear: int):
		"""
		Initialize a tyre compound
		
		Parameters:
		- name: Name of the compound (e.g., "Soft", "Medium", "Hard")
		- grip: Initial laptime advantage in ms (Soft has more grip than Hard)
		- wear: between 1 and 100, 
		"""
		self.supplier = supplier # supplier that provides the compound
		self.name = name
		self.grip = grip
		self.wear = wear

		