import os
import sys

import advance_test, simulate_race_weekend_test

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)

sys.path.append(parent_dir)

import main

def run_season(controller):
	model = controller.model

	while True:
		if model.season.current_week not in model.season.race_weeks:
			print(model.season.current_week)
			advance_test.advance_test(model) # calls model.advance()

		else:
			simulate_race_weekend_test.simulate_race_weekend_test(controller)

			break

		
controller = main.run(mode="headless")

run_season(controller)