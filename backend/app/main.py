import sys
import json
import logging
from app.core.grid import GridManager
from app.core.engine import GameEngine
from app.core.save_manager import save_game, load_game as load_game_file, has_save
from app.commands.game_commands import (
    build_finance_payload,
    handle_facilities_upgrade_preview,
    handle_get_replacement_candidates,
    handle_load_roster,
    handle_replace_driver,
    handle_start_facilities_upgrade,
    handle_simulate_race,
    handle_start_career,
)
from app.commands.query_commands import (
    get_car_payload,
    get_driver_payload,
    get_emails_payload,
    get_facilities_payload,
    get_grid_payload,
    get_staff_payload,
    get_standings_payload,
    read_email_payload,
)
from app.models.state import GameState

# Configure logging to write to a file, since stdout is used for IPC
logging.basicConfig(filename='backend_debug.log', level=logging.DEBUG)

# Global State Container
CURRENT_STATE: GameState = None

def process_command(command):
    global CURRENT_STATE
    logging.debug(f"Received command: {command}")
    
    cmd_type = command.get('type')

    if cmd_type == 'ping':
        return {"status": "success", "data": "pong"}
    
    if cmd_type == 'load_roster':
        state, response = handle_load_roster(logging)
        if state is not None:
            CURRENT_STATE = state
        return response

    if cmd_type == 'start_career':
        CURRENT_STATE, response = handle_start_career(CURRENT_STATE, logging, team_name=command.get("team_name"))
        if response.get("status") == "success":
            save_game(CURRENT_STATE)
        return response

    if cmd_type == 'get_grid':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}

            year = command.get('year')
            payload = get_grid_payload(CURRENT_STATE, year, GridManager())
            grid_data = json.loads(payload["grid_json"])
            
            return {
                "type": "grid_data",
                "status": "success",
                "data": grid_data,
                "year": payload["year"],
            }
        except Exception as e:
            logging.error(f"Error getting grid: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'get_calendar':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}
            
            schedule = CURRENT_STATE.calendar.get_schedule_data(CURRENT_STATE.circuits)
            
            return {
                "type": "calendar_data",
                "status": "success",
                "data": schedule
            }
        except Exception as e:
            logging.error(f"Error getting calendar: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'get_standings':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}
            standings_payload = get_standings_payload(CURRENT_STATE)
            
            return {
                "type": "standings_data",
                "status": "success",
                "data": standings_payload,
            }
        except Exception as e:
            logging.error(f"Error getting standings: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'advance_week':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}
            
            engine = GameEngine()
            summary = engine.advance_week(CURRENT_STATE)
            
            # Auto-save
            save_game(CURRENT_STATE)
            
            return {
                "type": "week_advanced",
                "status": "success",
                "data": summary
            }
        except Exception as e:
            logging.error(f"Error advancing week: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'skip_event':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}
            
            engine = GameEngine()
            summary = engine.handle_event_action(CURRENT_STATE, "skip")
            
            # Auto-save
            save_game(CURRENT_STATE)
            
            return {
                "type": "week_advanced", # Re-use same update type for UI
                "status": "success",
                "data": summary
            }
        except Exception as e:
            logging.error(f"Error skipping event: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'simulate_race':
        if not CURRENT_STATE:
            return {"status": "error", "message": "Game not started"}
        CURRENT_STATE, response = handle_simulate_race(CURRENT_STATE, logging)
        if response.get("status") == "success":
            save_game(CURRENT_STATE)
        return response

    if cmd_type == 'replace_driver':
        if not CURRENT_STATE:
            return {"status": "error", "message": "Game not started"}
        CURRENT_STATE, response = handle_replace_driver(
            CURRENT_STATE,
            logging,
            command.get("driver_id"),
            command.get("incoming_driver_id"),
        )
        if response.get("status") == "success":
            save_game(CURRENT_STATE)
        return response

    if cmd_type == 'get_replacement_candidates':
        if not CURRENT_STATE:
            return {"status": "error", "message": "Game not started"}
        return handle_get_replacement_candidates(CURRENT_STATE, logging, command.get("driver_id"))

    if cmd_type == 'preview_facilities_upgrade':
        if not CURRENT_STATE:
            return {"type": "facilities_upgrade_preview", "status": "error", "message": "Game not started"}
        return handle_facilities_upgrade_preview(CURRENT_STATE, logging, command.get("points"), command.get("years"))

    if cmd_type == 'start_facilities_upgrade':
        if not CURRENT_STATE:
            return {"type": "facilities_upgrade_started", "status": "error", "message": "Game not started"}
        response = handle_start_facilities_upgrade(CURRENT_STATE, logging, command.get("points"), command.get("years"))
        if response.get("status") == "success":
            save_game(CURRENT_STATE)
        return response

    if cmd_type == 'check_save':
        return {
            "type": "save_status",
            "status": "success",
            "data": {"has_save": has_save()}
        }

    if cmd_type == 'load_game':
        try:
            CURRENT_STATE = load_game_file()
            player_team = CURRENT_STATE.player_team
            
            return {
                "type": "game_loaded",
                "status": "success",
                "data": {
                    "team_name": player_team.name if player_team else "Unknown",
                    "week_display": CURRENT_STATE.week_display,
                    "next_event_display": CURRENT_STATE.next_event_display,
                    "year": CURRENT_STATE.year,
                    "balance": CURRENT_STATE.finance.balance,
                    "unread_count": sum(1 for e in CURRENT_STATE.emails if not e.read)
                }
            }
        except FileNotFoundError:
            return {"status": "error", "message": "No save file found"}
        except Exception as e:
            logging.error(f"Error loading game: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'get_staff':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}
            try:
                staff_payload = get_staff_payload(CURRENT_STATE)
            except ValueError as ve:
                return {"status": "error", "message": str(ve)}
            
            return {
                "type": "staff_data",
                "status": "success",
                "data": staff_payload,
            }
        except Exception as e:
            logging.error(f"Error getting staff: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'get_driver':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}

            driver_name = command.get('name')
            if not driver_name:
                return {"status": "error", "message": "Driver name is required"}
            try:
                driver_payload = get_driver_payload(CURRENT_STATE, driver_name)
            except ValueError as ve:
                return {"status": "error", "message": str(ve)}

            return {
                "type": "driver_data",
                "status": "success",
                "data": driver_payload,
            }
        except Exception as e:
            logging.error(f"Error getting driver: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'get_facilities':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}
            try:
                facilities_payload = get_facilities_payload(CURRENT_STATE)
            except ValueError as ve:
                return {"status": "error", "message": str(ve)}
            return {
                "type": "facilities_data",
                "status": "success",
                "data": facilities_payload,
            }
        except Exception as e:
            logging.error(f"Error getting facilities: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'get_car':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}

            return {
                "type": "car_data",
                "status": "success",
                "data": get_car_payload(CURRENT_STATE),
            }
        except Exception as e:
            logging.error(f"Error getting car data: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'get_finance':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}

            return {
                "type": "finance_data",
                "status": "success",
                "data": build_finance_payload(CURRENT_STATE),
            }
        except Exception as e:
            logging.error(f"Error getting finance: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'get_emails':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}
            return {
                "type": "email_data",
                "status": "success",
                "data": get_emails_payload(CURRENT_STATE),
            }
        except Exception as e:
            logging.error(f"Error getting emails: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'read_email':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}
            email_id = command.get('email_id')
            return {
                "type": "email_read",
                "status": "success",
                "data": read_email_payload(CURRENT_STATE, email_id),
            }
        except Exception as e:
            logging.error(f"Error reading email: {e}")
            return {"status": "error", "message": str(e)}

    return {"status": "error", "message": "Unknown command"}

def main():
    logging.info("Backend started")
    print(json.dumps({"type": "status", "message": "Backend ready"}), flush=True)

    for line in sys.stdin:
        try:
            line = line.strip()
            if not line:
                continue
            
            data = json.loads(line)
            response = process_command(data)
            
            # Send response back to Electron
            print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON: {line}")
            print(json.dumps({"status": "error", "message": "Invalid JSON"}), flush=True)
        except Exception as e:
            logging.error(f"Error processing command: {e}")
            print(json.dumps({"status": "error", "message": str(e)}), flush=True)

if __name__ == "__main__":
    main()
