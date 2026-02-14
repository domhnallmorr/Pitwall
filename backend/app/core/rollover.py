from app.models.state import GameState
from app.core.standings import StandingsManager
from app.models.email import EmailCategory


class SeasonRolloverManager:
    """
    Handles the transition from one season to the next (e.g., 1998 -> 1999).
    Resets points, advances the year, and resets the calendar.
    """

    def process_rollover(self, state: GameState) -> dict:
        """
        Processes the end-of-season rollover.
        Returns a summary of what changed, including final standings.
        """
        old_year = state.year

        # 1. Capture final standings before reset
        standings = StandingsManager()
        final_drivers = [
            {"name": d.name, "points": d.points}
            for d in standings.get_driver_standings(state)
            if d.points > 0
        ]
        final_constructors = [
            {"name": t.name, "points": t.points}
            for t in standings.get_constructor_standings(state)
            if t.points > 0
        ]

        # 2. Increment year
        state.year += 1

        # 3. Reset points
        standings.reset_season(state)

        # 4. Reset calendar to week 1
        state.calendar.current_week = 1

        # 5. Clear processed events
        state.events_processed.clear()

        # 6. Update drivers (age, etc.)
        self._update_drivers(state)

        # 7. Generate New Season email
        champion = final_drivers[0]["name"] if final_drivers else "Unknown"
        state.add_email(
            sender="Board of Directors",
            subject=f"New Season: {state.year}",
            body=f"The {old_year} season is over. {champion} won the Drivers' Championship.\n\nWelcome to {state.year}! All points have been reset. A new season awaits.",
            category=EmailCategory.SEASON
        )

        return {
            "old_year": old_year,
            "new_year": state.year,
            "final_driver_standings": final_drivers,
            "final_constructor_standings": final_constructors,
        }

    def _update_drivers(self, state: GameState):
        """
        End-of-season driver updates.
        Currently: increment age.
        Future: skill progression, retirement checks, contract expiry, etc.
        """
        for driver in state.drivers:
            driver.age += 1
