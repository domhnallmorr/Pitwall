from dataclasses import dataclass

from app.models.email import EmailCategory
from app.models.finance import TransactionCategory
from app.models.state import GameState, PlayerCarDevelopment


@dataclass
class DevelopmentSpec:
    key: str
    weeks: int
    total_cost: int
    speed_delta: int


class PlayerCarDevelopmentManager:
    MAX_WORKFORCE = 250
    SPECS = {
        "minor": DevelopmentSpec(key="minor", weeks=4, total_cost=100_000, speed_delta=1),
        "medium": DevelopmentSpec(key="medium", weeks=7, total_cost=750_000, speed_delta=3),
        "major": DevelopmentSpec(key="major", weeks=10, total_cost=1_500_000, speed_delta=5),
    }

    def _workforce_time_multiplier(self, workforce: int) -> float:
        bounded_workforce = max(0, min(int(workforce or 0), self.MAX_WORKFORCE))
        normalized = bounded_workforce / self.MAX_WORKFORCE
        # 250 staff => 1.0x base time, 0 staff => 2.0x base time.
        return 2.0 - normalized

    def _weeks_for_workforce(self, base_weeks: int, workforce: int) -> int:
        scaled = int(round(base_weeks * self._workforce_time_multiplier(workforce)))
        return max(base_weeks, min(base_weeks * 2, scaled))

    def get_catalog(self, workforce: int = MAX_WORKFORCE) -> list[dict]:
        return [
            {
                "type": spec.key,
                "weeks": self._weeks_for_workforce(spec.weeks, workforce),
                "total_cost": spec.total_cost,
                "weekly_cost": int(round(spec.total_cost / self._weeks_for_workforce(spec.weeks, workforce))),
                "speed_delta": spec.speed_delta,
            }
            for spec in self.SPECS.values()
        ]

    def start(self, state: GameState, development_type: str) -> PlayerCarDevelopment:
        if state.player_car_development and state.player_car_development.active:
            raise ValueError("A car development project is already active")

        key = (development_type or "").strip().lower()
        spec = self.SPECS.get(key)
        if spec is None:
            raise ValueError("Invalid development type")
        team = state.player_team
        if not team:
            raise ValueError("No player team assigned")

        duration_weeks = self._weeks_for_workforce(spec.weeks, team.workforce)
        weekly_cost = int(round(spec.total_cost / duration_weeks))
        state.player_car_development = PlayerCarDevelopment(
            active=True,
            development_type=spec.key,
            total_weeks=duration_weeks,
            weeks_remaining=duration_weeks,
            speed_delta=spec.speed_delta,
            total_cost=spec.total_cost,
            weekly_cost=weekly_cost,
            paid=0,
        )

        state.add_email(
            sender="Technical Department",
            subject=f"Car Development Started: {spec.key.title()}",
            body=(
                f"Development program initiated.\n\n"
                f"Type: {spec.key.title()}\n"
                f"Duration: {duration_weeks} weeks\n"
                f"Expected speed gain: +{spec.speed_delta}\n"
                f"Total cost: ${spec.total_cost:,}\n"
                f"Weekly cost: ${weekly_cost:,}"
            ),
            category=EmailCategory.GENERAL,
        )
        return state.player_car_development

    def process_week(self, state: GameState) -> dict | None:
        project = state.player_car_development
        if not project or not project.active:
            return None
        team = state.player_team
        if not team:
            return None

        remaining_cost = max(project.total_cost - project.paid, 0)
        if remaining_cost > 0 and project.weeks_remaining > 0:
            charge = min(remaining_cost, project.weekly_cost)
            state.finance.add_transaction(
                week=state.calendar.current_week,
                year=state.year,
                amount=-charge,
                category=TransactionCategory.DEVELOPMENT,
                description=f"Car development ({project.development_type}) weekly payment",
                event_name=None,
                event_type=None,
                circuit_country=None,
            )
            project.paid += charge

        if project.weeks_remaining > 0:
            project.weeks_remaining -= 1

        completed = project.weeks_remaining <= 0
        if completed:
            old_speed = team.car_speed
            team.car_speed = max(1, old_speed + project.speed_delta)
            project.active = False
            state.add_email(
                sender="Technical Department",
                subject=f"Car Development Complete: {project.development_type.title()}",
                body=(
                    f"Car development completed.\n\n"
                    f"Type: {project.development_type.title()}\n"
                    f"Car speed: {old_speed} -> {team.car_speed}\n"
                    f"Total paid: ${project.paid:,}"
                ),
                category=EmailCategory.GENERAL,
            )
            return {
                "status": "completed",
                "development_type": project.development_type,
                "old_speed": old_speed,
                "new_speed": team.car_speed,
                "paid": project.paid,
            }

        return {
            "status": "in_progress",
            "development_type": project.development_type,
            "weeks_remaining": project.weeks_remaining,
            "paid": project.paid,
            "total_cost": project.total_cost,
        }
