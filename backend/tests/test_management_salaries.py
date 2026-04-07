from app.core.management_salaries import ManagementSalaryManager
from app.models.calendar import Calendar, Event, EventType
from app.models.commercial_manager import CommercialManager
from app.models.circuit import Circuit
from app.models.finance import TransactionCategory
from app.models.state import GameState
from app.models.team import Team
from app.models.technical_director import TechnicalDirector


def test_management_salary_manager_charges_both_roles_per_race():
    events = [Event(name=f"Race {i}", week=i, type=EventType.RACE) for i in range(1, 17)]
    events[9] = Event(name="Albert Park", week=10, type=EventType.RACE)
    state = GameState(
        year=1998,
        teams=[Team(id=1, name="Warrick", country="United Kingdom")],
        drivers=[],
        technical_directors=[
            TechnicalDirector(id=21, name="Peter Heed", country="United Kingdom", age=52, skill=75, salary=4_800_000, team_id=1),
        ],
        commercial_managers=[
            CommercialManager(id=11, name="Jace Whitman", country="United Kingdom", age=29, skill=70, salary=360_000, team_id=1),
        ],
        calendar=Calendar(events=events, current_week=10),
        circuits=[
            Circuit(
                id=1,
                name="Albert Park",
                country="Australia",
                location="Melbourne",
                laps=58,
                base_laptime_ms=84000,
                length_km=5.303,
                overtaking_delta=1200,
                power_factor=6,
            )
        ],
        player_team_id=1,
    )

    charges = ManagementSalaryManager().charge_for_event(state, state.calendar.current_event)

    assert len(charges) == 2
    totals = {charge.role_name: charge.applied_cost for charge in charges}
    assert totals["Technical Director"] == 300_000
    assert totals["Commercial Manager"] == 22_500

    txs = [t for t in state.finance.transactions if t.category == TransactionCategory.MANAGEMENT_SALARIES]
    assert len(txs) == 2
    assert sum(-t.amount for t in txs) == 322_500
