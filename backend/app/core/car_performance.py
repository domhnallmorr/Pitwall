import random

from app.models.email import EmailCategory
from app.models.state import GameState


class CarPerformanceManager:
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
    ):
        self.staff_coeff = staff_coeff
        self.td_default_skill = td_default_skill
        self.tp_default_skill = tp_default_skill
        self.tp_skill_divisor = tp_skill_divisor
        self.tp_max_modifier = tp_max_modifier

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
            update = {
                "team_id": team.id,
                "team_name": team.name,
                "old_speed": old_speed,
                "new_speed": team.car_speed,
                "team_principal_modifier": tp_modifier,
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
