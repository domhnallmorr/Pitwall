from app.core.sponsorships import SponsorshipManager
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
                title_sponsor_name="Windale",
                title_sponsor_yearly=32_500_000,
                other_sponsorship_yearly=9_500_000,
                driver1_id=1,
                driver2_id=2,
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


def test_calculate_race_installment_from_yearly_value():
    manager = SponsorshipManager()
    assert manager.calculate_race_installment(32_500_000, 16) == 2_031_250


def test_apply_for_event_posts_sponsorship_income_transaction():
    state = create_state()
    manager = SponsorshipManager()

    charge = manager.apply_for_event(state, state.calendar.current_event)

    assert charge is not None
    assert charge.title_sponsor_name == "Windale"
    txs = [t for t in state.finance.transactions if t.category == TransactionCategory.SPONSORSHIP]
    assert len(txs) == 2
    assert all(t.amount > 0 for t in txs)
