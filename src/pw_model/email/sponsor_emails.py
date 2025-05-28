
import random

def gen_new_sponsor_signed_email(sponsor: str, team: str, role: str):
	messages = [
		f"{sponsor} has signed a contract with {team} to be their {role} for the next season.",
		f"{sponsor} has announced their partnership with {team} as their {role} for the upcoming season.",
		f"{sponsor} joins {team} as their {role} for the next season.",
		f"{sponsor} has secured a deal with {team} to become their {role} for the next season.",
		f"{sponsor} has signed a contract with {team} to be their {role} for the next season.",
	]

	return random.choice(messages)

