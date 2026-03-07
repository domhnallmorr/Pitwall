from app.core.fuel_supplier_costs import FuelSupplierCostManager
from app.models.calendar import Calendar, Event, EventType
from app.models.circuit import Circuit
from app.models.driver import Driver
from app.models.finance import TransactionCategory
from app.models.state import GameState
from app.models.team import Team


def create_state(yearly_cost: int) -> GameState:
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
                fuel_supplier_name="Brasoil",
                fuel_supplier_deal="partner",
                fuel_supplier_yearly_cost=yearly_cost,
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


def test_calculate_race_amount_for_expense_deal():
    manager = FuelSupplierCostManager()
    assert manager.calculate_race_amount(yearly_cost=150_000, races_in_season=16) == -9_375


def test_calculate_race_amount_for_income_deal():
    manager = FuelSupplierCostManager()
    assert manager.calculate_race_amount(yearly_cost=-3_000_000, races_in_season=16) == 187_500


def test_charge_for_race_adds_fuel_supplier_expense_transaction():
    state = create_state(yearly_cost=150_000)
    manager = FuelSupplierCostManager()

    charge = manager.charge_for_event(state, state.calendar.current_event)

    assert charge is not None
    assert charge.applied_amount == -75_000
    txs = [t for t in state.finance.transactions if t.category == TransactionCategory.FUEL_SUPPLIER]
    assert len(txs) == 1
    assert txs[0].amount == -75_000


def test_charge_for_race_adds_fuel_supplier_income_transaction():
    state = create_state(yearly_cost=-3_000_000)
    manager = FuelSupplierCostManager()

    charge = manager.charge_for_event(state, state.calendar.current_event)

    assert charge is not None
    assert charge.applied_amount == 1_500_000
    txs = [t for t in state.finance.transactions if t.category == TransactionCategory.FUEL_SUPPLIER]
    assert len(txs) == 1
    assert txs[0].amount == 1_500_000
