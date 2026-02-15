import random
from typing import List, Dict, Any, Optional

from app.models.state import GameState
from app.models.enums import DriverRole


class RecruitmentManager:
    """
    Handles offseason replacement recruitment.
    Current strategy: fill vacant seats with random free agents.
    """

    def fill_vacancies(self, state: GameState) -> List[Dict[str, Any]]:
        """
        Fill all team vacancies using random active free agents.
        Returns a list of completed signings.
        """
        signings: List[Dict[str, Any]] = []
        free_agents = self._get_free_agents(state)

        for team in state.teams:
            if team.driver1_id is None:
                signing = self._sign_for_seat(
                    state=state,
                    team_id=team.id,
                    seat="driver1_id",
                    role=DriverRole.DRIVER_1,
                    free_agents=free_agents
                )
                if signing:
                    signings.append(signing)

            if team.driver2_id is None:
                signing = self._sign_for_seat(
                    state=state,
                    team_id=team.id,
                    seat="driver2_id",
                    role=DriverRole.DRIVER_2,
                    free_agents=free_agents
                )
                if signing:
                    signings.append(signing)

        return signings

    def _get_free_agents(self, state: GameState):
        return [d for d in state.drivers if d.active and d.team_id is None]

    def _sign_for_seat(
        self,
        state: GameState,
        team_id: int,
        seat: str,
        role: DriverRole,
        free_agents: List,
    ) -> Optional[Dict[str, Any]]:
        if not free_agents:
            return None

        team = next((t for t in state.teams if t.id == team_id), None)
        if not team:
            return None

        driver = random.choice(free_agents)
        free_agents.remove(driver)

        setattr(team, seat, driver.id)
        driver.team_id = team.id
        driver.role = role

        seat_label = "Driver 1" if seat == "driver1_id" else "Driver 2"
        return {
            "team_id": team.id,
            "team_name": team.name,
            "seat": seat_label,
            "driver_id": driver.id,
            "driver_name": driver.name,
        }
