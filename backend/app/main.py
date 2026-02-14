import sys
import json
import logging
from app.core.roster import load_roster
from app.core.standings import StandingsManager
from app.core.grid import GridManager
from app.core.engine import GameEngine
from app.core.save_manager import save_game, load_game as load_game_file, has_save
from app.race.race_manager import RaceManager
from app.models.calendar import Calendar
from app.models.state import GameState
from app.models.email import EmailCategory

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

            # 4. Initialize Finance with team starting balance
            from app.models.finance import Finance
            CURRENT_STATE.finance = Finance(balance=warrick_team.balance)

            # 5. Send Welcome Email
            CURRENT_STATE.add_email(
                sender="Board of Directors",
                subject="Welcome to Pitwall",
                body=f"Welcome to {warrick_team.name}! As the new Team Principal, you have full control over the team's strategy, development, and driver lineup. We're counting on you to lead us to glory. Good luck!",
                category=EmailCategory.GENERAL
            )
            
            # 6. Auto-save
            save_game(CURRENT_STATE)

            # 7. Return Success with Game Info
            return {
                "type": "game_started",
                "status": "success",
                "data": {
                    "team_name": warrick_team.name,
                    "week_display": CURRENT_STATE.week_display,
                    "next_event_display": CURRENT_STATE.next_event_display,
                    "year": CURRENT_STATE.year,
                    "balance": CURRENT_STATE.finance.balance,
                    "unread_count": sum(1 for e in CURRENT_STATE.emails if not e.read)
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
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}
            
            race_manager = RaceManager()
            race_result = race_manager.simulate_race(CURRENT_STATE)

            # Generate race result email
            winner = race_result["results"][0]
            event_name = race_result.get("event_name", "Grand Prix")
            
            # Find player team results
            player_team_id = CURRENT_STATE.player_team_id
            player_results = [r for r in race_result["results"] if r["team_id"] == player_team_id]
            player_lines = ""
            for pr in player_results:
                player_lines += f"\n  P{pr['position']} - {pr['driver_name']} ({pr['points']} pts)"
            
            CURRENT_STATE.add_email(
                sender="Race Director",
                subject=f"Race Report: {event_name}",
                body=f"The {event_name} has concluded.\n\nWinner: {winner['driver_name']} ({winner['team_name']})\n\nYour Team Results:{player_lines}",
                category=EmailCategory.RACE_RESULT
            )
            
            # Auto-save
            save_game(CURRENT_STATE)
            
            return {
                "type": "race_result",
                "status": "success",
                "data": race_result
            }
        except Exception as e:
            logging.error(f"Error simulating race: {e}")
            return {"status": "error", "message": str(e)}

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
            
            player_team = next((t for t in CURRENT_STATE.teams if t.id == CURRENT_STATE.player_team_id), None)
            if not player_team:
                return {"status": "error", "message": "No player team assigned"}
            
            team_drivers = []
            for d in CURRENT_STATE.drivers:
                if d.team_id == player_team.id:
                    team_drivers.append({
                        "name": d.name,
                        "age": d.age,
                        "country": d.country,
                        "points": d.points,
                        "wage": d.wage,
                        "pay_driver": d.pay_driver,
                    })
            
            return {
                "type": "staff_data",
                "status": "success",
                "data": {
                    "team_name": player_team.name,
                    "drivers": team_drivers
                }
            }
        except Exception as e:
            logging.error(f"Error getting staff: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'get_facilities':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}
            
            player_team = CURRENT_STATE.player_team
            if not player_team:
                return {"status": "error", "message": "No player team assigned"}
            
            return {
                "type": "facilities_data",
                "status": "success",
                "data": {
                    "team_name": player_team.name,
                    "facilities": player_team.facilities
                }
            }
        except Exception as e:
            logging.error(f"Error getting facilities: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'get_finance':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}
            
            transactions = [t.model_dump() for t in CURRENT_STATE.finance.transactions]
            
            return {
                "type": "finance_data",
                "status": "success",
                "data": {
                    "balance": CURRENT_STATE.finance.balance,
                    "transactions": transactions
                }
            }
        except Exception as e:
            logging.error(f"Error getting finance: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'get_emails':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}
            
            emails_data = [e.model_dump() for e in reversed(CURRENT_STATE.emails)]  # Newest first
            unread_count = sum(1 for e in CURRENT_STATE.emails if not e.read)
            
            return {
                "type": "email_data",
                "status": "success",
                "data": {
                    "emails": emails_data,
                    "unread_count": unread_count
                }
            }
        except Exception as e:
            logging.error(f"Error getting emails: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'read_email':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}
            
            email_id = command.get('email_id')
            for email in CURRENT_STATE.emails:
                if email.id == email_id:
                    email.read = True
                    break
            
            unread_count = sum(1 for e in CURRENT_STATE.emails if not e.read)
            return {
                "type": "email_read",
                "status": "success",
                "data": {"email_id": email_id, "unread_count": unread_count}
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
