from dataclasses import dataclass
from typing import Iterable, Optional

from app.models.calendar import Event, EventType
from app.models.finance import TransactionCategory
from app.models.state import GameState


@dataclass(frozen=True)
class EventChargeContext:
    event_name: str
    event_type: str
    country: str
    week: int
    year: int


def count_races(state: GameState) -> int:
    return max(1, sum(1 for e in state.calendar.events if e.type == EventType.RACE))


def event_matches(event: Optional[Event], allowed_types: Iterable[EventType]) -> bool:
    if event is None:
        return False
    return event.type in set(allowed_types)


def resolve_event_charge_context(state: GameState, event: Event) -> EventChargeContext:
    circuit = next((c for c in state.circuits if c.name == event.name), None)
    return EventChargeContext(
        event_name=event.name,
        event_type=event.type.value,
        country=circuit.country if circuit else "Unknown",
        week=state.calendar.current_week,
        year=state.year,
    )


def post_event_transaction(
    state: GameState,
    context: EventChargeContext,
    *,
    amount: int,
    category: TransactionCategory,
    description: str,
) -> None:
    state.finance.add_transaction(
        week=context.week,
        year=context.year,
        amount=amount,
        category=category,
        description=description,
        event_name=context.event_name,
        event_type=context.event_type,
        circuit_country=context.country,
    )
