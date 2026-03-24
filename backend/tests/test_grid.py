import pytest
from app.core.grid import GridManager
from app.models.state import GameState
from app.models.driver import Driver
from app.models.team import Team
from app.models.commercial_manager import CommercialManager
from app.models.technical_director import TechnicalDirector
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
    assert "TechnicalDirector" in df.columns
    
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


def test_grid_dataframe_uses_year_snapshot_when_available():
    state = create_mock_state()
    manager = GridManager()
    state.grid_snapshots[1999] = [
        {"Team": "Team 1", "Country": "UK", "Driver1": "Next Driver 1", "Driver2": "Next Driver 2", "TechnicalDirector": "VACANT"},
        {"Team": "Team 2", "Country": "IT", "Driver1": "Next Driver 3", "Driver2": "VACANT", "TechnicalDirector": "VACANT"},
    ]

    df = manager.get_grid_dataframe(state, year=1999)

    row1 = df[df["Team"] == "Team 1"].iloc[0]
    assert row1["Driver1"] == "Next Driver 1"
    assert row1["Driver2"] == "Next Driver 2"
    assert row1["TechnicalDirector"] == "VACANT"


def test_grid_next_year_projection_excludes_retiring_drivers():
    drivers = [
        Driver(id=1, name="Retiring Driver", age=38, country="UK", points=0, team_id=1, retirement_year=1998),
        Driver(id=2, name="Staying Driver", age=24, country="DE", points=0, team_id=1),
    ]
    teams = [
        Team(id=1, name="Team 1", country="UK", driver1_id=1, driver2_id=2, points=0),
    ]
    calendar = Calendar(events=[], current_week=1)
    state = GameState(year=1998, teams=teams, drivers=drivers, calendar=calendar, circuits=[])
    manager = GridManager()

    df = manager.get_grid_dataframe(state, year=1999)

    row = df[df["Team"] == "Team 1"].iloc[0]
    assert row["Driver1"] == "VACANT"
    assert row["Driver2"] == "Staying Driver"


def test_grid_next_year_projection_marks_one_year_contract_as_vacant():
    drivers = [
        Driver(id=1, name="Expiring Driver", age=29, country="UK", points=0, team_id=1, contract_length=1),
        Driver(id=2, name="Secure Driver", age=24, country="DE", points=0, team_id=1, contract_length=3),
    ]
    teams = [
        Team(id=1, name="Team 1", country="UK", driver1_id=1, driver2_id=2, points=0),
    ]
    calendar = Calendar(events=[], current_week=1)
    state = GameState(year=1998, teams=teams, drivers=drivers, calendar=calendar, circuits=[])

    df = GridManager().get_grid_dataframe(state, year=1999)

    row = df[df["Team"] == "Team 1"].iloc[0]
    assert row["Driver1"] == "VACANT"
    assert row["Driver2"] == "Secure Driver"


def test_grid_next_year_projection_marks_expiring_commercial_manager_as_vacant():
    drivers = [
        Driver(id=1, name="Driver One", age=29, country="UK", points=0, team_id=1, contract_length=3),
        Driver(id=2, name="Driver Two", age=24, country="DE", points=0, team_id=1, contract_length=3),
    ]
    teams = [
        Team(id=1, name="Team 1", country="UK", driver1_id=1, driver2_id=2, points=0, commercial_manager_id=10),
    ]
    commercial_managers = [
        CommercialManager(id=10, name="CM Expiring", country="UK", age=40, skill=70, contract_length=1, salary=100_000, team_id=1),
    ]
    calendar = Calendar(events=[], current_week=1)
    state = GameState(
        year=1998,
        teams=teams,
        drivers=drivers,
        calendar=calendar,
        circuits=[],
        commercial_managers=commercial_managers,
    )

    df = GridManager().get_grid_dataframe(state, year=1999)
    row = df[df["Team"] == "Team 1"].iloc[0]
    assert row["CommercialManager"] == "VACANT"


def test_grid_next_year_projection_marks_expiring_title_sponsor_as_vacant():
    drivers = [
        Driver(id=1, name="Driver One", age=29, country="UK", points=0, team_id=1, contract_length=3),
        Driver(id=2, name="Driver Two", age=24, country="DE", points=0, team_id=1, contract_length=3),
    ]
    teams = [
        Team(
            id=1,
            name="Team 1",
            country="UK",
            driver1_id=1,
            driver2_id=2,
            points=0,
            title_sponsor_name="Windale",
            title_sponsor_contract_length=1,
        ),
    ]
    calendar = Calendar(events=[], current_week=1)
    state = GameState(year=1998, teams=teams, drivers=drivers, calendar=calendar, circuits=[])

    df = GridManager().get_grid_dataframe(state, year=1999)
    row = df[df["Team"] == "Team 1"].iloc[0]
    assert row["TitleSponsor"] == "VACANT"
    assert row["TitleSponsorContractLength"] == 0


def test_grid_next_year_projection_decrements_title_sponsor_contract_length():
    drivers = [
        Driver(id=1, name="Driver One", age=29, country="UK", points=0, team_id=1, contract_length=3),
        Driver(id=2, name="Driver Two", age=24, country="DE", points=0, team_id=1, contract_length=3),
    ]
    teams = [
        Team(
            id=1,
            name="Team 1",
            country="UK",
            driver1_id=1,
            driver2_id=2,
            points=0,
            title_sponsor_name="Windale",
            title_sponsor_contract_length=4,
        ),
    ]
    calendar = Calendar(events=[], current_week=1)
    state = GameState(year=1998, teams=teams, drivers=drivers, calendar=calendar, circuits=[])

    df = GridManager().get_grid_dataframe(state, year=1999)
    row = df[df["Team"] == "Team 1"].iloc[0]
    assert row["TitleSponsor"] == "Windale"
    assert row["TitleSponsorContractLength"] == 3


def test_grid_next_year_projection_marks_expiring_technical_director_as_vacant():
    drivers = [
        Driver(id=1, name="Driver One", age=29, country="UK", points=0, team_id=1, contract_length=3),
        Driver(id=2, name="Driver Two", age=24, country="DE", points=0, team_id=1, contract_length=3),
    ]
    teams = [
        Team(id=1, name="Team 1", country="UK", driver1_id=1, driver2_id=2, points=0, technical_director_id=10),
    ]
    technical_directors = [
        TechnicalDirector(
            id=10,
            name="TD Expiring",
            country="UK",
            age=45,
            skill=80,
            salary=200_000,
            contract_length=1,
            team_id=1,
        ),
    ]
    calendar = Calendar(events=[], current_week=1)
    state = GameState(
        year=1998,
        teams=teams,
        drivers=drivers,
        calendar=calendar,
        circuits=[],
        technical_directors=technical_directors,
    )

    df = GridManager().get_grid_dataframe(state, year=1999)
    row = df[df["Team"] == "Team 1"].iloc[0]
    assert row["TechnicalDirector"] == "VACANT"


def test_grid_next_year_projection_marks_inactive_technical_director_as_vacant():
    drivers = [
        Driver(id=1, name="Driver One", age=29, country="UK", points=0, team_id=1, contract_length=3),
        Driver(id=2, name="Driver Two", age=24, country="DE", points=0, team_id=1, contract_length=3),
    ]
    teams = [
        Team(id=1, name="Team 1", country="UK", driver1_id=1, driver2_id=2, points=0, technical_director_id=10),
    ]
    technical_directors = [
        TechnicalDirector(
            id=10,
            name="TD Retiring",
            country="UK",
            age=62,
            skill=80,
            salary=200_000,
            contract_length=2,
            team_id=1,
            active=False,
            retirement_year=1998,
            retired_year=1998,
        ),
    ]
    calendar = Calendar(events=[], current_week=1)
    state = GameState(
        year=1998,
        teams=teams,
        drivers=drivers,
        calendar=calendar,
        circuits=[],
        technical_directors=technical_directors,
    )

    df = GridManager().get_grid_dataframe(state, year=1999)
    row = df[df["Team"] == "Team 1"].iloc[0]
    assert row["TechnicalDirector"] == "VACANT"


def test_grid_includes_engine_and_tyre_supplier_columns():
    drivers = [
        Driver(id=1, name="Driver A", age=20, country="UK", points=0),
        Driver(id=2, name="Driver B", age=22, country="DE", points=0),
    ]
    teams = [
        Team(
            id=1,
            name="Team 1",
            country="UK",
            driver1_id=1,
            driver2_id=2,
            engine_supplier_name="Mechatron",
            engine_supplier_deal="customer",
            tyre_supplier_name="Greatday",
            tyre_supplier_deal="partner",
        ),
    ]
    calendar = Calendar(events=[], current_week=1)
    state = GameState(year=1998, teams=teams, drivers=drivers, calendar=calendar, circuits=[])

    rows = GridManager().get_grid_records(state)
    assert len(rows) == 1
    assert rows[0]["EngineSupplier"] == "Mechatron"
    assert rows[0]["EngineSupplierDeal"] == "customer"
    assert rows[0]["TyreSupplier"] == "Greatday"
    assert rows[0]["TyreSupplierDeal"] == "partner"
