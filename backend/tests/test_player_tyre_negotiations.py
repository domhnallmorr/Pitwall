from unittest.mock import patch

import pytest

from app.core.management_transfers import TyreSupplierTransferManager
from app.core.player_tyre_negotiations import PlayerTyreNegotiationManager
from app.models.commercial_manager import CommercialManager
from app.models.tyre_supplier import TyreSupplier
from tests.factories import make_calendar, make_circuit, make_race_event, make_state, make_team


def make_tyre_negotiation_state(manager_skill: int = 70, car_speed: int = 72):
    team = make_team(
        id=1,
        name="Schweizer",
        country="Switzerland",
        car_speed=car_speed,
        commercial_staff=48,
        commercial_manager_id=11,
        tyre_supplier_name="Greatday",
        tyre_supplier_deal="partner",
        tyre_supplier_contract_length=1,
    )
    calendar = make_calendar(events=[make_race_event("Albert Park", week=10)], current_week=10)
    return make_state(
        year=1998,
        teams=[team],
        drivers=[],
        commercial_managers=[
            CommercialManager(
                id=11,
                name="Jace Whitman",
                country="United Kingdom",
                age=36,
                skill=manager_skill,
                contract_length=2,
                salary=360_000,
                team_id=1,
            )
        ],
        tyre_suppliers=[
            TyreSupplier(
                id=1,
                name="Greatday",
                country="USA",
                wear=60,
                grip=80,
                resources=88,
                innovation=82,
                reliability=90,
                start_year=0,
            ),
            TyreSupplier(
                id=2,
                name="Spanrock",
                country="Japan",
                wear=80,
                grip=70,
                resources=86,
                innovation=91,
                reliability=84,
                start_year=0,
            ),
            TyreSupplier(
                id=3,
                name="Avonbridge",
                country="United Kingdom",
                wear=58,
                grip=63,
                resources=52,
                innovation=49,
                reliability=55,
                start_year=0,
            ),
        ],
        calendar=calendar,
        circuits=[make_circuit(name="Albert Park")],
        player_team_id=1,
    )


def test_tyre_negotiation_market_excludes_current_supplier_and_marks_targetable():
    state = make_tyre_negotiation_state()

    payload = PlayerTyreNegotiationManager().get_market_payload(state)

    assert payload["blocked_reason"] is None
    assert payload["current_supplier_name"] == "Greatday"
    assert [supplier["name"] for supplier in payload["suppliers"]] == ["Spanrock", "Avonbridge"]
    assert all(supplier["targetable"] for supplier in payload["suppliers"])
    assert payload["commercial_manager"] == {"name": "Jace Whitman", "skill": 70}


def test_tyre_negotiations_block_long_current_contract_and_existing_announced_deal():
    state = make_tyre_negotiation_state()
    state.player_team.tyre_supplier_contract_length = 2

    payload = PlayerTyreNegotiationManager().get_market_payload(state)
    assert "2 or more years" in payload["blocked_reason"]
    assert not any(supplier["targetable"] for supplier in payload["suppliers"])

    state.player_team.tyre_supplier_contract_length = 1
    state.announced_ai_tyre_supplier_signings = [{"team_id": state.player_team.id, "status": "announced"}]
    payload = PlayerTyreNegotiationManager().get_market_payload(state)
    assert "already been agreed" in payload["blocked_reason"]


def test_starting_and_updating_tyre_negotiation_staff_validates_bounds():
    state = make_tyre_negotiation_state()
    manager = PlayerTyreNegotiationManager()

    negotiation = manager.start_negotiation(state, supplier_id=2)

    assert negotiation["supplier_name"] == "Spanrock"
    assert negotiation["assigned_staff"] == 12
    assert negotiation["total_boxes"] >= 3
    assert state.player_tyre_negotiation is not None

    repeat = manager.start_negotiation(state, supplier_id=2)
    assert repeat["supplier_id"] == 2
    with pytest.raises(ValueError, match="Only one tyre supplier negotiation"):
        manager.start_negotiation(state, supplier_id=3)
    with pytest.raises(ValueError, match="between 0 and 48"):
        manager.update_assigned_staff(state, assigned_staff=49)

    updated = manager.update_assigned_staff(state, assigned_staff=24)
    assert updated["assigned_staff"] == 24
    assert state.player_tyre_negotiation["assigned_staff"] == 24


@patch("app.core.player_tyre_negotiations.random.uniform", return_value=0.0)
def test_tyre_negotiation_progress_uses_manager_skill_and_unlocks_email(mock_uniform):
    low_state = make_tyre_negotiation_state(manager_skill=35)
    high_state = make_tyre_negotiation_state(manager_skill=90)
    manager = PlayerTyreNegotiationManager()

    manager.start_negotiation(low_state, supplier_id=2)
    high_negotiation = manager.start_negotiation(high_state, supplier_id=2)
    manager.update_assigned_staff(low_state, assigned_staff=24)
    manager.update_assigned_staff(high_state, assigned_staff=24)
    high_state.player_tyre_negotiation["progress"] = float(high_negotiation["customer_threshold"] - 1)
    high_state.player_tyre_negotiation["progress_boxes"] = high_negotiation["customer_threshold"] - 1

    low_result = manager.progress_after_race(low_state)
    high_result = manager.progress_after_race(high_state)

    assert low_result is not None
    assert high_result is not None
    assert high_result["progress"] > low_result["progress"]
    assert "customer" in high_result["unlocked_tiers"]
    assert any(email.subject.startswith("Tyre Negotiation Progress: Spanrock") for email in high_state.emails)


def test_tyre_negotiation_hospitality_adds_progress_and_finance_charge():
    state = make_tyre_negotiation_state()
    manager = PlayerTyreNegotiationManager()
    manager.start_negotiation(state, supplier_id=2)

    payload = manager.book_hospitality(state)
    result = manager.apply_hospitality_bonus_after_race(state)

    assert payload["hospitality"]["booked"] is True
    assert result is not None
    assert result["progress"] == 1.0
    assert state.pending_hospitality_event is None
    assert state.finance.transactions[-1].amount == -100_000
    assert state.finance.transactions[-1].description == "Hospitality for Spanrock at Albert Park"


def test_signing_negotiated_tyre_deal_creates_announced_signing_and_applies_next_season():
    state = make_tyre_negotiation_state()
    manager = PlayerTyreNegotiationManager()
    negotiation = manager.start_negotiation(state, supplier_id=2)
    state.player_tyre_negotiation["progress"] = float(negotiation["customer_threshold"])
    state.player_tyre_negotiation["progress_boxes"] = negotiation["customer_threshold"]

    signing = manager.sign_deal(state, "customer")

    assert signing["supplier_name"] == "Spanrock"
    assert signing["deal_type"] == "customer"
    assert signing["yearly_cost"] == PlayerTyreNegotiationManager.CUSTOMER_COST
    assert state.player_tyre_negotiation is None
    assert state.announced_ai_tyre_supplier_signings == [signing]

    TyreSupplierTransferManager().apply_new_season_transfers(state, announced_year=state.year)
    assert state.player_team.tyre_supplier_name == "Spanrock"
    assert state.player_team.tyre_supplier_deal == "customer"
    assert state.player_team.tyre_supplier_contract_length == negotiation["contract_length"]


def test_tyre_signing_rejects_invalid_or_locked_tiers():
    state = make_tyre_negotiation_state()
    manager = PlayerTyreNegotiationManager()
    manager.start_negotiation(state, supplier_id=3)

    with pytest.raises(ValueError, match="must be customer, partner, or works"):
        manager.sign_deal(state, "premium")
    with pytest.raises(ValueError, match="has not been unlocked"):
        manager.sign_deal(state, "customer")
