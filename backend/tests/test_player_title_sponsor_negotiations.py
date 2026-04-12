from unittest.mock import patch

from app.core.management_transfer_markets.title_sponsor import TitleSponsorTransferManager
from app.core.player_title_sponsor_negotiations import PlayerTitleSponsorNegotiationManager
from app.models.commercial_manager import CommercialManager
from app.models.title_sponsor import TitleSponsor
from tests.factories import make_calendar, make_circuit, make_race_event, make_state, make_team


def make_sponsor_state(manager_skill: int = 70):
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
        title_sponsors=[
            TitleSponsor(id=31, name="Yellow Cow", wealth=55, start_year=0),
            TitleSponsor(id=32, name="Bright Shot", wealth=85, start_year=0),
            TitleSponsor(id=33, name="Purple", wealth=50, start_year=1999),
        ],
        calendar=calendar,
        circuits=[make_circuit(name="Albert Park")],
        player_team_id=1,
    )


def test_title_sponsor_market_excludes_current_and_future_sponsors():
    state = make_sponsor_state()

    payload = PlayerTitleSponsorNegotiationManager().get_market_payload(state)

    sponsor_names = [sponsor["name"] for sponsor in payload["sponsors"]]
    assert payload["blocked_reason"] is None
    assert "Yellow Cow" not in sponsor_names
    assert "Purple" not in sponsor_names
    assert sponsor_names == ["Bright Shot"]


@patch("app.core.player_title_sponsor_negotiations.random.uniform", return_value=0.0)
def test_title_sponsor_progress_uses_manager_skill(mock_uniform):
    low_state = make_sponsor_state(manager_skill=40)
    high_state = make_sponsor_state(manager_skill=90)
    manager = PlayerTitleSponsorNegotiationManager()

    manager.start_negotiation(low_state, sponsor_id=32)
    manager.start_negotiation(high_state, sponsor_id=32)
    manager.update_assigned_staff(low_state, assigned_staff=20)
    manager.update_assigned_staff(high_state, assigned_staff=20)

    low_result = manager.progress_after_race(low_state)
    high_result = manager.progress_after_race(high_state)

    assert low_result is not None
    assert high_result is not None
    assert high_result["progress"] > low_result["progress"]


def test_sign_title_sponsor_negotiation_creates_announced_signing_and_applies_terms():
    state = make_sponsor_state()
    manager = PlayerTitleSponsorNegotiationManager()
    negotiation = manager.start_negotiation(state, sponsor_id=32)
    state.player_title_sponsor_negotiation["progress"] = float(negotiation["total_boxes"])
    state.player_title_sponsor_negotiation["progress_boxes"] = negotiation["total_boxes"]

    signing = manager.sign_deal(state)

    assert signing["sponsor_name"] == "Bright Shot"
    assert signing["annual_value"] == negotiation["annual_value"]
    assert signing["contract_length"] == negotiation["contract_length"]
    assert state.player_title_sponsor_negotiation is None

    TitleSponsorTransferManager().apply_new_season_transfers(state, announced_year=state.year)
    assert state.player_team.title_sponsor_name == "Bright Shot"
    assert state.player_team.title_sponsor_yearly == negotiation["annual_value"]
    assert state.player_team.title_sponsor_contract_length == negotiation["contract_length"]
