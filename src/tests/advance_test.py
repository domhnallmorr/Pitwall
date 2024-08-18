

def advance_test(model):
	week_start = model.season.current_week
	model.advance()

	assert model.season.current_week == week_start + 1

