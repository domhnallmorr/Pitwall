from app.core.standings import StandingsManager
from app.models.state import GameState
from app.models.driver import Driver
from app.models.team import Team

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
    state = GameState(year=1998, teams=teams, drivers=drivers)
    
    # Action
    manager = StandingsManager()
    manager.reset_season(state)
    
    # Assert
    assert all(d.points == 0 for d in state.drivers)
    assert all(t.points == 0 for t in state.teams)

def test_driver_standings_order():
    drivers = [
        Driver(id=1, name="Alice", age=20, country="UK", points=10),
        Driver(id=2, name="Bob", age=20, country="UK", points=20),
        Driver(id=3, name="Charlie", age=20, country="UK", points=5)
    ]
    state = GameState(year=1998, teams=[], drivers=drivers)
    
    manager = StandingsManager()
    standings = manager.get_driver_standings(state)
    
    assert standings[0].name == "Bob"    # 20
    assert standings[1].name == "Alice"  # 10
    assert standings[2].name == "Charlie"# 5

def test_constructor_standings_order():
    teams = [
        Team(id=1, name="Ferrari", country="IT", points=50),
        Team(id=2, name="McLaren", country="UK", points=80)
    ]
    state = GameState(year=1998, teams=teams, drivers=[])
    
    manager = StandingsManager()
    standings = manager.get_constructor_standings(state)
    
    assert standings[0].name == "McLaren"
    assert standings[1].name == "Ferrari"
