from app.core.crash_damage import CrashDamageManager
from app.models.calendar import Calendar, Event, EventType
from app.models.circuit import Circuit
from app.models.driver import Driver
from app.models.finance import TransactionCategory
from app.models.state import GameState
from app.models.team import Team


class StubRng:
    def __init__(self, random_value: float, randint_value: int):
        self._random_value = random_value
        self._randint_value = randint_value

    def random(self) -> float:
        return self._random_value

    def randint(self, a: int, b: int) -> int:
        assert a <= self._randint_value <= b
        return self._randint_value


def create_state() -> GameState:
    event = Event(name="Albert Park", week=10, type=EventType.RACE)
    return GameState(
        year=1998,
        teams=[
            Team(id=1, name="Warrick", country="United Kingdom", driver1_id=1, driver2_id=2),
            Team(id=2, name="Ferano", country="Italy", driver1_id=3, driver2_id=4),
        ],
        drivers=[
            Driver(id=1, name="John Newhouse", age=27, country="Canada", team_id=1),
            Driver(id=2, name="Henrik Friedrich", age=31, country="Germany", team_id=1),
            Driver(id=3, name="Marco Schneider", age=29, country="Germany", team_id=2),
            Driver(id=4, name="Evan Irving", age=33, country="United Kingdom", team_id=2),
        ],
        calendar=Calendar(events=[event], current_week=10),
        circuits=[
            Circuit(
                id=1,
                name="Albert Park",
                country="Australia",
                location="Melbourne",
                laps=58,
                base_laptime_ms=84_000,
                length_km=5.303,
                overtaking_delta=1_200,
                power_factor=6,
            )
        ],
        player_team_id=1,
    )


def test_calculate_damage_cost_respects_minor_tier_range():
    manager = CrashDamageManager()
    tier, cost = manager.calculate_damage_cost(rng=StubRng(0.20, 120_000))
    assert tier.label == "minor"
    assert 50_000 <= cost <= 150_000


def test_calculate_damage_cost_respects_very_severe_tier_range():
    manager = CrashDamageManager()
    tier, cost = manager.calculate_damage_cost(rng=StubRng(0.99, 480_000))
    assert tier.label == "very severe"
    assert 450_000 <= cost <= 500_000


def test_charge_for_race_applies_only_to_player_team_crashes():
    state = create_state()
    manager = CrashDamageManager()
    race_result = {
        "event_name": "Albert Park",
        "crash_outs": [
            {"driver_id": 1, "driver_name": "John Newhouse", "team_id": 1, "team_name": "Warrick"},
            {"driver_id": 3, "driver_name": "Marco Schneider", "team_id": 2, "team_name": "Ferano"},
        ],
    }
    event = state.calendar.current_event

    charges = manager.charge_for_race(state, race_result, event, rng=StubRng(0.70, 200_000))

    assert len(charges) == 1
    assert charges[0].driver_name == "John Newhouse"
    assert charges[0].tier == "moderate"
    assert charges[0].applied_cost == 200_000
    damage_txs = [t for t in state.finance.transactions if t.category == TransactionCategory.CRASH_DAMAGE]
    assert len(damage_txs) == 1
    assert damage_txs[0].amount == -200_000
