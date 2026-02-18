from pathlib import Path

from app.core.save_manager import save_game, load_game, has_save
from app.models.state import GameState
from app.models.calendar import Calendar
from app.models.team import Team
from app.models.driver import Driver


def create_state() -> GameState:
    return GameState(
        year=1998,
        teams=[Team(id=1, name="Warrick", country="United Kingdom", driver1_id=1, driver2_id=2, car_speed=80)],
        drivers=[
            Driver(id=1, name="John Newhouse", age=27, country="Canada", team_id=1, speed=84, race_starts=33, wins=11),
            Driver(id=2, name="Henrik Friedrich", age=31, country="Germany", team_id=1, speed=72, race_starts=65, wins=1),
        ],
        calendar=Calendar(events=[], current_week=1),
        circuits=[],
        player_team_id=1,
    )


def test_save_and_load_round_trip(tmp_path: Path):
    state = create_state()
    save_path = tmp_path / "autosave.json"

    saved = save_game(state, path=str(save_path))
    loaded = load_game(path=str(save_path))

    assert saved == str(save_path)
    assert loaded.year == 1998
    assert loaded.player_team_id == 1
    assert loaded.drivers[0].race_starts == 33
    assert loaded.drivers[0].wins == 11


def test_has_save_true_and_false(tmp_path: Path):
    state = create_state()
    save_path = tmp_path / "autosave.json"

    assert has_save(path=str(save_path)) is False
    save_game(state, path=str(save_path))
    assert has_save(path=str(save_path)) is True
