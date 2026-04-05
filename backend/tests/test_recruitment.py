from unittest.mock import patch

from app.core.recruitment import RecruitmentManager
from app.models.calendar import Calendar
from app.models.driver import Driver
from app.models.state import GameState
from app.models.team import Team
from app.models.enums import DriverRole


def create_recruitment_state():
    teams = [
        Team(id=1, name="Team A", country="UK", driver1_id=None, driver2_id=2, points=0),
        Team(id=2, name="Team B", country="IT", driver1_id=None, driver2_id=None, points=0),
    ]
    drivers = [
        Driver(id=2, name="Contracted Driver", age=30, country="FR", team_id=1, role=DriverRole.DRIVER_2),
        Driver(id=10, name="Free Agent 1", age=27, country="DE"),
        Driver(id=11, name="Free Agent 2", age=24, country="ES"),
        Driver(id=12, name="Free Agent 3", age=22, country="BR"),
    ]
    return GameState(year=1998, teams=teams, drivers=drivers, calendar=Calendar(events=[], current_week=1), circuits=[])


@patch("app.core.recruitment.random.choice", side_effect=lambda choices: choices[0])
def test_recruitment_fills_vacancies_from_free_agents(mock_choice):
    state = create_recruitment_state()
    manager = RecruitmentManager()

    signings = manager.fill_vacancies(state)

    # 3 vacant seats should be filled by the 3 free agents.
    assert len(signings) == 3
    assert state.teams[0].driver1_id is not None
    assert state.teams[1].driver1_id is not None
    assert state.teams[1].driver2_id is not None

    # No duplicate assignments.
    assigned_ids = [state.teams[0].driver1_id, state.teams[0].driver2_id, state.teams[1].driver1_id, state.teams[1].driver2_id]
    assigned_ids = [i for i in assigned_ids if i is not None]
    assert len(assigned_ids) == len(set(assigned_ids))

    # Signed drivers are no longer free agents.
    free_agents_remaining = [d for d in state.drivers if d.active and d.team_id is None]
    assert len(free_agents_remaining) == 0


def test_recruitment_prioritizes_protected_driver_for_vacancy():
    teams = [
        Team(id=1, name="Team A", country="UK", driver1_id=None, driver2_id=2, points=0),
    ]
    drivers = [
        Driver(id=2, name="Contracted Driver", age=30, country="FR", team_id=1, role=DriverRole.DRIVER_2),
        Driver(id=10, name="Champion", age=29, country="DE", speed=95),
        Driver(id=11, name="Weaker Free Agent", age=24, country="ES", speed=60),
    ]
    state = GameState(
        year=2000,
        teams=teams,
        drivers=drivers,
        calendar=Calendar(events=[], current_week=1),
        circuits=[],
        driver_season_results={
            1999: {
                10: [{"round": 1, "event_name": "A", "position": 1, "status": "FINISHED"}],
            }
        },
    )

    signings = RecruitmentManager().fill_vacancies(state)

    assert len(signings) == 1
    assert state.teams[0].driver1_id == 10


def test_recruitment_bumps_weak_ai_driver_to_keep_protected_driver_on_grid():
    teams = [
        Team(id=1, name="Player Team", country="UK", driver1_id=1, driver2_id=2, points=0),
        Team(id=2, name="AI Team", country="IT", driver1_id=3, driver2_id=4, points=0),
    ]
    drivers = [
        Driver(id=1, name="Player Driver 1", age=30, country="UK", team_id=1, role=DriverRole.DRIVER_1, speed=80),
        Driver(id=2, name="Player Driver 2", age=31, country="UK", team_id=1, role=DriverRole.DRIVER_2, speed=78),
        Driver(id=3, name="Weak AI Driver", age=28, country="IT", team_id=2, role=DriverRole.DRIVER_1, speed=40),
        Driver(id=4, name="Other AI Driver", age=29, country="IT", team_id=2, role=DriverRole.DRIVER_2, speed=55),
        Driver(id=10, name="Recent Champion", age=29, country="DE", team_id=None, speed=96, active=True),
    ]
    state = GameState(
        year=2002,
        teams=teams,
        drivers=drivers,
        calendar=Calendar(events=[], current_week=1),
        circuits=[],
        player_team_id=1,
        driver_season_results={
            2001: {
                10: [
                    {"round": 1, "event_name": "A", "position": 1, "status": "FINISHED"},
                    {"round": 2, "event_name": "B", "position": 1, "status": "FINISHED"},
                ],
            }
        },
    )

    signings = RecruitmentManager().fill_vacancies(state)

    assert len(signings) == 1
    ai_team = next(team for team in state.teams if team.id == 2)
    assert 10 in {ai_team.driver1_id, ai_team.driver2_id}
    displaced = next(driver for driver in state.drivers if driver.id == 3)
    assert displaced.team_id is None


def test_recruitment_prefers_top_team_vacancy_for_elite_driver():
    teams = [
        Team(id=1, name="Weak Team", country="UK", driver1_id=None, driver2_id=2, points=5, car_speed=48),
        Team(id=2, name="Top Team", country="IT", driver1_id=None, driver2_id=3, points=90, car_speed=85),
        Team(id=3, name="Top Team 2", country="DE", driver1_id=4, driver2_id=5, points=80, car_speed=82),
        Team(id=4, name="Top Team 3", country="FR", driver1_id=6, driver2_id=7, points=70, car_speed=80),
        Team(id=5, name="Top Team 4", country="ES", driver1_id=8, driver2_id=9, points=60, car_speed=78),
    ]
    drivers = [
        Driver(id=2, name="Weak Team Driver", age=30, country="FR", team_id=1, role=DriverRole.DRIVER_2),
        Driver(id=3, name="Top Team Driver", age=31, country="IT", team_id=2, role=DriverRole.DRIVER_2),
        Driver(id=4, name="D4", age=30, country="DE", team_id=3, role=DriverRole.DRIVER_1),
        Driver(id=5, name="D5", age=29, country="DE", team_id=3, role=DriverRole.DRIVER_2),
        Driver(id=6, name="D6", age=30, country="FR", team_id=4, role=DriverRole.DRIVER_1),
        Driver(id=7, name="D7", age=29, country="FR", team_id=4, role=DriverRole.DRIVER_2),
        Driver(id=8, name="D8", age=30, country="ES", team_id=5, role=DriverRole.DRIVER_1),
        Driver(id=9, name="D9", age=29, country="ES", team_id=5, role=DriverRole.DRIVER_2),
        Driver(id=10, name="Elite Champion", age=29, country="DE", speed=96),
        Driver(id=11, name="Ordinary Free Agent", age=24, country="BR", speed=60),
    ]
    state = GameState(
        year=2002,
        teams=teams,
        drivers=drivers,
        calendar=Calendar(events=[], current_week=1),
        circuits=[],
        driver_season_results={
            2001: {
                10: [
                    {"round": 1, "event_name": "A", "position": 1, "status": "FINISHED"},
                    {"round": 2, "event_name": "B", "position": 1, "status": "FINISHED"},
                ],
                3: [{"round": 1, "event_name": "A", "position": 2, "status": "FINISHED"}],
            }
        },
    )

    RecruitmentManager().fill_vacancies(state)

    weak_team = next(team for team in state.teams if team.id == 1)
    top_team = next(team for team in state.teams if team.id == 2)
    assert top_team.driver1_id == 10
    assert weak_team.driver1_id != 10


def test_recruitment_bumps_weak_top_team_driver_for_elite_free_agent():
    teams = [
        Team(id=1, name="Top Team", country="UK", driver1_id=1, driver2_id=2, points=100, car_speed=88),
        Team(id=2, name="Top Team 2", country="IT", driver1_id=3, driver2_id=4, points=90, car_speed=84),
        Team(id=3, name="Top Team 3", country="DE", driver1_id=5, driver2_id=6, points=80, car_speed=82),
        Team(id=4, name="Top Team 4", country="FR", driver1_id=7, driver2_id=8, points=70, car_speed=80),
        Team(id=5, name="Midfield", country="ES", driver1_id=9, driver2_id=10, points=10, car_speed=55),
    ]
    drivers = [
        Driver(id=1, name="Weak Top Driver", age=31, country="UK", team_id=1, role=DriverRole.DRIVER_1, speed=40),
        Driver(id=2, name="Top Driver 2", age=30, country="UK", team_id=1, role=DriverRole.DRIVER_2, speed=82),
        Driver(id=3, name="Top Driver 3", age=30, country="IT", team_id=2, role=DriverRole.DRIVER_1, speed=80),
        Driver(id=4, name="Top Driver 4", age=29, country="IT", team_id=2, role=DriverRole.DRIVER_2, speed=78),
        Driver(id=5, name="Top Driver 5", age=30, country="DE", team_id=3, role=DriverRole.DRIVER_1, speed=77),
        Driver(id=6, name="Top Driver 6", age=29, country="DE", team_id=3, role=DriverRole.DRIVER_2, speed=76),
        Driver(id=7, name="Top Driver 7", age=30, country="FR", team_id=4, role=DriverRole.DRIVER_1, speed=75),
        Driver(id=8, name="Top Driver 8", age=29, country="FR", team_id=4, role=DriverRole.DRIVER_2, speed=74),
        Driver(id=9, name="Mid Driver 1", age=30, country="ES", team_id=5, role=DriverRole.DRIVER_1, speed=65),
        Driver(id=10, name="Mid Driver 2", age=29, country="ES", team_id=5, role=DriverRole.DRIVER_2, speed=64),
        Driver(id=20, name="Recent Champion", age=29, country="BR", team_id=None, speed=96, active=True),
    ]
    state = GameState(
        year=2002,
        teams=teams,
        drivers=drivers,
        calendar=Calendar(events=[], current_week=1),
        circuits=[],
        driver_season_results={
            2001: {
                20: [
                    {"round": 1, "event_name": "A", "position": 1, "status": "FINISHED"},
                    {"round": 2, "event_name": "B", "position": 1, "status": "FINISHED"},
                ],
            }
        },
    )

    RecruitmentManager().fill_vacancies(state)

    top_team = next(team for team in state.teams if team.id == 1)
    assert 20 in {top_team.driver1_id, top_team.driver2_id}
    weak_driver = next(driver for driver in state.drivers if driver.id == 1)
    assert weak_driver.team_id is None
