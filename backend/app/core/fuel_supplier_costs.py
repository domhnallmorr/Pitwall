from dataclasses import dataclass
from typing import Optional

from app.models.calendar import Event, EventType
from app.models.finance import TransactionCategory
from app.models.state import GameState


@dataclass
class FuelSupplierCharge:
    event_name: str
    country: str
    supplier_name: str
    deal_type: str
    yearly_cost: int
    races_in_season: int
    applied_amount: int


class FuelSupplierCostManager:
    def _count_races(self, state: GameState) -> int:
        return max(1, sum(1 for e in state.calendar.events if e.type == EventType.RACE))

    def calculate_race_amount(self, yearly_cost: int, races_in_season: int) -> int:
        if yearly_cost == 0:
            return 0
        per_race = int(round(abs(yearly_cost) / max(1, races_in_season)))
        return -per_race if yearly_cost > 0 else per_race

    def charge_for_event(self, state: GameState, event: Optional[Event]) -> Optional[FuelSupplierCharge]:
        team = state.player_team
        if not team:
            return None
        if event is None or event.type != EventType.RACE:
            return None

        supplier_name = getattr(team, "fuel_supplier_name", None)
        deal_type = getattr(team, "fuel_supplier_deal", None) or "-"
        yearly_cost = getattr(team, "fuel_supplier_yearly_cost", 0) or 0
        if not supplier_name or yearly_cost == 0:
            return None

        races_in_season = self._count_races(state)
        applied_amount = self.calculate_race_amount(yearly_cost, races_in_season)
        if applied_amount == 0:
            return None

        circuit = next((c for c in state.circuits if c.name == event.name), None)
        country = circuit.country if circuit else "Unknown"

        state.finance.add_transaction(
            week=state.calendar.current_week,
            year=state.year,
            amount=applied_amount,
            category=TransactionCategory.FUEL_SUPPLIER,
            description=f"Fuel supplier settlement: {supplier_name} ({deal_type})",
            event_name=event.name,
            event_type=event.type.value,
            circuit_country=country,
        )

        return FuelSupplierCharge(
            event_name=event.name,
            country=country,
            supplier_name=supplier_name,
            deal_type=deal_type,
            yearly_cost=yearly_cost,
            races_in_season=races_in_season,
            applied_amount=applied_amount,
        )
