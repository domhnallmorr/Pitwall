import sqlite3
import pytest

# Import the functions to test
from pw_model.load_save.car_development_load_save import save_car_development, load_car_development
from pw_model.car_development.car_development_model import CarDevelopmentEnums, CarDevelopmentStatusEnums, CarDevelopmentModel

# Dummy objects to simulate required dependencies

class DummyCarModel:
    def __init__(self):
        self.speed = 0

    def update_speed(self, new_speed: int) -> None:
        self.speed = new_speed

    def implement_car_development(self, speed_increase: int) -> None:
        self.speed += speed_increase

class DummyTeam:
    def __init__(self, name: str, is_player_team: bool = False):
        self.name = name
        self.car_model = DummyCarModel()
        # Create the car development model; we pass None for model since it’s not used here.
        self.car_development_model = CarDevelopmentModel(model=None, team_model=self)
        # For testing, initialize planned_updates explicitly.
        self.car_development_model.planned_updates = []
        self._is_player_team = is_player_team

    @property
    def is_player_team(self) -> bool:
        return self._is_player_team

class DummyModel:
    def __init__(self):
        # Create two teams: one player team and one AI team.
        self.teams = [
            DummyTeam("Team A", is_player_team=True),
            DummyTeam("Team B")
        ]
        self.player_team = "Team A"

    @property
    def player_team_model(self):
        for team in self.teams:
            if team.name == self.player_team:
                return team
        return None

# The actual test function
def test_save_and_load_car_development():
    # Use an in-memory SQLite database
    conn = sqlite3.connect(":memory:")
    
    # Set up the dummy model with initial car development data
    model = DummyModel()
    
    # Set player team car development data
    player_cd = model.player_team_model.car_development_model
    player_cd.current_status = CarDevelopmentStatusEnums.IN_PROGRESS
    player_cd.time_left = 3
    player_cd.current_development_type = CarDevelopmentEnums.MAJOR
    
    # Set planned updates for each team (player and AI)
    model.teams[0].car_development_model.planned_updates = [(1, CarDevelopmentEnums.MINOR)]
    model.teams[1].car_development_model.planned_updates = [(2, CarDevelopmentEnums.MEDIUM)]
    
    # Save the car development data to the database
    save_car_development(model, conn)
    
    # Change the in-memory values so we can verify that load_car_development restores them
    player_cd.current_status = CarDevelopmentStatusEnums.NOT_STARTED
    player_cd.time_left = 0
    player_cd.current_development_type = CarDevelopmentEnums.NONE
    for team in model.teams:
        team.car_development_model.planned_updates = []
    
    # Load the data from the database back into the model
    load_car_development(conn, model)
    
    # Check that the player team's car development values were restored
    assert player_cd.current_status == CarDevelopmentStatusEnums.IN_PROGRESS
    assert player_cd.time_left == 3
    assert player_cd.current_development_type == CarDevelopmentEnums.MAJOR
    
    # Check that planned updates for each team were restored correctly
    assert model.teams[0].car_development_model.planned_updates == [(1, CarDevelopmentEnums.MINOR)]
    assert model.teams[1].car_development_model.planned_updates == [(2, CarDevelopmentEnums.MEDIUM)]
    
    conn.close()
