import pytest
from app.core.engine import GameEngine
from app.models.state import GameState
from app.models.calendar import Calendar, Event, EventType
from app.models.team import Team
from app.models.driver import Driver
from app.models.circuit import Circuit
from app.models.finance import TransactionCategory

def create_mock_state(week=1):
    # Include an event at week 52 so season doesn't end prematurely
    dummy_event = Event(name="Season Finale", week=52, type=EventType.RACE)
    calendar = Calendar(events=[dummy_event], current_week=week)
    return GameState(year=1998, teams=[], drivers=[], calendar=calendar, circuits=[])

def test_advance_week_increments_week():
    state = create_mock_state(week=1)
    engine = GameEngine()
    
    summary = engine.advance_week(state)
    
    assert state.calendar.current_week == 2
    assert summary["week"] == 2
    assert "Week 2 1998" in summary["new_date_display"]

def test_advance_week_multiple_times():
    state = create_mock_state(week=1)
    engine = GameEngine()
    
    engine.advance_week(state) # 2
    engine.advance_week(state) # 3
    summary = engine.advance_week(state) # 4
    
    assert state.calendar.current_week == 4
    assert summary["week"] == 4
    assert state.calendar.current_week == 4
    assert summary["week"] == 4

def test_advance_week_identifies_race():
    from app.models.calendar import Event, EventType
    
    # Setup: Event in Week 2
    evt = Event(name="Test GP", week=2, type=EventType.RACE)
    calendar = Calendar(events=[evt], current_week=1)
    state = GameState(year=1998, teams=[], drivers=[], calendar=calendar, circuits=[])
    
    engine = GameEngine()
    summary = engine.advance_week(state)
    
    assert summary["week"] == 2
    assert summary["event_active"] is True
    assert summary["button_text"] == "GO TO RACE"
    assert summary["event_active"] is True
    assert summary["button_text"] == "GO TO RACE"

def test_skip_event_updates_button():
    from app.models.calendar import Event, EventType
    
    # Setup: Event in Week 1
    evt = Event(name="Test GP", week=1, type=EventType.TEST)
    calendar = Calendar(events=[evt], current_week=1)
    state = GameState(year=1998, teams=[], drivers=[], calendar=calendar, circuits=[])
    
    engine = GameEngine()
    
    # Verify initial state
    summary1 = engine.get_week_summary(state)
    assert summary1["button_text"] == "GO TO TEST"
    
    # Skip Event
    summary2 = engine.handle_event_action(state, "skip")
    
    # Verify updated state: Week still 1, but button is ADVANCE
    assert summary2["week"] == 1
    assert summary2["button_text"] == "ADVANCE"
    assert len(state.events_processed) == 1


def test_advance_week_publishes_queued_emails():
    state = create_mock_state(week=1)
    state.queue_email(
        sender="Competition Office",
        subject="Scheduled Notice",
        body="Delivered on week 2",
        week=2,
        year=1998
    )
    engine = GameEngine()

    engine.advance_week(state)

    delivered = [e for e in state.emails if e.subject == "Scheduled Notice"]
    assert len(delivered) == 1
    assert delivered[0].week == 2
    assert delivered[0].year == 1998


def create_test_event_state():
    evt = Event(name="Circuit de Barcelona-Catalunya", week=1, type=EventType.TEST)
    calendar = Calendar(events=[evt], current_week=1)
    team = Team(id=1, name="Warrick", country="United Kingdom", driver1_id=1, car_speed=80)
    driver = Driver(id=1, name="John Newhouse", age=27, country="Canada", team_id=1, speed=84)
    circuit = Circuit(
        id=1,
        name="Circuit de Barcelona-Catalunya",
        country="Spain",
        location="Barcelona",
        laps=66,
        base_laptime_ms=75000,
        length_km=4.728,
        overtaking_delta=1800,
        power_factor=5,
    )
    return GameState(
        year=1998,
        teams=[team],
        drivers=[driver],
        calendar=calendar,
        circuits=[circuit],
        player_team_id=1,
    )


def test_skip_test_event_does_not_charge_transport():
    state = create_test_event_state()
    engine = GameEngine()

    engine.handle_event_action(state, "skip")

    transport_txs = [t for t in state.finance.transactions if t.category == TransactionCategory.TRANSPORT]
    assert len(transport_txs) == 0


def test_attend_test_event_charges_transport_and_sends_email():
    state = create_test_event_state()
    engine = GameEngine()

    engine.handle_event_action(state, "attend")

    transport_txs = [t for t in state.finance.transactions if t.category == TransactionCategory.TRANSPORT]
    assert len(transport_txs) == 1
    assert transport_txs[0].amount < 0
    transport_emails = [e for e in state.emails if e.subject.startswith("Transport Confirmed:")]
    assert len(transport_emails) == 1
