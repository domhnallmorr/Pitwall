from unittest.mock import patch

from app.core.engine import GameEngine
from app.core.testing import TestSessionManager
from app.models.calendar import Calendar, Event, EventType
from app.models.chassis import Chassis
from app.models.driver import Driver
from app.models.finance import TransactionCategory
from app.models.state import GameState
from app.models.team import Team
from app.models.technical_director import TechnicalDirector


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
        player_chassis=[
            Chassis(id=1, team_id=1, name="Chassis 1", wear=0),
            Chassis(id=2, team_id=1, name="Chassis 2", wear=0),
            Chassis(id=3, team_id=1, name="Chassis 3", wear=0),
        ],
        player_test_chassis_id=2,
    )


@patch("app.core.testing.random.randint", return_value=900)
@patch("app.core.testing.random.random", return_value=0.5)
def test_test_session_attend_applies_player_cost_and_ai_gains(mock_random, mock_randint):
    state = create_state()
    event = state.calendar.current_event

    result = TestSessionManager().process_test_session(state, event, player_attended=True, player_kms=1200)

    assert result["player"]["gain"] == 4
    assert result["player"]["cost"] == 1_680_000
    assert result["player"]["setup_gain"] == 8
    assert result["player"]["old_setup_knowledge"] == 1
    assert result["player"]["new_setup_knowledge"] == 9
    assert state.player_setup_knowledge == 9
    assert state.player_team.car_speed == 84
    assert result["player"]["chassis_name"] == "Chassis 2"
    assert state.player_chassis[1].wear == 12
    ai_team = next(t for t in state.teams if t.id == 2)
    assert ai_team.car_speed == 87  # 900 km -> +3
    assert ai_team.setup_knowledge == 7  # 900 km scales the AI full-test setup gain.
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
    assert state.player_setup_knowledge == 1
    assert state.player_chassis[1].wear == 0
    ai_team = next(t for t in state.teams if t.id == 2)
    assert ai_team.car_speed == 86  # 600 km -> +2
    assert ai_team.setup_knowledge == 5
    txs = [t for t in state.finance.transactions if t.category == TransactionCategory.TESTING]
    assert len(txs) == 0
    assert any(e.subject.startswith("Test Session Summary:") for e in state.emails)


@patch("app.core.testing.random.random", return_value=0.99)
def test_player_test_can_fail_to_gain_speed(mock_random):
    state = GameState(
        year=1998,
        teams=[Team(id=1, name="Warrick", country="United Kingdom", car_speed=80)],
        drivers=[],
        player_chassis=[
            Chassis(id=1, team_id=1, name="Chassis 1", wear=0),
            Chassis(id=2, team_id=1, name="Chassis 2", wear=0),
            Chassis(id=3, team_id=1, name="Chassis 3", wear=0),
        ],
        player_test_chassis_id=2,
        calendar=Calendar(events=[Event(name="Test 1", week=5, type=EventType.TEST)], current_week=5),
        circuits=[],
        player_team_id=1,
    )
    event = state.calendar.current_event

    result = TestSessionManager().process_test_session(state, event, player_attended=True, player_kms=1500)

    assert result["player"]["attempted_gain"] == 5
    assert result["player"]["gain"] == 0
    assert result["player"]["succeeded"] is False
    assert result["player"]["setup_gain"] == 8
    assert state.player_setup_knowledge == 9
    assert state.player_team.car_speed == 80
    assert state.player_chassis[1].wear == 15


@patch("app.core.testing.random.randint", return_value=600)
@patch("app.core.testing.random.random", return_value=0.5)
def test_setup_gain_uses_team_resources_and_caps_per_test(mock_random, mock_randint):
    state = create_state()
    state.teams[0].driver1_id = 1
    state.teams[0].driver2_id = 2
    state.teams[0].facilities = 100
    state.drivers = [
        Driver(id=1, name="Driver 1", age=28, country="UK", team_id=1, consistency=100, racecraft=5),
        Driver(id=2, name="Driver 2", age=29, country="UK", team_id=1, consistency=100, racecraft=5),
    ]
    state.technical_directors = [
        TechnicalDirector(id=1, name="TD", country="UK", age=45, skill=100, team_id=1),
    ]
    event = state.calendar.current_event

    result = TestSessionManager().process_test_session(state, event, player_attended=True, player_kms=1200)

    assert result["player"]["setup_gain"] == 15
    assert state.player_setup_knowledge == 16


@patch("app.core.testing.random.randint", return_value=600)
@patch("app.core.testing.random.random", return_value=0.5)
def test_setup_gain_scales_with_test_distance(mock_random, mock_randint):
    state = create_state()
    event = state.calendar.current_event

    result = TestSessionManager().process_test_session(state, event, player_attended=True, player_kms=600)

    assert result["player"]["setup_gain"] == 4
    assert state.player_setup_knowledge == 5
