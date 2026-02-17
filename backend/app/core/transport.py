import random
from dataclasses import dataclass
from typing import Optional

from app.models.calendar import Event, EventType
from app.models.finance import TransactionCategory
from app.models.state import GameState


class TransportCosts:
    LOW = 140_000
    MEDIUM = 240_000
    HIGH = 340_000
    MAX = 440_000


COUNTRY_COST_TIER = {
    "Australia": TransportCosts.MAX,
    "Brazil": TransportCosts.HIGH,
    "Argentina": TransportCosts.HIGH,
    "San Marino": TransportCosts.LOW,
    "Spain": TransportCosts.MEDIUM,
    "Monaco": TransportCosts.LOW,
    "Canada": TransportCosts.HIGH,
    "France": TransportCosts.LOW,
    "United Kingdom": TransportCosts.LOW,
    "Austria": TransportCosts.MEDIUM,
    "Germany": TransportCosts.LOW,
    "Hungary": TransportCosts.MEDIUM,
    "Belgium": TransportCosts.LOW,
    "Italy": TransportCosts.LOW,
    "Luxembourg": TransportCosts.MEDIUM,
    "Japan": TransportCosts.MAX,
}


@dataclass
class TransportCharge:
    event_name: str
    event_type: EventType
    country: str
    base_cost: int
    applied_cost: int


class TransportManager:
    def __init__(self, volatility: float = 0.15):
        self.volatility = volatility

    def calculate_cost(self, country: str, rng: Optional[random.Random] = None) -> tuple[int, int]:
        base_cost = COUNTRY_COST_TIER.get(country, TransportCosts.MEDIUM)
        random_source = rng if rng is not None else random
        multiplier = random_source.uniform(1 - self.volatility, 1 + self.volatility)
        applied_cost = int(round(base_cost * multiplier))
        return base_cost, max(1, applied_cost)

    def charge_for_event(self, state: GameState, event: Optional[Event], attended: bool) -> Optional[TransportCharge]:
        if not state.player_team:
            return None
        if event is None:
            return None
        if not attended:
            return None
        if event.type not in {EventType.RACE, EventType.TEST}:
            return None

        circuit = next((c for c in state.circuits if c.name == event.name), None)
        country = circuit.country if circuit else "Unknown"
        base_cost, applied_cost = self.calculate_cost(country)

        state.finance.add_transaction(
            week=state.calendar.current_week,
            year=state.year,
            amount=-applied_cost,
            category=TransactionCategory.TRANSPORT,
            description=f"Transport to {event.name} ({country})",
            event_name=event.name,
            event_type=event.type.value,
            circuit_country=country,
        )

        return TransportCharge(
            event_name=event.name,
            event_type=event.type,
            country=country,
            base_cost=base_cost,
            applied_cost=applied_cost,
        )
