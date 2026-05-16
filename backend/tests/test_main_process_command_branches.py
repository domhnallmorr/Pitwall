from types import SimpleNamespace
from unittest.mock import Mock, call, patch

import app.main as app_main


def test_ping_and_check_save_commands():
    app_main.CURRENT_STATE = None
    assert app_main.process_command({"type": "ping"}) == {"status": "success", "data": "pong"}

    with patch("app.main.has_save", return_value=True):
        result = app_main.process_command({"type": "check_save"})
    assert result["status"] == "success"
    assert result["type"] == "save_status"
    assert result["data"]["has_save"] is True


def test_commands_require_game_started_return_error():
    app_main.CURRENT_STATE = None
    commands = [
        {"type": "get_grid"},
        {"type": "get_calendar"},
        {"type": "get_standings"},
        {"type": "advance_week"},
        {"type": "skip_event"},
        {"type": "attend_test"},
        {"type": "simulate_race"},
        {"type": "replace_driver"},
        {"type": "offer_driver"},
        {"type": "offer_technical_director"},
        {"type": "replace_commercial_manager"},
        {"type": "replace_technical_director"},
        {"type": "replace_title_sponsor"},
        {"type": "replace_engine_supplier"},
        {"type": "replace_tyre_supplier"},
        {"type": "get_replacement_candidates"},
        {"type": "get_manager_replacement_candidates"},
        {"type": "get_technical_director_replacement_candidates"},
        {"type": "get_title_sponsor_replacement_candidates"},
        {"type": "get_engine_supplier_replacement_candidates"},
        {"type": "get_tyre_supplier_replacement_candidates"},
        {"type": "get_tyre_negotiation_market"},
        {"type": "start_tyre_negotiation"},
        {"type": "update_tyre_negotiation_staff"},
        {"type": "sign_tyre_negotiated_deal"},
        {"type": "book_tyre_negotiation_hospitality"},
        {"type": "get_staff"},
        {"type": "get_home"},
        {"type": "get_driver", "name": "John Newhouse"},
        {"type": "get_facilities"},
        {"type": "get_car"},
        {"type": "get_finance"},
        {"type": "get_emails"},
        {"type": "read_email", "email_id": 1},
    ]
    for cmd in commands:
        result = app_main.process_command(cmd)
        assert result["status"] == "error"
        assert "Game not started" in result["message"]

    assert app_main.process_command({"type": "preview_facilities_upgrade"})["status"] == "error"
    assert app_main.process_command({"type": "start_facilities_upgrade"})["status"] == "error"
    assert app_main.process_command({"type": "start_car_development"})["status"] == "error"
    assert app_main.process_command({"type": "finish_car_development_stage"})["status"] == "error"
    assert app_main.process_command({"type": "set_car_development_allocation"})["status"] == "error"
    assert app_main.process_command({"type": "start_construction_project"})["status"] == "error"
    assert app_main.process_command({"type": "set_construction_allocation"})["status"] == "error"
    assert app_main.process_command({"type": "set_test_chassis"})["status"] == "error"
    assert app_main.process_command({"type": "set_race_chassis_assignments"})["status"] == "error"
    assert app_main.process_command({"type": "repair_chassis_wear"})["status"] == "error"


def test_get_driver_requires_name():
    app_main.CURRENT_STATE = SimpleNamespace()
    result = app_main.process_command({"type": "get_driver"})
    assert result["status"] == "error"
    assert "Driver name is required" in result["message"]


def test_grid_calendar_home_and_standings_exception_paths():
    app_main.CURRENT_STATE = SimpleNamespace(calendar=SimpleNamespace(), circuits=[])
    with patch("app.main.get_grid_payload", side_effect=RuntimeError("grid boom")):
        result = app_main.process_command({"type": "get_grid"})
        assert result["status"] == "error"
        assert result["message"] == "grid boom"

    app_main.CURRENT_STATE = SimpleNamespace()
    with patch("app.main.get_home_payload", side_effect=RuntimeError("home boom")):
        result = app_main.process_command({"type": "get_home"})
        assert result["status"] == "error"
        assert result["message"] == "home boom"

    app_main.CURRENT_STATE = SimpleNamespace(
        calendar=SimpleNamespace(get_schedule_data=Mock(side_effect=RuntimeError("cal boom"))),
        circuits=[],
    )
    result = app_main.process_command({"type": "get_calendar"})
    assert result["status"] == "error"
    assert result["message"] == "cal boom"

    app_main.CURRENT_STATE = SimpleNamespace()
    with patch("app.main.get_standings_payload", side_effect=RuntimeError("std boom")):
        result = app_main.process_command({"type": "get_standings"})
    assert result["status"] == "error"
    assert result["message"] == "std boom"


def test_advance_skip_and_attend_test_paths():
    fake_state = SimpleNamespace()
    app_main.CURRENT_STATE = fake_state

    with patch("app.main.GameEngine.advance_week", return_value={"ok": 1}), patch("app.main.save_game") as save_mock:
        result = app_main.process_command({"type": "advance_week"})
        assert result["status"] == "success"
        assert result["type"] == "week_advanced"
        assert result["data"]["ok"] == 1
        save_mock.assert_called_once_with(fake_state)

    with patch("app.main.GameEngine.handle_event_action", return_value={"ok": 2}), patch("app.main.save_game"):
        result = app_main.process_command({"type": "skip_event"})
    assert result["status"] == "success"
    assert result["type"] == "week_advanced"
    assert result["data"]["ok"] == 2

    with patch("app.main.GameEngine.handle_event_action", side_effect=RuntimeError("test boom")):
        result = app_main.process_command({"type": "attend_test", "kms": 1000})
    assert result["status"] == "error"
    assert result["message"] == "test boom"


def test_offer_driver_command_saves_only_when_offer_is_accepted():
    fake_state = SimpleNamespace()
    app_main.CURRENT_STATE = fake_state

    with patch("app.main.handle_offer_driver", return_value=(fake_state, {"type": "driver_offer_result", "status": "success", "data": {"accepted": True}})), patch("app.main.save_game") as save_mock:
        result = app_main.process_command({"type": "offer_driver", "driver_id": 1, "incoming_driver_id": 5, "salary_offer": 1000000, "contract_length": 2})
    assert result["type"] == "driver_offer_result"
    save_mock.assert_called_once_with(fake_state)

    with patch("app.main.handle_offer_driver", return_value=(fake_state, {"type": "driver_offer_result", "status": "success", "data": {"accepted": False}})), patch("app.main.save_game") as save_mock:
        result = app_main.process_command({"type": "offer_driver", "driver_id": 1, "incoming_driver_id": 5, "salary_offer": 1000000, "contract_length": 2})
    assert result["type"] == "driver_offer_result"
    save_mock.assert_not_called()


def test_offer_technical_director_command_saves_only_when_offer_is_accepted():
    fake_state = SimpleNamespace()
    app_main.CURRENT_STATE = fake_state

    with patch("app.main.handle_offer_technical_director", return_value=(fake_state, {"type": "technical_director_offer_result", "status": "success", "data": {"accepted": True}})), patch("app.main.save_game") as save_mock:
        result = app_main.process_command({"type": "offer_technical_director", "director_id": 1, "incoming_director_id": 5, "salary_offer": 1000000, "contract_length": 2})
    assert result["type"] == "technical_director_offer_result"
    save_mock.assert_called_once_with(fake_state)

    with patch("app.main.handle_offer_technical_director", return_value=(fake_state, {"type": "technical_director_offer_result", "status": "success", "data": {"accepted": False}})), patch("app.main.save_game") as save_mock:
        result = app_main.process_command({"type": "offer_technical_director", "director_id": 1, "incoming_director_id": 5, "salary_offer": 1000000, "contract_length": 2})
    assert result["type"] == "technical_director_offer_result"
    save_mock.assert_not_called()


def test_load_game_success_and_errors():
    fake_email_1 = SimpleNamespace(read=False)
    fake_email_2 = SimpleNamespace(read=True)
    loaded = SimpleNamespace(
        player_team=SimpleNamespace(name="Warrick"),
        week_display="Week 1 1998",
        next_event_display="Next: Albert Park - Week 10",
        year=1998,
        finance=SimpleNamespace(balance=123),
        emails=[fake_email_1, fake_email_2],
        game_over=False,
        game_over_reason=None,
        game_completed=False,
        completion_year=None,
    )

    with patch("app.main.load_game_file", return_value=loaded):
        result = app_main.process_command({"type": "load_game"})
    assert result["status"] == "success"
    assert result["type"] == "game_loaded"
    assert result["data"]["team_name"] == "Warrick"
    assert result["data"]["unread_count"] == 1

    with patch("app.main.load_game_file", side_effect=FileNotFoundError()):
        result = app_main.process_command({"type": "load_game"})
    assert result["status"] == "error"
    assert "No save file found" in result["message"]

    with patch("app.main.load_game_file", side_effect=RuntimeError("bad save")):
        result = app_main.process_command({"type": "load_game"})
    assert result["status"] == "error"
    assert result["message"] == "bad save"


def test_staff_driver_facilities_query_value_errors_and_exceptions():
    app_main.CURRENT_STATE = SimpleNamespace()

    with patch("app.main.get_staff_payload", side_effect=ValueError("bad staff")):
        result = app_main.process_command({"type": "get_staff"})
    assert result["status"] == "error"
    assert result["message"] == "bad staff"

    with patch("app.main.get_staff_payload", side_effect=RuntimeError("staff boom")):
        result = app_main.process_command({"type": "get_staff"})
    assert result["status"] == "error"
    assert result["message"] == "staff boom"

    with patch("app.main.get_driver_payload", side_effect=ValueError("bad driver")):
        result = app_main.process_command({"type": "get_driver", "name": "x"})
    assert result["status"] == "error"
    assert result["message"] == "bad driver"

    with patch("app.main.get_facilities_payload", side_effect=ValueError("bad fac")):
        result = app_main.process_command({"type": "get_facilities"})
    assert result["status"] == "error"
    assert result["message"] == "bad fac"


def test_unknown_command_branch():
    app_main.CURRENT_STATE = None
    result = app_main.process_command({"type": "no_such_command"})
    assert result["status"] == "error"
    assert result["message"] == "Unknown command"


def test_load_roster_and_start_career_update_state_and_save():
    loaded_state = SimpleNamespace(name="loaded")
    started_state = SimpleNamespace(name="started")

    app_main.CURRENT_STATE = None
    with patch("app.main.handle_load_roster", return_value=(loaded_state, {"status": "success", "type": "roster"})):
        response = app_main.process_command({"type": "load_roster"})
    assert response["status"] == "success"
    assert app_main.CURRENT_STATE is loaded_state

    with patch("app.main.handle_start_career", return_value=(started_state, {"status": "success", "type": "game_started"})), patch(
        "app.main.save_game"
    ) as save_mock:
        response = app_main.process_command({"type": "start_career", "team_name": "Warrick"})
    assert response["status"] == "success"
    assert app_main.CURRENT_STATE is started_state
    save_mock.assert_called_once_with(started_state)


def test_load_roster_does_not_replace_state_when_handler_returns_none():
    existing = SimpleNamespace(name="existing")
    app_main.CURRENT_STATE = existing

    with patch("app.main.handle_load_roster", return_value=(None, {"status": "error", "message": "bad roster"})):
        response = app_main.process_command({"type": "load_roster"})

    assert response["status"] == "error"
    assert app_main.CURRENT_STATE is existing


def test_race_weekend_and_qualifying_commands_cover_success_and_save_paths():
    state = SimpleNamespace(name="state")
    app_main.CURRENT_STATE = state

    with patch("app.main.handle_get_race_weekend", return_value=(state, {"status": "success", "type": "race_weekend"})):
        weekend = app_main.process_command({"type": "get_race_weekend"})
    assert weekend["type"] == "race_weekend"

    updated = SimpleNamespace(name="updated")
    with patch("app.main.handle_simulate_qualifying", return_value=(updated, {"status": "success", "type": "qualifying_result"})), patch(
        "app.main.save_game"
    ) as save_mock:
        qualifying = app_main.process_command({"type": "simulate_qualifying"})
    assert qualifying["type"] == "qualifying_result"
    assert app_main.CURRENT_STATE is updated
    save_mock.assert_called_once_with(updated)

    failed = SimpleNamespace(name="failed")
    with patch("app.main.handle_simulate_qualifying", return_value=(failed, {"status": "error", "message": "nope"})), patch(
        "app.main.save_game"
    ) as save_mock:
        qualifying = app_main.process_command({"type": "simulate_qualifying"})
    assert qualifying["status"] == "error"
    save_mock.assert_not_called()
    assert app_main.CURRENT_STATE is failed


def test_replace_and_team_commands_save_only_on_success():
    initial = SimpleNamespace(name="initial")
    success_state = SimpleNamespace(name="success")
    error_state = SimpleNamespace(name="error")

    save_cases = [
        ("simulate_race", "handle_simulate_race", {"status": "success", "type": "race_result"}),
        ("replace_driver", "handle_replace_driver", {"status": "success", "type": "driver_replaced"}),
        ("replace_commercial_manager", "handle_replace_commercial_manager", {"status": "success", "type": "commercial_manager_replaced"}),
        ("replace_technical_director", "handle_replace_technical_director", {"status": "success", "type": "technical_director_replaced"}),
        ("replace_title_sponsor", "handle_replace_title_sponsor", {"status": "success", "type": "title_sponsor_replaced"}),
        ("replace_engine_supplier", "handle_replace_engine_supplier", {"status": "success", "type": "engine_supplier_replaced"}),
        ("replace_tyre_supplier", "handle_replace_tyre_supplier", {"status": "success", "type": "tyre_supplier_replaced"}),
        ("start_tyre_negotiation", "handle_start_tyre_negotiation", {"status": "success", "type": "tyre_negotiation_updated"}),
        ("update_tyre_negotiation_staff", "handle_update_tyre_negotiation_staff", {"status": "success", "type": "tyre_negotiation_updated"}),
        ("sign_tyre_negotiated_deal", "handle_sign_tyre_negotiated_deal", {"status": "success", "type": "tyre_negotiation_signed"}),
        ("book_tyre_negotiation_hospitality", "handle_book_tyre_negotiation_hospitality", {"status": "success", "type": "tyre_negotiation_updated"}),
    ]

    for command_type, handler_name, payload in save_cases:
        app_main.CURRENT_STATE = initial
        with patch(f"app.main.{handler_name}", return_value=(success_state, payload)), patch("app.main.save_game") as save_mock:
            response = app_main.process_command({"type": command_type})
        assert response["status"] == "success"
        assert app_main.CURRENT_STATE is success_state
        save_mock.assert_called_once_with(success_state)

        app_main.CURRENT_STATE = initial
        with patch(f"app.main.{handler_name}", return_value=(error_state, {"status": "error", "message": "bad"})), patch(
            "app.main.save_game"
        ) as save_mock:
            response = app_main.process_command({"type": command_type})
        assert response["status"] == "error"
        assert app_main.CURRENT_STATE is error_state
        save_mock.assert_not_called()

    response_cases = [
        ("start_facilities_upgrade", "handle_start_facilities_upgrade", {"status": "success", "type": "facilities_upgrade_started"}),
        ("start_car_development", "handle_start_car_development", {"status": "success", "type": "car_development_started"}),
        ("finish_car_development_stage", "handle_finish_car_development_project_stage", {"status": "success", "type": "car_development_stage_finished"}),
        ("set_car_development_allocation", "handle_set_car_development_allocation", {"status": "success", "type": "car_development_allocation_updated"}),
        ("start_construction_project", "handle_start_construction_project", {"status": "success", "type": "construction_started"}),
        ("set_construction_allocation", "handle_set_construction_allocation", {"status": "success", "type": "construction_allocation_updated"}),
        ("set_test_chassis", "handle_set_test_chassis", {"status": "success", "type": "test_chassis_updated"}),
        ("set_race_chassis_assignments", "handle_set_race_chassis_assignments", {"status": "success", "type": "race_chassis_assignments_updated"}),
        ("repair_chassis_wear", "handle_repair_chassis_wear", {"status": "success", "type": "chassis_wear_repaired"}),
    ]

    for command_type, handler_name, payload in response_cases:
        app_main.CURRENT_STATE = initial
        with patch(f"app.main.{handler_name}", return_value=payload), patch("app.main.save_game") as save_mock:
            response = app_main.process_command({"type": command_type})
        assert response["status"] == "success"
        save_mock.assert_called_once_with(initial)

        app_main.CURRENT_STATE = initial
        with patch(f"app.main.{handler_name}", return_value={"status": "error", "message": "bad"}), patch(
            "app.main.save_game"
        ) as save_mock:
            response = app_main.process_command({"type": command_type})
        assert response["status"] == "error"
        save_mock.assert_not_called()


def test_query_and_read_email_exception_paths():
    app_main.CURRENT_STATE = SimpleNamespace()

    with patch("app.main.get_driver_payload", side_effect=RuntimeError("driver boom")):
        result = app_main.process_command({"type": "get_driver", "name": "Driver X"})
    assert result["status"] == "error"
    assert result["message"] == "driver boom"

    with patch("app.main.get_facilities_payload", side_effect=RuntimeError("fac boom")):
        result = app_main.process_command({"type": "get_facilities"})
    assert result["status"] == "error"
    assert result["message"] == "fac boom"

    with patch("app.main.get_car_payload", side_effect=RuntimeError("car boom")):
        result = app_main.process_command({"type": "get_car"})
    assert result["status"] == "error"
    assert result["message"] == "car boom"

    with patch("app.main.build_finance_payload", side_effect=RuntimeError("fin boom")):
        result = app_main.process_command({"type": "get_finance"})
    assert result["status"] == "error"
    assert result["message"] == "fin boom"

    with patch("app.main.get_emails_payload", side_effect=RuntimeError("mail boom")):
        result = app_main.process_command({"type": "get_emails"})
    assert result["status"] == "error"
    assert result["message"] == "mail boom"

    with patch("app.main.read_email_payload", side_effect=RuntimeError("read boom")):
        result = app_main.process_command({"type": "read_email", "email_id": 1})
    assert result["status"] == "error"
    assert result["message"] == "read boom"


def test_main_loop_handles_valid_json_invalid_json_and_processing_errors():
    fake_stdin = iter(["{\"type\":\"ping\"}\n", "not-json\n", "{\"type\":\"oops\"}\n", "\n"])
    print_mock = Mock()

    with patch("app.main.sys.stdin", fake_stdin), patch("app.main.print", print_mock), patch(
        "app.main.process_command",
        side_effect=[{"status": "success", "data": "pong"}, RuntimeError("process boom")],
    ), patch("app.main.logging.error") as log_error:
        app_main.main()

    assert print_mock.call_args_list[0] == call('{"type": "status", "message": "Backend ready"}', flush=True)
    assert print_mock.call_args_list[1] == call('{"status": "success", "data": "pong"}', flush=True)
    assert print_mock.call_args_list[2] == call('{"status": "error", "message": "Invalid JSON"}', flush=True)
    assert print_mock.call_args_list[3] == call('{"status": "error", "message": "process boom"}', flush=True)
    assert log_error.call_count == 2
