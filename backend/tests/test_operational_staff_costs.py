from app.core.operational_staff_costs import OperationalStaffCostManager
from app.models.finance import TransactionCategory
from tests.factories import make_calendar, make_circuit, make_driver, make_race_event, make_state, make_team


def create_state():
    events = [make_race_event("Albert Park", week=10), make_race_event("Interlagos", week=13)]
    return make_state(
        year=1998,
        teams=[
            make_team(
                id=1,
                name="Warrick",
                country="United Kingdom",
                design_staff=63,
                engineering_staff=61,
                mechanics_staff=58,
                workforce=182,
                driver1_id=1,
                driver2_id=2,
            )
        ],
        drivers=[
            make_driver(id=1, name="John Newhouse", age=27, country="Canada", team_id=1),
            make_driver(id=2, name="Henrik Friedrich", age=31, country="Germany", team_id=1),
        ],
        calendar=make_calendar(events=events, current_week=10),
        circuits=[make_circuit(name="Albert Park")],
        player_team_id=1,
    )


def test_calculate_department_race_costs_uses_split_wages():
    state = create_state()
    manager = OperationalStaffCostManager()

    costs = manager.calculate_department_race_costs(state.player_team, races_in_season=17)

    assert costs["design"] == 92_647
    assert costs["engineering"] == 78_941
    assert costs["mechanics"] == 68_235


def test_charge_for_race_adds_department_payroll_transactions():
    state = create_state()
    manager = OperationalStaffCostManager()

    charge_batch = manager.charge_for_event(state, state.calendar.current_event)

    assert charge_batch is not None
    assert charge_batch.total_cost == 2_038_500
    txs = state.finance.transactions
    categories = {t.category for t in txs}
    assert TransactionCategory.DESIGN_STAFF_WAGES in categories
    assert TransactionCategory.ENGINEERING_STAFF_WAGES in categories
    assert TransactionCategory.MECHANICS_STAFF_WAGES in categories
