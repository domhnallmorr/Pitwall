from unittest.mock import patch

from app.core.ai_car_development import AICarDevelopmentManager
from app.models.calendar import Calendar, Event, EventType
from app.models.state import GameState
from app.models.team import Team


def create_state() -> GameState:
    return GameState(
        year=1998,
        teams=[
            Team(id=1, name="Player Team", country="United Kingdom", car_speed=80, workforce=250, facilities=75),
            Team(id=2, name="AI Team A", country="Italy", car_speed=60, workforce=250, facilities=75),
            Team(id=3, name="AI Team B", country="France", car_speed=84, workforce=250, facilities=75),
        ],
        drivers=[],
        calendar=Calendar(
            events=[
                Event(name="Race 1", week=2, type=EventType.RACE),
                Event(name="Race 2", week=4, type=EventType.RACE),
                Event(name="Race 3", week=6, type=EventType.RACE),
                Event(name="Race 4", week=8, type=EventType.RACE),
                Event(name="Race 5", week=10, type=EventType.RACE),
            ],
            current_week=1,
        ),
        circuits=[],
        player_team_id=1,
    )


@patch("app.core.ai_car_development.random.randint", return_value=2)
@patch("app.core.ai_car_development.random.choices", return_value=["medium"])
def test_generate_for_season_plans_ai_only_and_skips_first_race(mock_choices, mock_randint):
    state = create_state()
    planned = AICarDevelopmentManager().generate_for_season(state)

    assert planned == state.planned_ai_car_updates
    assert all(p["team_id"] in {2, 3} for p in planned)
    assert all(p["week"] in {8, 10} for p in planned)
    assert all(p["update_type"] == "medium" and p["delta"] == 3 for p in planned)
    assert all(p["development_weeks"] == 7 for p in planned)
    assert all(p["start_week"] == p["week"] - p["development_weeks"] for p in planned)
    assert len([p for p in planned if p["team_id"] == 2]) == 2
    assert len([p for p in planned if p["team_id"] == 3]) == 2


def test_apply_for_week_updates_speed_and_sends_email():
    state = create_state()
    state.calendar.current_week = 6
    state.planned_ai_car_updates = [
        {
            "year": 1998,
            "team_id": 2,
            "team_name": "AI Team A",
            "week": 6,
            "update_type": "minor",
            "delta": 1,
            "applied": False,
        },
        {
            "year": 1998,
            "team_id": 3,
            "team_name": "AI Team B",
            "week": 6,
            "update_type": "major",
            "delta": 5,
            "applied": False,
        },
    ]

    applied = AICarDevelopmentManager().apply_for_week(state)

    team_a = next(t for t in state.teams if t.id == 2)
    team_b = next(t for t in state.teams if t.id == 3)
    assert team_a.car_speed == 61
    assert team_b.car_speed == 87
    assert len(applied) == 2
    assert all(u.get("applied") is True for u in state.planned_ai_car_updates)

    email = next((e for e in state.emails if e.subject == "AI Car Development Updates: Week 6"), None)
    assert email is not None
    assert "AI Team A: Minor (+1) 60 -> 61" in email.body
    assert "AI Team B: Major (+5) 84 -> 87" in email.body


@patch("app.core.ai_car_development.random.randint", return_value=1)
@patch("app.core.ai_car_development.random.choices", return_value=["minor"])
def test_generate_for_season_delays_low_workforce_updates(mock_choices, mock_randint):
    state = create_state()
    team_a = next(t for t in state.teams if t.id == 2)
    team_b = next(t for t in state.teams if t.id == 3)
    team_a.workforce = 250
    team_b.workforce = 0

    planned = AICarDevelopmentManager().generate_for_season(state)
    by_team = {p["team_id"]: p for p in planned}

    assert by_team[2]["development_weeks"] == 4
    assert by_team[3]["development_weeks"] == 8
    assert by_team[2]["week"] >= 6
    assert by_team[3]["week"] >= 9


def test_workforce_time_multiplier_and_development_weeks_are_bounded():
    manager = AICarDevelopmentManager()

    assert manager._workforce_time_multiplier(250) == 1.0
    assert manager._workforce_time_multiplier(0) == 2.0
    assert manager._workforce_time_multiplier(-10) == 2.0
    assert manager._workforce_time_multiplier(999) == 1.0

    assert manager._development_weeks_for_team("minor", 250) == 4
    assert manager._development_weeks_for_team("minor", 0) == 8
    assert manager._development_weeks_for_team("major", 0) == 20


def test_update_weights_and_soft_cap_favor_better_resourced_teams():
    manager = AICarDevelopmentManager()

    low_weights = manager._update_weights_for_team(90, 20)
    high_weights = manager._update_weights_for_team(250, 90)

    assert low_weights[0] > high_weights[0]
    assert low_weights[2] < high_weights[2]
    assert manager._resource_soft_cap(90, 20) < manager._resource_soft_cap(250, 90)


@patch("app.core.ai_car_development.random.choice", side_effect=lambda seq: seq[0])
def test_pick_spread_weeks_handles_empty_full_and_gap_filtered_cases(mock_choice):
    manager = AICarDevelopmentManager()

    assert manager._pick_spread_weeks([], 2) == []
    assert manager._pick_spread_weeks([2, 4], 0) == []
    assert manager._pick_spread_weeks([2, 4], 3) == [2, 4]

    picked = manager._pick_spread_weeks([2, 3, 4, 5, 6], 2)
    assert picked == [2, 4]


def test_generate_for_season_returns_empty_without_races_or_eligible_weeks():
    manager = AICarDevelopmentManager()

    no_race_state = GameState(
        year=1998,
        teams=[Team(id=1, name="AI Team", country="Italy", workforce=250)],
        drivers=[],
        calendar=Calendar(events=[Event(name="Test", week=1, type=EventType.TEST)], current_week=1),
        circuits=[],
    )
    assert manager.generate_for_season(no_race_state) == []
    assert no_race_state.planned_ai_car_updates == []

    only_opening_race_state = GameState(
        year=1998,
        teams=[Team(id=1, name="AI Team", country="Italy", workforce=250)],
        drivers=[],
        calendar=Calendar(events=[Event(name="Race 1", week=2, type=EventType.RACE)], current_week=1),
        circuits=[],
    )
    assert manager.generate_for_season(only_opening_race_state) == []
    assert only_opening_race_state.planned_ai_car_updates == []


@patch("app.core.ai_car_development.random.randint", return_value=2)
@patch("app.core.ai_car_development.random.choices", return_value=["major"])
def test_generate_for_season_skips_updates_when_completion_window_is_impossible(mock_choices, mock_randint):
    state = create_state()
    for team in state.teams:
        team.workforce = 0

    planned = AICarDevelopmentManager().generate_for_season(state)

    assert planned == []
    assert state.planned_ai_car_updates == []


def test_apply_for_week_handles_empty_due_updates_and_missing_team():
    state = create_state()
    manager = AICarDevelopmentManager()

    assert manager.apply_for_week(state, week=99) == []
    assert state.emails == []

    state.planned_ai_car_updates = [
        {
            "year": 1998,
            "team_id": 999,
            "team_name": "Ghost Team",
            "week": state.calendar.current_week,
            "update_type": "minor",
            "delta": 1,
            "applied": False,
        }
    ]

    applied = manager.apply_for_week(state)

    assert applied == []
    assert state.planned_ai_car_updates[0]["applied"] is True
    assert state.emails == []


def test_apply_for_week_compresses_low_resource_team_speed_growth():
    state = create_state()
    state.calendar.current_week = 6
    low_resource_team = next(t for t in state.teams if t.id == 2)
    low_resource_team.workforce = 90
    low_resource_team.facilities = 20
    low_resource_team.car_speed = 72
    state.planned_ai_car_updates = [
        {
            "year": 1998,
            "team_id": 2,
            "team_name": "AI Team A",
            "week": 6,
            "update_type": "major",
            "delta": 5,
            "applied": False,
        },
    ]

    applied = AICarDevelopmentManager().apply_for_week(state)

    assert applied[0]["new_speed"] == 72
    assert low_resource_team.car_speed == 72
