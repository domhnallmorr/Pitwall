import pytest
from pw_model.car_development.car_development_model import (
    CarDevelopmentModel,
    CarDevelopmentEnums,
    CarDevelopmentStatusEnums,
)
from pw_model.finance.car_development_costs import CarDevelopmentCostsEnums

# Dummy classes to simulate dependencies

class DummyInbox:
    def __init__(self):
        self.started_emails = []
        self.completed_emails = []
        self.ai_completed_emails = []
    
    def generate_car_development_started_email(self, development_type, time_left, cost):
        self.started_emails.append((development_type, time_left, cost))
    
    def generate_car_development_completed_email(self, development_type, speed_increase):
        self.completed_emails.append((development_type, speed_increase))
    
    def generate_ai_development_completed_email(self, development_type, team_name):
        self.ai_completed_emails.append((development_type, team_name))

class DummyCarModel:
    def __init__(self):
        self.speed_updates = []
    
    def implement_car_development(self, speed_increase):
        self.speed_updates.append(speed_increase)
    
    def update_speed(self, speed):
        self.speed_updates.append(speed)

class DummyCarDevelopmentCostsModel:
    def __init__(self):
        self.calls = []
    
    def start_development(self, total_cost, weeks):
        self.calls.append((total_cost, weeks))

class DummyFinanceModel:
    def __init__(self):
        self.car_development_costs_model = DummyCarDevelopmentCostsModel()

class DummyGameData:
    def __init__(self, current_week=1):
        self._current_week = current_week
    
    def current_week(self):
        return self._current_week

class DummyCalendar:
    def __init__(self, race_weeks):
        self.race_weeks = race_weeks

class DummySeason:
    def __init__(self, race_weeks):
        self.calendar = DummyCalendar(race_weeks)

class DummyModel:
    def __init__(self, current_week=1, race_weeks=None):
        if race_weeks is None:
            # Default race weeks: first week is skipped in AI update generation
            race_weeks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.inbox = DummyInbox()
        self.game_data = DummyGameData(current_week)
        self.season = DummySeason(race_weeks)

class DummyTeamModel:
    def __init__(self, model, is_player_team=True, team_name="Test Team"):
        self.model = model
        self._is_player_team = is_player_team
        self.name = team_name
        self.car_model = DummyCarModel()
        self.finance_model = DummyFinanceModel()
    
    @property
    def is_player_team(self):
        return self._is_player_team

# Tests for CarDevelopmentModel

def test_start_development_player_team():
    model = DummyModel()
    team_model = DummyTeamModel(model, is_player_team=True, team_name="Player Team")
    car_dev = CarDevelopmentModel(model, team_model)
    
    # Start development with MINOR update type.
    car_dev.start_development(CarDevelopmentEnums.MINOR)
    
    # Verify development type, status and time_left are set correctly.
    assert car_dev.current_development_type == CarDevelopmentEnums.MINOR
    assert car_dev.current_status == CarDevelopmentStatusEnums.IN_PROGRESS
    assert car_dev.time_left == 5
    
    # Check that the correct cost and weeks are passed to the finance model.
    expected_cost = CarDevelopmentCostsEnums.MINOR.value
    assert team_model.finance_model.car_development_costs_model.calls == [(expected_cost, 5)]
    
    # Verify that a start email was generated.
    assert model.inbox.started_emails == [(CarDevelopmentEnums.MINOR.value, 5, expected_cost)]

def test_advance_player_team_complete_development():
    model = DummyModel()
    team_model = DummyTeamModel(model, is_player_team=True, team_name="Player Team")
    car_dev = CarDevelopmentModel(model, team_model)
    
    # Start development with a MEDIUM update.
    car_dev.start_development(CarDevelopmentEnums.MEDIUM)
    # For quick testing, set time_left to 1.
    car_dev.time_left = 1
    # Calling advance should decrement time_left to 0 and trigger completion.
    car_dev.advance()
    
    # After completion, time_left should be 0 and status should be COMPLETED.
    assert car_dev.time_left == 0
    assert car_dev.current_status == CarDevelopmentStatusEnums.COMPLETED
    
    # complete_development should have implemented car development with a speed increase of 3 (for MEDIUM).
    assert team_model.car_model.speed_updates == [3]
    
    # Verify that a completion email was generated for the player team.
    assert model.inbox.completed_emails == [(CarDevelopmentEnums.MEDIUM.value, 3)]

def test_calculate_speed_increase():
    model = DummyModel()
    team_model = DummyTeamModel(model, is_player_team=True)
    car_dev = CarDevelopmentModel(model, team_model)
    
    # Test speed increase values for each development type.
    car_dev.current_development_type = CarDevelopmentEnums.MINOR
    assert car_dev.calculate_speed_increase() == 1
    
    car_dev.current_development_type = CarDevelopmentEnums.MEDIUM
    assert car_dev.calculate_speed_increase() == 3
    
    car_dev.current_development_type = CarDevelopmentEnums.MAJOR
    assert car_dev.calculate_speed_increase() == 5

def test_advance_ai_team():
    # For an AI-controlled team (non-player), the advance method should trigger implement_ai_update.
    current_week = 3
    model = DummyModel(current_week=current_week)
    team_model = DummyTeamModel(model, is_player_team=False, team_name="AI Team")
    car_dev = CarDevelopmentModel(model, team_model)
    
    # Manually set a planned update that matches the current week.
    car_dev.planned_updates = [(current_week, CarDevelopmentEnums.MAJOR)]
    
    # Calling advance should trigger the AI update.
    car_dev.advance()
    
    # complete_development should be called with a speed increase of 5 (for MAJOR).
    assert team_model.car_model.speed_updates == [5]
    
    # Verify that an AI completed email was generated.
    assert model.inbox.ai_completed_emails == [(CarDevelopmentEnums.MAJOR.value, team_model.name)]

def test_gen_ai_updates():
    # Test that for an AI team, gen_ai_updates populates planned_updates with valid and sorted race weeks.
    # Provide a custom list of race weeks (first week is skipped).
    model = DummyModel(race_weeks=[1, 3, 5, 7, 9])
    team_model = DummyTeamModel(model, is_player_team=False, team_name="AI Team")
    car_dev = CarDevelopmentModel(model, team_model)
    car_dev.planned_updates = []
    # Initially, planned_updates should be empty.
    assert not hasattr(car_dev, 'planned_updates') or car_dev.planned_updates == []
    
    # Generate AI updates.
    car_dev.gen_ai_updates()
    
    # Ensure planned_updates is populated and sorted by week.
    weeks = [week for week, _ in car_dev.planned_updates]
    assert weeks == sorted(weeks)
    # Since race_weeks[1:] is [3, 5, 7, 9], all update weeks should be among these.
    for week in weeks:
        assert week in [3, 5, 7, 9]
