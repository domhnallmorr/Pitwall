

def setup_practice(controller, time, session):
	print("here")

	controller.race_controller.race_model.setup_practice(120*60, "FP Friday")
	
def simulate_race_weekend_test(controller):

	# Friday Practice
	setup_practice(controller, 120*60, "FP Friday")

	# # Saturday Practice
	# controller.race_controller.race_model.setup_practice(90*60, "FP Saturday")

	# # Qualfying
	# controller.race_controller.race_model.setup_qualfying(60*60, "FP Saturday")
