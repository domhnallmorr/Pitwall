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
