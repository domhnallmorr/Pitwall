import random

from app.models.calendar import Event, EventType
from app.models.email import EmailCategory
from app.models.finance import TransactionCategory
from app.models.state import GameState


class TestSessionManager:
    COST_PER_KM = 1_400
    GAIN_PER_KM_BLOCK = 300
    MAX_GAIN_PER_TEST = 5
    AI_ATTENDANCE_CHANCE = 0.7
    AI_MIN_KM = 400
    AI_MAX_KM = 1_800
    PLAYER_MAX_KM = 2_000
    MIN_SUCCESS_PROBABILITY = 0.35
    MAX_SUCCESS_PROBABILITY = 0.85
    MAX_WEAR = 100

    def _gain_for_km(self, kms: int) -> int:
        km_value = max(0, int(kms))
        return min(self.MAX_GAIN_PER_TEST, km_value // self.GAIN_PER_KM_BLOCK)

    def _success_probability(self, kms: int) -> float:
        km_value = max(0, min(self.PLAYER_MAX_KM, int(kms)))
        span = self.MAX_SUCCESS_PROBABILITY - self.MIN_SUCCESS_PROBABILITY
        return self.MIN_SUCCESS_PROBABILITY + ((km_value / self.PLAYER_MAX_KM) * span)

    def _get_circuit_country(self, state: GameState, event_name: str) -> str:
        return next((c.country for c in state.circuits if c.name == event_name), None) or "Unknown"

    def _apply_team_gain(self, team, gain: int) -> tuple[int, int]:
        old_speed = team.car_speed
        team.car_speed = max(1, old_speed + max(0, int(gain)))
        return old_speed, team.car_speed

    def _add_player_wear(self, player_team, kms: int) -> int:
        old_wear = max(0, int(getattr(player_team, "car_wear", 0) or 0))
        increment = max(0, int(kms)) // 100
        player_team.car_wear = min(self.MAX_WEAR, old_wear + increment)
        return player_team.car_wear

    def _resolve_gain_with_risk(self, kms: int) -> tuple[int, int, float, bool]:
        attempted_gain = self._gain_for_km(kms)
        if attempted_gain <= 0:
            return 0, 0, self._success_probability(kms), False
        probability = self._success_probability(kms)
        succeeded = random.random() < probability
        actual_gain = attempted_gain if succeeded else 0
        return attempted_gain, actual_gain, probability, succeeded

    def process_test_session(
        self,
        state: GameState,
        event: Event,
        player_attended: bool,
        player_kms: int = 0,
    ) -> dict:
        if event.type != EventType.TEST:
            return {"player": None, "ai_updates": []}

        player_team = state.player_team
        player_summary = None
        if player_team:
            kms = max(0, min(self.PLAYER_MAX_KM, int(player_kms or 0))) if player_attended else 0
            attempted_gain, actual_gain, probability, succeeded = self._resolve_gain_with_risk(kms) if player_attended else (0, 0, self._success_probability(0), False)
            old_speed, new_speed = self._apply_team_gain(player_team, actual_gain)
            new_wear = self._add_player_wear(player_team, kms) if player_attended else player_team.car_wear
            cost = kms * self.COST_PER_KM
            if cost > 0:
                state.finance.add_transaction(
                    week=state.calendar.current_week,
                    year=state.year,
                    amount=-cost,
                    category=TransactionCategory.TESTING,
                    description=f"Test running ({kms} km)",
                    event_name=event.name,
                    event_type=event.type.value,
                    circuit_country=self._get_circuit_country(state, event.name),
                )
            player_summary = {
                "team_name": player_team.name,
                "attended": bool(player_attended),
                "kms": kms,
                "attempted_gain": attempted_gain,
                "gain": actual_gain,
                "success_probability": probability,
                "succeeded": succeeded,
                "cost": cost,
                "old_speed": old_speed,
                "new_speed": new_speed,
                "wear": new_wear,
            }

        ai_updates = []
        for team in state.teams:
            if player_team and team.id == player_team.id:
                continue
            attended = random.random() < self.AI_ATTENDANCE_CHANCE
            if not attended:
                continue
            kms = random.randint(self.AI_MIN_KM, self.AI_MAX_KM)
            attempted_gain, actual_gain, probability, succeeded = self._resolve_gain_with_risk(kms)
            old_speed, new_speed = self._apply_team_gain(team, actual_gain)
            ai_updates.append(
                {
                    "team_name": team.name,
                    "kms": kms,
                    "attempted_gain": attempted_gain,
                    "gain": actual_gain,
                    "success_probability": probability,
                    "succeeded": succeeded,
                    "old_speed": old_speed,
                    "new_speed": new_speed,
                }
            )

        lines = [f"Test session results for {event.name}:\n"]
        if player_summary:
            if player_summary["attended"]:
                outcome_label = "success" if player_summary["succeeded"] else "no effective gain"
                lines.append(
                    f"Your team ({player_summary['team_name']}): {player_summary['kms']} km, "
                    f"attempted +{player_summary['attempted_gain']} / actual +{player_summary['gain']} "
                    f"({outcome_label}), cost ${player_summary['cost']:,} "
                    f"({player_summary['old_speed']} -> {player_summary['new_speed']}), "
                    f"success chance {round(player_summary['success_probability'] * 100)}%, "
                    f"wear now {player_summary['wear']}"
                )
            else:
                lines.append(f"Your team ({player_summary['team_name']}): did not attend")
        if ai_updates:
            lines.append("\nAI teams:")
            for update in ai_updates:
                outcome_label = "success" if update["succeeded"] else "no gain"
                lines.append(
                    f"- {update['team_name']}: {update['kms']} km, attempted +{update['attempted_gain']} / "
                    f"actual +{update['gain']} ({outcome_label}) ({update['old_speed']} -> {update['new_speed']})"
                )
        else:
            lines.append("\nAI teams: no attendees")

        state.add_email(
            sender="Technical Department",
            subject=f"Test Session Summary: {event.name}",
            body="\n".join(lines),
            category=EmailCategory.GENERAL,
        )

        return {
            "player": player_summary,
            "ai_updates": ai_updates,
        }
