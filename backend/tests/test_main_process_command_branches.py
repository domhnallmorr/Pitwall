from types import SimpleNamespace
from unittest.mock import Mock, patch

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
        {"type": "replace_commercial_manager"},
        {"type": "replace_technical_director"},
        {"type": "replace_title_sponsor"},
        {"type": "get_replacement_candidates"},
        {"type": "get_manager_replacement_candidates"},
        {"type": "get_technical_director_replacement_candidates"},
        {"type": "get_title_sponsor_replacement_candidates"},
        {"type": "get_staff"},
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
    assert app_main.process_command({"type": "repair_car_wear"})["status"] == "error"
    assert app_main.process_command({"type": "update_workforce"})["status"] == "error"


def test_get_driver_requires_name():
    app_main.CURRENT_STATE = SimpleNamespace()
    result = app_main.process_command({"type": "get_driver"})
    assert result["status"] == "error"
    assert "Driver name is required" in result["message"]


def test_grid_calendar_and_standings_exception_paths():
    app_main.CURRENT_STATE = SimpleNamespace(calendar=SimpleNamespace(), circuits=[])
    with patch("app.main.get_grid_payload", side_effect=RuntimeError("grid boom")):
        result = app_main.process_command({"type": "get_grid"})
        assert result["status"] == "error"
        assert result["message"] == "grid boom"

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
