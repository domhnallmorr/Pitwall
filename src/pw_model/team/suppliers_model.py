from __future__ import annotations
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
	from pw_model.pw_base_model import Model

class SupplierDeals(Enum):
	WORKS = "works"
	PARTNER = "partner"
	CUSTOMER = "customer"
	

class SupplierModel:
	def __init__(self, model: Model, engine_supplier: str, engine_supplier_deal: SupplierDeals,
			  engine_supplier_cost: int,
			  tyre_supplier: str, tyre_supplier_deal: SupplierDeals, tyre_supplier_cost: int):
		self.model = model
		self.engine_supplier = engine_supplier
		self.engine_supplier_deal = engine_supplier_deal
		self.engine_supplier_cost = engine_supplier_cost
		
		self.tyre_supplier = tyre_supplier
		self.tyre_supplier_deal = tyre_supplier_deal
		self.tyre_supplier_cost = tyre_supplier_cost
		
		self.setup_new_season()
	def setup_new_season(self) -> None:
		self.engine_payments: list[int] = []
		self.tyre_payments: list[int] = []

	def process_race_payments(self) -> None:
		engine_payment = int(self.engine_supplier_cost / self.model.game_data.get_number_of_races())
		self.engine_payments.append(engine_payment)
		
		tyre_payment = int(self.tyre_supplier_cost / self.model.game_data.get_number_of_races())
		self.tyre_payments.append(tyre_payment)
