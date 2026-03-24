from app.core.rollover import SeasonRolloverManager
from app.core.engine import GameEngine
from app.core.management_retirement import TechnicalDirectorRetirementManager
from app.models.state import GameState
from app.models.calendar import Calendar, Event, EventType
from app.models.driver import Driver
from app.models.team import Team
from app.models.technical_director import TechnicalDirector
from app.models.commercial_manager import CommercialManager
from app.models.title_sponsor import TitleSponsor
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


@patch("app.core.rollover.random.choice", side_effect=[15, 12, 12])
@patch("app.core.rollover.random.choices", side_effect=[["increase"], ["decrease"], ["decrease"]])
def test_update_ai_workforce_applies_bounds_and_skips_player(mock_choices, mock_choice):
    teams = [
        Team(id=1, name="Player Team", country="UK", workforce=200),
        Team(id=2, name="AI Team A", country="IT", workforce=240),
        Team(id=3, name="AI Team B", country="FR", workforce=95),
        Team(id=4, name="AI Team C", country="DE", workforce=90),
    ]
    state = GameState(
        year=1998,
        teams=teams,
        drivers=[],
        calendar=Calendar(events=[Event(name="Race 1", week=3, type=EventType.RACE)], current_week=3),
        circuits=[],
        player_team_id=1,
    )

    updates = SeasonRolloverManager()._update_ai_workforce(state)

    player = next(t for t in state.teams if t.id == 1)
    ai_a = next(t for t in state.teams if t.id == 2)
    ai_b = next(t for t in state.teams if t.id == 3)
    ai_c = next(t for t in state.teams if t.id == 4)
    assert player.workforce == 200
    assert ai_a.workforce == 250  # 240 + 15 -> capped
    assert ai_b.workforce == 90   # 95 - 12 -> floored
    assert ai_c.workforce == 90   # stays at min
    assert len(updates) == 2
    assert any(u["team_id"] == 2 and u["old_workforce"] == 240 and u["new_workforce"] == 250 for u in updates)
    assert any(u["team_id"] == 3 and u["old_workforce"] == 95 and u["new_workforce"] == 90 for u in updates)


@patch.object(SeasonRolloverManager, "_update_ai_workforce", return_value=[{
    "team_id": 2,
    "team_name": "AI Team A",
    "old_workforce": 120,
    "new_workforce": 130,
    "delta": 10,
}])
@patch("app.core.rollover.load_roster", return_value=([], [], 1999, [], []))
def test_rollover_sends_ai_workforce_summary_email(mock_load_roster, mock_workforce_update):
    teams = [
        Team(id=1, name="Player Team", country="UK", driver1_id=1, driver2_id=2, points=10, facilities=70, workforce=200),
        Team(id=2, name="AI Team A", country="IT", driver1_id=3, driver2_id=4, points=8, facilities=60, workforce=120),
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

    result = SeasonRolloverManager().process_rollover(state)

    assert any(u["team_id"] == 2 for u in result["ai_workforce_updates"])
    email = next((e for e in state.emails if e.subject == "AI Workforce Update: 1999"), None)
    assert email is not None
    assert "AI Team A: 120 -> 130 (+10)" in email.body


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


@patch('app.core.management_retirement.random.random', return_value=1.0)
@patch('app.core.rollover.load_roster', return_value=([], [], 1999, [], []))
def test_rollover_updates_management_age_and_contracts(mock_load_roster, mock_management_random):
    teams = [
        Team(
            id=1,
            name="Team A",
            country="UK",
            driver1_id=1,
            driver2_id=2,
            technical_director_id=10,
            commercial_manager_id=20,
        ),
    ]
    drivers = [
        Driver(id=1, name="Driver A1", age=25, country="UK", team_id=1),
        Driver(id=2, name="Driver A2", age=28, country="FR", team_id=1),
    ]
    technical_directors = [
        TechnicalDirector(id=10, name="TD Expiring", country="UK", age=50, skill=80, contract_length=1, salary=1, team_id=1),
        TechnicalDirector(id=11, name="TD Secure", country="DE", age=45, skill=70, contract_length=3, salary=1, team_id=None),
    ]
    commercial_managers = [
        CommercialManager(id=20, name="CM Expiring", country="UK", age=40, skill=75, contract_length=1, salary=1, team_id=1),
        CommercialManager(id=21, name="CM Secure", country="IT", age=35, skill=60, contract_length=3, salary=1, team_id=None),
    ]
    events = [Event(name="Race 2", week=3, type=EventType.RACE)]
    state = GameState(
        year=1998,
        teams=teams,
        drivers=drivers,
        technical_directors=technical_directors,
        commercial_managers=commercial_managers,
        calendar=Calendar(events=events, current_week=3),
        circuits=[],
        events_processed=["3_Race 2"],
    )

    result = SeasonRolloverManager().process_rollover(state)

    td_expiring = next(td for td in state.technical_directors if td.id == 10)
    td_secure = next(td for td in state.technical_directors if td.id == 11)
    cm_expiring = next(cm for cm in state.commercial_managers if cm.id == 20)
    cm_secure = next(cm for cm in state.commercial_managers if cm.id == 21)
    team = state.teams[0]

    assert td_expiring.age == 51
    assert td_expiring.contract_length == 0
    assert td_expiring.team_id is None
    assert team.technical_director_id is None

    assert cm_expiring.age == 41
    assert cm_expiring.contract_length == 0
    assert cm_expiring.team_id is None
    assert team.commercial_manager_id is None

    assert td_secure.age == 46
    assert td_secure.contract_length == 3  # unassigned staff do not decrement
    assert cm_secure.age == 36
    assert cm_secure.contract_length == 3  # unassigned staff do not decrement

    assert any(x["name"] == "TD Expiring" for x in result["management_updates"]["expired_technical_directors"])
    assert any(x["name"] == "CM Expiring" for x in result["management_updates"]["expired_commercial_managers"])


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


@patch("app.core.management_retirement.random.random", return_value=0.0)
@patch("app.core.rollover.load_roster", return_value=([], [], 1999, [], []))
def test_rollover_retires_eligible_technical_director(mock_load_roster, mock_td_random):
    teams = [
        Team(id=1, name="Team A", country="UK", driver1_id=1, driver2_id=2, technical_director_id=10, points=50),
    ]
    drivers = [
        Driver(id=1, name="Driver A1", age=30, country="UK", team_id=1, role="DRIVER_1", points=30),
        Driver(id=2, name="Driver A2", age=29, country="FR", team_id=1, role="DRIVER_2", points=20),
    ]
    technical_directors = [
        TechnicalDirector(id=10, name="TD Veteran", country="UK", age=52, skill=70, contract_length=3, salary=100_000, team_id=1),
    ]
    events = [Event(name="Race 2", week=3, type=EventType.RACE)]
    state = GameState(
        year=1998,
        teams=teams,
        drivers=drivers,
        technical_directors=technical_directors,
        calendar=Calendar(events=events, current_week=3),
        circuits=[],
        events_processed=["3_Race 2"],
    )

    result = SeasonRolloverManager().process_rollover(state)

    director = state.technical_directors[0]
    assert director.active is False
    assert director.team_id is None
    assert director.retired_year == 1998
    assert state.teams[0].technical_director_id is None
    assert any(m["name"] == "TD Veteran" for m in result["retired_technical_directors"])
    email = next((e for e in state.emails if e.subject == "Technical Director Retirements Confirmed: End of 1998"), None)
    assert email is not None
    assert "TD Veteran" in email.body


@patch("app.core.management_retirement.random.random", return_value=0.0)
@patch("app.core.rollover.load_roster", return_value=([], [], 1999, [], []))
def test_rollover_retires_eligible_commercial_manager(mock_load_roster, mock_cm_random):
    teams = [
        Team(id=1, name="Team A", country="UK", driver1_id=1, driver2_id=2, commercial_manager_id=20, points=50),
    ]
    drivers = [
        Driver(id=1, name="Driver A1", age=30, country="UK", team_id=1, role="DRIVER_1", points=30),
        Driver(id=2, name="Driver A2", age=29, country="FR", team_id=1, role="DRIVER_2", points=20),
    ]
    commercial_managers = [
        CommercialManager(id=20, name="CM Veteran", country="UK", age=52, skill=70, contract_length=3, salary=100_000, team_id=1),
    ]
    events = [Event(name="Race 2", week=3, type=EventType.RACE)]
    state = GameState(
        year=1998,
        teams=teams,
        drivers=drivers,
        commercial_managers=commercial_managers,
        calendar=Calendar(events=events, current_week=3),
        circuits=[],
        events_processed=["3_Race 2"],
    )

    result = SeasonRolloverManager().process_rollover(state)

    manager = state.commercial_managers[0]
    assert manager.active is False
    assert manager.team_id is None
    assert manager.retired_year == 1998
    assert state.teams[0].commercial_manager_id is None
    assert any(m["name"] == "CM Veteran" for m in result["retired_commercial_managers"])
    email = next((e for e in state.emails if e.subject == "Management Retirements Confirmed: End of 1998"), None)
    assert email is not None
    assert "CM Veteran" in email.body


@patch("app.core.management_retirement.random.random", return_value=1.0)
@patch("app.core.rollover.load_roster", return_value=([], [], 1999, [], []))
def test_rollover_applies_announced_technical_director_transfer(mock_load_roster, mock_management_random):
    teams = [
        Team(id=1, name="Player Team", country="UK", driver1_id=1, driver2_id=2, technical_director_id=10, points=10),
        Team(id=2, name="AI Team", country="IT", driver1_id=3, driver2_id=4, technical_director_id=20, points=8),
    ]
    drivers = [
        Driver(id=1, name="P1", age=30, country="UK", team_id=1),
        Driver(id=2, name="P2", age=29, country="UK", team_id=1),
        Driver(id=3, name="A1", age=28, country="IT", team_id=2),
        Driver(id=4, name="A2", age=27, country="IT", team_id=2),
    ]
    technical_directors = [
        TechnicalDirector(id=10, name="Player TD", country="UK", age=45, skill=75, contract_length=2, salary=1, team_id=1),
        TechnicalDirector(id=20, name="AI Expiring TD", country="IT", age=50, skill=78, contract_length=1, salary=1, team_id=2),
        TechnicalDirector(id=30, name="Free TD", country="DE", age=43, skill=80, contract_length=0, salary=1, team_id=None),
    ]
    state = GameState(
        year=1998,
        teams=teams,
        drivers=drivers,
        technical_directors=technical_directors,
        calendar=Calendar(events=[Event(name="Race 2", week=3, type=EventType.RACE)], current_week=3),
        circuits=[],
        events_processed=["3_Race 2"],
        announced_ai_td_signings=[
            {
                "team_id": 2,
                "team_name": "AI Team",
                "seat": "technical_director_id",
                "seat_label": "Technical Director",
                "director_id": 30,
                "director_name": "Free TD",
                "announce_week": 2,
                "announce_year": 1998,
                "status": "announced",
            }
        ],
    )

    result = SeasonRolloverManager().process_rollover(state)

    ai_team = next(t for t in state.teams if t.id == 2)
    incoming = next(td for td in state.technical_directors if td.id == 30)
    outgoing = next(td for td in state.technical_directors if td.id == 20)
    assert ai_team.technical_director_id == 30
    assert incoming.team_id == 2
    assert incoming.contract_length == 2
    assert outgoing.team_id is None
    assert outgoing.contract_length == 0
    assert any(s["director_id"] == 30 for s in result["td_transfer_outcome"]["applied_signings"])


def test_technical_director_retirement_probability_bounds():
    manager = TechnicalDirectorRetirementManager()

    assert manager._retirement_probability(49) == 0.0
    assert manager._retirement_probability(50) == 0.05
    assert manager._retirement_probability(65) == 1.0


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


@patch('app.core.rollover.load_roster')
def test_rollover_adds_new_season_title_sponsors(mock_load_roster):
    teams = [
        Team(id=1, name="Team A", country="UK", title_sponsor_name="Windale", title_sponsor_contract_length=2),
    ]
    existing_sponsors = [
        TitleSponsor(id=1, name="Windale", wealth=70, start_year=0),
    ]
    calendar = Calendar(events=[Event(name="Race 1", week=3, type=EventType.RACE)], current_week=3)
    state = GameState(
        year=1998,
        teams=teams,
        drivers=[],
        title_sponsors=existing_sponsors.copy(),
        calendar=calendar,
        circuits=[],
    )

    future_sponsors = [
        TitleSponsor(id=1, name="Windale", wealth=70, start_year=0),
        TitleSponsor(id=20, name="Purple", wealth=50, start_year=1999),
        TitleSponsor(id=21, name="Zenteq", wealth=55, start_year=1999),
    ]
    mock_load_roster.side_effect = [
        ([], [], 1999, [], []),
        ([], [], 1999, [], [], future_sponsors),
    ]

    manager = SeasonRolloverManager()
    result = manager.process_rollover(state)

    sponsor_names = {s["name"] for s in result["new_title_sponsors"]}
    assert sponsor_names == {"Purple", "Zenteq"}
    assert {s.name for s in state.title_sponsors} == {"Windale", "Purple", "Zenteq"}

    sponsor_email = next((e for e in state.emails if e.subject == "New Title Sponsors Entering 1999"), None)
    assert sponsor_email is not None
    assert "Purple" in sponsor_email.body
    assert "Zenteq" in sponsor_email.body
