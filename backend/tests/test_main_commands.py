import app.main as app_main
from app.main import process_command
from app.models.state import GameState
from app.models.calendar import Calendar, Event, EventType
from app.models.team import Team
from app.models.driver import Driver
from app.models.circuit import Circuit
from app.models.finance import TransactionCategory


def create_state() -> GameState:
    teams = [
        Team(id=1, name="Warrick", country="United Kingdom", driver1_id=1, driver2_id=2, car_speed=80),
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
    assert len(result["data"]["track_profit_loss"]) == 1


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
