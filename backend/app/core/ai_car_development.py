import random

from app.models.calendar import EventType
from app.models.email import EmailCategory
from app.models.state import GameState


class AICarDevelopmentManager:
    MAX_WORKFORCE = 250
    MAX_FACILITIES = 100
    BASE_DEVELOPMENT_WEEKS = {
        "minor": 4,
        "medium": 7,
        "major": 10,
    }
    UPDATE_DELTAS = {
        "minor": 1,
        "medium": 3,
        "major": 5,
    }
    UPDATE_WEIGHTS = [0.5, 0.35, 0.15]
    RESOURCE_CAP_BASE = 55
    RESOURCE_CAP_RANGE = 35
    RESOURCE_CAP_EXCESS_RETENTION = 0.35

    def _race_weeks(self, state: GameState) -> list[int]:
        return sorted({e.week for e in state.calendar.events if e.type == EventType.RACE})

    def _workforce_time_multiplier(self, workforce: int) -> float:
        bounded_workforce = max(0, min(int(workforce or 0), self.MAX_WORKFORCE))
        normalized = bounded_workforce / self.MAX_WORKFORCE
        # 250 staff => 1.0x base time, 0 staff => 2.0x base time.
        return 2.0 - normalized

    def _development_weeks_for_team(self, update_type: str, workforce: int) -> int:
        base_weeks = self.BASE_DEVELOPMENT_WEEKS[update_type]
        scaled = int(round(base_weeks * self._workforce_time_multiplier(workforce)))
        return max(base_weeks, min(base_weeks * 2, scaled))

    def _resource_score(self, workforce: int, facilities: int) -> float:
        bounded_workforce = max(0, min(int(workforce or 0), self.MAX_WORKFORCE))
        bounded_facilities = max(0, min(int(facilities or 0), self.MAX_FACILITIES))
        workforce_score = bounded_workforce / self.MAX_WORKFORCE
        facilities_score = bounded_facilities / self.MAX_FACILITIES
        return (workforce_score + facilities_score) / 2

    def _update_weights_for_team(self, workforce: int, facilities: int) -> list[float]:
        resource_score = self._resource_score(workforce, facilities)
        return [
            0.70 - (0.25 * resource_score),
            0.23 + (0.10 * resource_score),
            0.07 + (0.15 * resource_score),
        ]

    def _resource_soft_cap(self, workforce: int, facilities: int) -> int:
        resource_score = self._resource_score(workforce, facilities)
        return int(round(self.RESOURCE_CAP_BASE + (self.RESOURCE_CAP_RANGE * resource_score)))

    def _compress_to_resource_cap(self, speed: int, workforce: int, facilities: int) -> int:
        soft_cap = self._resource_soft_cap(workforce, facilities)
        if speed <= soft_cap:
            return max(1, speed)
        excess = speed - soft_cap
        compressed = soft_cap + int(round(excess * self.RESOURCE_CAP_EXCESS_RETENTION))
        return max(1, compressed)

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
        if race_weeks:
            first_race_week = race_weeks[0]
        else:
            first_race_week = 1

        for team in state.teams:
            if state.player_team_id is not None and team.id == state.player_team_id:
                continue
            if not eligible_weeks:
                continue

            target_updates = min(random.randint(2, 6), len(eligible_weeks))
            min_gap = max(1, round(len(eligible_weeks) / (target_updates + 1)))
            selected_weeks: list[int] = []

            for _ in range(target_updates):
                update_type = random.choices(
                    ["minor", "medium", "major"],
                    weights=self._update_weights_for_team(team.workforce, team.facilities),
                    k=1,
                )[0]
                development_weeks = self._development_weeks_for_team(update_type, team.workforce)
                earliest_completion_week = max(first_race_week + 1, 1 + development_weeks)
                candidate_weeks = [w for w in eligible_weeks if w >= earliest_completion_week]
                gap_candidates = [
                    w
                    for w in candidate_weeks
                    if all(abs(w - selected) >= min_gap for selected in selected_weeks)
                ]
                pool = gap_candidates if gap_candidates else candidate_weeks
                if not pool:
                    continue

                week = random.choice(pool)
                selected_weeks.append(week)
                start_week = max(1, week - development_weeks)
                planned.append(
                    {
                        "year": state.year,
                        "team_id": team.id,
                        "team_name": team.name,
                        "start_week": start_week,
                        "week": week,
                        "development_weeks": development_weeks,
                        "update_type": update_type,
                        "delta": self.UPDATE_DELTAS[update_type],
                        "applied": False,
                    }
                )

        planned.sort(key=lambda item: (item["week"], item["team_name"]))
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
            proposed_speed = max(1, old_speed + int(update["delta"]))
            team.car_speed = max(
                old_speed,
                self._compress_to_resource_cap(proposed_speed, team.workforce, team.facilities),
            )
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
