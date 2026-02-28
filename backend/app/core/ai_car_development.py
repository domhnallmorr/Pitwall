import random

from app.models.calendar import EventType
from app.models.email import EmailCategory
from app.models.state import GameState


class AICarDevelopmentManager:
    UPDATE_DELTAS = {
        "minor": 1,
        "medium": 3,
        "major": 5,
    }
    UPDATE_WEIGHTS = [0.5, 0.35, 0.15]

    def _race_weeks(self, state: GameState) -> list[int]:
        return sorted({e.week for e in state.calendar.events if e.type == EventType.RACE})

    def _pick_spread_weeks(self, weeks: list[int], count: int) -> list[int]:
        if count <= 0 or not weeks:
            return []
        if count >= len(weeks):
            return sorted(weeks)

        selected: list[int] = []
        available = weeks.copy()
        min_gap = max(1, round(len(weeks) / (count + 1)))

        while len(selected) < count and available:
            chosen = random.choice(available)
            selected.append(chosen)
            available = [w for w in available if all(abs(w - s) >= min_gap for s in selected)]

        if len(selected) < count:
            remaining = [w for w in weeks if w not in selected]
            random.shuffle(remaining)
            selected.extend(remaining[: count - len(selected)])

        return sorted(selected[:count])

    def generate_for_season(self, state: GameState) -> list[dict]:
        race_weeks = self._race_weeks(state)
        eligible_weeks = race_weeks[1:]  # no updates before/at opening race
        planned: list[dict] = []

        for team in state.teams:
            if state.player_team_id is not None and team.id == state.player_team_id:
                continue
            if not eligible_weeks:
                continue

            target_updates = min(random.randint(2, 6), len(eligible_weeks))
            selected_weeks = self._pick_spread_weeks(eligible_weeks, target_updates)

            for week in selected_weeks:
                update_type = random.choices(
                    ["minor", "medium", "major"],
                    weights=self.UPDATE_WEIGHTS,
                    k=1,
                )[0]
                planned.append(
                    {
                        "year": state.year,
                        "team_id": team.id,
                        "team_name": team.name,
                        "week": week,
                        "update_type": update_type,
                        "delta": self.UPDATE_DELTAS[update_type],
                        "applied": False,
                    }
                )

        state.planned_ai_car_updates = planned
        return planned

    def apply_for_week(self, state: GameState, week: int | None = None) -> list[dict]:
        target_week = week if week is not None else state.calendar.current_week
        due = [
            u
            for u in state.planned_ai_car_updates
            if not u.get("applied") and u.get("year") == state.year and u.get("week") == target_week
        ]
        if not due:
            return []

        applied_updates: list[dict] = []
        for update in due:
            team = next((t for t in state.teams if t.id == update["team_id"]), None)
            if team is None:
                update["applied"] = True
                continue

            old_speed = team.car_speed
            team.car_speed = max(1, old_speed + int(update["delta"]))
            update["applied"] = True
            applied_updates.append(
                {
                    "team_id": team.id,
                    "team_name": team.name,
                    "update_type": update["update_type"],
                    "delta": int(update["delta"]),
                    "old_speed": old_speed,
                    "new_speed": team.car_speed,
                    "week": target_week,
                }
            )

        if applied_updates:
            lines = [
                f"- {u['team_name']}: {u['update_type'].title()} (+{u['delta']}) {u['old_speed']} -> {u['new_speed']}"
                for u in applied_updates
            ]
            state.add_email(
                sender="Technical Press Desk",
                subject=f"AI Car Development Updates: Week {target_week}",
                body="AI teams introduced car developments this week:\n\n" + "\n".join(lines),
                category=EmailCategory.GENERAL,
            )

        return applied_updates
