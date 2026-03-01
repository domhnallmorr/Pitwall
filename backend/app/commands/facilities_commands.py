import logging

from app.core.facilities_upgrades import FacilitiesUpgradeManager
from app.models.state import GameState


def handle_facilities_upgrade_preview(state: GameState, logger: logging.Logger, points: int | None, years: int | None):
    try:
        if points is None or years is None:
            return {"type": "facilities_upgrade_preview", "status": "error", "message": "points and years are required"}
        preview = FacilitiesUpgradeManager().preview(state, int(points), int(years))
        return {
            "type": "facilities_upgrade_preview",
            "status": "success",
            "data": {
                "requested_points": preview.requested_points,
                "effective_points": preview.effective_points,
                "years": preview.years,
                "total_races": preview.total_races,
                "total_cost": preview.total_cost,
                "per_race_payment": preview.per_race_payment,
                "current_facilities": preview.current_facilities,
                "projected_facilities": preview.projected_facilities,
            },
        }
    except ValueError as ve:
        return {"type": "facilities_upgrade_preview", "status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error previewing facilities upgrade: {e}")
        return {"type": "facilities_upgrade_preview", "status": "error", "message": str(e)}


def handle_start_facilities_upgrade(state: GameState, logger: logging.Logger, points: int | None, years: int | None):
    try:
        if points is None or years is None:
            return {"type": "facilities_upgrade_started", "status": "error", "message": "points and years are required"}
        preview = FacilitiesUpgradeManager().start_upgrade(state, int(points), int(years))
        return {
            "type": "facilities_upgrade_started",
            "status": "success",
            "data": {
                "effective_points": preview.effective_points,
                "years": preview.years,
                "total_races": preview.total_races,
                "total_cost": preview.total_cost,
                "per_race_payment": preview.per_race_payment,
                "projected_facilities": preview.projected_facilities,
            },
        }
    except ValueError as ve:
        return {"type": "facilities_upgrade_started", "status": "error", "message": str(ve)}
    except Exception as e:
        logger.error(f"Error starting facilities upgrade: {e}")
        return {"type": "facilities_upgrade_started", "status": "error", "message": str(e)}
