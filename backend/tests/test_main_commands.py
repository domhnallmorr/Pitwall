import app.main as app_main
from app.main import process_command
from app.models.state import GameState
from app.models.calendar import Calendar, Event, EventType
from app.models.team import Team
from app.models.driver import Driver
from app.models.commercial_manager import CommercialManager
from app.models.circuit import Circuit
from app.models.finance import TransactionCategory
from app.models.technical_director import TechnicalDirector
from app.models.title_sponsor import TitleSponsor
from app.models.engine_supplier import EngineSupplier
from app.models.tyre_supplier import TyreSupplier


def create_state() -> GameState:
    teams = [
        Team(
            id=1,
            name="Warrick",
            country="United Kingdom",
            driver1_id=1,
            driver2_id=2,
            technical_director_id=21,
            commercial_manager_id=11,
            car_speed=80,
            workforce=250,
            title_sponsor_name="Windale",
            title_sponsor_yearly=32_500_000,
            title_sponsor_contract_length=1,
            other_sponsorship_yearly=9_500_000,
            engine_supplier_name="Mechatron",
            engine_supplier_deal="customer",
            engine_supplier_yearly_cost=4_500_000,
            engine_supplier_contract_length=1,
            tyre_supplier_name="Greatday",
            tyre_supplier_deal="partner",
            tyre_supplier_yearly_cost=0,
            tyre_supplier_contract_length=1,
            fuel_supplier_name="Brasoil",
            fuel_supplier_deal="partner",
            fuel_supplier_yearly_cost=150_000,
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
        technical_directors=[
            TechnicalDirector(id=21, name="Peter Heed", country="United Kingdom", age=52, skill=75, contract_length=1, salary=4_800_000, team_id=1),
            TechnicalDirector(id=22, name="Free Director", country="Germany", age=43, skill=66, contract_length=0, salary=0, team_id=None),
        ],
        commercial_managers=[
            CommercialManager(id=11, name="Jace Whitman", country="United Kingdom", age=29, skill=70, contract_length=1, salary=360_000, team_id=1),
            CommercialManager(id=12, name="Free Manager", country="Germany", age=43, skill=66, contract_length=0, salary=0, team_id=None),
        ],
        title_sponsors=[
            TitleSponsor(id=31, name="Windale", wealth=70, start_year=0),
            TitleSponsor(id=32, name="Bright Shot", wealth=85, start_year=0),
        ],
        engine_suppliers=[
            EngineSupplier(id=40, name="Ferano", country="Italy", resources=90, power=72, start_year=0),
            EngineSupplier(id=41, name="Mechatron", country="France", resources=55, power=60, start_year=0),
            EngineSupplier(id=42, name="Frost", country="USA", resources=65, power=38, start_year=0),
        ],
        tyre_suppliers=[
            TyreSupplier(id=41, name="Greatday", country="USA", wear=60, grip=80, start_year=0),
            TyreSupplier(id=42, name="Spanrock", country="Japan", wear=80, grip=70, start_year=0),
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
    assert "fuel_supplier_total" in result["data"]["summary"]
    assert "sponsorship_total" in result["data"]["summary"]
    assert len(result["data"]["track_profit_loss"]) == 1
    assert result["data"]["sponsor"]["name"] == "Windale"
    assert result["data"]["other_sponsorship"]["annual_value"] == 9_500_000
    assert result["data"]["engine_supplier"]["name"] == "Mechatron"
    assert result["data"]["engine_supplier"]["contract_length"] == 1
    assert result["data"]["tyre_supplier"]["name"] == "Greatday"
    assert result["data"]["fuel_supplier"]["name"] == "Brasoil"


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


def test_email_inbox_is_capped_and_oldest_messages_are_pruned():
    state = create_state()
    cap = state.MAX_EMAILS

    for i in range(cap + 5):
        state.add_email(sender="System", subject=f"Msg {i}", body="x")

    app_main.CURRENT_STATE = state
    emails_result = process_command({"type": "get_emails"})

    assert emails_result["status"] == "success"
    assert len(emails_result["data"]["emails"]) == cap
    subjects = [e["subject"] for e in emails_result["data"]["emails"]]
    assert "Msg 0" not in subjects
    assert f"Msg {cap + 4}" in subjects


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


def test_replace_technical_director_respects_contract_rule_and_signs_replacement():
    state = create_state()
    app_main.CURRENT_STATE = state

    candidates = process_command({"type": "get_technical_director_replacement_candidates", "director_id": 21})
    assert candidates["status"] == "success"
    assert any(m["id"] == 22 for m in candidates["data"]["candidates"])

    success = process_command({"type": "replace_technical_director", "director_id": 21, "incoming_director_id": 22})
    assert success["status"] == "success"
    assert success["type"] == "technical_director_replaced"
    assert success["data"]["team_id"] == 1
    assert success["data"]["director_id"] == 22

    director = next(d for d in app_main.CURRENT_STATE.technical_directors if d.id == 21)
    director.contract_length = 2
    locked = process_command({"type": "replace_technical_director", "director_id": 21})
    assert locked["status"] == "error"
    assert "2 or more years" in locked["message"]


def test_replace_title_sponsor_respects_contract_rule_and_signs_replacement():
    state = create_state()
    app_main.CURRENT_STATE = state

    candidates = process_command({"type": "get_title_sponsor_replacement_candidates", "sponsor_name": "Windale"})
    assert candidates["status"] == "success"
    assert any(s["id"] == 32 for s in candidates["data"]["candidates"])

    success = process_command({"type": "replace_title_sponsor", "sponsor_name": "Windale", "incoming_sponsor_id": 32})
    assert success["status"] == "success"
    assert success["type"] == "title_sponsor_replaced"
    assert success["data"]["team_id"] == 1
    assert success["data"]["sponsor_id"] == 32

    app_main.CURRENT_STATE.player_team.title_sponsor_contract_length = 2
    locked = process_command({"type": "replace_title_sponsor", "sponsor_name": "Windale"})
    assert locked["status"] == "error"
    assert "2 or more years" in locked["message"]


def test_replace_engine_supplier_respects_contract_rule_and_signs_replacement():
    state = create_state()
    app_main.CURRENT_STATE = state

    candidates = process_command({"type": "get_engine_supplier_replacement_candidates", "supplier_name": "Mechatron"})
    assert candidates["status"] == "success"
    assert any(s["id"] == 41 for s in candidates["data"]["candidates"])
    assert any(s["id"] == 42 for s in candidates["data"]["candidates"])

    success = process_command({"type": "replace_engine_supplier", "supplier_name": "Mechatron", "incoming_supplier_id": 42})
    assert success["status"] == "success"
    assert success["type"] == "engine_supplier_replaced"
    assert success["data"]["team_id"] == 1
    assert success["data"]["supplier_id"] == 42

    app_main.CURRENT_STATE.player_team.engine_supplier_contract_length = 2
    locked = process_command({"type": "replace_engine_supplier", "supplier_name": "Mechatron"})
    assert locked["status"] == "error"
    assert "2 or more years" in locked["message"]


def test_replace_engine_supplier_blocks_self_built_engine_team():
    state = create_state()
    state.player_team.name = "Ferano"
    state.player_team.country = "Italy"
    state.player_team.engine_supplier_name = "Ferano"
    state.player_team.engine_supplier_deal = "works"
    state.player_team.engine_supplier_contract_length = 0
    state.player_team.builds_own_engine = True
    app_main.CURRENT_STATE = state

    candidates = process_command({"type": "get_engine_supplier_replacement_candidates", "supplier_name": "Ferano"})
    assert candidates["status"] == "error"
    assert "cannot be replaced" in candidates["message"]

    blocked = process_command({"type": "replace_engine_supplier", "supplier_name": "Ferano"})
    assert blocked["status"] == "error"
    assert "cannot be replaced" in blocked["message"]


def test_replace_tyre_supplier_respects_contract_rule_and_signs_replacement():
    state = create_state()
    app_main.CURRENT_STATE = state

    candidates = process_command({"type": "get_tyre_supplier_replacement_candidates", "supplier_name": "Greatday"})
    assert candidates["status"] == "success"
    assert any(s["id"] == 41 for s in candidates["data"]["candidates"])
    assert any(s["id"] == 42 for s in candidates["data"]["candidates"])

    success = process_command({"type": "replace_tyre_supplier", "supplier_name": "Greatday", "incoming_supplier_id": 42})
    assert success["status"] == "success"
    assert success["type"] == "tyre_supplier_replaced"
    assert success["data"]["team_id"] == 1
    assert success["data"]["supplier_id"] == 42

    app_main.CURRENT_STATE.player_team.tyre_supplier_contract_length = 2
    locked = process_command({"type": "replace_tyre_supplier", "supplier_name": "Greatday"})
    assert locked["status"] == "error"
    assert "2 or more years" in locked["message"]


def test_pending_player_replacements_are_reflected_in_staff_and_finance_payloads():
    state = create_state()
    state.drivers[0].contract_length = 1
    state.commercial_managers[0].contract_length = 1
    state.technical_directors[0].contract_length = 1
    state.announced_ai_signings = [
        {
            "team_id": 1,
            "seat": "driver1_id",
            "driver_id": 99,
            "status": "announced",
        }
    ]
    state.announced_ai_cm_signings = [{"team_id": 1, "manager_id": 12, "status": "announced"}]
    state.announced_ai_td_signings = [{"team_id": 1, "director_id": 22, "status": "announced"}]
    state.announced_ai_title_sponsor_signings = [{"team_id": 1, "sponsor_id": 32, "status": "announced"}]
    state.announced_ai_engine_supplier_signings = [{"team_id": 1, "supplier_id": 42, "status": "announced"}]
    state.announced_ai_tyre_supplier_signings = [{"team_id": 1, "supplier_id": 42, "status": "announced"}]
    app_main.CURRENT_STATE = state

    staff = process_command({"type": "get_staff"})
    finance = process_command({"type": "get_finance"})

    assert staff["status"] == "success"
    assert finance["status"] == "success"
    assert next(d for d in staff["data"]["drivers"] if d["id"] == 1)["pending_replacement"] is True
    assert staff["data"]["commercial_manager"]["pending_replacement"] is True
    assert staff["data"]["technical_director"]["pending_replacement"] is True
    assert finance["data"]["sponsor"]["pending_replacement"] is True
    assert finance["data"]["engine_supplier"]["pending_replacement"] is True
    assert finance["data"]["tyre_supplier"]["pending_replacement"] is True


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
