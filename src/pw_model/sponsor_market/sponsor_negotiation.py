
from pw_model.pw_model_enums import SponsorTypes

def determine_sponsor_payment_range(sponsor_wealth: int, sponsor_type: SponsorTypes) -> list[int]:

	# TITLE SPONSOR

	if sponsor_type == SponsorTypes.TITLE:
		return determine_title_sponsor_payment_range(sponsor_wealth)
	

def determine_title_sponsor_payment_range(sponsor_wealth: int) -> list[int]:
	if sponsor_wealth >= 90:
		return [4_000_000, 5_000_000]
	elif sponsor_wealth >= 80:
		return [3_000_000, 4_000_000]
	elif sponsor_wealth >= 70:
		return [2_000_000, 3_000_000]
	elif sponsor_wealth >= 50:
		return [1_000_000, 2_000_000]
	else:
		return [500_000, 1_000_000]