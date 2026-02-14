import sys
import json
import logging
from app.core.roster import load_roster
from app.core.standings import StandingsManager
from app.core.grid import GridManager
from app.models.calendar import Calendar
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
        try:
            teams, drivers, year, events, circuits = load_roster(year=0) # Load default
            calendar = Calendar(events=events, current_week=1) 
            CURRENT_STATE = GameState(year=year, teams=teams, drivers=drivers, calendar=calendar, circuits=circuits)
            
            grid_manager = GridManager()
            grid_json = grid_manager.get_grid_json(CURRENT_STATE)
            grid_data = json.loads(grid_json) 
            
            return {
                "status": "success", 
                "message": f"Roster loaded for {year}",
                "data": grid_data
            }
        except Exception as e:
            logging.error(f"Error loading roster: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'start_career':
        try:
            # 1. Ensure Roster is loaded
            if not CURRENT_STATE:
                 teams, drivers, year, events, circuits = load_roster(year=0)
                 calendar = Calendar(events=events, current_week=1)
                 CURRENT_STATE = GameState(year=year, teams=teams, drivers=drivers, calendar=calendar, circuits=circuits)
            
            # 2. Find Team "Warrick"
            warrick_team = next((t for t in CURRENT_STATE.teams if t.name == "Warrick"), None)
            
            if not warrick_team:
                return {"status": "error", "message": "Team 'Warrick' not found in roster."}

            # 3. Assign Player
            CURRENT_STATE.player_team_id = warrick_team.id
            
            # 4. Return Success with Game Info
            return {
                "type": "game_started",
                "status": "success",
                "data": {
                    "team_name": warrick_team.name,
                    "week_display": CURRENT_STATE.week_display,
                    "next_event_display": CURRENT_STATE.next_event_display,
                    "year": CURRENT_STATE.year
                }
            }
        except Exception as e:
            logging.error(f"Error starting career: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'get_grid':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}
            
            grid_manager = GridManager()
            grid_json = grid_manager.get_grid_json(CURRENT_STATE)
            grid_data = json.loads(grid_json)
            
            return {
                "type": "grid_data",
                "status": "success",
                "data": grid_data,
                "year": CURRENT_STATE.year
            }
        except Exception as e:
            logging.error(f"Error getting grid: {e}")
            return {"status": "error", "message": str(e)}

            return {
                "type": "grid_data",
                "status": "success",
                "data": grid_data,
                "year": CURRENT_STATE.year
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
            
            manager = StandingsManager()
            try:
                # Try Pydantic v2
                d_standings = [d.model_dump() for d in manager.get_driver_standings(CURRENT_STATE)]
                c_standings = [t.model_dump() for t in manager.get_constructor_standings(CURRENT_STATE)]
            except AttributeError:
                # Fallback to Pydantic v1
                d_standings = [d.dict() for d in manager.get_driver_standings(CURRENT_STATE)]
                c_standings = [t.dict() for t in manager.get_constructor_standings(CURRENT_STATE)]
            
            return {
                "type": "standings_data",
                "status": "success",
                "data": {
                    "drivers": d_standings,
                    "constructors": c_standings
                }
            }
        except Exception as e:
            logging.error(f"Error getting standings: {e}")
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
