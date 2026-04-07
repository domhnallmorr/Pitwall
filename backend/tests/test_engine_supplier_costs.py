from app.core.engine_supplier_costs import EngineSupplierCostManager
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
        teams=[
            Team(
                id=1,
                name="Warrick",
                country="United Kingdom",
                driver1_id=1,
                driver2_id=2,
                engine_supplier_name="Mechatron",
                engine_supplier_deal="customer",
                engine_supplier_yearly_cost=4_500_000,
            )
        ],
        drivers=[
            Driver(id=1, name="John Newhouse", age=27, country="Canada", team_id=1),
            Driver(id=2, name="Henrik Friedrich", age=31, country="Germany", team_id=1),
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


def test_calculate_race_cost_splits_engine_supplier_cost():
    manager = EngineSupplierCostManager()
    assert manager.calculate_race_amount(yearly_cost=4_500_000, races_in_season=16) == -281_250
    assert manager.calculate_race_amount(yearly_cost=-12_000_000, races_in_season=16) == 750_000


def test_charge_for_race_adds_engine_supplier_transaction():
    state = create_state()
    manager = EngineSupplierCostManager()

    charge = manager.charge_for_event(state, state.calendar.current_event)

    assert charge is not None
    assert charge.applied_amount == -2_250_000
    txs = [t for t in state.finance.transactions if t.category == TransactionCategory.ENGINE_SUPPLIER]
    assert len(txs) == 1
    assert txs[0].amount == -2_250_000


def test_charge_for_race_adds_engine_supplier_income_transaction_for_works_deal():
    state = create_state()
    state.teams[0].engine_supplier_deal = "works"
    state.teams[0].engine_supplier_yearly_cost = -12_000_000
    manager = EngineSupplierCostManager()

    charge = manager.charge_for_event(state, state.calendar.current_event)

    assert charge is not None
    assert charge.applied_amount == 6_000_000
    txs = [t for t in state.finance.transactions if t.category == TransactionCategory.ENGINE_SUPPLIER]
    assert len(txs) == 1
    assert txs[0].amount == 6_000_000
