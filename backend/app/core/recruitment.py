import random
from typing import List, Dict, Any, Optional

from app.models.state import GameState
from app.models.enums import DriverRole
from app.race.constants import POINTS_TABLE


class RecruitmentManager:
    """
    Handles offseason replacement recruitment.
    Current strategy: fill vacant seats with random free agents.
    """
    PROTECTED_DRIVER_COUNT = 8
    ELITE_DRIVER_COUNT = 3
    TOP_TEAM_TARGET_COUNT = 4

    def fill_vacancies(self, state: GameState) -> List[Dict[str, Any]]:
        """
        Fill all team vacancies using random active free agents.
        Returns a list of completed signings.
        """
        signings: List[Dict[str, Any]] = []
        free_agents = self._get_free_agents(state)
        protected_rankings = self._protected_driver_rankings(state)
        protected_points = {
            driver_id: points
            for driver_id, points in protected_rankings[: self.PROTECTED_DRIVER_COUNT]
        }
        elite_driver_ids = {
            driver_id for driver_id, _ in protected_rankings[: self.ELITE_DRIVER_COUNT]
        }
        top_team_ids = self._top_team_ids(state)
        vacancies: List[tuple[int, str, DriverRole]] = []

        for team in state.teams:
            if team.driver1_id is None:
                vacancies.append((team.id, "driver1_id", DriverRole.DRIVER_1))

            if team.driver2_id is None:
                vacancies.append((team.id, "driver2_id", DriverRole.DRIVER_2))

        top_team_vacancies = [vacancy for vacancy in vacancies if vacancy[0] in top_team_ids]
        other_vacancies = [vacancy for vacancy in vacancies if vacancy[0] not in top_team_ids]

        for team_id, seat, role in top_team_vacancies:
            signing = self._sign_for_seat(
                state=state,
                team_id=team_id,
                seat=seat,
                role=role,
                free_agents=free_agents,
                protected_points=protected_points,
                preferred_driver_ids=elite_driver_ids,
            )
            if signing:
                signings.append(signing)

        signings.extend(
            self._ensure_elite_drivers_on_top_teams(
                state=state,
                free_agents=free_agents,
                elite_driver_ids=elite_driver_ids,
                protected_points=protected_points,
                top_team_ids=top_team_ids,
            )
        )

        for team_id, seat, role in other_vacancies:
            signing = self._sign_for_seat(
                state=state,
                team_id=team_id,
                seat=seat,
                role=role,
                free_agents=free_agents,
                protected_points=protected_points,
            )
            if signing:
                signings.append(signing)

        signings.extend(self._ensure_protected_drivers_on_grid(state, free_agents, protected_points))
        return signings

    def _get_free_agents(self, state: GameState):
        return [d for d in state.drivers if d.active and d.team_id is None]

    def _protected_driver_rankings(self, state: GameState) -> List[tuple[int, int]]:
        previous_year = state.year - 1
        year_bucket = state.driver_season_results.get(previous_year, {})
        if not year_bucket:
            return []

        points_by_driver: Dict[int, int] = {}
        for driver_id, results in year_bucket.items():
            total = 0
            for result in results:
                if result.get("status") == "FINISHED":
                    total += POINTS_TABLE.get(int(result.get("position", 0) or 0), 0)
            points_by_driver[int(driver_id)] = total

        ranked = sorted(
            (
                driver for driver in state.drivers
                if driver.active and driver.id in points_by_driver
            ),
            key=lambda driver: (
                points_by_driver.get(driver.id, 0),
                getattr(driver, "wins", 0),
                getattr(driver, "speed", 0),
            ),
            reverse=True,
        )
        return [(driver.id, points_by_driver.get(driver.id, 0)) for driver in ranked]

    def _top_team_ids(self, state: GameState) -> set[int]:
        ranked_teams = sorted(
            (
                team for team in state.teams
                if state.player_team_id is None or team.id != state.player_team_id
            ),
            key=lambda team: (
                getattr(team, "points", 0),
                getattr(team, "car_speed", 0),
                getattr(team, "facilities", 0),
                getattr(team, "workforce", 0),
            ),
            reverse=True,
        )
        return {team.id for team in ranked_teams[: self.TOP_TEAM_TARGET_COUNT]}

    def _sign_for_seat(
        self,
        state: GameState,
        team_id: int,
        seat: str,
        role: DriverRole,
        free_agents: List,
        protected_points: Dict[int, int],
        preferred_driver_ids: Optional[set[int]] = None,
    ) -> Optional[Dict[str, Any]]:
        if not free_agents:
            return None

        team = next((t for t in state.teams if t.id == team_id), None)
        if not team:
            return None

        preferred_driver_ids = preferred_driver_ids or set()
        protected_candidates = [
            driver for driver in free_agents
            if driver.id in protected_points and (
                not preferred_driver_ids or driver.id in preferred_driver_ids
            )
        ]
        if protected_candidates:
            driver = sorted(
                protected_candidates,
                key=lambda candidate: (
                    protected_points.get(candidate.id, 0),
                    getattr(candidate, "speed", 0),
                ),
                reverse=True,
            )[0]
        else:
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

    def _ensure_elite_drivers_on_top_teams(
        self,
        state: GameState,
        free_agents: List,
        elite_driver_ids: set[int],
        protected_points: Dict[int, int],
        top_team_ids: set[int],
    ) -> List[Dict[str, Any]]:
        if not elite_driver_ids or not top_team_ids:
            return []

        teams_by_id = {team.id: team for team in state.teams}
        signings: List[Dict[str, Any]] = []
        elite_free_agents = sorted(
            [driver for driver in free_agents if driver.id in elite_driver_ids],
            key=lambda driver: (
                protected_points.get(driver.id, 0),
                getattr(driver, "speed", 0),
            ),
            reverse=True,
        )

        for driver in elite_free_agents:
            replacement = self._find_displaceable_driver(
                state=state,
                protected_points=protected_points,
                restricted_team_ids=top_team_ids,
            )
            if replacement is None:
                break

            team_id, seat, displaced_driver = replacement
            team = teams_by_id.get(team_id)
            if team is None:
                continue

            displaced_driver.team_id = None
            displaced_driver.role = None
            displaced_driver.contract_length = 0
            if driver in free_agents:
                free_agents.remove(driver)

            setattr(team, seat, driver.id)
            driver.team_id = team.id
            driver.role = DriverRole.DRIVER_1 if seat == "driver1_id" else DriverRole.DRIVER_2

            signings.append(
                {
                    "team_id": team.id,
                    "team_name": team.name,
                    "seat": "Driver 1" if seat == "driver1_id" else "Driver 2",
                    "driver_id": driver.id,
                    "driver_name": driver.name,
                }
            )

        return signings

    def _ensure_protected_drivers_on_grid(
        self,
        state: GameState,
        free_agents: List,
        protected_points: Dict[int, int],
    ) -> List[Dict[str, Any]]:
        if not protected_points:
            return []

        teams_by_id = {team.id: team for team in state.teams}
        signings: List[Dict[str, Any]] = []
        protected_free_agents = sorted(
            [driver for driver in free_agents if driver.id in protected_points],
            key=lambda driver: (
                protected_points.get(driver.id, 0),
                getattr(driver, "speed", 0),
            ),
            reverse=True,
        )

        for driver in protected_free_agents:
            replacement = self._find_displaceable_driver(state, protected_points)
            if replacement is None:
                break

            team_id, seat, displaced_driver = replacement
            team = teams_by_id.get(team_id)
            if team is None:
                continue

            displaced_driver.team_id = None
            displaced_driver.role = None
            displaced_driver.contract_length = 0
            if driver in free_agents:
                free_agents.remove(driver)

            setattr(team, seat, driver.id)
            driver.team_id = team.id
            driver.role = DriverRole.DRIVER_1 if seat == "driver1_id" else DriverRole.DRIVER_2

            signings.append(
                {
                    "team_id": team.id,
                    "team_name": team.name,
                    "seat": "Driver 1" if seat == "driver1_id" else "Driver 2",
                    "driver_id": driver.id,
                    "driver_name": driver.name,
                }
            )

        return signings

    def _find_displaceable_driver(
        self,
        state: GameState,
        protected_points: Dict[int, int],
        restricted_team_ids: Optional[set[int]] = None,
    ) -> Optional[tuple[int, str, Any]]:
        driver_by_id = {driver.id: driver for driver in state.drivers}
        candidates: list[tuple[int, int, int, int, str, Any]] = []

        for team in state.teams:
            if state.player_team_id is not None and team.id == state.player_team_id:
                continue
            if restricted_team_ids is not None and team.id not in restricted_team_ids:
                continue
            for seat in ("driver1_id", "driver2_id"):
                driver_id = getattr(team, seat)
                driver = driver_by_id.get(driver_id)
                if driver is None or not driver.active:
                    continue
                if driver.id in protected_points:
                    continue
                candidates.append(
                    (
                        protected_points.get(driver.id, 0),
                        getattr(driver, "speed", 0),
                        getattr(driver, "wins", 0),
                        team.id,
                        seat,
                        driver,
                    )
                )

        if not candidates:
            return None

        _, _, _, team_id, seat, driver = min(candidates, key=lambda item: (item[0], item[1], item[2]))
        return team_id, seat, driver
