import random
from typing import List, Dict, Any

from app.models.state import GameState


class RetirementManager:
    """
    Handles retirement planning and execution.
    """

    # Drivers younger than this are not considered for retirement planning.
    MIN_RETIREMENT_AGE = 34

    # Driver at this age or older is guaranteed to be in their final season.
    GUARANTEED_FINAL_SEASON_AGE = 39

    def mark_final_season_drivers(self, state: GameState) -> List[Dict[str, Any]]:
        """
        At season start, flag active drivers whose current season is their last.
        Returns a list of newly flagged drivers.
        """
        planned: List[Dict[str, Any]] = []
        team_lookup = {t.id: t for t in state.teams}

        for driver in state.drivers:
            if not driver.active:
                continue
            if driver.retirement_year is not None:
                continue

            probability = self._final_season_probability(driver.age)
            if probability <= 0:
                continue

            if random.random() <= probability:
                driver.retirement_year = state.year
                team_name = "Free Agent"
                if driver.team_id in team_lookup:
                    team_name = team_lookup[driver.team_id].name
                planned.append({
                    "name": driver.name,
                    "age": driver.age,
                    "team_name": team_name,
                })

        return planned

    def retire_due_drivers(self, state: GameState, completed_year: int) -> List[Dict[str, Any]]:
        """
        Retire drivers whose planned retirement is due at the end of completed_year.
        Returns a list of retired drivers.
        """
        retired: List[Dict[str, Any]] = []

        for driver in state.drivers:
            if not driver.active:
                continue
            if driver.retirement_year != completed_year:
                continue

            team_name = "Free Agent"
            old_team_id = driver.team_id
            for team in state.teams:
                if team.id == old_team_id:
                    team_name = team.name
                    if team.driver1_id == driver.id:
                        team.driver1_id = None
                    if team.driver2_id == driver.id:
                        team.driver2_id = None
                    break

            driver.active = False
            driver.team_id = None
            driver.role = None
            driver.retired_year = completed_year

            retired.append({
                "name": driver.name,
                "age": driver.age,
                "team_name": team_name,
            })

        return retired

    def _final_season_probability(self, age: int) -> float:
        """
        Returns retirement planning probability for the current season.
        """
        if age < self.MIN_RETIREMENT_AGE:
            return 0.0
        if age >= self.GUARANTEED_FINAL_SEASON_AGE:
            return 1.0

        # 34->15%, 35->30%, 36->45%, 37->60%, 38->75%
        return (age - self.MIN_RETIREMENT_AGE + 1) * 0.15
