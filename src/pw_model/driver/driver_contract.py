from dataclasses import dataclass

@dataclass
class DriverContract:
	contract_length: int = 9999 # in years

	salary: int = 4_000_000 # yearly salary


	def end_season(self):
		if self.contract_length > 0:
			self.contract_length -= 1
