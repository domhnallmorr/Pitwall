from unittest.mock import patch

from app.core.engine import GameEngine
from app.core.testing import TestSessionManager
from app.models.calendar import Calendar, Event, EventType
from app.models.finance import TransactionCategory
from app.models.state import GameState
from app.models.team import Team


def create_state() -> GameState:
    return GameState(
        year=1998,
        teams=[
            Team(id=1, name="Warrick", country="United Kingdom", car_speed=80),
            Team(id=2, name="Ferano", country="Italy", car_speed=84),
        ],
        drivers=[],
        calendar=Calendar(events=[Event(name="Test 1", week=5, type=EventType.TEST)], current_week=5),
        circuits=[],
        player_team_id=1,
    )


@patch("app.core.testing.random.randint", return_value=900)
@patch("app.core.testing.random.random", return_value=0.5)
def test_test_session_attend_applies_player_cost_and_ai_gains(mock_random, mock_randint):
    state = create_state()
    event = state.calendar.current_event

    result = TestSessionManager().process_test_session(state, event, player_attended=True, player_kms=1200)

    assert result["player"]["gain"] == 4
    assert result["player"]["cost"] == 1_680_000
    assert state.player_team.car_speed == 84
    assert state.player_team.car_wear == 12
    ai_team = next(t for t in state.teams if t.id == 2)
    assert ai_team.car_speed == 87  # 900 km -> +3
    assert ai_team.car_wear == 0
    txs = [t for t in state.finance.transactions if t.category == TransactionCategory.TESTING]
    assert len(txs) == 1
    assert txs[0].amount == -1_680_000


@patch("app.core.testing.random.randint", return_value=600)
@patch("app.core.testing.random.random", return_value=0.4)
def test_skip_test_still_allows_ai_to_improve(mock_random, mock_randint):
    state = create_state()
    engine = GameEngine()

    engine.handle_event_action(state, "skip")

    assert state.player_team.car_speed == 80
    assert state.player_team.car_wear == 0
    ai_team = next(t for t in state.teams if t.id == 2)
    assert ai_team.car_speed == 86  # 600 km -> +2
    txs = [t for t in state.finance.transactions if t.category == TransactionCategory.TESTING]
    assert len(txs) == 0
    assert any(e.subject.startswith("Test Session Summary:") for e in state.emails)


@patch("app.core.testing.random.random", return_value=0.99)
def test_player_test_can_fail_to_gain_speed(mock_random):
    state = GameState(
        year=1998,
        teams=[Team(id=1, name="Warrick", country="United Kingdom", car_speed=80)],
        drivers=[],
        calendar=Calendar(events=[Event(name="Test 1", week=5, type=EventType.TEST)], current_week=5),
        circuits=[],
        player_team_id=1,
    )
    event = state.calendar.current_event

    result = TestSessionManager().process_test_session(state, event, player_attended=True, player_kms=1500)

    assert result["player"]["attempted_gain"] == 5
    assert result["player"]["gain"] == 0
    assert result["player"]["succeeded"] is False
    assert state.player_team.car_speed == 80
