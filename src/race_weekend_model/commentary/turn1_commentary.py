import random


def gen_leading_after_turn1_message(driver):
	messages = [
		f"{driver} is leading after Turn 1!",
		f"{driver} takes the lead after Turn 1!",
		f"{driver} is out front after Turn 1!",
		f"{driver} is in the lead after Turn 1!",
		f"{driver} leads the fields out of Turn 1!",
	]
	return random.choice(messages)