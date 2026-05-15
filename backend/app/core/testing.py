import random

from app.core.player_chassis import apply_player_test_wear, get_player_test_chassis
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
    SETUP_BASE_GAIN = 8
    SETUP_MAX_GAIN_PER_TEST = 15

    def _gain_for_km(self, kms: int) -> int:
        km_value = max(0, int(kms))
        return min(self.MAX_GAIN_PER_TEST, km_value // self.GAIN_PER_KM_BLOCK)

    def _success_probability(self, kms: int) -> float:
        km_value = max(0, min(self.PLAYER_MAX_KM, int(kms)))
        span = self.MAX_SUCCESS_PROBABILITY - self.MIN_SUCCESS_PROBABILITY
        return self.MIN_SUCCESS_PROBABILITY + ((km_value / self.PLAYER_MAX_KM) * span)

    def _get_circuit_country(self, state: GameState, event_name: str) -> str:
        return next((c.country for c in state.circuits if c.name == event_name), None) or "Unknown"

    def _technical_director_skill(self, state: GameState) -> int:
        player_team = state.player_team
        if not player_team:
            return 0
        director_id = getattr(player_team, "technical_director_id", None)
        director = next(
            (
                item
                for item in getattr(state, "technical_directors", [])
                if item.team_id == player_team.id or (director_id is not None and item.id == director_id)
            ),
            None,
        )
        return max(0, min(100, int(getattr(director, "skill", 0) or 0)))

    def _driver_feedback_rating(self, state: GameState) -> int:
        player_team = state.player_team
        if not player_team:
            return 0
        driver_ids = {player_team.driver1_id, player_team.driver2_id}
        drivers = [driver for driver in state.drivers if driver.id in driver_ids]
        if not drivers:
            return 0
        ratings = [
            (max(0, min(100, int(getattr(driver, "consistency", 50) or 50))) + (max(1, min(5, int(getattr(driver, "racecraft", 3) or 3))) * 20)) / 2
            for driver in drivers
        ]
        return round(sum(ratings) / len(ratings))

    def _setup_gain_for_test(self, state: GameState, kms: int) -> int:
        if kms <= 0:
            return 0
        player_team = state.player_team
        facilities = max(0, min(100, int(getattr(player_team, "facilities", 0) or 0))) if player_team else 0
        full_test_gain = (
            self.SETUP_BASE_GAIN
            + (facilities // 25)
            + (self._technical_director_skill(state) // 35)
            + (self._driver_feedback_rating(state) // 35)
        )
        distance_factor = min(1.0, max(0, int(kms)) / 1_200)
        gain = round(full_test_gain * distance_factor)
        return max(0, min(self.SETUP_MAX_GAIN_PER_TEST, gain))

    def _apply_setup_gain(self, state: GameState, gain: int) -> tuple[int, int]:
        old_setup = max(1, min(100, int(getattr(state, "player_setup_knowledge", 1) or 1)))
        new_setup = max(1, min(100, old_setup + max(0, int(gain))))
        state.player_setup_knowledge = new_setup
        return old_setup, new_setup

    def _apply_team_gain(self, team, gain: int) -> tuple[int, int]:
        old_speed = team.car_speed
        team.car_speed = max(1, old_speed + max(0, int(gain)))
        return old_speed, team.car_speed

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
            setup_gain = self._setup_gain_for_test(state, kms) if player_attended else 0
            old_setup, new_setup = self._apply_setup_gain(state, setup_gain)
            selected_chassis = get_player_test_chassis(state)
            new_wear = apply_player_test_wear(state, kms) if player_attended else int(getattr(selected_chassis, "wear", 0) or 0)
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
                "setup_gain": setup_gain,
                "old_setup_knowledge": old_setup,
                "new_setup_knowledge": new_setup,
                "chassis_name": selected_chassis.name if selected_chassis else None,
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
                    f"setup knowledge {player_summary['old_setup_knowledge']} -> {player_summary['new_setup_knowledge']}, "
                    f"success chance {round(player_summary['success_probability'] * 100)}%, "
                    f"{player_summary['chassis_name'] or 'Chassis'} wear now {player_summary['wear']}"
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
