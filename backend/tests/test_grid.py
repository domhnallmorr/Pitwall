import pytest
from app.core.grid import GridManager
from app.models.state import GameState
from app.models.driver import Driver
from app.models.team import Team
from app.models.calendar import Calendar

def create_mock_state():
    drivers = [
        Driver(id=1, name="Driver A", age=20, country="UK", points=0),
        Driver(id=2, name="Driver B", age=22, country="DE", points=0)
    ]
    teams = [
        Team(id=1, name="Team 1", country="UK", driver1_id=1, driver2_id=2, points=0),
        Team(id=2, name="Team 2", country="IT", driver1_id=None, driver2_id=None, points=0)
    ]
    calendar = Calendar(events=[], current_week=1)
    return GameState(year=1998, teams=teams, drivers=drivers, calendar=calendar, circuits=[])

def test_grid_dataframe_structure():
    state = create_mock_state()
    manager = GridManager()
    
    df = manager.get_grid_dataframe(state)
    
    assert len(df) == 2
    assert "Team" in df.columns
    assert "Driver1" in df.columns
    assert "Driver2" in df.columns
    
    # Check Team 1 (Full)
    row1 = df[df["Team"] == "Team 1"].iloc[0]
    assert row1["Driver1"] == "Driver A"
    assert row1["Driver2"] == "Driver B"
    
    # Check Team 2 (Vacant)
    row2 = df[df["Team"] == "Team 2"].iloc[0]
    assert row2["Driver1"] == "VACANT"
    assert row2["Driver2"] == "VACANT"

def test_grid_json_output():
    state = create_mock_state()
    manager = GridManager()
    
    json_output = manager.get_grid_json(state)
    assert isinstance(json_output, str)
    assert "Driver A" in json_output
    assert "VACANT" in json_output
