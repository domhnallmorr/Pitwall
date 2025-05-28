from dataclasses import dataclass
import logging

from pw_model.pw_model_enums import SponsorTypes

@dataclass
class SponsorContract:
    sponsor_type: SponsorTypes = SponsorTypes.NONE
    contract_length: int = 9999  # in years
    total_payment: int = 4_000_000  # yearly payment

    def end_season(self, increase_year: bool=True) -> None:
        logging.debug(f"End Season, Sponsor Type: {self.sponsor_type.value}")
        logging.debug(f"Initial Contract Length: {self.contract_length}")

        if increase_year:
            if self.contract_length > 0:
                self.contract_length -= 1

        logging.debug(f"Final Contract Length: {self.contract_length}")