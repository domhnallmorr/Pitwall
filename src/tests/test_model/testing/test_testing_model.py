import pytest
from unittest.mock import MagicMock

from pw_model.testing.testing_model import TestingModel

@pytest.fixture
def dummy_model():
    model = MagicMock()
    # Setup nested mocks for player team
    player_team = MagicMock()
    player_team.finance_model.apply_testing_costs = MagicMock()
    player_team.car_model.implement_testing_progess = MagicMock()
    model.player_team_model = player_team

    # Season and calendar
    calendar = MagicMock()
    calendar.current_week = 1
    season = MagicMock()
    season.calendar = calendar
    model.season = season

    # Inbox
    inbox = MagicMock()
    model.inbox = inbox
    return model


def test_run_test_updates_progress_and_calls_models(dummy_model):
    tm = TestingModel(dummy_model)
    tm.run_test(500)

    assert tm.testing_progress == 25
    dummy_model.player_team_model.finance_model.apply_testing_costs.assert_called_once_with(500)
    dummy_model.season.calendar.post_test_actions.assert_called_once()
    dummy_model.inbox.generate_testing_completed_email.assert_called_once_with(500)


def test_skip_test_does_not_change_progress(dummy_model):
    tm = TestingModel(dummy_model)
    tm.testing_progress = 30
    tm.skip_test()

    assert tm.testing_progress == 30
    dummy_model.player_team_model.finance_model.apply_testing_costs.assert_called_once_with(0)
    dummy_model.season.calendar.post_test_actions.assert_called_once()
    dummy_model.inbox.generate_testing_completed_email.assert_not_called()


def test_completion_resets_progress_and_updates_car(dummy_model):
    tm = TestingModel(dummy_model)
    tm.run_test(2000)

    assert tm.testing_progress == 0
    dummy_model.player_team_model.car_model.implement_testing_progess.assert_called_once_with(1)
    dummy_model.player_team_model.finance_model.apply_testing_costs.assert_called_once_with(2000)
    dummy_model.season.calendar.post_test_actions.assert_called_once()
    dummy_model.inbox.generate_testing_progress_email.assert_called_once()
    dummy_model.inbox.generate_testing_completed_email.assert_not_called()