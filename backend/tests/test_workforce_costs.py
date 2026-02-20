from app.core.workforce_costs import WorkforceCostManager
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
        Event(name="Barcelona Test", week=5, type=EventType.TEST),
    ]
    return GameState(
        year=1998,
        teams=[Team(id=1, name="Warrick", country="United Kingdom", workforce=250, driver1_id=1, driver2_id=2)],
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


def test_calculate_race_cost_splits_annual_workforce_wage_across_races():
    manager = WorkforceCostManager(annual_avg_wage=28_000)
    assert manager.calculate_race_cost(workforce=250, races_in_season=17) == 411_765


def test_charge_for_race_adds_workforce_wage_transaction():
    state = create_state()
    manager = WorkforceCostManager(annual_avg_wage=28_000)

    charge = manager.charge_for_event(state, state.calendar.current_event)

    assert charge is not None
    assert charge.applied_cost == 3_500_000
    txs = [t for t in state.finance.transactions if t.category == TransactionCategory.WORKFORCE_WAGES]
    assert len(txs) == 1
    assert txs[0].amount == -3_500_000
