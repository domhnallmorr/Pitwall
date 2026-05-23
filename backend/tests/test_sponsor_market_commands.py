from unittest.mock import Mock, patch

from app.commands.sponsor_market_commands import (
    handle_book_title_sponsor_hospitality,
    handle_get_title_sponsor_negotiation_market,
    handle_sign_title_sponsor_negotiated_deal,
    handle_start_title_sponsor_negotiation,
    handle_update_title_sponsor_negotiation_staff,
)
from app.models.commercial_manager import CommercialManager
from app.models.title_sponsor import TitleSponsor
from tests.factories import make_calendar, make_circuit, make_race_event, make_state, make_team


def make_sponsor_command_state():
    team = make_team(
        id=1,
        name="Schweizer",
        country="Switzerland",
        car_speed=72,
        commercial_staff=49,
        commercial_manager_id=11,
        title_sponsor_name="Yellow Cow",
        title_sponsor_yearly=21_500_000,
        title_sponsor_contract_length=1,
    )
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
                skill=70,
                contract_length=2,
                salary=360_000,
                team_id=1,
            )
        ],
        title_sponsors=[
            TitleSponsor(id=31, name="Yellow Cow", wealth=55, start_year=0),
            TitleSponsor(id=32, name="Bright Shot", wealth=85, start_year=0),
        ],
        calendar=make_calendar(events=[make_race_event("Albert Park", week=10)], current_week=10),
        circuits=[make_circuit(name="Albert Park")],
        player_team_id=1,
    )


def test_get_title_sponsor_negotiation_market_returns_payload_and_handles_errors():
    state = make_sponsor_command_state()
    logger = Mock()

    result = handle_get_title_sponsor_negotiation_market(state, logger)
    assert result["type"] == "title_sponsor_negotiation_market"
    assert result["status"] == "success"
    assert result["data"]["current_sponsor_name"] == "Yellow Cow"

    with patch("app.commands.sponsor_market_commands.PlayerTitleSponsorNegotiationManager.get_market_payload", side_effect=RuntimeError("boom")):
        result = handle_get_title_sponsor_negotiation_market(state, logger)
    assert result["status"] == "error"
    assert result["message"] == "boom"
    logger.error.assert_called()


def test_start_title_sponsor_negotiation_validates_and_returns_updated_market():
    state = make_sponsor_command_state()
    logger = Mock()

    _, result = handle_start_title_sponsor_negotiation(state, logger, sponsor_id=None)
    assert result["status"] == "error"
    assert result["message"] == "Title sponsor id is required"

    _, result = handle_start_title_sponsor_negotiation(state, logger, sponsor_id=32)
    assert result["type"] == "title_sponsor_negotiation_updated"
    assert result["status"] == "success"
    assert result["data"]["active_negotiation"]["sponsor_name"] == "Bright Shot"

    with patch("app.commands.sponsor_market_commands.PlayerTitleSponsorNegotiationManager.start_negotiation", side_effect=RuntimeError("start boom")):
        _, result = handle_start_title_sponsor_negotiation(make_sponsor_command_state(), logger, sponsor_id=32)
    assert result["status"] == "error"
    assert result["message"] == "start boom"


def test_update_title_sponsor_negotiation_staff_validates_and_returns_updated_market():
    state = make_sponsor_command_state()
    logger = Mock()

    _, result = handle_update_title_sponsor_negotiation_staff(state, logger, assigned_staff=None)
    assert result["status"] == "error"
    assert result["message"] == "Assigned staff is required"

    handle_start_title_sponsor_negotiation(state, logger, sponsor_id=32)
    _, result = handle_update_title_sponsor_negotiation_staff(state, logger, assigned_staff=20)
    assert result["type"] == "title_sponsor_negotiation_updated"
    assert result["status"] == "success"
    assert result["data"]["active_negotiation"]["assigned_staff"] == 20

    with patch("app.commands.sponsor_market_commands.PlayerTitleSponsorNegotiationManager.update_assigned_staff", side_effect=RuntimeError("staff boom")):
        _, result = handle_update_title_sponsor_negotiation_staff(state, logger, assigned_staff=20)
    assert result["status"] == "error"
    assert result["message"] == "staff boom"


def test_sign_title_sponsor_negotiated_deal_returns_signing_and_handles_errors():
    state = make_sponsor_command_state()
    logger = Mock()
    handle_start_title_sponsor_negotiation(state, logger, sponsor_id=32)
    state.player_title_sponsor_negotiation["progress"] = float(state.player_title_sponsor_negotiation["total_boxes"])
    state.player_title_sponsor_negotiation["progress_boxes"] = state.player_title_sponsor_negotiation["total_boxes"]

    _, result = handle_sign_title_sponsor_negotiated_deal(state, logger)
    assert result["type"] == "title_sponsor_negotiation_signed"
    assert result["status"] == "success"
    assert result["data"]["sponsor_name"] == "Bright Shot"

    with patch("app.commands.sponsor_market_commands.PlayerTitleSponsorNegotiationManager.sign_deal", side_effect=RuntimeError("sign boom")):
        _, result = handle_sign_title_sponsor_negotiated_deal(make_sponsor_command_state(), logger)
    assert result["status"] == "error"
    assert result["message"] == "sign boom"


def test_book_title_sponsor_hospitality_returns_updated_market_and_typed_errors():
    state = make_sponsor_command_state()
    logger = Mock()

    _, result = handle_book_title_sponsor_hospitality(state, logger)
    assert result["type"] == "title_sponsor_negotiation_updated"
    assert result["status"] == "error"
    assert result["message"] == "No active title sponsor negotiation"

    handle_start_title_sponsor_negotiation(state, logger, sponsor_id=32)
    _, result = handle_book_title_sponsor_hospitality(state, logger)
    assert result["type"] == "title_sponsor_negotiation_updated"
    assert result["status"] == "success"
    assert result["data"]["hospitality"]["booked"] is True

    with patch("app.commands.sponsor_market_commands.PlayerTitleSponsorNegotiationManager.book_hospitality", side_effect=RuntimeError("hospitality boom")):
        _, result = handle_book_title_sponsor_hospitality(state, logger)
    assert result["type"] == "title_sponsor_negotiation_updated"
    assert result["status"] == "error"
    assert result["message"] == "hospitality boom"
