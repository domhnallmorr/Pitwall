from app.models.state import GameState
from app.core.standings import StandingsManager
from app.core.retirement import RetirementManager
from app.core.recruitment import RecruitmentManager
from app.core.prize_money import PrizeMoneyManager
from app.core.grid import GridManager
from app.models.email import EmailCategory


class SeasonRolloverManager:
    """
    Handles the transition from one season to the next (e.g., 1998 -> 1999).
    Resets points, advances the year, and resets the calendar.
    """

    def __init__(self):
        self.retirement_manager = RetirementManager()
        self.recruitment_manager = RecruitmentManager()
        self.prize_money_manager = PrizeMoneyManager()
        self.grid_manager = GridManager()

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

        # 1b. Set next season prize entitlement from final constructor standings
        next_season_prize_money = self.prize_money_manager.assign_next_season_entitlement_from_standings(state)

        # 2. Retire drivers whose final season just ended
        retired_drivers = self.retirement_manager.retire_due_drivers(state, old_year)

        # 3. Increment year
        state.year += 1

        # 4. Reset points
        standings.reset_season(state)

        # 5. Reset calendar to week 1
        state.calendar.current_week = 1

        # 6. Clear processed events
        state.events_processed.clear()

        # 7. Update drivers (age, etc.)
        self._update_drivers(state)

        # 8. Fill vacancies from free agents
        signings = self.recruitment_manager.fill_vacancies(state)

        # 9. Snapshot the new season grid after retirements/signings
        self.grid_manager.capture_season_snapshot(state, year=state.year)

        # 10. Generate New Season email
        champion = final_drivers[0]["name"] if final_drivers else "Unknown"
        state.add_email(
            sender="Board of Directors",
            subject=f"New Season: {state.year}",
            body=f"The {old_year} season is over. {champion} won the Drivers' Championship.\n\nWelcome to {state.year}! All points have been reset. A new season awaits.",
            category=EmailCategory.SEASON
        )

        # 11. Notify player about confirmed retirements from last season
        if retired_drivers:
            retired_lines = [f"- {d['name']} ({d['team_name']})" for d in retired_drivers]
            state.add_email(
                sender="Competition Office",
                subject=f"Retirements Confirmed: End of {old_year}",
                body=(
                    f"The following drivers retired after the {old_year} season:\n\n"
                    + "\n".join(retired_lines)
                ),
                category=EmailCategory.SEASON
            )

        # 12. Queue and publish Week 1 signing announcements
        if signings:
            signing_lines = [f"- {s['team_name']}: {s['driver_name']} ({s['seat']})" for s in signings]
            state.queue_email(
                sender="Driver Market Desk",
                subject=f"Driver Signings: {state.year}",
                body=(
                    f"Completed signings for Week 1 of {state.year}:\n\n"
                    + "\n".join(signing_lines)
                ),
                week=1,
                year=state.year,
                category=EmailCategory.SEASON
            )
            state.publish_queued_emails(week=1, year=state.year)

        # 13. Plan and announce final seasons for the new year
        final_season_drivers = self.retirement_manager.mark_final_season_drivers(state)
        if final_season_drivers:
            lines = [f"- {d['name']} ({d['team_name']}), age {d['age']}" for d in final_season_drivers]
            state.add_email(
                sender="Competition Office",
                subject=f"Retirement Watch: {state.year} Final Seasons",
                body=(
                    "The following drivers have announced this will be their final season:\n\n"
                    + "\n".join(lines)
                ),
                category=EmailCategory.SEASON
            )

        return {
            "old_year": old_year,
            "new_year": state.year,
            "final_driver_standings": final_drivers,
            "final_constructor_standings": final_constructors,
            "retired_drivers": retired_drivers,
            "signings": signings,
            "next_season_prize_money": next_season_prize_money,
            "next_season_final_season_drivers": final_season_drivers,
        }

    def _update_drivers(self, state: GameState):
        """
        End-of-season driver updates.
        Currently: increment age for active drivers.
        Future: skill progression, retirement checks, contract expiry, etc.
        """
        for driver in state.drivers:
            if driver.active:
                driver.age += 1
