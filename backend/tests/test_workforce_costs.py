from app.core.workforce_costs import WorkforceCostManager
from app.models.finance import TransactionCategory
from tests.factories import make_calendar, make_circuit, make_driver, make_race_event, make_state, make_team, make_test_event


def create_state():
    events = [
        make_race_event("Albert Park", week=10),
        make_race_event("Interlagos", week=13),
        make_test_event("Barcelona Test", week=5),
    ]
    return make_state(
        year=1998,
        teams=[make_team(id=1, name="Warrick", country="United Kingdom", workforce=250, driver1_id=1, driver2_id=2)],
        drivers=[
            make_driver(id=1, name="John Newhouse", age=27, country="Canada", team_id=1),
            make_driver(id=2, name="Henrik Friedrich", age=31, country="Germany", team_id=1),
        ],
        calendar=make_calendar(events=events, current_week=10),
        circuits=[make_circuit(name="Albert Park")],
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
