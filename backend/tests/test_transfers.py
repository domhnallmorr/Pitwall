from unittest.mock import patch

from app.core.engine import GameEngine
from app.core.grid import GridManager
from app.core.management_transfers import CommercialManagerTransferManager
from app.core.transfers import TransferManager
from app.models.calendar import Calendar, Event, EventType
from app.models.commercial_manager import CommercialManager
from app.models.driver import Driver
from app.models.state import GameState
from app.models.team import Team


def create_transfer_state() -> GameState:
    teams = [
        Team(id=1, name="Player Team", country="UK", driver1_id=1, driver2_id=2, commercial_manager_id=1),
        Team(id=2, name="AI Team", country="IT", driver1_id=3, driver2_id=4, commercial_manager_id=2),
    ]
    drivers = [
        Driver(id=1, name="Player Expiring", age=30, country="UK", team_id=1, contract_length=1),
        Driver(id=2, name="Player Secure", age=29, country="UK", team_id=1, contract_length=3),
        Driver(id=3, name="AI Expiring", age=28, country="IT", team_id=2, contract_length=1),
        Driver(id=4, name="AI Secure", age=27, country="IT", team_id=2, contract_length=2),
        Driver(id=5, name="Free Agent", age=24, country="DE", team_id=None, contract_length=0),
    ]
    calendar = Calendar(events=[Event(name="Finale", week=52, type=EventType.RACE)], current_week=1)
    commercial_managers = [
        CommercialManager(id=1, name="Player CM", country="UK", age=40, skill=70, contract_length=2, salary=100, team_id=1),
        CommercialManager(id=2, name="AI Expiring CM", country="IT", age=45, skill=72, contract_length=1, salary=100, team_id=2),
        CommercialManager(id=3, name="Free CM", country="DE", age=38, skill=68, contract_length=0, salary=0, team_id=None),
    ]
    return GameState(
        year=1998,
        teams=teams,
        drivers=drivers,
        commercial_managers=commercial_managers,
        calendar=calendar,
        circuits=[],
        player_team_id=1,
    )


@patch("app.core.transfers.random.shuffle", side_effect=lambda x: None)
@patch("app.core.transfers.random.randint", return_value=6)
@patch("app.core.transfers.random.choice", side_effect=lambda choices: choices[0])
def test_recompute_ai_signings_plans_only_ai_vacancies(mock_choice, mock_randint, mock_shuffle):
    state = create_transfer_state()

    planned = TransferManager().recompute_ai_signings(state)

    assert len(planned) == 1
    assert planned[0]["team_id"] == 2
    assert planned[0]["seat"] == "driver1_id"
    assert planned[0]["status"] == "planned"
    assert planned[0]["announce_week"] == 6


def test_publish_due_announcements_moves_planned_to_announced_and_emails():
    state = create_transfer_state()
    state.calendar.current_week = 3
    state.planned_ai_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "driver1_id",
            "seat_label": "Driver 1",
            "driver_id": 5,
            "driver_name": "Free Agent",
            "announce_week": 3,
            "announce_year": 1998,
            "status": "planned",
        }
    ]

    published = TransferManager().publish_due_announcements(state)

    assert len(published) == 1
    assert len(state.planned_ai_signings) == 0
    assert len(state.announced_ai_signings) == 1
    assert state.announced_ai_signings[0]["status"] == "announced"
    assert any(e.subject == "Transfer Confirmed: Free Agent to AI Team" for e in state.emails)


def test_engine_advance_week_publishes_due_transfer_announcements():
    state = create_transfer_state()
    state.planned_ai_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "driver1_id",
            "seat_label": "Driver 1",
            "driver_id": 5,
            "driver_name": "Free Agent",
            "announce_week": 2,
            "announce_year": 1998,
            "status": "planned",
        }
    ]

    GameEngine().advance_week(state)

    assert len(state.announced_ai_signings) == 1
    assert len(state.planned_ai_signings) == 0
    assert any(e.subject == "Transfer Confirmed: Free Agent to AI Team" for e in state.emails)


def test_grid_next_year_projection_uses_announced_transfer_signings():
    state = create_transfer_state()
    state.announced_ai_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "driver1_id",
            "seat_label": "Driver 1",
            "driver_id": 5,
            "driver_name": "Free Agent",
            "announce_week": 2,
            "announce_year": 1998,
            "status": "announced",
        }
    ]

    df = GridManager().get_grid_dataframe(state, year=1999)
    row = df[df["Team"] == "AI Team"].iloc[0]
    assert row["Driver1"] == "Free Agent"
    assert row["Driver1Country"] == "DE"
    assert row["Driver2"] == "AI Secure"


@patch("app.core.transfers.random.shuffle", side_effect=lambda x: None)
@patch("app.core.transfers.random.choice", side_effect=lambda choices: choices[0])
def test_recompute_ai_signings_announce_after_first_race(mock_choice, mock_shuffle):
    state = create_transfer_state()
    state.calendar.events = [
        Event(name="Preseason Test", week=5, type=EventType.TEST),
        Event(name="Round 1", week=10, type=EventType.RACE),
        Event(name="Round 2", week=12, type=EventType.RACE),
    ]
    state.calendar.current_week = 1

    planned = TransferManager().recompute_ai_signings(state)

    assert len(planned) == 1
    assert planned[0]["announce_week"] >= 11


@patch("app.core.transfers.random.choice", side_effect=lambda choices: choices[0])
def test_player_replacement_signing_updates_announced_and_replans_ai(mock_choice):
    state = create_transfer_state()

    signing = TransferManager().sign_player_replacement(state, outgoing_driver_id=1)

    assert signing["team_id"] == 1
    assert signing["seat"] == "driver1_id"
    assert signing["status"] == "announced"
    assert len(state.announced_ai_signings) == 1
    assert any(s["team_id"] == 2 for s in state.planned_ai_signings)
    assert any(e.subject.startswith("Driver Signed:") for e in state.emails)


def test_player_replacement_rejects_driver_with_two_or_more_years():
    state = create_transfer_state()

    try:
        TransferManager().sign_player_replacement(state, outgoing_driver_id=2)
        assert False, "Expected ValueError"
    except ValueError as ve:
        assert "2 or more years" in str(ve)


def test_apply_new_season_transfers_moves_announced_driver_and_sets_contract():
    state = create_transfer_state()
    state.announced_ai_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "driver1_id",
            "seat_label": "Driver 1",
            "driver_id": 5,
            "driver_name": "Free Agent",
            "announce_week": 20,
            "announce_year": 1998,
            "status": "announced",
        }
    ]

    outcome = TransferManager().apply_new_season_transfers(state, announced_year=1998)

    ai_team = next(t for t in state.teams if t.id == 2)
    free_agent = next(d for d in state.drivers if d.id == 5)
    outgoing = next(d for d in state.drivers if d.id == 3)
    assert ai_team.driver1_id == 5
    assert free_agent.team_id == 2
    assert free_agent.contract_length == 2
    assert outgoing.team_id is None
    assert any(s["driver_id"] == 5 for s in outcome["applied_signings"])


def test_apply_new_season_transfers_expiring_driver_without_deal_becomes_free_agent():
    state = create_transfer_state()
    state.announced_ai_signings = []

    outcome = TransferManager().apply_new_season_transfers(state, announced_year=1998)

    ai_team = next(t for t in state.teams if t.id == 2)
    expiring = next(d for d in state.drivers if d.id == 3)
    secure = next(d for d in state.drivers if d.id == 4)
    assert ai_team.driver1_id is None
    assert expiring.team_id is None
    assert expiring.contract_length == 0
    assert secure.team_id == 2
    assert secure.contract_length == 1
    assert any(l["driver_id"] == 3 for l in outcome["expiring_leavers"])


@patch("app.core.management_transfers.random.shuffle", side_effect=lambda x: None)
@patch("app.core.management_transfers.random.randint", return_value=6)
@patch("app.core.management_transfers.random.choice", side_effect=lambda choices: choices[0])
def test_recompute_ai_cm_signings_plans_only_ai_vacancies(mock_choice, mock_randint, mock_shuffle):
    state = create_transfer_state()

    planned = CommercialManagerTransferManager().recompute_ai_signings(state)

    assert len(planned) == 1
    assert planned[0]["team_id"] == 2
    assert planned[0]["seat"] == "commercial_manager_id"
    assert planned[0]["manager_id"] in {2, 3}
    assert planned[0]["status"] == "planned"
    assert planned[0]["announce_week"] == 6


def test_publish_due_cm_announcements_moves_planned_to_announced_and_emails():
    state = create_transfer_state()
    state.calendar.current_week = 3
    state.planned_ai_cm_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "commercial_manager_id",
            "seat_label": "Commercial Manager",
            "manager_id": 3,
            "manager_name": "Free CM",
            "announce_week": 3,
            "announce_year": 1998,
            "status": "planned",
        }
    ]

    published = CommercialManagerTransferManager().publish_due_announcements(state)

    assert len(published) == 1
    assert len(state.planned_ai_cm_signings) == 0
    assert len(state.announced_ai_cm_signings) == 1
    assert state.announced_ai_cm_signings[0]["status"] == "announced"
    assert any(e.subject == "Management Signing Confirmed: Free CM to AI Team" for e in state.emails)


def test_engine_advance_week_publishes_due_cm_transfer_announcements():
    state = create_transfer_state()
    state.planned_ai_cm_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "commercial_manager_id",
            "seat_label": "Commercial Manager",
            "manager_id": 3,
            "manager_name": "Free CM",
            "announce_week": 2,
            "announce_year": 1998,
            "status": "planned",
        }
    ]

    GameEngine().advance_week(state)

    assert len(state.announced_ai_cm_signings) == 1
    assert len(state.planned_ai_cm_signings) == 0
    assert any(e.subject == "Management Signing Confirmed: Free CM to AI Team" for e in state.emails)


def test_grid_next_year_projection_uses_announced_cm_signings():
    state = create_transfer_state()
    state.announced_ai_cm_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "commercial_manager_id",
            "seat_label": "Commercial Manager",
            "manager_id": 3,
            "manager_name": "Free CM",
            "announce_week": 2,
            "announce_year": 1998,
            "status": "announced",
        }
    ]

    df = GridManager().get_grid_dataframe(state, year=1999)
    row = df[df["Team"] == "AI Team"].iloc[0]
    assert row["CommercialManager"] == "Free CM"


def test_apply_new_season_cm_transfers_moves_announced_manager_and_sets_contract():
    state = create_transfer_state()
    state.announced_ai_cm_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "commercial_manager_id",
            "seat_label": "Commercial Manager",
            "manager_id": 3,
            "manager_name": "Free CM",
            "announce_week": 20,
            "announce_year": 1998,
            "status": "announced",
        }
    ]

    outcome = CommercialManagerTransferManager().apply_new_season_transfers(state, announced_year=1998)

    ai_team = next(t for t in state.teams if t.id == 2)
    incoming = next(m for m in state.commercial_managers if m.id == 3)
    outgoing = next(m for m in state.commercial_managers if m.id == 2)
    assert ai_team.commercial_manager_id == 3
    assert incoming.team_id == 2
    assert incoming.contract_length == 2
    assert outgoing.team_id is None
    assert any(s["manager_id"] == 3 for s in outcome["applied_signings"])
