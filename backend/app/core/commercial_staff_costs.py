from dataclasses import dataclass
from typing import Optional

from app.models.calendar import Event, EventType
from app.models.finance import TransactionCategory
from app.models.state import GameState


@dataclass
class CommercialStaffCharge:
    event_name: str
    country: str
    annual_avg_wage: int
    commercial_staff: int
    races_in_season: int
    applied_cost: int


class CommercialStaffCostManager:
    def __init__(self, annual_avg_wage: int = 20_000):
        self.annual_avg_wage = annual_avg_wage

    def _count_races(self, state: GameState) -> int:
        return max(1, sum(1 for e in state.calendar.events if e.type == EventType.RACE))

    def calculate_race_cost(self, commercial_staff: int, races_in_season: int) -> int:
        return max(0, int(round((max(0, commercial_staff) * self.annual_avg_wage) / max(1, races_in_season))))

    def charge_for_event(self, state: GameState, event: Optional[Event]) -> Optional[CommercialStaffCharge]:
        if not state.player_team:
            return None
        if event is None or event.type != EventType.RACE:
            return None

        commercial_staff = getattr(state.player_team, "commercial_staff", 0) or 0
        races_in_season = self._count_races(state)
        applied_cost = self.calculate_race_cost(commercial_staff, races_in_season)
        if applied_cost <= 0:
            return None

        circuit = next((c for c in state.circuits if c.name == event.name), None)
        country = circuit.country if circuit else "Unknown"

        state.finance.add_transaction(
            week=state.calendar.current_week,
            year=state.year,
            amount=-applied_cost,
            category=TransactionCategory.COMMERCIAL_STAFF_WAGES,
            description=f"Race commercial staff payroll ({commercial_staff} staff)",
            event_name=event.name,
            event_type=event.type.value,
            circuit_country=country,
        )

        return CommercialStaffCharge(
            event_name=event.name,
            country=country,
            annual_avg_wage=self.annual_avg_wage,
            commercial_staff=commercial_staff,
            races_in_season=races_in_season,
            applied_cost=applied_cost,
        )
