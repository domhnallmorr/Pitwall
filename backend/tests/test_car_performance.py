from unittest.mock import patch

from app.core.car_performance import CarPerformanceManager
from app.models.calendar import Calendar
from app.models.state import GameState
from app.models.team import Team
from app.models.technical_director import TechnicalDirector


@patch("app.core.car_performance.random.randint", return_value=0)
def test_calculate_next_speed_uses_four_term_average(mock_randint):
    manager = CarPerformanceManager(staff_coeff=0.4)
    # workforce -> 250 * 0.4 = 100
    # (100 + 75 + 80 + 0) / 4 = 63.75 -> round = 64
    speed = manager.calculate_next_speed(workforce=250, facilities=75, technical_director_skill=80)
    assert speed == 64


@patch("app.core.car_performance.random.randint", return_value=-30)
def test_calculate_next_speed_clamps_to_minimum(mock_randint):
    manager = CarPerformanceManager(staff_coeff=0.4)
    speed = manager.calculate_next_speed(workforce=0, facilities=0, technical_director_skill=0)
    assert speed == 1


@patch("app.core.car_performance.random.randint", return_value=20)
def test_calculate_next_speed_allows_values_above_hundred(mock_randint):
    manager = CarPerformanceManager(staff_coeff=0.4)
    speed = manager.calculate_next_speed(workforce=500, facilities=100, technical_director_skill=100)
    assert speed == 105


@patch("app.core.car_performance.random.randint", return_value=0)
def test_apply_for_new_season_updates_teams_and_sends_player_email(mock_randint):
    teams = [
        Team(id=1, name="Warrick", country="United Kingdom", workforce=250, facilities=75, car_speed=80),
        Team(id=2, name="Ferano", country="Italy", workforce=230, facilities=70, car_speed=84),
    ]
    tds = [
        TechnicalDirector(id=1, name="Peter Heed", country="United Kingdom", age=52, skill=75, team_id=1),
        TechnicalDirector(id=2, name="Rob Brann", country="United Kingdom", age=48, skill=90, team_id=2),
    ]
    state = GameState(
        year=1999,
        teams=teams,
        drivers=[],
        technical_directors=tds,
        calendar=Calendar(events=[], current_week=1),
        circuits=[],
        player_team_id=1,
    )

    updates = CarPerformanceManager().apply_for_new_season(state)

    assert len(updates) == 2
    assert teams[0].car_speed == 62  # (100 + 75 + 75 + 0)/4
    assert teams[1].car_speed == 63  # (92 + 70 + 90 + 0)/4

    emails = [e for e in state.emails if e.subject.startswith("New Car Performance:")]
    assert len(emails) == 1
    assert "Previous rating: 80" in emails[0].body
    assert "New rating: 62" in emails[0].body
