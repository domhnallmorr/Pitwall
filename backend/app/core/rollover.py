import random

from app.models.state import GameState
from app.core.standings import StandingsManager
from app.core.retirement import RetirementManager
from app.core.recruitment import RecruitmentManager
from app.core.prize_money import PrizeMoneyManager
from app.core.grid import GridManager
from app.core.roster import load_roster
from app.core.car_performance import CarPerformanceManager
from app.core.ai_car_development import AICarDevelopmentManager
from app.core.transfers import TransferManager
from app.core.management_transfers import CommercialManagerTransferManager
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
        self.car_performance_manager = CarPerformanceManager()
        self.ai_car_development_manager = AICarDevelopmentManager()
        self.transfer_manager = TransferManager()
        self.cm_transfer_manager = CommercialManagerTransferManager()
        self.ai_workforce_min = 90
        self.ai_workforce_max = 250

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
        management_updates = self._update_management_staff(state)

        # 8. Degrade facilities to reflect aging infrastructure.
        facilities_updates = self._degrade_facilities(state)

        # 9. AI teams may invest in facilities upgrades for the new season.
        ai_facilities_upgrades = self._apply_ai_facilities_upgrades(state)
        if ai_facilities_upgrades:
            lines = [
                f"- {u['team_name']}: {u['old_facilities']} -> {u['new_facilities']} (+{u['increase']})"
                for u in ai_facilities_upgrades
            ]
            body = (
                f"The following AI teams upgraded facilities for {state.year}:\n\n"
                + "\n".join(lines)
            )
        else:
            body = f"No AI teams upgraded facilities for {state.year}."
        state.add_email(
            sender="Competition Office",
            subject=f"Facilities Development Update: {state.year}",
            body=body,
            category=EmailCategory.SEASON,
        )

        # 10. Update AI workforce counts for the new season.
        ai_workforce_updates = self._update_ai_workforce(state)
        if ai_workforce_updates:
            lines = [
                f"- {u['team_name']}: {u['old_workforce']} -> {u['new_workforce']} ({u['delta']:+})"
                for u in ai_workforce_updates
            ]
            workforce_body = (
                f"The following AI teams adjusted workforce for {state.year}:\n\n"
                + "\n".join(lines)
            )
        else:
            workforce_body = f"No AI teams changed workforce for {state.year}."
        state.add_email(
            sender="Competition Office",
            subject=f"AI Workforce Update: {state.year}",
            body=workforce_body,
            category=EmailCategory.SEASON,
        )

        # 11. Load new seasonal driver entrants into free-agent pool
        new_entrants = self._add_new_season_drivers(state)

        # 12. Apply contract expiry and all announced transfer deals for the season that just ended.
        transfer_outcome = self.transfer_manager.apply_new_season_transfers(state, announced_year=old_year)
        management_transfer_outcome = self.cm_transfer_manager.apply_new_season_transfers(state, announced_year=old_year)

        # 13. Fill any remaining vacancies from free agents
        signings = self.recruitment_manager.fill_vacancies(state)

        # 14. Recalculate all team car performance for the new season.
        car_speed_updates = self.car_performance_manager.apply_for_new_season(state)
        if state.player_team:
            state.player_team.car_wear = 0

        # 15. Snapshot the new season grid after retirements/signings
        self.grid_manager.capture_season_snapshot(state, year=state.year)

        # 16. Generate New Season email
        champion = final_drivers[0]["name"] if final_drivers else "Unknown"
        state.add_email(
            sender="Board of Directors",
            subject=f"New Season: {state.year}",
            body=f"The {old_year} season is over. {champion} won the Drivers' Championship.\n\nWelcome to {state.year}! All points have been reset. A new season awaits.",
            category=EmailCategory.SEASON
        )

        # 17. Notify player about confirmed retirements from last season
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

        # 18. Notify player about new season entrants
        if new_entrants:
            entrant_lines = [f"- {d['name']} ({d['country']})" for d in new_entrants]
            state.add_email(
                sender="Competition Office",
                subject=f"New Drivers Entering {state.year}",
                body=(
                    f"The following drivers have entered the championship pool for {state.year}:\n\n"
                    + "\n".join(entrant_lines)
                ),
                category=EmailCategory.SEASON
            )

        # 19. Queue and publish Week 1 signing announcements
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

        # 20. Plan and announce final seasons for the new year
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

        # 21. Reset transfer planning for the new season and generate fresh AI plans.
        state.planned_ai_signings.clear()
        state.announced_ai_signings.clear()
        state.planned_ai_cm_signings.clear()
        state.announced_ai_cm_signings.clear()
        planned_transfers = self.transfer_manager.recompute_ai_signings(state)
        planned_management_transfers = self.cm_transfer_manager.recompute_ai_signings(state)
        planned_car_updates = self.ai_car_development_manager.generate_for_season(state)

        return {
            "old_year": old_year,
            "new_year": state.year,
            "final_driver_standings": final_drivers,
            "final_constructor_standings": final_constructors,
            "retired_drivers": retired_drivers,
            "facilities_updates": facilities_updates,
            "ai_facilities_upgrades": ai_facilities_upgrades,
            "ai_workforce_updates": ai_workforce_updates,
            "new_entrants": new_entrants,
            "management_updates": management_updates,
            "transfer_outcome": transfer_outcome,
            "management_transfer_outcome": management_transfer_outcome,
            "signings": signings,
            "car_speed_updates": car_speed_updates,
            "next_season_prize_money": next_season_prize_money,
            "next_season_final_season_drivers": final_season_drivers,
            "planned_transfers": planned_transfers,
            "planned_management_transfers": planned_management_transfers,
            "planned_car_updates": planned_car_updates,
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

    def _update_management_staff(self, state: GameState) -> dict:
        """
        End-of-season updates for technical directors and commercial managers.
        - Age increments by 1 for all management staff.
        - Team-assigned contracts decrement by 1.
        - Expired contracts vacate the role on the team.
        """
        teams_by_id = {team.id: team for team in state.teams}
        expired_technical_directors = []
        expired_commercial_managers = []

        for director in state.technical_directors:
            director.age += 1
            if director.team_id is None:
                continue
            if director.contract_length > 1:
                director.contract_length -= 1
                continue

            team = teams_by_id.get(director.team_id)
            if team and team.technical_director_id == director.id:
                team.technical_director_id = None
            expired_technical_directors.append(
                {"id": director.id, "name": director.name, "team_id": director.team_id, "team_name": team.name if team else None}
            )
            director.team_id = None
            director.contract_length = 0

        for manager in state.commercial_managers:
            manager.age += 1
            if manager.team_id is None:
                continue
            if manager.contract_length > 1:
                manager.contract_length -= 1
                continue

            team = teams_by_id.get(manager.team_id)
            if team and team.commercial_manager_id == manager.id:
                team.commercial_manager_id = None
            expired_commercial_managers.append(
                {"id": manager.id, "name": manager.name, "team_id": manager.team_id, "team_name": team.name if team else None}
            )
            manager.team_id = None
            manager.contract_length = 0

        return {
            "expired_technical_directors": expired_technical_directors,
            "expired_commercial_managers": expired_commercial_managers,
        }

    def _degrade_facilities(self, state: GameState) -> list[dict]:
        updates = []
        for team in state.teams:
            old_value = team.facilities if team.facilities is not None else 0
            team.facilities = max(1, old_value - 4)
            updates.append(
                {
                    "team_id": team.id,
                    "team_name": team.name,
                    "old_facilities": old_value,
                    "new_facilities": team.facilities,
                }
            )
        return updates

    def _apply_ai_facilities_upgrades(self, state: GameState) -> list[dict]:
        updates = []
        for team in state.teams:
            if state.player_team_id is not None and team.id == state.player_team_id:
                continue
            if random.random() >= 0.2:
                continue
            old_value = team.facilities if team.facilities is not None else 0
            increase = random.randint(20, 40)
            team.facilities = min(100, old_value + increase)
            updates.append(
                {
                    "team_id": team.id,
                    "team_name": team.name,
                    "old_facilities": old_value,
                    "increase": increase,
                    "new_facilities": team.facilities,
                }
            )
        return updates

    def _update_ai_workforce(self, state: GameState) -> list[dict]:
        updates = []
        for team in state.teams:
            if state.player_team_id is not None and team.id == state.player_team_id:
                continue

            old_workforce = int(team.workforce if team.workforce is not None else self.ai_workforce_min)
            # Keep AI workforce in the configured operating window each offseason.
            bounded_old = min(self.ai_workforce_max, max(self.ai_workforce_min, old_workforce))

            trend = random.choices(
                ["increase", "decrease", "flat"],
                weights=[0.45, 0.25, 0.30],
                k=1,
            )[0]

            delta = 0
            if trend == "increase":
                delta = random.choice([3, 5, 7, 10, 12, 15])
            elif trend == "decrease":
                delta = -random.choice([3, 5, 7, 9, 12])

            new_workforce = min(self.ai_workforce_max, max(self.ai_workforce_min, bounded_old + delta))
            applied_delta = new_workforce - bounded_old
            team.workforce = new_workforce

            if applied_delta != 0:
                updates.append(
                    {
                        "team_id": team.id,
                        "team_name": team.name,
                        "old_workforce": bounded_old,
                        "new_workforce": new_workforce,
                        "delta": applied_delta,
                    }
                )

        return updates

    def _add_new_season_drivers(self, state: GameState) -> list[dict]:
        """Load and append drivers whose start_year matches the new season."""
        _, season_drivers, _, _, _ = load_roster(year=state.year)
        existing_ids = {d.id for d in state.drivers}
        new_entrants = []

        for driver in season_drivers:
            if driver.id in existing_ids:
                continue
            # Ensure entrants begin as active free agents.
            driver.team_id = None
            driver.role = None
            driver.active = True
            driver.retirement_year = None
            driver.retired_year = None
            state.drivers.append(driver)
            new_entrants.append({
                "id": driver.id,
                "name": driver.name,
                "country": driver.country,
                "age": driver.age,
                "pay_driver": driver.pay_driver,
            })

        return new_entrants
