from app.models.calendar import Calendar, Event, EventType
from app.models.circuit import Circuit
from app.models.driver import Driver
from app.models.state import GameState
from app.models.team import Team


def make_team(**overrides) -> Team:
    data = {
        "id": 1,
        "name": "Team A",
        "country": "United Kingdom",
    }
    data.update(overrides)
    return Team(**data)


def make_driver(**overrides) -> Driver:
    data = {
        "id": 1,
        "name": "Driver A",
        "age": 25,
        "country": "United Kingdom",
    }
    data.update(overrides)
    return Driver(**data)


def make_race_event(name: str = "Albert Park", week: int = 10) -> Event:
    return Event(name=name, week=week, type=EventType.RACE)


def make_test_event(name: str = "Barcelona Test", week: int = 5) -> Event:
    return Event(name=name, week=week, type=EventType.TEST)


def make_calendar(events=None, current_week: int = 1) -> Calendar:
    return Calendar(events=events or [], current_week=current_week)


def make_circuit(**overrides) -> Circuit:
    data = {
        "id": 1,
        "name": "Albert Park",
        "country": "Australia",
        "location": "Melbourne",
        "laps": 58,
        "base_laptime_ms": 84_000,
        "length_km": 5.303,
        "overtaking_delta": 1_200,
        "power_factor": 6,
    }
    data.update(overrides)
    return Circuit(**data)


def make_state(year: int = 1998, teams=None, drivers=None, calendar=None, circuits=None, **overrides) -> GameState:
    data = {
        "year": year,
        "teams": teams or [],
        "drivers": drivers or [],
        "calendar": calendar or make_calendar(),
        "circuits": circuits or [],
    }
    data.update(overrides)
    return GameState(**data)
