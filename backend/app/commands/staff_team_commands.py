import logging

from app.core.player_car_development import PlayerCarDevelopmentManager
from app.core.workforce_costs import WorkforceCostManager
from app.models.calendar import EventType
from app.models.email import EmailCategory
from app.models.finance import TransactionCategory
from app.models.state import GameState


def handle_start_car_development(state: GameState, logger: logging.Logger, development_type: str | None):
    try:
        if not development_type:
            return {"type": "car_development_started", "status": "error", "message": "development_type is required"}
        project = PlayerCarDevelopmentManager().start(state, development_type)
        return {
            "type": "car_development_started",
            "status": "success",
            "data": {
                "active": project.active,
                "development_type": project.development_type,
                "total_weeks": project.total_weeks,
                "weeks_remaining": project.weeks_remaining,
                "speed_delta": project.speed_delta,
                "total_cost": project.total_cost,
                "weekly_cost": project.weekly_cost,
                "paid": project.paid,
            },
        }
    except ValueError as ve:
        return {"type": "car_development_started", "status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error starting car development: {e}")
        return {"type": "car_development_started", "status": "error", "message": str(e)}


def handle_repair_car_wear(state: GameState, logger: logging.Logger, wear_points: int | None):
    try:
        team = state.player_team
        if not team:
            return {"type": "car_wear_repaired", "status": "error", "message": "No player team assigned"}
        current_wear = max(0, int(getattr(team, "car_wear", 0) or 0))
        if current_wear <= 0:
            return {"type": "car_wear_repaired", "status": "error", "message": "No wear to repair"}
        if wear_points is None:
            return {"type": "car_wear_repaired", "status": "error", "message": "wear_points is required"}
        requested = max(0, int(wear_points))
        if requested <= 0:
            return {"type": "car_wear_repaired", "status": "error", "message": "Repair amount must be greater than zero"}

        applied = min(requested, current_wear)
        cost = applied * 3_200
        team.car_wear = current_wear - applied

        state.finance.add_transaction(
            week=state.calendar.current_week,
            year=state.year,
            amount=-cost,
            category=TransactionCategory.MAINTENANCE,
            description=f"Car wear repair ({applied} wear)",
        )
        state.add_email(
            sender="Chief Mechanic",
            subject="Car Wear Repairs Completed",
            body=(
                f"Wear repairs have been completed.\n\n"
                f"Wear repaired: {applied}\n"
                f"Wear before: {current_wear}\n"
                f"Wear after: {team.car_wear}\n"
                f"Cost: ${cost:,}"
            ),
            category=EmailCategory.GENERAL,
        )
        return {
            "type": "car_wear_repaired",
            "status": "success",
            "data": {
                "applied_wear_repair": applied,
                "cost": cost,
                "wear_before": current_wear,
                "wear_after": team.car_wear,
            },
        }
    except Exception as e:
        logger.error(f"Error repairing car wear: {e}")
        return {"type": "car_wear_repaired", "status": "error", "message": str(e)}


def handle_update_workforce(state: GameState, logger: logging.Logger, workforce: int | None):
    try:
        team = state.player_team
        if not team:
            return {"type": "workforce_updated", "status": "error", "message": "No player team assigned"}
        if workforce is None:
            return {"type": "workforce_updated", "status": "error", "message": "workforce is required"}

        requested = int(workforce)
        if requested < 0 or requested > 250:
            return {"type": "workforce_updated", "status": "error", "message": "Workforce must be between 0 and 250"}

        previous = int(getattr(team, "workforce", 0) or 0)
        team.workforce = requested

        manager = WorkforceCostManager()
        races_in_season = max(1, sum(1 for e in state.calendar.events if e.type == EventType.RACE))
        projected_race_cost = manager.calculate_race_cost(team.workforce, races_in_season)
        annual_payroll = max(0, team.workforce) * manager.annual_avg_wage
        delta = team.workforce - previous

        state.add_email(
            sender="Human Resources",
            subject="Workforce Updated",
            body=(
                f"Workforce has been updated.\n\n"
                f"Previous staff count: {previous}\n"
                f"New staff count: {team.workforce}\n"
                f"Change: {delta:+}\n"
                f"Projected payroll per race: ${projected_race_cost:,}\n"
                f"Projected annual payroll: ${annual_payroll:,}"
            ),
            category=EmailCategory.GENERAL,
        )

        return {
            "type": "workforce_updated",
            "status": "success",
            "data": {
                "team_name": team.name,
                "previous_workforce": previous,
                "new_workforce": team.workforce,
                "delta": delta,
                "annual_avg_wage": manager.annual_avg_wage,
                "projected_race_cost": projected_race_cost,
                "projected_annual_payroll": annual_payroll,
                "races_in_season": races_in_season,
            },
        }
    except Exception as e:
        logger.error(f"Error updating workforce: {e}")
        return {"type": "workforce_updated", "status": "error", "message": str(e)}
