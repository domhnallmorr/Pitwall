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
from app.models.chassis import Chassis
from app.models.driver import Driver
from app.models.engine_supplier import EngineSupplier
from app.models.finance import Finance
from app.models.state import GameState
from app.models.team import Team
from app.models.tyre_compound import TyreCompound
from app.models.tyre_supplier import TyreSupplier


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
                mechanics_staff=58,
                engine_supplier_name="Mechatron",
                facilities=70,
            )
        ],
        drivers=[
            Driver(id=1, name="John Newhouse", age=27, country="Canada", team_id=1, speed=84, consistency=68, qualifying=3, race_starts=1, wins=1, podiums=2, poles=1, fastest_laps=1, championships=1),
            Driver(id=2, name="Henrik Friedrich", age=31, country="Germany", team_id=1, speed=72, consistency=58, qualifying=3),
        ],
        player_spares=6,
        player_chassis=[
            Chassis(id=1, team_id=1, name="Chassis 1", wear=5),
            Chassis(id=2, team_id=1, name="Chassis 2", wear=9),
            Chassis(id=3, team_id=1, name="Chassis 3", wear=0),
        ],
        player_test_chassis_id=3,
        player_setup_knowledge=42,
        player_race_chassis_assignments={1: 1, 2: 2},
        calendar=Calendar(events=[Event(name="Albert Park", week=10, type=EventType.RACE)], current_week=1),
        circuits=[],
        player_team_id=1,
        engine_suppliers=[EngineSupplier(id=1, name="Mechatron", country="France", resources=55, power=60)],
        tyre_suppliers=[
            TyreSupplier(id=1, name="Greatday", country="USA", wear=60, grip=80, resources=88, innovation=82, reliability=90),
            TyreSupplier(id=2, name="Spanrock", country="Japan", wear=80, grip=70, resources=86, innovation=91, reliability=84),
        ],
        season_tyre_compounds={
            "Greatday": [
                TyreCompound(supplier_name="Greatday", name="Hard", grip=67, wear=93, stiffness=87, year=1998),
                TyreCompound(supplier_name="Greatday", name="Medium", grip=77, wear=79, stiffness=67, year=1998),
                TyreCompound(supplier_name="Greatday", name="Soft", grip=88, wear=64, stiffness=47, year=1998),
            ],
            "Spanrock": [
                TyreCompound(supplier_name="Spanrock", name="Hard", grip=66, wear=89, stiffness=84, year=1998),
                TyreCompound(supplier_name="Spanrock", name="Medium", grip=78, wear=77, stiffness=64, year=1998),
                TyreCompound(supplier_name="Spanrock", name="Soft", grip=90, wear=60, stiffness=44, year=1998),
            ],
        },
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
    ), patch(
        "app.commands.query_commands.StandingsManager.build_driver_countback_notes", return_value={}
    ), patch(
        "app.commands.query_commands.StandingsManager.build_constructor_countback_notes", return_value={}
    ):
        payload = get_standings_payload(state)
    assert payload["drivers"][0]["value"] == "d1"
    assert payload["constructors"][0]["value"] == "c1"


def test_get_standings_payload_dict_fallback_path():
    state = create_state()
    with patch("app.commands.query_commands.StandingsManager.get_driver_standings", return_value=[DictOnlyObj("d1")]), patch(
        "app.commands.query_commands.StandingsManager.get_constructor_standings", return_value=[DictOnlyObj("c1")]
    ), patch(
        "app.commands.query_commands.StandingsManager.build_driver_countback_notes", return_value={}
    ), patch(
        "app.commands.query_commands.StandingsManager.build_constructor_countback_notes", return_value={}
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


def test_driver_and_staff_payloads_include_overall_rating_consistency_and_qualifying():
    state = create_state()

    staff_payload = get_staff_payload(state)
    driver_payload = get_driver_payload(state, "John Newhouse")

    assert staff_payload["drivers"][0]["consistency"] == 68
    assert staff_payload["drivers"][0]["qualifying"] == 3
    assert staff_payload["drivers"][0]["overall_rating"] == 80
    assert driver_payload["consistency"] == 68
    assert driver_payload["qualifying"] == 3
    assert driver_payload["overall_rating"] == 80


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
    assert payload["player_setup_knowledge"] == 42
    assert payload["player_development"]["active"] is False


def test_get_car_payload_includes_player_chassis_state():
    state = create_state()
    state.teams[0].tyre_supplier_name = "Greatday"

    payload = get_car_payload(state)

    assert payload["player_spares"] == 6
    assert payload["construction"]["spares"]["available"] == 6
    assert payload["construction"]["spares"]["build_cost"] == 52_500
    assert payload["construction"]["spares"]["construction_usage_percent"] == 0
    assert payload["construction"]["spares"]["construction_capacity_remaining"] == 100
    assert payload["maintenance"]["mechanics_usage_percent"] == 0
    assert payload["maintenance"]["mechanics_capacity_remaining"] == 100
    assert payload["maintenance"]["mechanics_staff_available"] == 58
    assert payload["maintenance"]["mechanics_required_percent_per_spare"] == 22
    assert payload["player_setup_knowledge"] == 42
    assert payload["player_test_chassis_id"] == 3
    assert payload["player_tyre_supplier_name"] == "Greatday"
    assert payload["player_drivers"][0]["name"] == "John Newhouse"
    assert len(payload["tyres"]["suppliers"]) == 2
    assert payload["tyres"]["suppliers"][0]["name"] == "Greatday"
    assert payload["tyres"]["suppliers"][0]["is_player_supplier"] is True
    assert payload["tyres"]["suppliers"][0]["compounds"][2]["name"] == "Soft"
    assert len(payload["player_chassis"]) == 3
    assert payload["player_chassis"][0]["name"] == "Chassis 1"
    assert payload["player_chassis"][0]["assigned_driver_id"] == 1
    assert payload["player_chassis"][0]["assigned_driver_name"] == "John Newhouse"
    assert payload["player_chassis"][1]["assigned_driver_id"] == 2
    assert payload["player_chassis"][2]["assigned_to_test"] is True
