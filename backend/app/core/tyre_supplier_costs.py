from dataclasses import dataclass
from typing import Optional

from app.models.calendar import Event, EventType
from app.models.finance import TransactionCategory
from app.models.state import GameState


@dataclass
class TyreSupplierCharge:
    event_name: str
    country: str
    supplier_name: str
    deal_type: str
    yearly_cost: int
    races_in_season: int
    applied_cost: int


class TyreSupplierCostManager:
    def _count_races(self, state: GameState) -> int:
        return max(1, sum(1 for e in state.calendar.events if e.type == EventType.RACE))

    def calculate_race_cost(self, yearly_cost: int, races_in_season: int) -> int:
        return max(0, int(round(max(0, yearly_cost) / max(1, races_in_season))))

    def charge_for_event(self, state: GameState, event: Optional[Event]) -> Optional[TyreSupplierCharge]:
        team = state.player_team
        if not team:
            return None
        if event is None or event.type != EventType.RACE:
            return None

        supplier_name = getattr(team, "tyre_supplier_name", None)
        deal_type = getattr(team, "tyre_supplier_deal", None) or "-"
        yearly_cost = getattr(team, "tyre_supplier_yearly_cost", 0) or 0
        if not supplier_name or yearly_cost <= 0:
            return None

        races_in_season = self._count_races(state)
        applied_cost = self.calculate_race_cost(yearly_cost, races_in_season)
        if applied_cost <= 0:
            return None

        circuit = next((c for c in state.circuits if c.name == event.name), None)
        country = circuit.country if circuit else "Unknown"

        state.finance.add_transaction(
            week=state.calendar.current_week,
            year=state.year,
            amount=-applied_cost,
            category=TransactionCategory.TYRE_SUPPLIER,
            description=f"Tyre supplier fee: {supplier_name} ({deal_type})",
            event_name=event.name,
            event_type=event.type.value,
            circuit_country=country,
        )

        return TyreSupplierCharge(
            event_name=event.name,
            country=country,
            supplier_name=supplier_name,
            deal_type=deal_type,
            yearly_cost=yearly_cost,
            races_in_season=races_in_season,
            applied_cost=applied_cost,
        )
