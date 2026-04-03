from unittest.mock import patch

from app.core.engine import GameEngine
from app.core.grid import GridManager
from app.core.management_transfers import (
    CommercialManagerTransferManager,
    TechnicalDirectorTransferManager,
    TitleSponsorTransferManager,
    TyreSupplierTransferManager,
)
from app.core.transfers import TransferManager
from app.models.calendar import Calendar, Event, EventType
from app.models.commercial_manager import CommercialManager
from app.models.driver import Driver
from app.models.state import GameState
from app.models.team import Team
from app.models.technical_director import TechnicalDirector
from app.models.title_sponsor import TitleSponsor
from app.models.tyre_supplier import TyreSupplier


def create_transfer_state() -> GameState:
    teams = [
        Team(
            id=1,
            name="Player Team",
            country="UK",
            driver1_id=1,
            driver2_id=2,
            commercial_manager_id=1,
            title_sponsor_name="Windale",
            title_sponsor_yearly=70,
            title_sponsor_contract_length=2,
            tyre_supplier_name="Greatday",
            tyre_supplier_deal="partner",
            tyre_supplier_contract_length=1,
        ),
        Team(
            id=2,
            name="AI Team",
            country="IT",
            driver1_id=3,
            driver2_id=4,
            commercial_manager_id=2,
            title_sponsor_name="Bright Shot",
            title_sponsor_yearly=85,
            title_sponsor_contract_length=1,
            tyre_supplier_name="Greatday",
            tyre_supplier_deal="customer",
            tyre_supplier_contract_length=1,
        ),
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
    technical_directors = [
        TechnicalDirector(id=1, name="Player TD", country="UK", age=46, skill=78, contract_length=2, salary=100, team_id=1),
        TechnicalDirector(id=2, name="AI Expiring TD", country="IT", age=49, skill=80, contract_length=1, salary=100, team_id=2),
        TechnicalDirector(id=3, name="Free TD", country="DE", age=43, skill=76, contract_length=0, salary=0, team_id=None),
    ]
    teams[0].technical_director_id = 1
    teams[1].technical_director_id = 2
    return GameState(
        year=1998,
        teams=teams,
        drivers=drivers,
        technical_directors=technical_directors,
        commercial_managers=commercial_managers,
        title_sponsors=[
            TitleSponsor(id=1, name="Windale", wealth=70, start_year=0),
            TitleSponsor(id=2, name="Bright Shot", wealth=85, start_year=0),
            TitleSponsor(id=3, name="Purple", wealth=50, start_year=1999),
        ],
        tyre_suppliers=[
            TyreSupplier(id=1, name="Greatday", country="USA", wear=60, grip=80, start_year=0),
            TyreSupplier(id=2, name="Spanrock", country="Japan", wear=80, grip=70, start_year=0),
        ],
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


@patch("app.core.management_transfer_markets.commercial_manager.random.shuffle", side_effect=lambda x: None)
@patch("app.core.management_transfer_markets.commercial_manager.random.randint", return_value=6)
@patch("app.core.management_transfer_markets.commercial_manager.random.choice", side_effect=lambda choices: choices[0])
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


@patch("app.core.management_transfer_markets.technical_director.random.shuffle", side_effect=lambda x: None)
@patch("app.core.management_transfer_markets.technical_director.random.randint", return_value=6)
@patch("app.core.management_transfer_markets.technical_director.random.choice", side_effect=lambda choices: choices[0])
def test_recompute_ai_td_signings_plans_only_ai_vacancies(mock_choice, mock_randint, mock_shuffle):
    state = create_transfer_state()

    planned = TechnicalDirectorTransferManager().recompute_ai_signings(state)

    assert len(planned) == 1
    assert planned[0]["team_id"] == 2
    assert planned[0]["seat"] == "technical_director_id"
    assert planned[0]["director_id"] in {2, 3}
    assert planned[0]["status"] == "planned"
    assert planned[0]["announce_week"] == 6


def test_publish_due_td_announcements_moves_planned_to_announced_and_emails():
    state = create_transfer_state()
    state.calendar.current_week = 3
    state.planned_ai_td_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "technical_director_id",
            "seat_label": "Technical Director",
            "director_id": 3,
            "director_name": "Free TD",
            "announce_week": 3,
            "announce_year": 1998,
            "status": "planned",
        }
    ]

    published = TechnicalDirectorTransferManager().publish_due_announcements(state)

    assert len(published) == 1
    assert len(state.planned_ai_td_signings) == 0
    assert len(state.announced_ai_td_signings) == 1
    assert state.announced_ai_td_signings[0]["status"] == "announced"
    assert any(e.subject == "Technical Director Signing Confirmed: Free TD to AI Team" for e in state.emails)


def test_engine_advance_week_publishes_due_td_transfer_announcements():
    state = create_transfer_state()
    state.planned_ai_td_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "technical_director_id",
            "seat_label": "Technical Director",
            "director_id": 3,
            "director_name": "Free TD",
            "announce_week": 2,
            "announce_year": 1998,
            "status": "planned",
        }
    ]

    GameEngine().advance_week(state)

    assert len(state.announced_ai_td_signings) == 1
    assert len(state.planned_ai_td_signings) == 0
    assert any(e.subject == "Technical Director Signing Confirmed: Free TD to AI Team" for e in state.emails)


def test_grid_next_year_projection_uses_announced_td_signings():
    state = create_transfer_state()
    state.announced_ai_td_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "technical_director_id",
            "seat_label": "Technical Director",
            "director_id": 3,
            "director_name": "Free TD",
            "announce_week": 2,
            "announce_year": 1998,
            "status": "announced",
        }
    ]

    df = GridManager().get_grid_dataframe(state, year=1999)
    row = df[df["Team"] == "AI Team"].iloc[0]
    assert row["TechnicalDirector"] == "Free TD"
    assert row["TechnicalDirectorCountry"] == "DE"


def test_apply_new_season_td_transfers_moves_announced_director_and_sets_contract():
    state = create_transfer_state()
    state.announced_ai_td_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "technical_director_id",
            "seat_label": "Technical Director",
            "director_id": 3,
            "director_name": "Free TD",
            "announce_week": 20,
            "announce_year": 1998,
            "status": "announced",
        }
    ]

    outcome = TechnicalDirectorTransferManager().apply_new_season_transfers(state, announced_year=1998)

    ai_team = next(t for t in state.teams if t.id == 2)
    incoming = next(d for d in state.technical_directors if d.id == 3)
    outgoing = next(d for d in state.technical_directors if d.id == 2)
    assert ai_team.technical_director_id == 3
    assert incoming.team_id == 2
    assert incoming.contract_length == 2
    assert outgoing.team_id is None
    assert any(s["director_id"] == 3 for s in outcome["applied_signings"])


@patch("app.core.management_transfer_markets.title_sponsor.random.shuffle", side_effect=lambda x: None)
@patch("app.core.management_transfer_markets.title_sponsor.random.randint", return_value=6)
@patch("app.core.management_transfer_markets.title_sponsor.random.choice", side_effect=lambda choices: choices[0])
def test_recompute_ai_title_sponsor_signings_plans_only_ai_vacancies(mock_choice, mock_randint, mock_shuffle):
    state = create_transfer_state()

    planned = TitleSponsorTransferManager().recompute_ai_signings(state)

    assert len(planned) == 1
    assert planned[0]["team_id"] == 2
    assert planned[0]["seat"] == "title_sponsor_name"
    assert planned[0]["sponsor_id"] in {2, 3}
    assert planned[0]["status"] == "planned"
    assert planned[0]["announce_week"] == 6


def test_publish_due_title_sponsor_announcements_moves_planned_to_announced_and_emails():
    state = create_transfer_state()
    state.calendar.current_week = 3
    state.planned_ai_title_sponsor_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "title_sponsor_name",
            "seat_label": "Title Sponsor",
            "sponsor_id": 3,
            "sponsor_name": "Purple",
            "sponsor_wealth": 50,
            "announce_week": 3,
            "announce_year": 1998,
            "status": "planned",
        }
    ]

    published = TitleSponsorTransferManager().publish_due_announcements(state)

    assert len(published) == 1
    assert len(state.planned_ai_title_sponsor_signings) == 0
    assert len(state.announced_ai_title_sponsor_signings) == 1
    assert state.announced_ai_title_sponsor_signings[0]["status"] == "announced"
    assert any(e.subject == "Title Sponsor Signing Confirmed: Purple to AI Team" for e in state.emails)


def test_engine_advance_week_publishes_due_title_sponsor_announcements():
    state = create_transfer_state()
    state.planned_ai_title_sponsor_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "title_sponsor_name",
            "seat_label": "Title Sponsor",
            "sponsor_id": 3,
            "sponsor_name": "Purple",
            "sponsor_wealth": 50,
            "announce_week": 2,
            "announce_year": 1998,
            "status": "planned",
        }
    ]

    GameEngine().advance_week(state)

    assert len(state.announced_ai_title_sponsor_signings) == 1
    assert len(state.planned_ai_title_sponsor_signings) == 0
    assert any(e.subject == "Title Sponsor Signing Confirmed: Purple to AI Team" for e in state.emails)


def test_grid_next_year_projection_uses_announced_title_sponsor_signings():
    state = create_transfer_state()
    state.announced_ai_title_sponsor_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "title_sponsor_name",
            "seat_label": "Title Sponsor",
            "sponsor_id": 3,
            "sponsor_name": "Purple",
            "sponsor_wealth": 50,
            "announce_week": 2,
            "announce_year": 1998,
            "status": "announced",
        }
    ]

    df = GridManager().get_grid_dataframe(state, year=1999)
    row = df[df["Team"] == "AI Team"].iloc[0]
    assert row["TitleSponsor"] == "Purple"
    assert row["TitleSponsorContractLength"] == 2


def test_apply_new_season_title_sponsor_transfers_moves_announced_sponsor_and_sets_contract():
    state = create_transfer_state()
    state.announced_ai_title_sponsor_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "title_sponsor_name",
            "seat_label": "Title Sponsor",
            "sponsor_id": 3,
            "sponsor_name": "Purple",
            "sponsor_wealth": 50,
            "announce_week": 20,
            "announce_year": 1998,
            "status": "announced",
        }
    ]

    outcome = TitleSponsorTransferManager().apply_new_season_transfers(state, announced_year=1998)

    ai_team = next(t for t in state.teams if t.id == 2)
    player_team = next(t for t in state.teams if t.id == 1)
    assert ai_team.title_sponsor_name == "Purple"
    assert ai_team.title_sponsor_yearly == 50
    assert ai_team.title_sponsor_contract_length == 2
    assert player_team.title_sponsor_name == "Windale"
    assert player_team.title_sponsor_contract_length == 1
    assert any(s["sponsor_id"] == 3 for s in outcome["applied_signings"])


@patch("app.core.management_transfer_markets.tyre_supplier.random.shuffle", side_effect=lambda x: None)
@patch("app.core.management_transfer_markets.tyre_supplier.random.randint", return_value=6)
@patch("app.core.management_transfer_markets.tyre_supplier.random.choices", side_effect=lambda choices, weights, k: [choices[0]])
@patch("app.core.management_transfer_markets.tyre_supplier.random.choice", side_effect=lambda choices: choices[-1])
def test_recompute_ai_tyre_supplier_signings_plans_only_ai_vacancies(mock_choice, mock_choices, mock_randint, mock_shuffle):
    state = create_transfer_state()

    planned = TyreSupplierTransferManager().recompute_ai_signings(state)

    assert len(planned) == 1
    assert planned[0]["team_id"] == 2
    assert planned[0]["seat"] == "tyre_supplier_name"
    assert planned[0]["supplier_id"] == 2
    assert planned[0]["deal_type"] == "works"
    assert planned[0]["yearly_cost"] == 0
    assert planned[0]["status"] == "planned"
    assert planned[0]["announce_week"] == 6


def test_publish_due_tyre_supplier_announcements_moves_planned_to_announced_and_emails():
    state = create_transfer_state()
    state.calendar.current_week = 3
    state.planned_ai_tyre_supplier_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "tyre_supplier_name",
            "seat_label": "Tyre Supplier",
            "supplier_id": 2,
            "supplier_name": "Spanrock",
            "deal_type": "partner",
            "yearly_cost": 0,
            "announce_week": 3,
            "announce_year": 1998,
            "status": "planned",
        }
    ]

    published = TyreSupplierTransferManager().publish_due_announcements(state)

    assert len(published) == 1
    assert len(state.planned_ai_tyre_supplier_signings) == 0
    assert len(state.announced_ai_tyre_supplier_signings) == 1
    assert state.announced_ai_tyre_supplier_signings[0]["status"] == "announced"
    assert any(e.subject == "Tyre Supplier Signing Confirmed: Spanrock to AI Team" for e in state.emails)


def test_engine_advance_week_publishes_due_tyre_supplier_announcements():
    state = create_transfer_state()
    state.planned_ai_tyre_supplier_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "tyre_supplier_name",
            "seat_label": "Tyre Supplier",
            "supplier_id": 2,
            "supplier_name": "Spanrock",
            "deal_type": "partner",
            "yearly_cost": 0,
            "announce_week": 2,
            "announce_year": 1998,
            "status": "planned",
        }
    ]

    GameEngine().advance_week(state)

    assert len(state.announced_ai_tyre_supplier_signings) == 1
    assert len(state.planned_ai_tyre_supplier_signings) == 0
    assert any(e.subject == "Tyre Supplier Signing Confirmed: Spanrock to AI Team" for e in state.emails)


def test_grid_next_year_projection_uses_announced_tyre_supplier_signings():
    state = create_transfer_state()
    state.announced_ai_tyre_supplier_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "tyre_supplier_name",
            "seat_label": "Tyre Supplier",
            "supplier_id": 2,
            "supplier_name": "Spanrock",
            "deal_type": "partner",
            "yearly_cost": 0,
            "announce_week": 2,
            "announce_year": 1998,
            "status": "announced",
        }
    ]

    df = GridManager().get_grid_dataframe(state, year=1999)
    row = df[df["Team"] == "AI Team"].iloc[0]
    assert row["TyreSupplier"] == "Spanrock"
    assert row["TyreSupplierDeal"] == "partner"
    assert row["TyreSupplierContractLength"] == 2


def test_apply_new_season_tyre_supplier_transfers_moves_announced_supplier_and_sets_contract():
    state = create_transfer_state()
    state.announced_ai_tyre_supplier_signings = [
        {
            "team_id": 2,
            "team_name": "AI Team",
            "seat": "tyre_supplier_name",
            "seat_label": "Tyre Supplier",
            "supplier_id": 2,
            "supplier_name": "Spanrock",
            "deal_type": "partner",
            "yearly_cost": 0,
            "announce_week": 20,
            "announce_year": 1998,
            "status": "announced",
        }
    ]

    outcome = TyreSupplierTransferManager().apply_new_season_transfers(state, announced_year=1998)

    ai_team = next(t for t in state.teams if t.id == 2)
    player_team = next(t for t in state.teams if t.id == 1)
    assert ai_team.tyre_supplier_name == "Spanrock"
    assert ai_team.tyre_supplier_deal == "partner"
    assert ai_team.tyre_supplier_yearly_cost == 0
    assert ai_team.tyre_supplier_contract_length == 2
    assert player_team.tyre_supplier_name is None
    assert player_team.tyre_supplier_contract_length == 0
    assert any(s["supplier_id"] == 2 for s in outcome["applied_signings"])


@patch("app.core.management_transfer_markets.title_sponsor.random.choice", side_effect=lambda choices: choices[0])
def test_player_title_sponsor_replacement_updates_announced_and_replans_ai(mock_choice):
    state = create_transfer_state()
    player_team = next(t for t in state.teams if t.id == 1)
    player_team.title_sponsor_contract_length = 1

    signing = TitleSponsorTransferManager().sign_player_replacement(state, outgoing_sponsor_name="Windale")

    assert signing["team_id"] == 1
    assert signing["seat"] == "title_sponsor_name"
    assert signing["status"] == "announced"
    assert len(state.announced_ai_title_sponsor_signings) == 1
    assert any(s["team_id"] == 2 for s in state.planned_ai_title_sponsor_signings)
    assert any(e.subject.startswith("Title Sponsor Signed:") for e in state.emails)


@patch("app.core.management_transfer_markets.tyre_supplier.random.choices", side_effect=lambda choices, weights, k: [choices[1]])
@patch("app.core.management_transfer_markets.tyre_supplier.random.choice", side_effect=lambda choices: choices[0])
def test_player_tyre_supplier_replacement_updates_announced_and_replans_ai(mock_choice, mock_choices):
    state = create_transfer_state()
    player_team = next(t for t in state.teams if t.id == 1)
    player_team.tyre_supplier_contract_length = 1

    signing = TyreSupplierTransferManager().sign_player_replacement(
        state,
        outgoing_supplier_name="Greatday",
        incoming_supplier_id=2,
    )

    assert signing["team_id"] == 1
    assert signing["seat"] == "tyre_supplier_name"
    assert signing["status"] == "announced"
    assert signing["supplier_name"] == "Spanrock"
    assert signing["deal_type"] == "partner"
    assert len(state.announced_ai_tyre_supplier_signings) == 1
    assert any(s["team_id"] == 2 for s in state.planned_ai_tyre_supplier_signings)
    assert any(e.subject.startswith("Tyre Supplier Signed:") for e in state.emails)


def test_player_tyre_supplier_replacement_rejects_supplier_with_two_or_more_years():
    state = create_transfer_state()
    player_team = next(t for t in state.teams if t.id == 1)
    player_team.tyre_supplier_contract_length = 2

    try:
        TyreSupplierTransferManager().sign_player_replacement(state, outgoing_supplier_name="Greatday")
        assert False, "Expected ValueError"
    except ValueError as ve:
        assert "2 or more years" in str(ve)


@patch("app.core.management_transfer_markets.technical_director.random.choice", side_effect=lambda choices: choices[0])
def test_player_td_replacement_signing_updates_announced_and_replans_ai(mock_choice):
    state = create_transfer_state()
    player_director = next(d for d in state.technical_directors if d.id == 1)
    player_director.contract_length = 1

    signing = TechnicalDirectorTransferManager().sign_player_replacement(state, outgoing_director_id=1)

    assert signing["team_id"] == 1
    assert signing["seat"] == "technical_director_id"
    assert signing["status"] == "announced"
    assert len(state.announced_ai_td_signings) == 1
    assert any(s["team_id"] == 2 for s in state.planned_ai_td_signings)
    assert any(e.subject.startswith("Technical Director Signed:") for e in state.emails)


@patch("app.core.management_transfer_markets.technical_director.random.shuffle", side_effect=lambda x: None)
@patch("app.core.management_transfer_markets.technical_director.random.randint", return_value=6)
@patch("app.core.management_transfer_markets.technical_director.random.choice", side_effect=lambda choices: choices[0])
def test_recompute_ai_td_signings_excludes_retired_directors(mock_choice, mock_randint, mock_shuffle):
    state = create_transfer_state()
    retired = next(d for d in state.technical_directors if d.id == 3)
    retired.active = False

    planned = TechnicalDirectorTransferManager().recompute_ai_signings(state)

    assert len(planned) == 1
    assert planned[0]["director_id"] == 2


@patch("app.core.management_transfer_markets.commercial_manager.random.shuffle", side_effect=lambda x: None)
@patch("app.core.management_transfer_markets.commercial_manager.random.randint", return_value=6)
@patch("app.core.management_transfer_markets.commercial_manager.random.choice", side_effect=lambda choices: choices[0])
def test_recompute_ai_cm_signings_excludes_retired_managers(mock_choice, mock_randint, mock_shuffle):
    state = create_transfer_state()
    retired = next(m for m in state.commercial_managers if m.id == 3)
    retired.active = False

    planned = CommercialManagerTransferManager().recompute_ai_signings(state)

    assert len(planned) == 1
    assert planned[0]["manager_id"] == 2
