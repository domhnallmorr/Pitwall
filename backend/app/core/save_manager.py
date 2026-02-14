import os
import json
import logging
from app.models.state import GameState

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves")
AUTOSAVE_PATH = os.path.join(SAVE_DIR, "autosave.json")


def save_game(state: GameState, path: str = None) -> str:
    """
    Save the current game state to a JSON file.
    Returns the path the file was saved to.
    """
    save_path = path or AUTOSAVE_PATH
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(save_path, "w") as f:
        f.write(state.model_dump_json(indent=2))

    logging.info(f"Game saved to {save_path}")
    return save_path


def load_game(path: str = None) -> GameState:
    """
    Load a game state from a JSON file.
    Returns the reconstructed GameState.
    """
    load_path = path or AUTOSAVE_PATH

    if not os.path.exists(load_path):
        raise FileNotFoundError(f"No save file found at {load_path}")

    with open(load_path, "r") as f:
        data = f.read()

    state = GameState.model_validate_json(data)
    logging.info(f"Game loaded from {load_path}")
    return state


def has_save(path: str = None) -> bool:
    """Check if a save file exists."""
    return os.path.exists(path or AUTOSAVE_PATH)
