import sys
import json
import logging
from app.core.roster import load_roster
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
            teams, drivers = load_roster(year=0) # Load default
            CURRENT_STATE = GameState(year=2025, teams=teams, drivers=drivers)
            
            grid_json = CURRENT_STATE.get_grid_json()
            # Parse it back to object so it's nested in our response JSON properly
            grid_data = json.loads(grid_json) 
            
            return {
                "status": "success", 
                "message": "Roster loaded",
                "data": grid_data
            }
        except Exception as e:
            logging.error(f"Error loading roster: {e}")
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
