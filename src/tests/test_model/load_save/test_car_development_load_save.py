# tests/test_model/load_save/test_car_development_load_save.py

import sqlite3
from pw_model.car_development.car_development_model import (
    CarDevelopmentEnums,
    CarDevelopmentStatusEnums,
)
from pw_model.load_save.car_development_load_save import (
    save_car_development,
    load_car_development,
)

# --------- Minimal fakes that match what load/save expects ----------

class _FakeCarDev:
    def __init__(self):
        self.current_status = CarDevelopmentStatusEnums.NOT_STARTED
        self.time_left = 0
        self.current_development_type = CarDevelopmentEnums.NONE
        self.car_speed_history = []
        self.planned_updates = []  # list[(int_week, CarDevelopmentEnums)]


class _FakeTeam:
    def __init__(self, name: str):
        self.name = name
        self.car_development_model = _FakeCarDev()


class _FakeEntityManager:
    def __init__(self, teams):
        self._by_name = {t.name: t for t in teams}

    def get_team_model(self, name: str):
        return self._by_name[name]


class _FakeModel:
    """Matches just the attributes the loader/saver touch."""
    def __init__(self, teams, player_team_name: str | None):
        self.teams = teams
        self.player_team = player_team_name
        self.entity_manager = _FakeEntityManager(teams)

    @property
    def player_team_model(self):
        if self.player_team is None:
            return None
        return self.entity_manager.get_team_model(self.player_team)


# ------------------------------- Tests --------------------------------

def test_save_and_load_car_development():
    # Arrange: two teams, TeamA is player
    A = _FakeTeam("TeamA")
    B = _FakeTeam("TeamB")

    # Player fields + histories
    A.car_development_model.current_status = CarDevelopmentStatusEnums.IN_PROGRESS
    A.car_development_model.time_left = 7
    A.car_development_model.current_development_type = CarDevelopmentEnums.MEDIUM
    A.car_development_model.car_speed_history = [50, 52, 53]
    A.car_development_model.planned_updates = [(5, CarDevelopmentEnums.MINOR), (10, CarDevelopmentEnums.MAJOR)]

    # Non-player only history
    B.car_development_model.car_speed_history = [48, 49]

    model = _FakeModel([A, B], player_team_name="TeamA")

    # Use in-memory SQLite
    conn = sqlite3.connect(":memory:")

    # Act: save then blank in-memory state, then load
    save_car_development(model, conn)

    # Blank everything to prove load repopulates
    A.car_development_model.current_status = CarDevelopmentStatusEnums.NOT_STARTED
    A.car_development_model.time_left = 0
    A.car_development_model.current_development_type = CarDevelopmentEnums.NONE
    A.car_development_model.car_speed_history = []
    A.car_development_model.planned_updates = []
    B.car_development_model.car_speed_history = []
    B.car_development_model.planned_updates = []

    load_car_development(conn, model)

    # Assert: player-only fields restored as enums/ints
    assert A.car_development_model.current_status is CarDevelopmentStatusEnums.IN_PROGRESS
    assert A.car_development_model.time_left == 7
    assert A.car_development_model.current_development_type is CarDevelopmentEnums.MEDIUM

    # Histories restored for all teams
    assert A.car_development_model.car_speed_history == [50, 52, 53]
    assert B.car_development_model.car_speed_history == [48, 49]

    # Planned updates restored (only player had them)
    assert A.car_development_model.planned_updates == [(5, CarDevelopmentEnums.MINOR), (10, CarDevelopmentEnums.MAJOR)]
    assert B.car_development_model.planned_updates == []


def test_load_does_not_modify_non_player_status_type_time():
    # Arrange
    A = _FakeTeam("TeamA")
    B = _FakeTeam("TeamB")
    model = _FakeModel([A, B], player_team_name="TeamA")
    conn = sqlite3.connect(":memory:")
    save_car_development(model, conn)

    # Give B some in-memory values that should remain untouched by loader
    B.car_development_model.current_status = CarDevelopmentStatusEnums.COMPLETED
    B.car_development_model.time_left = 99
    B.car_development_model.current_development_type = CarDevelopmentEnums.MAJOR

    # Act
    load_car_development(conn, model)

    # Assert: loader only updates player team for these fields
    assert B.car_development_model.current_status is CarDevelopmentStatusEnums.COMPLETED
    assert B.car_development_model.time_left == 99
    assert B.car_development_model.current_development_type is CarDevelopmentEnums.MAJOR
