from dataclasses import dataclass
from unittest.mock import patch

from app.commands.query_commands import (
    get_car_payload,
    get_driver_payload,
    get_facilities_payload,
    get_grid_payload,
    get_staff_payload,
    get_standings_payload,
)
from app.models.calendar import Calendar, Event, EventType
from app.models.driver import Driver
from app.models.engine_supplier import EngineSupplier
from app.models.finance import Finance
from app.models.state import GameState
from app.models.team import Team


def create_state() -> GameState:
    return GameState(
        year=1998,
        teams=[
            Team(
                id=1,
                name="Warrick",
                country="United Kingdom",
                driver1_id=1,
                driver2_id=2,
                car_speed=80,
                workforce=200,
                engine_supplier_name="Mechatron",
                facilities=70,
            )
        ],
        drivers=[
            Driver(id=1, name="John Newhouse", age=27, country="Canada", team_id=1, speed=84, race_starts=1, wins=1),
            Driver(id=2, name="Henrik Friedrich", age=31, country="Germany", team_id=1, speed=72),
        ],
        calendar=Calendar(events=[Event(name="Albert Park", week=10, type=EventType.RACE)], current_week=1),
        circuits=[],
        player_team_id=1,
        engine_suppliers=[EngineSupplier(id=1, name="Mechatron", country="France", resources=55, power=60)],
        finance=Finance(),
    )


def test_get_grid_payload_uses_state_year_when_none():
    class FakeGrid:
        def get_grid_json(self, state, year=None):
            return "[]"

    payload = get_grid_payload(create_state(), None, FakeGrid())
    assert payload["grid_json"] == "[]"
    assert payload["year"] == 1998


@dataclass
class DumpObj:
    value: str

    def model_dump(self):
        return {"value": self.value}


class DictOnlyObj:
    def __init__(self, value):
        self.value = value

    def dict(self):
        return {"value": self.value}


def test_get_standings_payload_model_dump_path():
    state = create_state()
    with patch("app.commands.query_commands.StandingsManager.get_driver_standings", return_value=[DumpObj("d1")]), patch(
        "app.commands.query_commands.StandingsManager.get_constructor_standings", return_value=[DumpObj("c1")]
    ):
        payload = get_standings_payload(state)
    assert payload["drivers"][0]["value"] == "d1"
    assert payload["constructors"][0]["value"] == "c1"


def test_get_standings_payload_dict_fallback_path():
    state = create_state()
    with patch("app.commands.query_commands.StandingsManager.get_driver_standings", return_value=[DictOnlyObj("d1")]), patch(
        "app.commands.query_commands.StandingsManager.get_constructor_standings", return_value=[DictOnlyObj("c1")]
    ):
        payload = get_standings_payload(state)
    assert payload["drivers"][0]["value"] == "d1"
    assert payload["constructors"][0]["value"] == "c1"


def test_get_staff_payload_requires_player_team():
    state = create_state()
    state.player_team_id = None
    try:
        get_staff_payload(state)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "No player team assigned" in str(exc)


def test_get_driver_payload_requires_existing_driver():
    try:
        get_driver_payload(create_state(), "Missing Driver")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "not found" in str(exc)


def test_get_facilities_payload_requires_player_team():
    state = create_state()
    state.player_team_id = None
    try:
        get_facilities_payload(state)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "No player team assigned" in str(exc)


def test_get_car_payload_without_player_team_returns_defaults():
    state = create_state()
    state.player_team_id = None
    payload = get_car_payload(state)
    assert payload["player_team_name"] is None
    assert payload["player_car_speed"] == 0
    assert payload["player_car_wear"] == 0
    assert payload["player_development"]["active"] is False
