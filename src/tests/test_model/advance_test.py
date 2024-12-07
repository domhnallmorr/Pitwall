from tests import create_model
import pytest

def test_advance():
	model = create_model.create_model()
	week_start = model.season.current_week
	model.advance()

	assert model.season.current_week == week_start + 1

