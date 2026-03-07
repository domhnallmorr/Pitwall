import random
from typing import Any, Dict, List

from app.models.state import GameState


class CommercialManagerRetirementManager:
    """
    Handles commercial manager retirements.
    """

    MIN_RETIREMENT_AGE = 50
    GUARANTEED_RETIREMENT_AGE = 65

    def retire_due_managers(self, state: GameState, completed_year: int) -> List[Dict[str, Any]]:
        retired: List[Dict[str, Any]] = []

        for manager in state.commercial_managers:
            if not getattr(manager, "active", True):
                continue

            probability = self._retirement_probability(manager.age)
            if probability <= 0:
                continue
            if random.random() > probability:
                continue

            team_name = "Free Agent"
            old_team_id = manager.team_id
            for team in state.teams:
                if team.id == old_team_id:
                    team_name = team.name
                    if team.commercial_manager_id == manager.id:
                        team.commercial_manager_id = None
                    break

            manager.active = False
            manager.team_id = None
            manager.contract_length = 0
            manager.retired_year = completed_year
            manager.retirement_year = completed_year

            retired.append(
                {
                    "name": manager.name,
                    "age": manager.age,
                    "team_name": team_name,
                }
            )

        return retired

    def _retirement_probability(self, age: int) -> float:
        if age < self.MIN_RETIREMENT_AGE:
            return 0.0
        if age >= self.GUARANTEED_RETIREMENT_AGE:
            return 1.0
        # 50->5%, 55->30%, 60->55%, 64->75%
        return min(1.0, (age - self.MIN_RETIREMENT_AGE + 1) * 0.05)

