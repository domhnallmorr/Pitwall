import json
import logging
import sys
from typing import Any, Callable

from app.commands.game_commands import (
    build_finance_payload,
    handle_facilities_upgrade_preview,
    handle_get_engine_negotiation_market,
    handle_get_engine_supplier_replacement_candidates,
    handle_get_manager_replacement_candidates,
    handle_get_race_weekend,
    handle_get_replacement_candidates,
    handle_get_technical_director_replacement_candidates,
    handle_get_title_sponsor_negotiation_market,
    handle_get_tyre_negotiation_market,
    handle_get_title_sponsor_replacement_candidates,
    handle_get_tyre_supplier_replacement_candidates,
    handle_build_spare_set,
    handle_finish_car_development_stage,
    handle_finish_car_development_project_stage,
    handle_load_roster,
    handle_offer_driver,
    handle_repair_chassis_wear,
    handle_book_engine_negotiation_hospitality,
    handle_book_tyre_negotiation_hospitality,
    handle_book_title_sponsor_hospitality,
    handle_replace_commercial_manager,
    handle_replace_driver,
    handle_replace_engine_supplier,
    handle_replace_technical_director,
    handle_replace_title_sponsor,
    handle_replace_tyre_supplier,
    handle_set_race_strategy,
    handle_sign_engine_negotiated_deal,
    handle_sign_tyre_negotiated_deal,
    handle_sign_title_sponsor_negotiated_deal,
    handle_simulate_qualifying,
    handle_simulate_race,
    handle_start_career,
    handle_start_car_development,
    handle_set_construction_allocation,
    handle_start_construction_project,
    handle_set_race_chassis_assignments,
    handle_set_car_development_allocation,
    handle_set_test_chassis,
    handle_start_engine_negotiation,
    handle_start_tyre_negotiation,
    handle_start_facilities_upgrade,
    handle_start_title_sponsor_negotiation,
    handle_update_engine_negotiation_staff,
    handle_update_tyre_negotiation_staff,
    handle_update_title_sponsor_negotiation_staff,
)
from app.commands.query_commands import (
    get_car_payload,
    get_driver_payload,
    get_emails_payload,
    get_facilities_payload,
    get_grid_payload,
    get_home_payload,
    get_staff_payload,
    get_standings_payload,
    read_email_payload,
)
from app.core.engine import GameEngine
from app.core.grid import GridManager
from app.core.save_manager import has_save, load_game as load_game_file, save_game
from app.models.state import GameState

# Configure logging to write to a file, since stdout is used for IPC
logging.basicConfig(filename="backend_debug.log", level=logging.DEBUG)

# Global State Container
CURRENT_STATE: GameState = None


def _error(message: str, *, response_type: str | None = None) -> dict[str, Any]:
    payload = {"status": "error", "message": message}
    if response_type is not None:
        payload["type"] = response_type
    return payload


def _game_not_started(*, response_type: str | None = None) -> dict[str, Any]:
    return _error("Game not started", response_type=response_type)


def _require_state(*, response_type: str | None = None) -> GameState | dict[str, Any]:
    if not CURRENT_STATE:
        return _game_not_started(response_type=response_type)
    return CURRENT_STATE


def _save_if_needed(
    response: dict[str, Any],
    state: GameState,
    *,
    save_on_success: bool = False,
    save_predicate: Callable[[dict[str, Any]], bool] | None = None,
) -> None:
    if response.get("status") != "success":
        return
    if save_predicate is not None:
        if save_predicate(response):
            save_game(state)
        return
    if save_on_success:
        save_game(state)


def _run_state_handler(
    handler: Callable[..., tuple[GameState, dict[str, Any]]],
    *args: Any,
    save_on_success: bool = False,
    save_predicate: Callable[[dict[str, Any]], bool] | None = None,
    response_type_on_missing_state: str | None = None,
) -> dict[str, Any]:
    global CURRENT_STATE
    state_or_error = _require_state(response_type=response_type_on_missing_state)
    if isinstance(state_or_error, dict):
        return state_or_error

    CURRENT_STATE, response = handler(CURRENT_STATE, logging, *args)
    _save_if_needed(response, CURRENT_STATE, save_on_success=save_on_success, save_predicate=save_predicate)
    return response


def _run_response_handler(
    handler: Callable[..., dict[str, Any]],
    *args: Any,
    save_on_success: bool = False,
    response_type_on_missing_state: str | None = None,
) -> dict[str, Any]:
    state_or_error = _require_state(response_type=response_type_on_missing_state)
    if isinstance(state_or_error, dict):
        return state_or_error

    response = handler(CURRENT_STATE, logging, *args)
    _save_if_needed(response, CURRENT_STATE, save_on_success=save_on_success)
    return response


def _run_query(
    build_fn: Callable[..., Any],
    *,
    response_type: str,
    error_context: str,
    builder: Callable[[Any], dict[str, Any]] | None = None,
    args: tuple[Any, ...] = (),
    response_type_on_missing_state: str | None = None,
) -> dict[str, Any]:
    state_or_error = _require_state(response_type=response_type_on_missing_state)
    if isinstance(state_or_error, dict):
        return state_or_error

    try:
        payload = build_fn(CURRENT_STATE, *args)
        if builder is not None:
            return builder(payload)
        return {
            "type": response_type,
            "status": "success",
            "data": payload,
        }
    except Exception as e:
        logging.error(f"Error getting {error_context}: {e}")
        return _error(str(e))


def _build_saved_success_response(response_type: str, payload: Any) -> dict[str, Any]:
    save_game(CURRENT_STATE)
    return {
        "type": response_type,
        "status": "success",
        "data": payload,
    }


def _build_calendar_response() -> dict[str, Any]:
    drivers = getattr(CURRENT_STATE, "drivers", []) or []
    driver_name_by_id = {driver.id: driver.name for driver in drivers}
    winners_by_event: dict[str, str] = {}
    season_results = getattr(CURRENT_STATE, "driver_season_results", {}) or {}
    current_year = getattr(CURRENT_STATE, "year", None)
    for driver_id, results in season_results.get(current_year, {}).items():
        for result in results:
            if result.get("position") != 1:
                continue
            event_name = result.get("event_name")
            if not event_name:
                continue
            winners_by_event[event_name] = driver_name_by_id.get(driver_id, "")

    schedule = CURRENT_STATE.calendar.get_schedule_data(
        CURRENT_STATE.circuits,
        winners_by_event=winners_by_event,
    )
    return {
        "type": "calendar_data",
        "status": "success",
        "data": schedule,
    }


def _build_grid_response(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "grid_data",
        "status": "success",
        "data": json.loads(payload["grid_json"]),
        "year": payload["year"],
    }


def _load_game_response() -> dict[str, Any]:
    global CURRENT_STATE
    try:
        CURRENT_STATE = load_game_file()
        player_team = CURRENT_STATE.player_team
        return {
            "type": "game_loaded",
            "status": "success",
            "data": {
                "team_name": player_team.name if player_team else "Unknown",
                "week_display": CURRENT_STATE.week_display,
                "next_event_display": (
                    "Game Over"
                    if CURRENT_STATE.game_over
                    else ("Career Complete" if CURRENT_STATE.game_completed else CURRENT_STATE.next_event_display)
                ),
                "year": CURRENT_STATE.year,
                "balance": CURRENT_STATE.finance.balance,
                "unread_count": sum(1 for e in CURRENT_STATE.emails if not e.read),
                "game_over": CURRENT_STATE.game_over,
                "game_over_reason": CURRENT_STATE.game_over_reason,
                "game_completed": CURRENT_STATE.game_completed,
                "completion_year": CURRENT_STATE.completion_year,
            },
        }
    except FileNotFoundError:
        return _error("No save file found")
    except Exception as e:
        logging.error(f"Error loading game: {e}")
        return _error(str(e))


def process_command(command: dict[str, Any]) -> dict[str, Any]:
    global CURRENT_STATE
    logging.debug(f"Received command: {command}")

    cmd_type = command.get("type")

    if cmd_type == "ping":
        return {"status": "success", "data": "pong"}

    if cmd_type == "load_roster":
        state, response = handle_load_roster(logging)
        if state is not None:
            CURRENT_STATE = state
        return response

    if cmd_type == "start_career":
        CURRENT_STATE, response = handle_start_career(CURRENT_STATE, logging, team_name=command.get("team_name"))
        _save_if_needed(response, CURRENT_STATE, save_on_success=True)
        return response

    if cmd_type == "check_save":
        return {
            "type": "save_status",
            "status": "success",
            "data": {"has_save": has_save()},
        }

    if cmd_type == "load_game":
        return _load_game_response()

    if cmd_type == "get_grid":
        return _run_query(
            get_grid_payload,
            response_type="grid_data",
            error_context="grid",
            builder=_build_grid_response,
            args=(command.get("year"), GridManager()),
        )

    if cmd_type == "get_home":
        return _run_query(get_home_payload, response_type="home_data", error_context="home data")

    if cmd_type == "get_calendar":
        return _run_query(
            lambda _state: _build_calendar_response(),
            response_type="calendar_data",
            error_context="calendar",
            builder=lambda payload: payload,
        )

    if cmd_type == "get_standings":
        return _run_query(get_standings_payload, response_type="standings_data", error_context="standings")

    if cmd_type == "advance_week":
        return _run_query(
            lambda state: GameEngine().advance_week(state),
            response_type="week_advanced",
            error_context="advancing week",
            builder=lambda payload: _build_saved_success_response("week_advanced", payload),
        )

    if cmd_type == "skip_event":
        return _run_query(
            lambda state: GameEngine().handle_event_action(state, "skip"),
            response_type="week_advanced",
            error_context="skipping event",
            builder=lambda payload: _build_saved_success_response("week_advanced", payload),
        )

    if cmd_type == "attend_test":
        return _run_query(
            lambda state: GameEngine().handle_event_action(state, "attend", test_kms=command.get("kms")),
            response_type="week_advanced",
            error_context="attending test",
            builder=lambda payload: _build_saved_success_response("week_advanced", payload),
        )

    if cmd_type == "simulate_race":
        return _run_state_handler(handle_simulate_race, save_on_success=True)

    if cmd_type == "get_race_weekend":
        return _run_state_handler(handle_get_race_weekend)

    if cmd_type == "set_race_strategy":
        return _run_state_handler(handle_set_race_strategy, command.get("strategies"), save_on_success=True)

    if cmd_type == "simulate_qualifying":
        return _run_state_handler(handle_simulate_qualifying, save_on_success=True)

    if cmd_type == "replace_driver":
        return _run_state_handler(
            handle_replace_driver,
            command.get("driver_id"),
            command.get("incoming_driver_id"),
            save_on_success=True,
        )

    if cmd_type == "offer_driver":
        return _run_state_handler(
            handle_offer_driver,
            command.get("driver_id"),
            command.get("incoming_driver_id"),
            command.get("salary_offer"),
            command.get("contract_length"),
            save_predicate=lambda response: response.get("data", {}).get("accepted", False),
        )

    if cmd_type == "replace_commercial_manager":
        return _run_state_handler(
            handle_replace_commercial_manager,
            command.get("manager_id"),
            command.get("incoming_manager_id"),
            save_on_success=True,
        )

    if cmd_type == "replace_technical_director":
        return _run_state_handler(
            handle_replace_technical_director,
            command.get("director_id"),
            command.get("incoming_director_id"),
            save_on_success=True,
        )

    if cmd_type == "replace_title_sponsor":
        return _run_state_handler(
            handle_replace_title_sponsor,
            command.get("sponsor_name"),
            command.get("incoming_sponsor_id"),
            save_on_success=True,
        )

    if cmd_type == "get_title_sponsor_negotiation_market":
        return _run_query(
            lambda state: handle_get_title_sponsor_negotiation_market(state, logging),
            response_type="title_sponsor_negotiation_market",
            error_context="title sponsor negotiation market",
            builder=lambda payload: payload,
        )

    if cmd_type == "start_title_sponsor_negotiation":
        return _run_state_handler(
            handle_start_title_sponsor_negotiation,
            command.get("sponsor_id"),
            save_on_success=True,
        )

    if cmd_type == "update_title_sponsor_negotiation_staff":
        return _run_state_handler(
            handle_update_title_sponsor_negotiation_staff,
            command.get("assigned_staff"),
            save_on_success=True,
        )

    if cmd_type == "sign_title_sponsor_negotiated_deal":
        return _run_state_handler(handle_sign_title_sponsor_negotiated_deal, save_on_success=True)

    if cmd_type == "book_title_sponsor_hospitality":
        return _run_state_handler(handle_book_title_sponsor_hospitality, save_on_success=True)

    if cmd_type == "replace_engine_supplier":
        return _run_state_handler(
            handle_replace_engine_supplier,
            command.get("supplier_name"),
            command.get("incoming_supplier_id"),
            save_on_success=True,
        )

    if cmd_type == "get_engine_negotiation_market":
        return _run_query(
            lambda state: handle_get_engine_negotiation_market(state, logging),
            response_type="engine_negotiation_market",
            error_context="engine negotiation market",
            builder=lambda payload: payload,
        )

    if cmd_type == "start_engine_negotiation":
        return _run_state_handler(
            handle_start_engine_negotiation,
            command.get("supplier_id"),
            save_on_success=True,
        )

    if cmd_type == "update_engine_negotiation_staff":
        return _run_state_handler(
            handle_update_engine_negotiation_staff,
            command.get("assigned_staff"),
            save_on_success=True,
        )

    if cmd_type == "sign_engine_negotiated_deal":
        return _run_state_handler(
            handle_sign_engine_negotiated_deal,
            command.get("tier"),
            save_on_success=True,
        )

    if cmd_type == "book_engine_negotiation_hospitality":
        return _run_state_handler(handle_book_engine_negotiation_hospitality, save_on_success=True)

    if cmd_type == "get_tyre_negotiation_market":
        return _run_query(
            lambda state: handle_get_tyre_negotiation_market(state, logging),
            response_type="tyre_negotiation_market",
            error_context="tyre negotiation market",
            builder=lambda payload: payload,
        )

    if cmd_type == "start_tyre_negotiation":
        return _run_state_handler(
            handle_start_tyre_negotiation,
            command.get("supplier_id"),
            save_on_success=True,
        )

    if cmd_type == "update_tyre_negotiation_staff":
        return _run_state_handler(
            handle_update_tyre_negotiation_staff,
            command.get("assigned_staff"),
            save_on_success=True,
        )

    if cmd_type == "sign_tyre_negotiated_deal":
        return _run_state_handler(
            handle_sign_tyre_negotiated_deal,
            command.get("tier"),
            save_on_success=True,
        )

    if cmd_type == "book_tyre_negotiation_hospitality":
        return _run_state_handler(handle_book_tyre_negotiation_hospitality, save_on_success=True)

    if cmd_type == "replace_tyre_supplier":
        return _run_state_handler(
            handle_replace_tyre_supplier,
            command.get("supplier_name"),
            command.get("incoming_supplier_id"),
            save_on_success=True,
        )

    if cmd_type == "get_replacement_candidates":
        return _run_query(
            lambda state: handle_get_replacement_candidates(state, logging, command.get("driver_id")),
            response_type="replacement_candidates",
            error_context="replacement candidates",
            builder=lambda payload: payload,
        )

    if cmd_type == "get_manager_replacement_candidates":
        return _run_query(
            lambda state: handle_get_manager_replacement_candidates(state, logging, command.get("manager_id")),
            response_type="manager_replacement_candidates",
            error_context="manager replacement candidates",
            builder=lambda payload: payload,
        )

    if cmd_type == "get_technical_director_replacement_candidates":
        return _run_query(
            lambda state: handle_get_technical_director_replacement_candidates(state, logging, command.get("director_id")),
            response_type="manager_replacement_candidates",
            error_context="technical director replacement candidates",
            builder=lambda payload: payload,
        )

    if cmd_type == "get_title_sponsor_replacement_candidates":
        return _run_query(
            lambda state: handle_get_title_sponsor_replacement_candidates(state, logging, command.get("sponsor_name")),
            response_type="title_sponsor_replacement_candidates",
            error_context="title sponsor replacement candidates",
            builder=lambda payload: payload,
        )

    if cmd_type == "get_engine_supplier_replacement_candidates":
        return _run_query(
            lambda state: handle_get_engine_supplier_replacement_candidates(state, logging, command.get("supplier_name")),
            response_type="engine_supplier_replacement_candidates",
            error_context="engine supplier replacement candidates",
            builder=lambda payload: payload,
        )

    if cmd_type == "get_tyre_supplier_replacement_candidates":
        return _run_query(
            lambda state: handle_get_tyre_supplier_replacement_candidates(state, logging, command.get("supplier_name")),
            response_type="tyre_supplier_replacement_candidates",
            error_context="tyre supplier replacement candidates",
            builder=lambda payload: payload,
        )

    if cmd_type == "preview_facilities_upgrade":
        return _run_response_handler(
            handle_facilities_upgrade_preview,
            command.get("points"),
            command.get("years"),
            response_type_on_missing_state="facilities_upgrade_preview",
        )

    if cmd_type == "start_facilities_upgrade":
        return _run_response_handler(
            handle_start_facilities_upgrade,
            command.get("points"),
            command.get("years"),
            save_on_success=True,
            response_type_on_missing_state="facilities_upgrade_started",
        )

    if cmd_type == "start_car_development":
        return _run_response_handler(
            handle_start_car_development,
            command.get("development_type"),
            save_on_success=True,
            response_type_on_missing_state="car_development_started",
        )

    if cmd_type == "finish_car_development_stage":
        return _run_response_handler(
            handle_finish_car_development_project_stage,
            command.get("scope"),
            save_on_success=True,
            response_type_on_missing_state="car_development_stage_finished",
        )

    if cmd_type == "set_car_development_allocation":
        return _run_response_handler(
            handle_set_car_development_allocation,
            command.get("scope"),
            command.get("allocation_percent"),
            save_on_success=True,
            response_type_on_missing_state="car_development_allocation_updated",
        )

    if cmd_type == "set_construction_allocation":
        return _run_response_handler(
            handle_set_construction_allocation,
            command.get("scope"),
            command.get("allocation_percent"),
            save_on_success=True,
            response_type_on_missing_state="construction_allocation_updated",
        )

    if cmd_type == "start_construction_project":
        return _run_response_handler(
            handle_start_construction_project,
            command.get("scope"),
            save_on_success=True,
            response_type_on_missing_state="construction_started",
        )

    if cmd_type == "set_test_chassis":
        return _run_response_handler(
            handle_set_test_chassis,
            command.get("chassis_id"),
            save_on_success=True,
            response_type_on_missing_state="test_chassis_updated",
        )

    if cmd_type == "set_race_chassis_assignments":
        return _run_response_handler(
            handle_set_race_chassis_assignments,
            command.get("driver1_chassis_id"),
            command.get("driver2_chassis_id"),
            save_on_success=True,
            response_type_on_missing_state="race_chassis_assignments_updated",
        )

    if cmd_type == "repair_chassis_wear":
        return _run_response_handler(
            handle_repair_chassis_wear,
            command.get("chassis_id"),
            command.get("wear_points"),
            save_on_success=True,
            response_type_on_missing_state="chassis_wear_repaired",
        )

    if cmd_type == "build_spare_set":
        return _run_response_handler(
            handle_build_spare_set,
            save_on_success=True,
            response_type_on_missing_state="spare_set_built",
        )

    if cmd_type == "get_staff":
        return _run_query(get_staff_payload, response_type="staff_data", error_context="staff")

    if cmd_type == "get_driver":
        state_or_error = _require_state()
        if isinstance(state_or_error, dict):
            return state_or_error
        driver_name = command.get("name")
        if not driver_name:
            return _error("Driver name is required")
        return _run_query(
            get_driver_payload,
            response_type="driver_data",
            error_context="driver",
            args=(driver_name,),
        )

    if cmd_type == "get_facilities":
        return _run_query(get_facilities_payload, response_type="facilities_data", error_context="facilities")

    if cmd_type == "get_car":
        return _run_query(get_car_payload, response_type="car_data", error_context="car data")

    if cmd_type == "get_finance":
        return _run_query(build_finance_payload, response_type="finance_data", error_context="finance")

    if cmd_type == "get_emails":
        return _run_query(get_emails_payload, response_type="email_data", error_context="emails")

    if cmd_type == "read_email":
        return _run_query(
            read_email_payload,
            response_type="email_read",
            error_context="reading email",
            args=(command.get("email_id"),),
        )

    return _error("Unknown command")


def main() -> None:
    logging.info("Backend started")
    print(json.dumps({"type": "status", "message": "Backend ready"}), flush=True)

    for line in sys.stdin:
        try:
            line = line.strip()
            if not line:
                continue

            data = json.loads(line)
            response = process_command(data)

            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON: {line}")
            print(json.dumps({"status": "error", "message": "Invalid JSON"}), flush=True)
        except Exception as e:
            logging.error(f"Error processing command: {e}")
            print(json.dumps({"status": "error", "message": str(e)}), flush=True)


if __name__ == "__main__":
    main()
