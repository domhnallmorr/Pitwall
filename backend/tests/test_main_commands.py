import app.main as app_main
from app.main import process_command
from app.models.state import GameState
from app.models.calendar import Calendar, Event, EventType
from app.models.team import Team
from app.models.driver import Driver
from app.models.commercial_manager import CommercialManager
from app.models.circuit import Circuit
from app.models.finance import TransactionCategory


def create_state() -> GameState:
    teams = [
        Team(
            id=1,
            name="Warrick",
            country="United Kingdom",
            driver1_id=1,
            driver2_id=2,
            commercial_manager_id=11,
            car_speed=80,
            workforce=250,
            title_sponsor_name="Windale",
            title_sponsor_yearly=32_500_000,
            other_sponsorship_yearly=9_500_000,
            engine_supplier_name="Mechatron",
            engine_supplier_deal="customer",
            engine_supplier_yearly_cost=4_500_000,
            tyre_supplier_name="Greatday",
            tyre_supplier_deal="partner",
            tyre_supplier_yearly_cost=0,
        ),
        Team(id=2, name="Ferano", country="Italy", driver1_id=3, driver2_id=4, car_speed=84),
    ]
    drivers = [
        Driver(id=1, name="John Newhouse", age=27, country="Canada", team_id=1, speed=84, race_starts=33, wins=11),
        Driver(id=2, name="Henrik Friedrich", age=31, country="Germany", team_id=1, speed=72, race_starts=65, wins=1),
        Driver(id=3, name="Marco Schneider", age=29, country="Germany", team_id=2, speed=98, race_starts=101, wins=28),
        Driver(id=4, name="Evan Irving", age=33, country="United Kingdom", team_id=2, speed=75, race_starts=65, wins=0),
    ]
    circuits = [
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
    ]
    calendar = Calendar(events=[Event(name="Albert Park", week=10, type=EventType.RACE)], current_week=10)
    return GameState(
        year=1998,
        teams=teams,
        drivers=drivers,
        commercial_managers=[
            CommercialManager(id=11, name="Jace Whitman", country="United Kingdom", age=29, skill=70, contract_length=1, salary=360_000, team_id=1),
            CommercialManager(id=12, name="Free Manager", country="Germany", age=43, skill=66, contract_length=0, salary=0, team_id=None),
        ],
        calendar=calendar,
        circuits=circuits,
        player_team_id=1,
        driver_season_results={
            1998: {
                1: [{"round": 1, "event_name": "Albert Park", "country": "Australia", "position": 2}]
            }
        },
    )


def test_get_driver_returns_profile_payload():
    app_main.CURRENT_STATE = create_state()

    result = process_command({"type": "get_driver", "name": "John Newhouse"})

    assert result["status"] == "success"
    assert result["type"] == "driver_data"
    assert result["data"]["wins"] == 11
    assert result["data"]["race_starts"] == 33
    assert len(result["data"]["season_results"]) == 1
    assert result["data"]["season_results"][0]["event_name"] == "Albert Park"


def test_get_car_returns_team_car_speed_data():
    app_main.CURRENT_STATE = create_state()

    result = process_command({"type": "get_car"})

    assert result["status"] == "success"
    assert result["type"] == "car_data"
    assert len(result["data"]["teams"]) == 2
    assert result["data"]["teams"][0]["car_speed"] in {80, 84}
    assert "development_catalog" in result["data"]
    assert "player_development" in result["data"]
    assert result["data"]["player_team_name"] == "Warrick"
    assert result["data"]["player_car_speed"] == 80
    assert "player_car_wear" in result["data"]
    assert "player_mechanical_fail_probability" in result["data"]


def test_unknown_command_returns_error():
    app_main.CURRENT_STATE = create_state()

    result = process_command({"type": "not_a_real_command"})

    assert result["status"] == "error"
    assert "Unknown command" in result["message"]


def test_get_finance_returns_summary_and_track_profit_loss():
    state = create_state()
    state.finance.prize_money_entitlement = 1_000_000
    state.finance.prize_money_paid = 100_000
    state.finance.prize_money_total_races = 16
    state.finance.prize_money_races_paid = 1
    state.finance.add_transaction(
        week=10,
        year=1998,
        amount=100_000,
        category=TransactionCategory.PRIZE_MONEY,
        description="Prize",
        event_name="Albert Park",
        event_type="RACE",
        circuit_country="Australia",
    )
    state.finance.add_transaction(
        week=10,
        year=1998,
        amount=-200_000,
        category=TransactionCategory.TRANSPORT,
        description="Transport",
        event_name="Albert Park",
        event_type="RACE",
        circuit_country="Australia",
    )
    app_main.CURRENT_STATE = state

    result = process_command({"type": "get_finance"})

    assert result["status"] == "success"
    assert result["type"] == "finance_data"
    assert "summary" in result["data"]
    assert "track_profit_loss" in result["data"]
    assert result["data"]["summary"]["transport_total"] == 200_000
    assert "workforce_total" in result["data"]["summary"]
    assert "engine_supplier_total" in result["data"]["summary"]
    assert "tyre_supplier_total" in result["data"]["summary"]
    assert "sponsorship_total" in result["data"]["summary"]
    assert len(result["data"]["track_profit_loss"]) == 1
    assert result["data"]["sponsor"]["name"] == "Windale"
    assert result["data"]["other_sponsorship"]["annual_value"] == 9_500_000
    assert result["data"]["engine_supplier"]["name"] == "Mechatron"
    assert result["data"]["tyre_supplier"]["name"] == "Greatday"


def test_get_emails_and_read_email_updates_unread_count():
    state = create_state()
    first = state.add_email(sender="A", subject="One", body="x")
    second = state.add_email(sender="B", subject="Two", body="y")
    second.read = True
    app_main.CURRENT_STATE = state

    emails_result = process_command({"type": "get_emails"})
    assert emails_result["status"] == "success"
    assert emails_result["type"] == "email_data"
    assert emails_result["data"]["unread_count"] == 1
    assert len(emails_result["data"]["emails"]) == 2

    read_result = process_command({"type": "read_email", "email_id": first.id})
    assert read_result["status"] == "success"
    assert read_result["type"] == "email_read"
    assert read_result["data"]["unread_count"] == 0


def test_replace_driver_respects_contract_rule_and_signs_replacement():
    state = create_state()
    # Make driver 1 replaceable; keep driver 2 locked.
    state.drivers[0].contract_length = 1
    state.drivers[1].contract_length = 2
    # Provide a candidate free agent for random replacement.
    state.drivers.append(
        Driver(id=99, name="Free Agent", age=24, country="Germany", team_id=None, contract_length=0, wage=0)
    )
    app_main.CURRENT_STATE = state

    candidates = process_command({"type": "get_replacement_candidates", "driver_id": 1})
    assert candidates["status"] == "success"
    assert any(d["id"] == 99 for d in candidates["data"]["candidates"])

    success = process_command({"type": "replace_driver", "driver_id": 1, "incoming_driver_id": 99})
    assert success["status"] == "success"
    assert success["type"] == "driver_replaced"
    assert success["data"]["team_id"] == 1
    assert success["data"]["driver_id"] == 99

    locked = process_command({"type": "replace_driver", "driver_id": 2})
    assert locked["status"] == "error"
    assert "2 or more years" in locked["message"]


def test_replace_commercial_manager_respects_contract_rule_and_signs_replacement():
    state = create_state()
    app_main.CURRENT_STATE = state

    candidates = process_command({"type": "get_manager_replacement_candidates", "manager_id": 11})
    assert candidates["status"] == "success"
    assert any(m["id"] == 12 for m in candidates["data"]["candidates"])

    success = process_command({"type": "replace_commercial_manager", "manager_id": 11, "incoming_manager_id": 12})
    assert success["status"] == "success"
    assert success["type"] == "commercial_manager_replaced"
    assert success["data"]["team_id"] == 1
    assert success["data"]["manager_id"] == 12

    # Lock the currently assigned manager and verify replacement is blocked.
    manager = next(m for m in app_main.CURRENT_STATE.commercial_managers if m.id == 11)
    manager.contract_length = 2
    locked = process_command({"type": "replace_commercial_manager", "manager_id": 11})
    assert locked["status"] == "error"
    assert "2 or more years" in locked["message"]


def test_get_facilities_returns_player_and_team_comparison_data():
    state = create_state()
    state.teams[0].facilities = 75
    state.teams[1].facilities = 68
    app_main.CURRENT_STATE = state

    result = process_command({"type": "get_facilities"})

    assert result["status"] == "success"
    assert result["type"] == "facilities_data"
    assert result["data"]["team_name"] == "Warrick"
    assert result["data"]["facilities"] == 75
    assert len(result["data"]["teams"]) == 2
    assert any(t["name"] == "Ferano" and t["facilities"] == 68 for t in result["data"]["teams"])


def test_preview_facilities_upgrade_returns_expected_payload():
    state = create_state()
    state.teams[0].facilities = 70
    app_main.CURRENT_STATE = state

    result = process_command({"type": "preview_facilities_upgrade", "points": 20, "years": 2})

    assert result["status"] == "success"
    assert result["type"] == "facilities_upgrade_preview"
    assert result["data"]["current_facilities"] == 70
    assert result["data"]["projected_facilities"] == 90
    assert result["data"]["effective_points"] == 20
    assert result["data"]["total_cost"] == 10_000_000


def test_start_facilities_upgrade_sets_active_financing_and_blocks_second_upgrade():
    state = create_state()
    state.teams[0].facilities = 65
    app_main.CURRENT_STATE = state

    started = process_command({"type": "start_facilities_upgrade", "points": 20, "years": 1})
    assert started["status"] == "success"
    assert started["type"] == "facilities_upgrade_started"

    facilities = process_command({"type": "get_facilities"})
    assert facilities["status"] == "success"
    assert facilities["data"]["facilities"] == 85
    assert facilities["data"]["upgrade_financing"]["active"] is True

    blocked = process_command({"type": "start_facilities_upgrade", "points": 20, "years": 1})
    assert blocked["status"] == "error"
    assert "already active" in blocked["message"]


def test_start_car_development_creates_project_and_blocks_second_start():
    app_main.CURRENT_STATE = create_state()

    started = process_command({"type": "start_car_development", "development_type": "minor"})
    assert started["status"] == "success"
    assert started["type"] == "car_development_started"
    assert started["data"]["development_type"] == "minor"
    assert started["data"]["weekly_cost"] == 25_000

    blocked = process_command({"type": "start_car_development", "development_type": "major"})
    assert blocked["status"] == "error"
    assert "already active" in blocked["message"]


def test_attend_test_command_applies_testing_cost():
    state = create_state()
    state.calendar = Calendar(events=[Event(name="Barcelona Test", week=11, type=EventType.TEST)], current_week=11)
    app_main.CURRENT_STATE = state

    result = process_command({"type": "attend_test", "kms": 900})
    assert result["status"] == "success"
    assert result["type"] == "week_advanced"
    txs = [t for t in state.finance.transactions if t.category == TransactionCategory.TESTING]
    assert len(txs) == 1
    assert txs[0].amount == -1_260_000


def test_repair_car_wear_reduces_wear_and_records_cost():
    state = create_state()
    state.teams[0].car_wear = 25
    app_main.CURRENT_STATE = state

    result = process_command({"type": "repair_car_wear", "wear_points": 10})
    assert result["status"] == "success"
    assert result["type"] == "car_wear_repaired"
    assert result["data"]["cost"] == 32_000
    assert state.teams[0].car_wear == 15
    txs = [t for t in state.finance.transactions if t.category == TransactionCategory.MAINTENANCE]
    assert len(txs) == 1
    assert txs[0].amount == -32_000


def test_update_workforce_updates_player_team_and_returns_cost_projection():
    state = create_state()
    state.teams[0].workforce = 150
    app_main.CURRENT_STATE = state

    result = process_command({"type": "update_workforce", "workforce": 200})

    assert result["status"] == "success"
    assert result["type"] == "workforce_updated"
    assert result["data"]["previous_workforce"] == 150
    assert result["data"]["new_workforce"] == 200
    assert result["data"]["projected_race_cost"] > 0
    assert state.teams[0].workforce == 200


def test_update_workforce_rejects_values_above_cap():
    state = create_state()
    app_main.CURRENT_STATE = state

    result = process_command({"type": "update_workforce", "workforce": 251})

    assert result["status"] == "error"
    assert "between 0 and 250" in result["message"]


def test_update_workforce_requires_workforce_value():
    state = create_state()
    app_main.CURRENT_STATE = state

    result = process_command({"type": "update_workforce"})

    assert result["status"] == "error"
    assert "workforce is required" in result["message"]


def test_update_workforce_rejects_negative_values():
    state = create_state()
    app_main.CURRENT_STATE = state

    result = process_command({"type": "update_workforce", "workforce": -1})

    assert result["status"] == "error"
    assert "between 0 and 250" in result["message"]


def test_update_workforce_fails_when_game_not_started():
    app_main.CURRENT_STATE = None

    result = process_command({"type": "update_workforce", "workforce": 120})

    assert result["status"] == "error"
    assert result["type"] == "workforce_updated"
    assert "Game not started" in result["message"]
