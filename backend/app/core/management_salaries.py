from dataclasses import dataclass
from typing import Optional

from app.models.calendar import Event, EventType
from app.models.finance import TransactionCategory
from app.models.state import GameState
from app.core.finance_event_charges import (
    count_races,
    event_matches,
    post_event_transaction,
    resolve_event_charge_context,
)


@dataclass
class ManagementSalaryCharge:
    staff_name: str
    role_name: str
    annual_salary: int
    races_in_season: int
    applied_cost: int
    event_name: str
    country: str


class ManagementSalaryManager:
    def _count_races(self, state: GameState) -> int:
        return count_races(state)

    def calculate_race_salary(self, annual_salary: int, races_in_season: int) -> int:
        return max(0, int(round(max(0, annual_salary) / max(1, races_in_season))))

    def charge_for_event(self, state: GameState, event: Optional[Event]) -> list[ManagementSalaryCharge]:
        if not state.player_team:
            return []
        if not event_matches(event, [EventType.RACE]):
            return []

        races_in_season = self._count_races(state)
        context = resolve_event_charge_context(state, event)
        charges: list[ManagementSalaryCharge] = []

        team_id = state.player_team_id
        td = next((d for d in state.technical_directors if d.team_id == team_id), None)
        cm = next((m for m in state.commercial_managers if m.team_id == team_id), None)
        staff_entries = [
            ("Technical Director", td),
            ("Commercial Manager", cm),
        ]

        for role_name, staff_member in staff_entries:
            if staff_member is None:
                continue
            annual_salary = int(getattr(staff_member, "salary", 0) or 0)
            race_salary = self.calculate_race_salary(annual_salary, races_in_season)
            if race_salary <= 0:
                continue

            post_event_transaction(
                state,
                context,
                amount=-race_salary,
                category=TransactionCategory.MANAGEMENT_SALARIES,
                description=f"Race salary: {staff_member.name} ({role_name})",
            )

            charges.append(
                ManagementSalaryCharge(
                    staff_name=staff_member.name,
                    role_name=role_name,
                    annual_salary=annual_salary,
                    races_in_season=races_in_season,
                    applied_cost=race_salary,
                    event_name=context.event_name,
                    country=context.country,
                )
            )

        return charges
