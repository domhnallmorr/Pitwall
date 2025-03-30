import random



def gen_overtake_message(driver_a, driver_b):
	messages = [
		f"And there's the pass! {driver_a} takes the inside line and muscles past {driver_b} for position!",
		f"{driver_a} with a bold move! A late lunge down the outside sees them snatch the place from {driver_b}!",
		f"Patient work from {driver_a} pays off! They close the gap on {driver_b} and make the pass stick!",
		f"{driver_a} makes a daring overtake! A risky maneuver, but it's come off perfectly!",
		f"Textbook move from {driver_a}! They time the pass to perfection and leave {driver_b} with no answer.",
	]

	return random.choice(messages)