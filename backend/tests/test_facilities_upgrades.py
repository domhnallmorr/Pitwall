from app.core.facilities_upgrades import FacilitiesUpgradeManager
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
        teams=[Team(id=1, name="Warrick", country="United Kingdom", driver1_id=1, driver2_id=2, facilities=70)],
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


def test_facilities_upgrade_preview_calculates_cost_and_installments():
    state = create_state()
    manager = FacilitiesUpgradeManager()

    preview = manager.preview(state, points=20, years=2)

    assert preview.current_facilities == 70
    assert preview.projected_facilities == 90
    assert preview.effective_points == 20
    assert preview.total_cost == 10_000_000
    assert preview.total_races == 4
    assert preview.per_race_payment == 2_500_000


def test_start_upgrade_updates_facilities_and_financing_state():
    state = create_state()
    manager = FacilitiesUpgradeManager()

    preview = manager.start_upgrade(state, points=25, years=1)

    assert preview.projected_facilities == 95
    assert state.player_team.facilities == 95
    assert state.finance.facilities_upgrade_active is True
    assert state.finance.facilities_upgrade_total_cost > 0
    assert state.finance.facilities_upgrade_races_paid == 0


def test_charge_for_race_records_installment_and_completes_plan():
    state = create_state()
    manager = FacilitiesUpgradeManager()
    manager.start_upgrade(state, points=20, years=1)  # 2 race installments

    first = manager.charge_for_event(state, state.calendar.current_event)
    assert first is not None
    assert first.applied_cost == 5_000_000
    txs = [t for t in state.finance.transactions if t.category == TransactionCategory.FACILITIES]
    assert len(txs) == 1
    assert txs[0].amount == -5_000_000
    assert state.finance.facilities_upgrade_active is True

    state.calendar.current_week = 13
    second = manager.charge_for_event(state, state.calendar.current_event)
    assert second is not None
    txs = [t for t in state.finance.transactions if t.category == TransactionCategory.FACILITIES]
    assert len(txs) == 2
    assert state.finance.facilities_upgrade_active is False
