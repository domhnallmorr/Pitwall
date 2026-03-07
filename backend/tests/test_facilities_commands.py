from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.commands.facilities_commands import (
    handle_facilities_upgrade_preview,
    handle_start_facilities_upgrade,
)
from app.models.calendar import Calendar
from app.models.state import GameState


def create_state() -> GameState:
    return GameState(year=1998, teams=[], drivers=[], calendar=Calendar(events=[]), circuits=[])


def test_facilities_preview_requires_points_and_years():
    logger = Mock()
    result = handle_facilities_upgrade_preview(create_state(), logger, points=None, years=2)
    assert result["status"] == "error"
    assert "required" in result["message"]


def test_facilities_preview_returns_success_payload():
    logger = Mock()
    preview = SimpleNamespace(
        requested_points=20,
        effective_points=18,
        years=2,
        total_races=32,
        total_cost=10_000_000,
        per_race_payment=312_500,
        current_facilities=70,
        projected_facilities=88,
    )
    with patch("app.commands.facilities_commands.FacilitiesUpgradeManager.preview", return_value=preview):
        result = handle_facilities_upgrade_preview(create_state(), logger, points=20, years=2)
    assert result["status"] == "success"
    assert result["data"]["effective_points"] == 18
    assert result["data"]["projected_facilities"] == 88


def test_facilities_preview_handles_value_error():
    logger = Mock()
    with patch("app.commands.facilities_commands.FacilitiesUpgradeManager.preview", side_effect=ValueError("bad points")):
        result = handle_facilities_upgrade_preview(create_state(), logger, points=0, years=2)
    assert result["status"] == "error"
    assert result["message"] == "bad points"


def test_facilities_preview_handles_unexpected_error_and_logs():
    logger = Mock()
    with patch("app.commands.facilities_commands.FacilitiesUpgradeManager.preview", side_effect=RuntimeError("boom")):
        result = handle_facilities_upgrade_preview(create_state(), logger, points=20, years=2)
    assert result["status"] == "error"
    assert result["message"] == "boom"
    logger.error.assert_called_once()


def test_start_facilities_upgrade_requires_points_and_years():
    logger = Mock()
    result = handle_start_facilities_upgrade(create_state(), logger, points=20, years=None)
    assert result["status"] == "error"
    assert "required" in result["message"]


def test_start_facilities_upgrade_returns_success_payload():
    logger = Mock()
    preview = SimpleNamespace(
        effective_points=20,
        years=1,
        total_races=16,
        total_cost=10_000_000,
        per_race_payment=625_000,
        projected_facilities=90,
    )
    with patch("app.commands.facilities_commands.FacilitiesUpgradeManager.start_upgrade", return_value=preview):
        result = handle_start_facilities_upgrade(create_state(), logger, points=20, years=1)
    assert result["status"] == "success"
    assert result["data"]["projected_facilities"] == 90


def test_start_facilities_upgrade_handles_value_error():
    logger = Mock()
    with patch("app.commands.facilities_commands.FacilitiesUpgradeManager.start_upgrade", side_effect=ValueError("already active")):
        result = handle_start_facilities_upgrade(create_state(), logger, points=20, years=1)
    assert result["status"] == "error"
    assert result["message"] == "already active"


def test_start_facilities_upgrade_handles_unexpected_error_and_logs():
    logger = Mock()
    with patch("app.commands.facilities_commands.FacilitiesUpgradeManager.start_upgrade", side_effect=RuntimeError("oops")):
        result = handle_start_facilities_upgrade(create_state(), logger, points=20, years=1)
    assert result["status"] == "error"
    assert result["message"] == "oops"
    logger.error.assert_called_once()
