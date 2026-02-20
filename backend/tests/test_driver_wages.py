from app.core.driver_wages import DriverWageManager
from app.models.calendar import Calendar, Event, EventType
from app.models.circuit import Circuit
from app.models.driver import Driver
from app.models.finance import TransactionCategory
from app.models.state import GameState
from app.models.team import Team


def create_state() -> GameState:
    events = [
        Event(name="Albert Park", week=10, type=EventType.RACE),
        Event(name="Interlagos", week=13, type=EventType.RACE),
    ]
    return GameState(
        year=1998,
        teams=[Team(id=1, name="Warrick", country="United Kingdom", workforce=250, driver1_id=1, driver2_id=2)],
        drivers=[
            Driver(id=1, name="John Newhouse", age=27, country="Canada", team_id=1, wage=9_600_000),
            Driver(id=2, name="Pay Driver", age=22, country="Argentina", team_id=1, wage=-4_300_000, pay_driver=True),
        ],
        calendar=Calendar(events=events, current_week=10),
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


def test_calculate_race_wage_splits_annual_wage_across_races():
    manager = DriverWageManager()
    assert manager.calculate_race_wage(annual_wage=9_600_000, races_in_season=16) == 600_000


def test_charge_for_race_adds_driver_wage_transactions_with_sign_handling():
    state = create_state()
    manager = DriverWageManager()

    charges = manager.charge_for_event(state, state.calendar.current_event)

    assert len(charges) == 2
    txs = [t for t in state.finance.transactions if t.category == TransactionCategory.DRIVER_WAGES]
    assert len(txs) == 2
    assert any(t.amount < 0 for t in txs)  # regular driver expense
    assert any(t.amount > 0 for t in txs)  # pay driver income
