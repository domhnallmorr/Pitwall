import random

from app.models.state import GameState
from app.core.standings import StandingsManager
from app.core.retirement import RetirementManager
from app.core.management_retirement import (
    CommercialManagerRetirementManager,
    TeamPrincipalRetirementManager,
    TechnicalDirectorRetirementManager,
)
from app.core.recruitment import RecruitmentManager
from app.core.prize_money import PrizeMoneyManager
from app.core.grid import GridManager
from app.core.roster import load_roster
from app.core.car_performance import CarPerformanceManager
from app.core.ai_car_development import AICarDevelopmentManager
from app.core.player_car_development import PlayerCarDevelopmentManager
from app.core.transfers import TransferManager
from app.core.management_transfers import (
    CommercialManagerTransferManager,
    EngineSupplierTransferManager,
    TeamPrincipalTransferManager,
    TechnicalDirectorTransferManager,
    TitleSponsorTransferManager,
    TyreSupplierTransferManager,
)
from app.core.rollover_notifications import (
    publish_week_one_signings_email,
    send_ai_workforce_update_email,
    send_facilities_update_email,
    send_new_drivers_email,
    send_new_season_email,
    send_new_title_sponsors_email,
    send_retirement_email,
    send_retirement_watch_email,
)
from app.core.rollover_updates import (
    AI_WORKFORCE_MAX,
    AI_WORKFORCE_MIN,
    add_new_season_drivers,
    add_new_season_title_sponsors,
    apply_ai_facilities_upgrades,
    degrade_facilities,
    update_ai_workforce,
    update_drivers,
    update_management_staff,
)


class SeasonRolloverManager:
    """
    Handles the transition from one season to the next (e.g., 1998 -> 1999).
    Resets points, advances the year, and resets the calendar.
    """

    def __init__(self):
        self.retirement_manager = RetirementManager()
        self.td_retirement_manager = TechnicalDirectorRetirementManager()
        self.cm_retirement_manager = CommercialManagerRetirementManager()
        self.tp_retirement_manager = TeamPrincipalRetirementManager()
        self.recruitment_manager = RecruitmentManager()
        self.prize_money_manager = PrizeMoneyManager()
        self.grid_manager = GridManager()
        self.car_performance_manager = CarPerformanceManager()
        self.ai_car_development_manager = AICarDevelopmentManager()
        self.player_car_development_manager = PlayerCarDevelopmentManager()
        self.transfer_manager = TransferManager()
        self.cm_transfer_manager = CommercialManagerTransferManager()
        self.engine_supplier_transfer_manager = EngineSupplierTransferManager()
        self.tp_transfer_manager = TeamPrincipalTransferManager()
        self.td_transfer_manager = TechnicalDirectorTransferManager()
        self.title_sponsor_transfer_manager = TitleSponsorTransferManager()
        self.tyre_supplier_transfer_manager = TyreSupplierTransferManager()
        self.ai_workforce_min = AI_WORKFORCE_MIN
        self.ai_workforce_max = AI_WORKFORCE_MAX

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
        if final_drivers:
            champion_name = final_drivers[0]["name"]
            champion = next((driver for driver in state.drivers if driver.name == champion_name), None)
            if champion is not None:
                champion.championships += 1

        # 1b. Set next season prize entitlement from final constructor standings
        next_season_prize_money = self.prize_money_manager.assign_next_season_entitlement_from_standings(state)

        # 2. Retire drivers whose final season just ended
        retired_drivers = self.retirement_manager.retire_due_drivers(state, old_year)
        retired_technical_directors = self.td_retirement_manager.retire_due_directors(state, old_year)
        retired_commercial_managers = self.cm_retirement_manager.retire_due_managers(state, old_year)
        retired_team_principals = self.tp_retirement_manager.retire_due_principals(state, old_year)

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
        send_facilities_update_email(state, ai_facilities_upgrades)

        # 10. Update AI workforce counts for the new season.
        ai_workforce_updates = self._update_ai_workforce(state)
        send_ai_workforce_update_email(state, ai_workforce_updates)

        # 11. Load new seasonal driver entrants and title sponsors for the new year
        new_entrants = self._add_new_season_drivers(state)
        new_title_sponsors = self._add_new_season_title_sponsors(state)

        # 12. Apply contract expiry and all announced transfer deals for the season that just ended.
        transfer_outcome = self.transfer_manager.apply_new_season_transfers(state, announced_year=old_year)
        management_transfer_outcome = self.cm_transfer_manager.apply_new_season_transfers(state, announced_year=old_year)
        team_principal_transfer_outcome = self.tp_transfer_manager.apply_new_season_transfers(state, announced_year=old_year)
        td_transfer_outcome = self.td_transfer_manager.apply_new_season_transfers(state, announced_year=old_year)
        title_sponsor_transfer_outcome = self.title_sponsor_transfer_manager.apply_new_season_transfers(
            state, announced_year=old_year
        )
        engine_supplier_transfer_outcome = self.engine_supplier_transfer_manager.apply_new_season_transfers(
            state, announced_year=old_year
        )
        tyre_supplier_transfer_outcome = self.tyre_supplier_transfer_manager.apply_new_season_transfers(
            state, announced_year=old_year
        )

        offseason_tp_fillings = self.tp_transfer_manager.fill_current_vacancies(state)
        if offseason_tp_fillings:
            team_principal_transfer_outcome["offseason_fillings"] = offseason_tp_fillings

        # 13. Fill any remaining vacancies from free agents
        signings = self.recruitment_manager.fill_vacancies(state)

        # 14. Recalculate all team car performance for the new season.
        car_speed_updates = self.car_performance_manager.apply_for_new_season(state)
        player_next_year_chassis_update = self.player_car_development_manager.apply_next_year_project_for_rollover(state)
        self.player_car_development_manager.reset_for_new_season(state)
        if state.player_team:
            state.player_team.car_wear = 0

        # 15. Snapshot the new season grid after retirements/signings
        self.grid_manager.capture_season_snapshot(state, year=state.year)

        # 16. Generate New Season email
        champion = final_drivers[0]["name"] if final_drivers else "Unknown"
        send_new_season_email(state, old_year, champion)

        # 17. Notify player about confirmed retirements from last season
        send_retirement_email(
            state,
            f"Retirements Confirmed: End of {old_year}",
            f"The following drivers retired after the {old_year} season:",
            retired_drivers,
        )
        send_retirement_email(
            state,
            f"Technical Director Retirements Confirmed: End of {old_year}",
            f"The following technical directors retired after the {old_year} season:",
            retired_technical_directors,
        )
        send_retirement_email(
            state,
            f"Team Principal Retirements Confirmed: End of {old_year}",
            f"The following team principals retired after the {old_year} season:",
            retired_team_principals,
        )
        send_retirement_email(
            state,
            f"Management Retirements Confirmed: End of {old_year}",
            f"The following commercial managers retired after the {old_year} season:",
            retired_commercial_managers,
        )

        # 18. Notify player about new season entrants
        send_new_drivers_email(state, new_entrants)
        send_new_title_sponsors_email(state, new_title_sponsors)

        # 19. Queue and publish Week 1 signing announcements
        publish_week_one_signings_email(state, signings)

        # 20. Plan and announce final seasons for the new year
        final_season_drivers = self.retirement_manager.mark_final_season_drivers(state)
        send_retirement_watch_email(state, final_season_drivers)

        # 21. Reset transfer planning for the new season and generate fresh AI plans.
        state.planned_ai_signings.clear()
        state.announced_ai_signings.clear()
        state.planned_ai_cm_signings.clear()
        state.announced_ai_cm_signings.clear()
        state.planned_ai_td_signings.clear()
        state.announced_ai_td_signings.clear()
        state.planned_ai_tp_signings.clear()
        state.announced_ai_tp_signings.clear()
        state.planned_ai_title_sponsor_signings.clear()
        state.announced_ai_title_sponsor_signings.clear()
        state.planned_ai_engine_supplier_signings.clear()
        state.announced_ai_engine_supplier_signings.clear()
        state.planned_ai_tyre_supplier_signings.clear()
        state.announced_ai_tyre_supplier_signings.clear()
        planned_transfers = self.transfer_manager.recompute_ai_signings(state)
        planned_management_transfers = self.cm_transfer_manager.recompute_ai_signings(state)
        planned_tp_transfers = self.tp_transfer_manager.recompute_ai_signings(state)
        planned_td_transfers = self.td_transfer_manager.recompute_ai_signings(state)
        planned_title_sponsor_transfers = self.title_sponsor_transfer_manager.recompute_ai_signings(state)
        planned_engine_supplier_transfers = self.engine_supplier_transfer_manager.recompute_ai_signings(state)
        planned_tyre_supplier_transfers = self.tyre_supplier_transfer_manager.recompute_ai_signings(state)
        planned_car_updates = self.ai_car_development_manager.generate_for_season(state)

        return {
            "old_year": old_year,
            "new_year": state.year,
            "final_driver_standings": final_drivers,
            "final_constructor_standings": final_constructors,
            "retired_drivers": retired_drivers,
            "retired_technical_directors": retired_technical_directors,
            "retired_commercial_managers": retired_commercial_managers,
            "retired_team_principals": retired_team_principals,
            "facilities_updates": facilities_updates,
            "ai_facilities_upgrades": ai_facilities_upgrades,
            "ai_workforce_updates": ai_workforce_updates,
            "new_entrants": new_entrants,
            "new_title_sponsors": new_title_sponsors,
            "management_updates": management_updates,
            "transfer_outcome": transfer_outcome,
            "management_transfer_outcome": management_transfer_outcome,
            "team_principal_transfer_outcome": team_principal_transfer_outcome,
            "td_transfer_outcome": td_transfer_outcome,
            "title_sponsor_transfer_outcome": title_sponsor_transfer_outcome,
            "engine_supplier_transfer_outcome": engine_supplier_transfer_outcome,
            "tyre_supplier_transfer_outcome": tyre_supplier_transfer_outcome,
            "signings": signings,
            "car_speed_updates": car_speed_updates,
            "player_next_year_chassis_update": player_next_year_chassis_update,
            "next_season_prize_money": next_season_prize_money,
            "next_season_final_season_drivers": final_season_drivers,
            "planned_transfers": planned_transfers,
            "planned_management_transfers": planned_management_transfers,
            "planned_tp_transfers": planned_tp_transfers,
            "planned_td_transfers": planned_td_transfers,
            "planned_title_sponsor_transfers": planned_title_sponsor_transfers,
            "planned_engine_supplier_transfers": planned_engine_supplier_transfers,
            "planned_tyre_supplier_transfers": planned_tyre_supplier_transfers,
            "planned_car_updates": planned_car_updates,
        }

    def _update_drivers(self, state: GameState):
        update_drivers(state)

    def _update_management_staff(self, state: GameState) -> dict:
        return update_management_staff(state)

    def _degrade_facilities(self, state: GameState) -> list[dict]:
        return degrade_facilities(state)

    def _apply_ai_facilities_upgrades(self, state: GameState) -> list[dict]:
        return apply_ai_facilities_upgrades(state, random_module=random)

    def _update_ai_workforce(self, state: GameState) -> list[dict]:
        return update_ai_workforce(
            state,
            ai_workforce_min=self.ai_workforce_min,
            ai_workforce_max=self.ai_workforce_max,
            random_module=random,
        )

    def _add_new_season_drivers(self, state: GameState) -> list[dict]:
        return add_new_season_drivers(state, load_roster_func=load_roster)

    def _add_new_season_title_sponsors(self, state: GameState) -> list[dict]:
        return add_new_season_title_sponsors(state, load_roster_func=load_roster)
