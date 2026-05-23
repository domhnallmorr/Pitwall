import logging
from typing import Callable, TypeVar

from app.models.state import GameState


T = TypeVar("T")


def error_response(message: str, response_type: str | None = None):
    payload = {"status": "error", "message": message}
    if response_type:
        payload["type"] = response_type
    return payload


def success_response(response_type: str, data):
    return {"type": response_type, "status": "success", "data": data}


def state_error_response(state: GameState, message: str, response_type: str | None = None):
    return state, error_response(message, response_type=response_type)


def state_success_response(state: GameState, response_type: str, data):
    return state, success_response(response_type, data)


def require_value(value: T | None, message: str) -> T:
    if value is None:
        raise ValueError(message)
    return value


def require_text(value: str | None, message: str):
    if not value:
        raise ValueError(message)
    return value


def run_handler(logger: logging.Logger, error_message: str, action: Callable, response_type: str | None = None):
    try:
        return action()
    except ValueError as exc:
        return error_response(str(exc), response_type=response_type)
    except Exception as exc:
        logger.error(f"{error_message}: {exc}")
        return error_response(str(exc), response_type=response_type)


def run_state_handler(
    state: GameState,
    logger: logging.Logger,
    error_message: str,
    action: Callable,
    response_type: str | None = None,
):
    try:
        return action()
    except ValueError as exc:
        return state_error_response(state, str(exc), response_type=response_type)
    except Exception as exc:
        logger.error(f"{error_message}: {exc}")
        return state_error_response(state, str(exc), response_type=response_type)
