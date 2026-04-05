import random

from app.models.email import EmailCategory
from app.models.state import GameState


class CarPerformanceManager:
    MAX_WORKFORCE = 250
    MAX_FACILITIES = 100
    MAX_TD_SKILL = 100
    """
    Handles end-of-season car performance recalculation.
    """

    def __init__(
        self,
        staff_coeff: float = 0.4,
        td_default_skill: int = 50,
        tp_default_skill: int = 50,
        tp_skill_divisor: int = 12,
        tp_max_modifier: int = 3,
        resource_cap_base: int = 55,
        resource_cap_range: int = 35,
        resource_cap_excess_retention: float = 0.35,
    ):
        self.staff_coeff = staff_coeff
        self.td_default_skill = td_default_skill
        self.tp_default_skill = tp_default_skill
        self.tp_skill_divisor = tp_skill_divisor
        self.tp_max_modifier = tp_max_modifier
        self.resource_cap_base = resource_cap_base
        self.resource_cap_range = resource_cap_range
        self.resource_cap_excess_retention = resource_cap_excess_retention

    def _get_td_skill(self, state: GameState, team_id: int) -> int:
        td = next((d for d in state.technical_directors if d.team_id == team_id), None)
        if td is None:
            return self.td_default_skill
        return td.skill if td.skill is not None else self.td_default_skill

    def _get_tp_skill(self, state: GameState, team_id: int) -> int:
        principal = next((p for p in state.team_principals if p.team_id == team_id), None)
        if principal is None:
            return self.tp_default_skill
        return principal.skill if principal.skill is not None else self.tp_default_skill

    def _ai_team_principal_modifier(self, team_principal_skill: int) -> int:
        raw_modifier = round((team_principal_skill - 50) / self.tp_skill_divisor)
        return max(-self.tp_max_modifier, min(self.tp_max_modifier, raw_modifier))

    def _resource_score(self, workforce: int, facilities: int, technical_director_skill: int) -> float:
        bounded_workforce = max(0, min(int(workforce or 0), self.MAX_WORKFORCE))
        bounded_facilities = max(0, min(int(facilities or 0), self.MAX_FACILITIES))
        bounded_td = max(0, min(int(technical_director_skill or 0), self.MAX_TD_SKILL))
        workforce_score = bounded_workforce / self.MAX_WORKFORCE
        facilities_score = bounded_facilities / self.MAX_FACILITIES
        td_score = bounded_td / self.MAX_TD_SKILL
        return (0.45 * workforce_score) + (0.35 * facilities_score) + (0.20 * td_score)

    def _resource_soft_cap(self, workforce: int, facilities: int, technical_director_skill: int) -> int:
        resource_score = self._resource_score(workforce, facilities, technical_director_skill)
        return int(round(self.resource_cap_base + (self.resource_cap_range * resource_score)))

    def _compress_to_resource_cap(self, speed: int, workforce: int, facilities: int, technical_director_skill: int) -> int:
        soft_cap = self._resource_soft_cap(workforce, facilities, technical_director_skill)
        if speed <= soft_cap:
            return max(1, speed)
        excess = speed - soft_cap
        compressed = soft_cap + int(round(excess * self.resource_cap_excess_retention))
        return max(1, compressed)

    def calculate_next_speed(self, workforce: int, facilities: int, technical_director_skill: int) -> int:
        random_element = random.randint(-30, 20)
        staff_speed = (max(0, workforce) * self.staff_coeff)
        base_speed = (staff_speed + max(0, facilities) + technical_director_skill + random_element) / 4
        return int(max(1, round(base_speed)))

    def apply_for_new_season(self, state: GameState) -> list[dict]:
        updates: list[dict] = []
        player_update: dict | None = None

        for team in state.teams:
            old_speed = team.car_speed
            td_skill = self._get_td_skill(state, team.id)
            team.car_speed = self.calculate_next_speed(team.workforce, team.facilities, td_skill)
            tp_modifier = 0
            if state.player_team_id != team.id:
                tp_skill = self._get_tp_skill(state, team.id)
                tp_modifier = self._ai_team_principal_modifier(tp_skill)
                team.car_speed = max(1, team.car_speed + tp_modifier)
                team.car_speed = self._compress_to_resource_cap(team.car_speed, team.workforce, team.facilities, td_skill)
            update = {
                "team_id": team.id,
                "team_name": team.name,
                "old_speed": old_speed,
                "new_speed": team.car_speed,
                "team_principal_modifier": tp_modifier,
                "resource_soft_cap": self._resource_soft_cap(team.workforce, team.facilities, td_skill) if state.player_team_id != team.id else None,
            }
            updates.append(update)
            if state.player_team_id == team.id:
                player_update = update

        if player_update:
            state.add_email(
                sender="Technical Department",
                subject=f"New Car Performance: {state.year}",
                body=(
                    f"Your car performance has been updated for {state.year}.\n\n"
                    f"Previous rating: {player_update['old_speed']}\n"
                    f"New rating: {player_update['new_speed']}"
                ),
                category=EmailCategory.SEASON,
            )

        return updates
