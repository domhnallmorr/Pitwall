from pw_model.tyre.tyre_compound import TyreCompound
from enum import Enum

class CompoundNames(Enum):
	SOFT = "Soft"
	HARD = "Hard"

class TyreSupplierModel:
	def __init__(self, name: str, wear: int, grip: int): # wear and grip are between 1 and 100, 100 being the best and 1 the worst
		self.name = name
		
		self.compound = TyreCompound(self, CompoundNames.SOFT, grip, wear)
		