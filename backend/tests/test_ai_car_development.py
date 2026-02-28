from unittest.mock import patch

from app.core.ai_car_development import AICarDevelopmentManager
from app.models.calendar import Calendar, Event, EventType
from app.models.state import GameState
from app.models.team import Team


def create_state() -> GameState:
    return GameState(
        year=1998,
        teams=[
            Team(id=1, name="Player Team", country="United Kingdom", car_speed=80),
            Team(id=2, name="AI Team A", country="Italy", car_speed=60),
            Team(id=3, name="AI Team B", country="France", car_speed=98),
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
    assert all(p["week"] in {4, 6, 8, 10} for p in planned)
    assert all(p["update_type"] == "medium" and p["delta"] == 3 for p in planned)
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
    assert team_b.car_speed == 103
    assert len(applied) == 2
    assert all(u.get("applied") is True for u in state.planned_ai_car_updates)

    email = next((e for e in state.emails if e.subject == "AI Car Development Updates: Week 6"), None)
    assert email is not None
    assert "AI Team A: Minor (+1) 60 -> 61" in email.body
    assert "AI Team B: Major (+5) 98 -> 103" in email.body
