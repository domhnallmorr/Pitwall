from unittest.mock import patch

from app.core.management_transfers import EngineSupplierTransferManager
from app.core.player_engine_negotiations import PlayerEngineNegotiationManager
from app.models.commercial_manager import CommercialManager
from app.models.engine_supplier import EngineSupplier
from tests.factories import make_calendar, make_circuit, make_race_event, make_state, make_team


def make_negotiation_state(manager_skill: int = 70):
    team = make_team(
        id=1,
        name="Schweizer",
        country="Switzerland",
        car_speed=72,
        commercial_staff=49,
        commercial_manager_id=11,
        engine_supplier_name="Mechatron",
        engine_supplier_contract_length=1,
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
        engine_suppliers=[
            EngineSupplier(id=1, name="Ferano", country="Italy", resources=90, power=72, start_year=0),
            EngineSupplier(id=2, name="Mechatron", country="France", resources=55, power=60, start_year=0),
            EngineSupplier(id=3, name="Frost", country="USA", resources=65, power=38, start_year=0),
            EngineSupplier(id=4, name="Marcado", country="Germany", resources=92, power=80, start_year=0),
        ],
        calendar=calendar,
        circuits=[make_circuit(name="Albert Park")],
        player_team_id=1,
    )


def test_engine_negotiation_market_excludes_current_and_self_built_suppliers():
    state = make_negotiation_state()

    payload = PlayerEngineNegotiationManager().get_market_payload(state)

    assert payload["blocked_reason"] is None
    assert payload["current_supplier_name"] == "Mechatron"
    supplier_names = [supplier["name"] for supplier in payload["suppliers"]]
    assert "Ferano" not in supplier_names
    assert "Mechatron" not in supplier_names
    assert supplier_names == ["Frost", "Marcado"]


def test_start_and_update_engine_negotiation_staff():
    state = make_negotiation_state()
    manager = PlayerEngineNegotiationManager()

    negotiation = manager.start_negotiation(state, supplier_id=4)

    assert negotiation["supplier_name"] == "Marcado"
    assert negotiation["assigned_staff"] == 12
    assert negotiation["total_boxes"] >= 2
    assert state.player_engine_negotiation is not None

    updated = manager.update_assigned_staff(state, assigned_staff=24)
    assert updated["assigned_staff"] == 24
    assert state.player_engine_negotiation["assigned_staff"] == 24


@patch("app.core.player_engine_negotiations.random.uniform", return_value=0.0)
def test_engine_negotiation_progress_uses_commercial_manager_skill(mock_uniform):
    low_state = make_negotiation_state(manager_skill=40)
    high_state = make_negotiation_state(manager_skill=90)
    manager = PlayerEngineNegotiationManager()

    manager.start_negotiation(low_state, supplier_id=4)
    manager.start_negotiation(high_state, supplier_id=4)
    manager.update_assigned_staff(low_state, assigned_staff=20)
    manager.update_assigned_staff(high_state, assigned_staff=20)

    low_result = manager.progress_after_race(low_state)
    high_result = manager.progress_after_race(high_state)

    assert low_result is not None
    assert high_result is not None
    assert high_result["progress"] > low_result["progress"]


def test_signing_negotiated_deal_creates_announced_signing_and_applies_contract_length():
    state = make_negotiation_state()
    manager = PlayerEngineNegotiationManager()
    negotiation = manager.start_negotiation(state, supplier_id=3)
    state.player_engine_negotiation["progress"] = float(negotiation["customer_threshold"])
    state.player_engine_negotiation["progress_boxes"] = negotiation["customer_threshold"]

    signing = manager.sign_deal(state, "customer")

    assert signing["supplier_name"] == "Frost"
    assert signing["deal_type"] == "customer"
    assert signing["contract_length"] == negotiation["contract_length"]
    assert state.player_engine_negotiation is None
    assert len(state.announced_ai_engine_supplier_signings) == 1

    EngineSupplierTransferManager().apply_new_season_transfers(state, announced_year=state.year)
    assert state.player_team.engine_supplier_name == "Frost"
    assert state.player_team.engine_supplier_contract_length == negotiation["contract_length"]


def test_engine_negotiations_block_self_built_programmes():
    state = make_negotiation_state()
    state.player_team.builds_own_engine = True
    state.player_team.engine_supplier_name = "Ferano"
    state.player_team.engine_supplier_contract_length = 0

    payload = PlayerEngineNegotiationManager().get_market_payload(state)

    assert "cannot negotiate external engine deals" in payload["blocked_reason"]
