from app.core.rollover import SeasonRolloverManager
from app.core.engine import GameEngine
from app.models.state import GameState
from app.models.calendar import Calendar, Event, EventType
from app.models.driver import Driver
from app.models.team import Team
from unittest.mock import patch
from app.models.enums import DriverRole


def create_end_of_season_state():
    """Creates a state near end of season (last event at week 3)."""
    teams = [
        Team(id=1, name="Team A", country="UK", driver1_id=1, driver2_id=2, points=50),
    ]
    drivers = [
        Driver(id=1, name="Driver A1", age=25, country="UK", team_id=1, points=30),
        Driver(id=2, name="Driver A2", age=28, country="FR", team_id=1, points=20),
    ]
    events = [
        Event(name="Race 1", week=1, type=EventType.RACE),
        Event(name="Race 2", week=3, type=EventType.RACE),
    ]
    calendar = Calendar(events=events, current_week=3)
    state = GameState(
        year=1998, teams=teams, drivers=drivers,
        calendar=calendar, circuits=[],
        events_processed=["1_Race 1", "3_Race 2"]
    )
    return state


def test_rollover_resets_points():
    state = create_end_of_season_state()
    manager = SeasonRolloverManager()
    result = manager.process_rollover(state)

    assert result["old_year"] == 1998
    assert result["new_year"] == 1999
    assert state.year == 1999
    assert state.drivers[0].points == 0
    assert state.drivers[1].points == 0
    assert state.teams[0].points == 0


def test_rollover_resets_calendar():
    state = create_end_of_season_state()
    manager = SeasonRolloverManager()
    manager.process_rollover(state)

    assert state.calendar.current_week == 1
    assert len(state.events_processed) == 0


@patch("app.core.rollover.random.random", return_value=1.0)
def test_rollover_degrades_facilities_by_four_with_floor_one(mock_random):
    teams = [
        Team(id=1, name="Team A", country="UK", driver1_id=1, driver2_id=2, points=10, facilities=75),
        Team(id=2, name="Team B", country="IT", driver1_id=3, driver2_id=4, points=8, facilities=3),
    ]
    drivers = [
        Driver(id=1, name="A1", age=30, country="UK", team_id=1),
        Driver(id=2, name="A2", age=31, country="UK", team_id=1),
        Driver(id=3, name="B1", age=28, country="IT", team_id=2),
        Driver(id=4, name="B2", age=27, country="IT", team_id=2),
    ]
    state = GameState(
        year=1998,
        teams=teams,
        drivers=drivers,
        calendar=Calendar(events=[Event(name="Race 1", week=3, type=EventType.RACE)], current_week=3),
        circuits=[],
    )

    result = SeasonRolloverManager().process_rollover(state)

    team_a = next(t for t in state.teams if t.id == 1)
    team_b = next(t for t in state.teams if t.id == 2)
    assert team_a.facilities == 71
    assert team_b.facilities == 1
    assert any(u["team_id"] == 1 and u["old_facilities"] == 75 and u["new_facilities"] == 71 for u in result["facilities_updates"])


@patch("app.core.rollover.random.randint", return_value=30)
@patch("app.core.rollover.random.random", side_effect=[0.1, 0.9])
def test_rollover_ai_facilities_upgrade_flat_chance_and_range(mock_random, mock_randint):
    teams = [
        Team(id=1, name="Player Team", country="UK", driver1_id=1, driver2_id=2, points=10, facilities=70),
        Team(id=2, name="AI Team A", country="IT", driver1_id=3, driver2_id=4, points=8, facilities=60),
        Team(id=3, name="AI Team B", country="FR", driver1_id=5, driver2_id=6, points=6, facilities=50),
    ]
    drivers = [
        Driver(id=1, name="P1", age=30, country="UK", team_id=1),
        Driver(id=2, name="P2", age=31, country="UK", team_id=1),
        Driver(id=3, name="A1", age=28, country="IT", team_id=2),
        Driver(id=4, name="A2", age=27, country="IT", team_id=2),
        Driver(id=5, name="B1", age=29, country="FR", team_id=3),
        Driver(id=6, name="B2", age=26, country="FR", team_id=3),
    ]
    state = GameState(
        year=1998,
        teams=teams,
        drivers=drivers,
        calendar=Calendar(events=[Event(name="Race 1", week=3, type=EventType.RACE)], current_week=3),
        circuits=[],
        player_team_id=1,
    )

    manager = SeasonRolloverManager()
    manager._degrade_facilities(state)
    upgrades = manager._apply_ai_facilities_upgrades(state)

    # Degrade first: 70->66, 60->56, 50->46
    # Then only AI Team A upgrades (+30): 56->86
    player = next(t for t in state.teams if t.id == 1)
    ai_a = next(t for t in state.teams if t.id == 2)
    ai_b = next(t for t in state.teams if t.id == 3)
    assert player.facilities == 66
    assert ai_a.facilities == 86
    assert ai_b.facilities == 46
    assert len(upgrades) == 1
    assert upgrades[0]["team_id"] == 2
    assert upgrades[0]["increase"] == 30


@patch("app.core.rollover.random.randint", return_value=25)
@patch("app.core.rollover.random.random", return_value=0.1)
@patch("app.core.rollover.load_roster", return_value=([], [], 1999, [], []))
def test_rollover_sends_facilities_upgrade_summary_email(mock_load_roster, mock_random, mock_randint):
    teams = [
        Team(id=1, name="Player Team", country="UK", driver1_id=1, driver2_id=2, points=10, facilities=70),
        Team(id=2, name="AI Team A", country="IT", driver1_id=3, driver2_id=4, points=8, facilities=60),
    ]
    drivers = [
        Driver(id=1, name="P1", age=30, country="UK", team_id=1),
        Driver(id=2, name="P2", age=31, country="UK", team_id=1),
        Driver(id=3, name="A1", age=28, country="IT", team_id=2),
        Driver(id=4, name="A2", age=27, country="IT", team_id=2),
    ]
    state = GameState(
        year=1998,
        teams=teams,
        drivers=drivers,
        calendar=Calendar(events=[Event(name="Race 1", week=3, type=EventType.RACE)], current_week=3),
        circuits=[],
        player_team_id=1,
    )

    SeasonRolloverManager().process_rollover(state)

    email = next((e for e in state.emails if e.subject == "Facilities Development Update: 1999"), None)
    assert email is not None
    assert "AI Team A" in email.body
    assert "56 -> 81 (+25)" in email.body


def test_engine_triggers_rollover_after_last_event():
    state = create_end_of_season_state()
    engine = GameEngine()

    # Advance past last event (week 3 -> 4, which is past last event)
    summary = engine.advance_week(state)

    assert summary.get("season_rollover") is True
    assert summary["rollover_info"]["new_year"] == 1999
    assert summary["year"] == 1999
    assert summary["week"] == 1


def test_calendar_season_over_property():
    events = [Event(name="GP", week=5, type=EventType.RACE)]
    cal = Calendar(events=events, current_week=5)
    assert cal.season_over is False

    cal.current_week = 6
    assert cal.season_over is True


@patch('app.core.rollover.load_roster', return_value=([], [], 1999, [], []))
def test_rollover_increments_driver_ages(mock_load_roster):
    state = create_end_of_season_state()
    original_ages = [d.age for d in state.drivers]  # [25, 28]

    manager = SeasonRolloverManager()
    manager.process_rollover(state)

    for i, driver in enumerate(state.drivers):
        assert driver.age == original_ages[i] + 1


@patch('app.core.retirement.random.random', return_value=1.0)
def test_rollover_updates_next_season_prize_money_from_constructor_position(mock_random):
    teams = [
        Team(id=1, name="Team A", country="UK", driver1_id=1, driver2_id=2, points=15),
        Team(id=2, name="Team B", country="IT", driver1_id=3, driver2_id=4, points=25),
    ]
    drivers = [
        Driver(id=1, name="A1", age=30, country="UK", team_id=1),
        Driver(id=2, name="A2", age=31, country="UK", team_id=1),
        Driver(id=3, name="B1", age=28, country="IT", team_id=2),
        Driver(id=4, name="B2", age=27, country="IT", team_id=2),
    ]
    state = GameState(
        year=1998,
        teams=teams,
        drivers=drivers,
        calendar=Calendar(events=[Event(name="Race 1", week=3, type=EventType.RACE)], current_week=3),
        circuits=[],
        player_team_id=1
    )

    manager = SeasonRolloverManager()
    result = manager.process_rollover(state)

    # Team A finished 2nd in constructors, so next season entitlement is 31,000,000.
    assert result["next_season_prize_money"]["position"] == 2
    assert result["next_season_prize_money"]["entitlement"] == 31_000_000
    assert state.finance.prize_money_entitlement == 31_000_000
    assert state.finance.prize_money_paid == 0
    assert state.finance.prize_money_races_paid == 0


@patch('app.core.rollover.load_roster', return_value=([], [], 1999, [], []))
@patch('app.core.retirement.random.random', return_value=1.0)
def test_rollover_retires_due_driver_and_vacates_seat(mock_random, mock_load_roster):
    teams = [
        Team(id=1, name="Team A", country="UK", driver1_id=1, driver2_id=2, points=50),
    ]
    drivers = [
        Driver(
            id=1, name="Veteran Driver", age=38, country="UK", team_id=1, role="DRIVER_1",
            points=30, retirement_year=1998
        ),
        Driver(id=2, name="Younger Driver", age=30, country="FR", team_id=1, role="DRIVER_2", points=20),
    ]
    events = [Event(name="Race 2", week=3, type=EventType.RACE)]
    state = GameState(
        year=1998, teams=teams, drivers=drivers,
        calendar=Calendar(events=events, current_week=3),
        circuits=[],
        events_processed=["3_Race 2"]
    )

    manager = SeasonRolloverManager()
    result = manager.process_rollover(state)

    retired = state.drivers[0]
    remaining = state.drivers[1]

    assert result["old_year"] == 1998
    assert retired.active is False
    assert retired.retired_year == 1998
    assert retired.team_id is None
    assert retired.role is None
    assert retired.age == 38
    # No entrants/free-agents were loaded in this test, so seat stays vacant.
    assert state.teams[0].driver1_id is None

    assert remaining.active is True
    assert remaining.age == 31


@patch('app.core.recruitment.random.choice', side_effect=lambda choices: choices[0])
@patch('app.core.retirement.random.random', return_value=1.0)
def test_rollover_recruits_replacements_announces_and_snapshots(mock_random, mock_choice):
    teams = [
        Team(id=1, name="Team A", country="UK", driver1_id=1, driver2_id=2, points=50),
    ]
    drivers = [
        Driver(
            id=1, name="Retiring Driver", age=38, country="UK", team_id=1, role="DRIVER_1",
            points=30, retirement_year=1998
        ),
        Driver(id=2, name="Staying Driver", age=30, country="FR", team_id=1, role="DRIVER_2", points=20),
        Driver(id=99, name="Free Agent", age=24, country="DE"),
    ]
    events = [Event(name="Race 2", week=3, type=EventType.RACE)]
    state = GameState(
        year=1998, teams=teams, drivers=drivers,
        calendar=Calendar(events=events, current_week=3),
        circuits=[],
        events_processed=["3_Race 2"]
    )

    manager = SeasonRolloverManager()
    result = manager.process_rollover(state)

    # Free agent is signed into retired seat.
    assert state.teams[0].driver1_id == 99
    assert state.drivers[2].team_id == 1

    # Signing appears in rollover summary.
    assert len(result["signings"]) == 1
    assert result["signings"][0]["driver_name"] == "Free Agent"

    # Week 1 signing announcement is published.
    signing_emails = [e for e in state.emails if e.subject == "Driver Signings: 1999"]
    assert len(signing_emails) == 1
    assert "Team A: Free Agent (Driver 1)" in signing_emails[0].body
    assert signing_emails[0].week == 1
    assert signing_emails[0].year == 1999

    # Snapshot for next season contains updated lineup.
    assert 1999 in state.grid_snapshots
    team_row = next(r for r in state.grid_snapshots[1999] if r["Team"] == "Team A")
    assert team_row["Driver1"] == "Free Agent"


@patch('app.core.rollover.load_roster')
@patch('app.core.recruitment.random.choice', side_effect=lambda choices: choices[0])
@patch('app.core.retirement.random.random', return_value=1.0)
def test_rollover_adds_new_season_entrants(mock_random, mock_choice, mock_load_roster):
    teams = [
        Team(id=1, name="Team A", country="UK", driver1_id=1, driver2_id=2, points=50),
    ]
    existing_drivers = [
        Driver(id=1, name="Driver A1", age=25, country="UK", team_id=1, role=DriverRole.DRIVER_1, points=10),
        Driver(id=2, name="Driver A2", age=26, country="UK", team_id=1, role=DriverRole.DRIVER_2, points=8),
    ]
    calendar = Calendar(events=[Event(name="Race 1", week=3, type=EventType.RACE)], current_week=3)
    state = GameState(year=1998, teams=teams, drivers=existing_drivers, calendar=calendar, circuits=[])

    entrants = [
        Driver(id=101, name="Jenson Button", age=19, country="United Kingdom", wage=0, pay_driver=False),
        Driver(id=102, name="Nick Heidfeld", age=22, country="Germany", wage=0, pay_driver=False),
        Driver(id=103, name="Gaston Mazzacane", age=24, country="Argentina", wage=0, pay_driver=True),
    ]
    mock_load_roster.return_value = ([], existing_drivers + entrants, 1999, [], [])

    manager = SeasonRolloverManager()
    result = manager.process_rollover(state)

    entrant_names = {d["name"] for d in result["new_entrants"]}
    assert {"Jenson Button", "Nick Heidfeld", "Gaston Mazzacane"} <= entrant_names

    jb = next(d for d in state.drivers if d.name == "Jenson Button")
    nh = next(d for d in state.drivers if d.name == "Nick Heidfeld")
    gm = next(d for d in state.drivers if d.name == "Gaston Mazzacane")
    assert jb.wage == 0 and jb.team_id is None and jb.active is True
    assert nh.wage == 0 and nh.team_id is None and nh.active is True
    assert gm.wage == 0 and gm.pay_driver is True and gm.team_id is None and gm.active is True

    entrants_email = [e for e in state.emails if e.subject == "New Drivers Entering 1999"]
    assert len(entrants_email) == 1
    assert "Jenson Button" in entrants_email[0].body
    assert "Nick Heidfeld" in entrants_email[0].body
    assert "Gaston Mazzacane" in entrants_email[0].body
