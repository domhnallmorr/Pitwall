from dataclasses import dataclass
from typing import Optional

from app.models.calendar import Event, EventType
from app.models.finance import TransactionCategory
from app.models.state import GameState


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
        return max(1, sum(1 for e in state.calendar.events if e.type == EventType.RACE))

    def calculate_race_salary(self, annual_salary: int, races_in_season: int) -> int:
        return max(0, int(round(max(0, annual_salary) / max(1, races_in_season))))

    def charge_for_event(self, state: GameState, event: Optional[Event]) -> list[ManagementSalaryCharge]:
        if not state.player_team:
            return []
        if event is None or event.type != EventType.RACE:
            return []

        races_in_season = self._count_races(state)
        circuit = next((c for c in state.circuits if c.name == event.name), None)
        country = circuit.country if circuit else "Unknown"
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

            state.finance.add_transaction(
                week=state.calendar.current_week,
                year=state.year,
                amount=-race_salary,
                category=TransactionCategory.MANAGEMENT_SALARIES,
                description=f"Race salary: {staff_member.name} ({role_name})",
                event_name=event.name,
                event_type=event.type.value,
                circuit_country=country,
            )

            charges.append(
                ManagementSalaryCharge(
                    staff_name=staff_member.name,
                    role_name=role_name,
                    annual_salary=annual_salary,
                    races_in_season=races_in_season,
                    applied_cost=race_salary,
                    event_name=event.name,
                    country=country,
                )
            )

        return charges
