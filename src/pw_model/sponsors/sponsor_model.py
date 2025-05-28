import logging
from pw_model.sponsors.sponsor_contract import SponsorContract
from pw_model.pw_model_enums import SponsorTypes

class SponsorModel:
	def __init__(self, name: str,
			  wealth : int,
			  sponsor_type : SponsorTypes,
			  contract_length: int=0,
			  total_payment: int=0):
		
		self.name = name
		self.wealth = wealth # between 1 and 100
		self.contract = SponsorContract(sponsor_type, contract_length=contract_length, total_payment=total_payment)

		self.retiring = False

	def __repr__(self) -> str:
		return f"SponsorModel <{self.name}>"
	
	@property
	def overall_rating(self) -> int:
		return self.wealth

	def end_season(self, increase_year: bool=True) -> None:
		logging.debug(f"End Season Sponsor {self.name}")
		self.contract.end_season(increase_year=increase_year)