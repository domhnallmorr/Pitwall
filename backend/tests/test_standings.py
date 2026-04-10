from app.core.standings import StandingsManager
from app.models.state import GameState
from app.models.driver import Driver
from app.models.team import Team
from app.models.calendar import Calendar
from unittest.mock import MagicMock

def create_mock_state(year, teams, drivers):
    return GameState(
        year=year,
        teams=teams,
        drivers=drivers,
        calendar=Calendar(events=[], current_week=1),
        circuits=[]
    )

def test_reset_season():
    # Setup Data with points
    drivers = [
        Driver(id=1, name="D1", age=20, country="UK", points=10),
        Driver(id=2, name="D2", age=20, country="UK", points=5)
    ]
    teams = [
        Team(id=1, name="T1", country="UK", points=20),
        Team(id=2, name="T2", country="UK", points=15)
    ]
    state = create_mock_state(year=1998, teams=teams, drivers=drivers)
    
    # Action
    manager = StandingsManager()
    manager.reset_season(state)
    
    # Assert
    assert all(d.points == 0 for d in state.drivers)
    assert all(t.points == 0 for t in state.teams)

def test_driver_standings_order():
    teams = [
        Team(id=1, name="Team A", country="UK", points=0),
        Team(id=2, name="Team B", country="UK", points=0),
    ]
    drivers = [
        Driver(id=1, name="Alice", age=20, country="UK", team_id=1, points=10),
        Driver(id=2, name="Bob", age=20, country="UK", team_id=2, points=20),
        Driver(id=3, name="Charlie", age=20, country="UK", team_id=2, points=5)
    ]
    state = create_mock_state(year=1998, teams=teams, drivers=drivers)
    
    manager = StandingsManager()
    standings = manager.get_driver_standings(state)
    
    assert standings[0].name == "Bob"    # 20
    assert standings[1].name == "Alice"  # 10
    assert standings[2].name == "Charlie"# 5


def test_driver_standings_use_countback_on_tied_points():
    teams = [
        Team(id=1, name="Team A", country="UK", points=0),
        Team(id=2, name="Team B", country="IT", points=0),
    ]
    drivers = [
        Driver(id=1, name="Alice", age=20, country="UK", team_id=1, points=10),
        Driver(id=2, name="Bob", age=20, country="UK", team_id=2, points=10),
    ]
    state = create_mock_state(year=1998, teams=teams, drivers=drivers)
    state.driver_season_results = {
        1998: {
            1: [{"round": 1, "position": 1}],
            2: [{"round": 1, "position": 2}],
        }
    }

    standings = StandingsManager().get_driver_standings(state)

    assert standings[0].name == "Alice"
    assert standings[1].name == "Bob"


def test_driver_standings_zero_point_tie_uses_best_finish():
    teams = [
        Team(id=1, name="Team A", country="UK", points=0),
    ]
    drivers = [
        Driver(id=1, name="Alice", age=20, country="UK", team_id=1, points=0),
        Driver(id=2, name="Bob", age=20, country="UK", team_id=1, points=0),
        Driver(id=3, name="Charlie", age=20, country="UK", team_id=1, points=0),
    ]
    state = create_mock_state(year=1998, teams=teams, drivers=drivers)
    state.driver_season_results = {
        1998: {
            1: [{"round": 1, "position": 7}],
            2: [{"round": 1, "position": 9}],
        }
    }

    standings = StandingsManager().get_driver_standings(state)

    assert [driver.name for driver in standings] == ["Alice", "Bob", "Charlie"]


def test_driver_standings_excludes_unassigned_and_inactive_drivers():
    teams = [
        Team(id=1, name="Team A", country="UK", points=0),
    ]
    drivers = [
        Driver(id=1, name="Assigned Active", age=25, country="UK", team_id=1, points=8, active=True),
        Driver(id=2, name="Free Agent", age=28, country="DE", team_id=None, points=99, active=True),
        Driver(id=3, name="Retired Driver", age=40, country="FR", team_id=None, points=50, active=False),
    ]
    state = create_mock_state(year=1998, teams=teams, drivers=drivers)

    manager = StandingsManager()
    standings = manager.get_driver_standings(state)

    assert len(standings) == 1
    assert standings[0].name == "Assigned Active"

def test_constructor_standings_order():
    teams = [
        Team(id=1, name="Ferrari", country="IT", points=50),
        Team(id=2, name="McLaren", country="UK", points=80)
    ]
    state = create_mock_state(year=1998, teams=teams, drivers=[])
    
    manager = StandingsManager()
    standings = manager.get_constructor_standings(state)
    
    assert standings[0].name == "McLaren"
    assert standings[1].name == "Ferrari"


def test_constructor_standings_uses_countback_on_tied_points():
    teams = [
        Team(id=1, name="Team A", country="UK", points=10),
        Team(id=2, name="Team B", country="IT", points=10),
    ]
    drivers = [
        Driver(id=1, name="A1", age=25, country="UK", team_id=1),
        Driver(id=2, name="A2", age=25, country="UK", team_id=1),
        Driver(id=3, name="B1", age=25, country="IT", team_id=2),
        Driver(id=4, name="B2", age=25, country="IT", team_id=2),
    ]
    state = create_mock_state(year=1998, teams=teams, drivers=drivers)
    state.driver_season_results = {
        1998: {
            1: [{"round": 1, "position": 1}],
            2: [{"round": 1, "position": 8}],
            3: [{"round": 1, "position": 2}],
            4: [{"round": 1, "position": 2}],
        }
    }

    standings = StandingsManager().get_constructor_standings(state)

    assert standings[0].name == "Team A"
    assert standings[1].name == "Team B"


def test_constructor_standings_orders_zero_point_teams_by_best_finish():
    teams = [
        Team(id=1, name="Team A", country="UK", points=0),
        Team(id=2, name="Team B", country="IT", points=0),
        Team(id=3, name="Team C", country="DE", points=0),
    ]
    drivers = [
        Driver(id=1, name="A1", age=25, country="UK", team_id=1),
        Driver(id=2, name="A2", age=25, country="UK", team_id=1),
        Driver(id=3, name="B1", age=25, country="IT", team_id=2),
        Driver(id=4, name="B2", age=25, country="IT", team_id=2),
        Driver(id=5, name="C1", age=25, country="DE", team_id=3),
        Driver(id=6, name="C2", age=25, country="DE", team_id=3),
    ]
    state = create_mock_state(year=1998, teams=teams, drivers=drivers)
    state.driver_season_results = {
        1998: {
            1: [{"round": 1, "position": 7}],
            3: [{"round": 1, "position": 9}],
            5: [{"round": 1, "position": 10}],
        }
    }

    standings = StandingsManager().get_constructor_standings(state)

    assert [team.name for team in standings] == ["Team A", "Team B", "Team C"]


def test_constructor_countback_notes_show_team_best_result():
    teams = [
        Team(id=1, name="Team A", country="UK", points=0),
        Team(id=2, name="Team B", country="IT", points=0),
    ]
    drivers = [
        Driver(id=1, name="A1", age=25, country="UK", team_id=1),
        Driver(id=2, name="A2", age=25, country="UK", team_id=1),
        Driver(id=3, name="B1", age=25, country="IT", team_id=2),
        Driver(id=4, name="B2", age=25, country="IT", team_id=2),
    ]
    state = create_mock_state(year=1998, teams=teams, drivers=drivers)
    state.driver_season_results = {
        1998: {
            1: [{"round": 1, "position": 16}],
            3: [{"round": 1, "position": 17}],
        }
    }

    manager = StandingsManager()
    standings = manager.get_constructor_standings(state)
    notes = manager.build_constructor_countback_notes(state, standings)

    assert notes[1] == "x1 P16"
    assert notes[2] == "x1 P17"


def test_driver_countback_notes_show_driver_best_result():
    teams = [
        Team(id=1, name="Team A", country="UK", points=0),
    ]
    drivers = [
        Driver(id=1, name="Alice", age=20, country="UK", team_id=1, points=0),
        Driver(id=2, name="Bob", age=20, country="UK", team_id=1, points=0),
    ]
    state = create_mock_state(year=1998, teams=teams, drivers=drivers)
    state.driver_season_results = {
        1998: {
            1: [{"round": 1, "position": 17}],
            2: [{"round": 1, "position": 18}],
        }
    }

    manager = StandingsManager()
    standings = manager.get_driver_standings(state)
    notes = manager.build_driver_countback_notes(state, standings)

    assert notes[1] == "x1 P17"
    assert notes[2] == "x1 P18"
