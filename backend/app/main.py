import sys
import json
import logging
from app.core.roster import load_roster
from app.core.standings import StandingsManager
from app.core.grid import GridManager
from app.core.engine import GameEngine
from app.core.retirement import RetirementManager
from app.core.prize_money import PrizeMoneyManager
from app.core.transport import TransportManager
from app.core.crash_damage import CrashDamageManager
from app.core.driver_wages import DriverWageManager
from app.core.workforce_costs import WorkforceCostManager
from app.core.finance_reporting import build_finance_report
from app.core.save_manager import save_game, load_game as load_game_file, has_save
from app.race.race_manager import RaceManager
from app.models.calendar import Calendar
from app.models.state import GameState
from app.models.email import EmailCategory
from app.models.finance import TransactionCategory

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
            teams, drivers, year, events, circuits, technical_directors = load_roster(
                year=0,
                include_technical_directors=True,
            ) # Load default
            calendar = Calendar(events=events, current_week=1) 
            CURRENT_STATE = GameState(
                year=year,
                teams=teams,
                drivers=drivers,
                technical_directors=technical_directors,
                calendar=calendar,
                circuits=circuits,
            )
            
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
                 teams, drivers, year, events, circuits, technical_directors = load_roster(
                     year=0,
                     include_technical_directors=True,
                 )
                 calendar = Calendar(events=events, current_week=1)
                 CURRENT_STATE = GameState(
                     year=year,
                     teams=teams,
                     drivers=drivers,
                     technical_directors=technical_directors,
                     calendar=calendar,
                     circuits=circuits,
                 )
            
            # 2. Find Team "Warrick"
            warrick_team = next((t for t in CURRENT_STATE.teams if t.name == "Warrick"), None)
            
            if not warrick_team:
                return {"status": "error", "message": "Team 'Warrick' not found in roster."}

            # 3. Assign Player
            CURRENT_STATE.player_team_id = warrick_team.id

            # 4. Initialize Finance with team starting balance
            from app.models.finance import Finance
            CURRENT_STATE.finance = Finance(balance=warrick_team.balance)
            prize_money_manager = PrizeMoneyManager()
            prize_money_manager.assign_initial_entitlement_from_roster_order(CURRENT_STATE)

            # 5. Send Welcome Email
            CURRENT_STATE.add_email(
                sender="Board of Directors",
                subject="Welcome to Pitwall",
                body=f"Welcome to {warrick_team.name}! As the new Team Principal, you have full control over the team's strategy, development, and driver lineup. We're counting on you to lead us to glory. Good luck!",
                category=EmailCategory.GENERAL
            )

            # 6. Plan season-end retirements and notify player about final seasons
            retirement_manager = RetirementManager()
            final_season_drivers = retirement_manager.mark_final_season_drivers(CURRENT_STATE)
            if final_season_drivers:
                lines = [f"- {d['name']} ({d['team_name']}), age {d['age']}" for d in final_season_drivers]
                CURRENT_STATE.add_email(
                    sender="Competition Office",
                    subject=f"Retirement Watch: {CURRENT_STATE.year} Final Seasons",
                    body=(
                        "The following drivers have announced this will be their final season:\n\n"
                        + "\n".join(lines)
                    ),
                    category=EmailCategory.SEASON
                )

            # 7. Capture initial grid snapshot for current season
            grid_manager = GridManager()
            grid_manager.capture_season_snapshot(CURRENT_STATE, year=CURRENT_STATE.year)
            
            # 8. Auto-save
            save_game(CURRENT_STATE)

            # 9. Return Success with Game Info
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

            year = command.get('year')
            grid_manager = GridManager()
            grid_json = grid_manager.get_grid_json(CURRENT_STATE, year=year)
            grid_data = json.loads(grid_json)
            
            return {
                "type": "grid_data",
                "status": "success",
                "data": grid_data,
                "year": year if year is not None else CURRENT_STATE.year
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
            current_event = CURRENT_STATE.calendar.current_event
            event_name = race_result.get("event_name", "Grand Prix")

            prize_money_manager = PrizeMoneyManager()
            prize_money_manager.process_race_payout(CURRENT_STATE)
            driver_wage_manager = DriverWageManager()
            driver_wage_manager.charge_for_event(
                CURRENT_STATE,
                current_event,
            )
            workforce_cost_manager = WorkforceCostManager()
            workforce_charge = workforce_cost_manager.charge_for_event(
                CURRENT_STATE,
                current_event,
            )
            transport_manager = TransportManager()
            transport_charge = transport_manager.charge_for_event(
                CURRENT_STATE,
                current_event,
                attended=True,
            )
            crash_damage_manager = CrashDamageManager()
            crash_damage_charges = crash_damage_manager.charge_for_race(
                CURRENT_STATE,
                race_result,
                current_event,
            )

            if transport_charge:
                CURRENT_STATE.add_email(
                    sender="Logistics Coordinator",
                    subject=f"Transport Confirmed: {transport_charge.event_name}",
                    body=(
                        f"Transport for {transport_charge.event_name} has been confirmed.\n\n"
                        f"Destination: {transport_charge.country}\n"
                        f"Cost: ${transport_charge.applied_cost:,}"
                    ),
                    category=EmailCategory.GENERAL
                )
            if workforce_charge:
                CURRENT_STATE.add_email(
                    sender="HR & Operations",
                    subject=f"Workforce Payroll Processed: {workforce_charge.event_name}",
                    body=(
                        f"Race workforce payroll has been processed for {workforce_charge.event_name}.\n\n"
                        f"Staff count: {workforce_charge.workforce}\n"
                        f"Cost this race: ${workforce_charge.applied_cost:,}\n"
                        f"(Based on average annual wage ${workforce_charge.annual_avg_wage:,})"
                    ),
                    category=EmailCategory.GENERAL,
                )
            if crash_damage_charges:
                total_damage = sum(c.applied_cost for c in crash_damage_charges)
                lines = "\n".join(
                    f"- {c.driver_name}: {c.tier.title()} damage (${c.applied_cost:,})"
                    for c in crash_damage_charges
                )
                CURRENT_STATE.add_email(
                    sender="Chief Mechanic",
                    subject=f"Crash Damage Report: {race_result.get('event_name', 'Grand Prix')}",
                    body=(
                        "The following crash repair work has been logged:\n\n"
                        f"{lines}\n\n"
                        f"Total repair cost: ${total_damage:,}"
                    ),
                    category=EmailCategory.GENERAL,
                )

            # Send race finance summary after all race-linked transactions are posted.
            race_transactions = [
                t for t in CURRENT_STATE.finance.transactions
                if t.week == CURRENT_STATE.calendar.current_week
                and t.year == CURRENT_STATE.year
                and t.event_name == event_name
                and t.event_type == "RACE"
            ]
            if race_transactions:
                income_total = sum(t.amount for t in race_transactions if t.amount > 0)
                expense_total = sum(-t.amount for t in race_transactions if t.amount < 0)
                net_total = income_total - expense_total

                def category_total(category):
                    return sum(t.amount for t in race_transactions if t.category == category)

                prize_total = category_total(TransactionCategory.PRIZE_MONEY)
                driver_wage_total = category_total(TransactionCategory.DRIVER_WAGES)
                workforce_total = category_total(TransactionCategory.WORKFORCE_WAGES)
                transport_total = category_total(TransactionCategory.TRANSPORT)
                crash_total = category_total(TransactionCategory.CRASH_DAMAGE)

                CURRENT_STATE.add_email(
                    sender="Finance Department",
                    subject=f"Race Finance Summary: {event_name}",
                    body=(
                        f"Financial summary for {event_name}:\n\n"
                        f"Prize money: {'+' if prize_total >= 0 else '-'}${abs(prize_total):,}\n"
                        f"Driver wages: {'+' if driver_wage_total >= 0 else '-'}${abs(driver_wage_total):,}\n"
                        f"Workforce payroll: {'+' if workforce_total >= 0 else '-'}${abs(workforce_total):,}\n"
                        f"Transport: {'+' if transport_total >= 0 else '-'}${abs(transport_total):,}\n"
                        f"Crash damage: {'+' if crash_total >= 0 else '-'}${abs(crash_total):,}\n\n"
                        f"Income: ${income_total:,}\n"
                        f"Expenses: ${expense_total:,}\n"
                        f"Net: {'+' if net_total >= 0 else '-'}${abs(net_total):,}"
                    ),
                    category=EmailCategory.GENERAL,
                )

            # Generate race result email
            winner = race_result["results"][0]
            
            # Find player team results
            player_team_id = CURRENT_STATE.player_team_id
            player_results = [r for r in race_result["results"] if r["team_id"] == player_team_id]
            player_lines = ""
            for pr in player_results:
                result_label = f"P{pr['position']}" if pr.get("position") else pr.get("status", "DNF")
                player_lines += f"\n  {result_label} - {pr['driver_name']} ({pr['points']} pts)"
            
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
                        "speed": d.speed,
                        "points": d.points,
                        "wage": d.wage,
                        "pay_driver": d.pay_driver,
                    })

            team_td = next(
                (td for td in CURRENT_STATE.technical_directors if td.team_id == player_team.id),
                None,
            )
            
            return {
                "type": "staff_data",
                "status": "success",
                "data": {
                    "team_name": player_team.name,
                    "drivers": team_drivers,
                    "technical_director": (
                        {
                            "id": team_td.id,
                            "name": team_td.name,
                            "country": team_td.country,
                            "age": team_td.age,
                            "skill": team_td.skill,
                            "contract_length": team_td.contract_length,
                            "salary": team_td.salary,
                        }
                        if team_td else None
                    ),
                    "player_workforce": player_team.workforce,
                    "teams": [
                        {
                            "id": t.id,
                            "name": t.name,
                            "country": t.country,
                            "workforce": t.workforce,
                        }
                        for t in CURRENT_STATE.teams
                    ],
                }
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

            driver = next((d for d in CURRENT_STATE.drivers if d.name == driver_name), None)
            if not driver:
                return {"status": "error", "message": f"Driver '{driver_name}' not found"}

            team = next((t for t in CURRENT_STATE.teams if t.id == driver.team_id), None)
            team_name = team.name if team else "Free Agent"
            state_year_results = CURRENT_STATE.driver_season_results.get(CURRENT_STATE.year, {})

            return {
                "type": "driver_data",
                "status": "success",
                "data": {
                    "id": driver.id,
                    "name": driver.name,
                    "age": driver.age,
                    "country": driver.country,
                    "team_name": team_name,
                    "speed": driver.speed,
                    "race_starts": driver.race_starts,
                    "wins": driver.wins,
                    "points": driver.points,
                    "wage": driver.wage,
                    "pay_driver": driver.pay_driver,
                    "season_results": sorted(
                        state_year_results.get(driver.id, []),
                        key=lambda r: r.get("round", 0)
                    ),
                }
            }
        except Exception as e:
            logging.error(f"Error getting driver: {e}")
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

    if cmd_type == 'get_car':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}

            teams_data = [
                {
                    "id": t.id,
                    "name": t.name,
                    "country": t.country,
                    "car_speed": t.car_speed,
                }
                for t in CURRENT_STATE.teams
            ]

            return {
                "type": "car_data",
                "status": "success",
                "data": {"teams": teams_data},
            }
        except Exception as e:
            logging.error(f"Error getting car data: {e}")
            return {"status": "error", "message": str(e)}

    if cmd_type == 'get_finance':
        try:
            if not CURRENT_STATE:
                return {"status": "error", "message": "Game not started"}
            
            transactions = [t.model_dump() for t in CURRENT_STATE.finance.transactions]
            report = build_finance_report(CURRENT_STATE)
            
            return {
                "type": "finance_data",
                "status": "success",
                "data": {
                    "balance": CURRENT_STATE.finance.balance,
                    "prize_money_entitlement": CURRENT_STATE.finance.prize_money_entitlement,
                    "prize_money_paid": CURRENT_STATE.finance.prize_money_paid,
                    "prize_money_remaining": max(
                        CURRENT_STATE.finance.prize_money_entitlement - CURRENT_STATE.finance.prize_money_paid, 0
                    ),
                    "prize_money_races_paid": CURRENT_STATE.finance.prize_money_races_paid,
                    "prize_money_total_races": CURRENT_STATE.finance.prize_money_total_races,
                    "transactions": transactions,
                    "summary": report["summary"],
                    "track_profit_loss": report["track_profit_loss"],
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
