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

def gen_turn1_spin_message(driver):
	messages = [
		f"{driver} has a spin at Turn 1!",
		f"{driver} has been spun around at Turn 1!",
		f"Disaster for {driver} at Turn 1!, They've spun off the track!",
	]
	return random.choice(messages)