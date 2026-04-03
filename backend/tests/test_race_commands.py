from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.commands.race_commands import (
    _build_race_weekend_payload,
    handle_get_race_weekend,
    handle_simulate_qualifying,
    handle_simulate_race,
)
from app.models.calendar import Calendar, Event, EventType
from app.models.circuit import Circuit
from app.models.driver import Driver
from app.models.finance import TransactionCategory
from app.models.state import GameState
from app.models.team import Team


def create_state():
    team = Team(id=1, name="Warrick", country="United Kingdom", driver1_id=1, driver2_id=2)
    drivers = [
        Driver(id=1, name="Driver One", age=30, country="United Kingdom", team_id=1),
        Driver(id=2, name="Driver Two", age=29, country="France", team_id=1),
    ]
    calendar = Calendar(events=[Event(name="Test GP", week=10, type=EventType.RACE)], current_week=10)
    circuits = [
        Circuit(
            id=1,
            name="Test GP",
            country="Australia",
            location="Melbourne",
            laps=58,
            base_laptime_ms=86_000,
            length_km=5.3,
            overtaking_delta=1.2,
            power_factor=5.0,
        )
    ]
    return GameState(
        year=1998,
        teams=[team],
        drivers=drivers,
        calendar=calendar,
        circuits=circuits,
        player_team_id=1,
    )


def test_build_race_weekend_payload_returns_empty_when_no_active_race():
    state = create_state()
    state.calendar.current_week = 1

    assert _build_race_weekend_payload(state) == {}


def test_build_race_weekend_payload_includes_qualifying_and_processed_status():
    state = create_state()
    event_key = f"{state.year}_{state.calendar.current_week}_Test GP"
    state.qualifying_results_by_event[event_key] = [{"position": 1, "driver_name": "Driver One"}]
    state.events_processed.append("10_Test GP")

    payload = _build_race_weekend_payload(state)

    assert payload["event_name"] == "Test GP"
    assert payload["qualifying_complete"] is True
    assert payload["race_complete"] is True
    assert payload["qualifying_results"] == [{"position": 1, "driver_name": "Driver One"}]


def test_handle_get_race_weekend_returns_error_when_no_weekend():
    state = create_state()
    state.calendar.current_week = 1

    returned_state, response = handle_get_race_weekend(state, Mock())

    assert returned_state is state
    assert response["status"] == "error"
    assert response["message"] == "No active race weekend"


def test_handle_get_race_weekend_handles_exceptions():
    state = create_state()
    logger = Mock()

    with patch("app.commands.race_commands._build_race_weekend_payload", side_effect=RuntimeError("broken")):
        returned_state, response = handle_get_race_weekend(state, logger)

    assert returned_state is state
    assert response["status"] == "error"
    assert response["message"] == "broken"
    logger.error.assert_called_once()


def test_handle_simulate_qualifying_handles_exceptions():
    state = create_state()
    logger = Mock()

    with patch("app.commands.race_commands.RaceManager.simulate_qualifying", side_effect=RuntimeError("bad quali")):
        returned_state, response = handle_simulate_qualifying(state, logger)

    assert returned_state is state
    assert response["status"] == "error"
    assert response["message"] == "bad quali"
    logger.error.assert_called_once()


def test_handle_simulate_race_emits_tyre_facilities_and_finance_emails():
    state = create_state()
    logger = Mock()
    event_name = "Test GP"
    current_event = state.calendar.current_event

    state.finance.add_transaction(
        week=state.calendar.current_week,
        year=state.year,
        amount=100,
        category=TransactionCategory.PRIZE_MONEY,
        description="Prize",
        event_name=event_name,
        event_type="RACE",
    )
    state.finance.add_transaction(
        week=state.calendar.current_week,
        year=state.year,
        amount=-20,
        category=TransactionCategory.TYRE_SUPPLIER,
        description="Tyres",
        event_name=event_name,
        event_type="RACE",
    )
    state.finance.add_transaction(
        week=state.calendar.current_week,
        year=state.year,
        amount=-15,
        category=TransactionCategory.FACILITIES,
        description="Facilities",
        event_name=event_name,
        event_type="RACE",
    )

    race_result = {
        "event_name": event_name,
        "results": [
            {"position": 1, "driver_name": "Driver One", "team_name": "Warrick", "team_id": 1, "points": 10},
            {"position": 2, "driver_name": "Driver Two", "team_name": "Warrick", "team_id": 1, "points": 6},
        ],
    }
    tyre_charge = SimpleNamespace(
        event_name=event_name,
        supplier_name="Greatday",
        deal_type="partner",
        applied_cost=20,
        yearly_cost=0,
    )
    facilities_charge = SimpleNamespace(
        event_name=event_name,
        applied_cost=15,
        remaining_cost=120_000,
        races_paid=1,
        total_races=10,
    )

    with (
        patch("app.commands.race_commands.RaceManager.simulate_race", return_value=race_result),
        patch("app.commands.race_commands.PrizeMoneyManager.process_race_payout"),
        patch("app.commands.race_commands.SponsorshipManager.apply_for_event", return_value=None),
        patch("app.commands.race_commands.DriverWageManager.charge_for_event"),
        patch("app.commands.race_commands.WorkforceCostManager.charge_for_event", return_value=None),
        patch("app.commands.race_commands.EngineSupplierCostManager.charge_for_event", return_value=None),
        patch("app.commands.race_commands.TyreSupplierCostManager.charge_for_event", return_value=tyre_charge),
        patch("app.commands.race_commands.FuelSupplierCostManager.charge_for_event", return_value=None),
        patch("app.commands.race_commands.TransportManager.charge_for_event", return_value=None),
        patch("app.commands.race_commands.CrashDamageManager.charge_for_race", return_value=[]),
        patch("app.commands.race_commands.FacilitiesUpgradeManager.charge_for_event", return_value=facilities_charge),
    ):
        returned_state, response = handle_simulate_race(state, logger)

    assert returned_state is state
    assert response["status"] == "success"
    assert response["type"] == "race_result"
    subjects = [email.subject for email in state.emails]
    assert f"Tyre Supplier Invoice: {event_name}" in subjects
    assert f"Facilities Upgrade Installment: {event_name}" in subjects
    assert f"Race Finance Summary: {event_name}" in subjects
    assert f"Race Report: {event_name}" in subjects
    finance_email = next(email for email in state.emails if email.subject == f"Race Finance Summary: {event_name}")
    assert "Tyre supplier: -$20" in finance_email.body
    assert "Facilities financing: -$15" in finance_email.body
    assert current_event is not None


def test_handle_simulate_race_handles_exceptions():
    state = create_state()
    logger = Mock()

    with patch("app.commands.race_commands.RaceManager.simulate_race", side_effect=RuntimeError("race failed")):
        returned_state, response = handle_simulate_race(state, logger)

    assert returned_state is state
    assert response["status"] == "error"
    assert response["message"] == "race failed"
    logger.error.assert_called_once()
