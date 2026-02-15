from app.core.prize_money import PrizeMoneyManager
from app.models.state import GameState
from app.models.calendar import Calendar, Event, EventType
from app.models.driver import Driver
from app.models.team import Team
from app.models.finance import Finance, TransactionCategory


def create_prize_state() -> GameState:
    teams = [
        Team(id=1, name="Team A", country="UK", driver1_id=1, driver2_id=2, points=10),
        Team(id=2, name="Team B", country="IT", driver1_id=3, driver2_id=4, points=5),
    ]
    drivers = [
        Driver(id=1, name="D1", age=30, country="UK", team_id=1),
        Driver(id=2, name="D2", age=31, country="UK", team_id=1),
        Driver(id=3, name="D3", age=27, country="IT", team_id=2),
        Driver(id=4, name="D4", age=28, country="IT", team_id=2),
    ]
    events = [
        Event(name="R1", week=2, type=EventType.RACE),
        Event(name="R2", week=4, type=EventType.RACE),
        Event(name="R3", week=6, type=EventType.RACE),
    ]
    return GameState(
        year=1998,
        teams=teams,
        drivers=drivers,
        calendar=Calendar(events=events, current_week=2),
        circuits=[],
        player_team_id=1,
        finance=Finance(balance=0),
    )


def test_race_installments_put_remainder_in_first_payment():
    state = create_prize_state()
    manager = PrizeMoneyManager()
    state.finance.prize_money_entitlement = 10
    state.finance.prize_money_total_races = 3

    p1 = manager.process_race_payout(state)
    p2 = manager.process_race_payout(state)
    p3 = manager.process_race_payout(state)

    assert p1["installment"] == 4
    assert p2["installment"] == 3
    assert p3["installment"] == 3
    assert state.finance.prize_money_paid == 10
    assert state.finance.balance == 10

    prize_tx = [t for t in state.finance.transactions if t.category == TransactionCategory.PRIZE_MONEY]
    assert len(prize_tx) == 3


def test_initial_entitlement_uses_roster_order():
    state = create_prize_state()
    manager = PrizeMoneyManager()

    info = manager.assign_initial_entitlement_from_roster_order(state)

    assert info["position"] == 1
    assert info["entitlement"] == 33_000_000
    assert state.finance.prize_money_entitlement == 33_000_000
    assert state.finance.prize_money_races_paid == 0
