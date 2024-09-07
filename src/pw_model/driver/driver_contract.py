from dataclasses import dataclass

@dataclass
class DriverContract:
	contract_length: int = 9999 # in years


	def end_season(self):
		if self.contract_length > 0:
			self.contract_length -= 1
