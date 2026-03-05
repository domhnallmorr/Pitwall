from app.core.player_car_development import PlayerCarDevelopmentManager
from app.models.calendar import Calendar, Event, EventType
from app.models.finance import TransactionCategory
from app.models.state import GameState
from app.models.team import Team


def create_state() -> GameState:
    return GameState(
        year=1998,
        teams=[Team(id=1, name="Warrick", country="United Kingdom", car_speed=80, workforce=250)],
        drivers=[],
        calendar=Calendar(events=[Event(name="Race 1", week=2, type=EventType.RACE)], current_week=1),
        circuits=[],
        player_team_id=1,
    )


def test_start_creates_active_project():
    state = create_state()
    manager = PlayerCarDevelopmentManager()

    project = manager.start(state, "minor")

    assert project.active is True
    assert project.development_type == "minor"
    assert project.total_weeks == 4
    assert project.weeks_remaining == 4
    assert project.weekly_cost == 25_000


def test_process_week_charges_weekly_and_completes_with_speed_gain():
    state = create_state()
    manager = PlayerCarDevelopmentManager()
    manager.start(state, "minor")

    for week in [2, 3, 4, 5]:
        state.calendar.current_week = week
        result = manager.process_week(state)
        assert result is not None

    project = state.player_car_development
    assert project is not None
    assert project.active is False
    assert project.paid == 100_000
    assert state.player_team.car_speed == 81

    txs = [t for t in state.finance.transactions if t.category == TransactionCategory.DEVELOPMENT]
    assert len(txs) == 4
    assert sum(-t.amount for t in txs) == 100_000


def test_start_scales_duration_with_low_workforce():
    state = create_state()
    state.player_team.workforce = 0
    manager = PlayerCarDevelopmentManager()

    project = manager.start(state, "minor")

    assert project.total_weeks == 8
    assert project.weeks_remaining == 8
    assert project.weekly_cost == 12_500
